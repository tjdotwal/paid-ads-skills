#!/usr/bin/env python3
"""Call every MCP server against the live APIs. Requires real credentials.

This is the half that scripts/smoke-test.py cannot do. CI runs without
credentials, so it can prove a server starts and still exposes its tools, but
not that a tool's request payload is still valid. Both bugs fixed in
keyword-planner 2.0.0 were exactly that: `get_keyword_forecast` posted a field
the API does not define, and `get_historical_metrics` silently returned zero
results. A tools/list check sees neither.

Every call here is read-only. Nothing is created, updated, or deleted.

Usage:  python3 scripts/live-check.py [plugin ...]
        python3 scripts/live-check.py keyword-planner
Reads credentials from ~/.env via each plugin's own start script.
Exit:   0 all passed, 1 one or more failures, 2 nothing could run
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (tool, arguments, predicate on the returned text). Read-only calls only.
CHECKS = {
    "google-ads": {
        "script": "google-ads/scripts/start-server.sh",
        "calls": [
            ("list_accounts", {}, lambda t: "Account ID" in t),
        ],
    },
    "meta-ads": {
        "script": "meta-ads/scripts/start-server.sh",
        "calls": [
            ("ad_account_list", {}, lambda t: '"id"' in t or "act_" in t),
        ],
    },
    "keyword-planner": {
        "script": "keyword-planner/scripts/start-keyword-planner.sh",
        "calls": [
            # All three, because all three are what broke.
            (
                "generate_keyword_ideas",
                {"seed_keywords": ["managed it services"], "geo_targets": ["CA"],
                 "page_size": 5},
                lambda t: "Avg monthly" in t and "keyword(s)" in t,
            ),
            (
                "get_historical_metrics",
                {"keywords": ["managed it services"], "geo_targets": ["CA"]},
                # The old binary returned an empty set here rather than erroring,
                # so an empty result must count as a failure, not a pass.
                lambda t: "Avg monthly" in t and "No keywords returned" not in t,
            ),
            (
                "get_keyword_forecast",
                {"keywords": ["managed it services"], "geo_targets": ["CA"],
                 "max_cpc": 5.0, "forecast_days": 7},
                lambda t: "Impressions" in t and "Error" not in t,
            ),
        ],
    },
}

failures: list[str] = []
passes = 0


def record(name: str, ok: bool, detail: str = "") -> None:
    global passes
    if ok:
        passes += 1
        print(f"  PASS  {name}")
    else:
        failures.append(f"{name}: {detail}")
        print(f"  FAIL  {name} — {detail}")


def run_plugin(plugin: str, spec: dict) -> None:
    print(f"\n{plugin}")
    script = ROOT / spec["script"]
    if not script.is_file():
        record(f"{plugin} start script", False, f"not found: {spec['script']}")
        return

    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(ROOT / plugin)}
    proc = subprocess.Popen(
        ["bash", str(script)],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    def send(obj):
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def response(req_id, max_lines=400):
        for _ in range(max_lines):
            line = proc.stdout.readline()
            if not line:
                return None
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == req_id:
                return msg
        return None

    try:
        send({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "live-check", "version": "1"},
            },
        })
        if response(1) is None:
            record(
                f"{plugin} starts",
                False,
                proc.stderr.read()[-300:].strip() or "no response to initialize",
            )
            return
        record(f"{plugin} starts", True)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        for i, (tool, args, predicate) in enumerate(spec["calls"], start=10):
            send({
                "jsonrpc": "2.0", "id": i, "method": "tools/call",
                "params": {"name": tool, "arguments": args},
            })
            msg = response(i)
            if msg is None:
                record(f"{plugin}.{tool}", False, "no response")
                continue
            if "error" in msg:
                record(f"{plugin}.{tool}", False, str(msg["error"])[:200])
                continue
            content = msg.get("result", {}).get("content", [])
            text = content[0].get("text", "") if content else ""
            if msg.get("result", {}).get("isError"):
                record(f"{plugin}.{tool}", False, text[:200])
                continue
            record(
                f"{plugin}.{tool} returns live data",
                predicate(text),
                f"unexpected response: {text[:200]}",
            )
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> int:
    wanted = sys.argv[1:] or list(CHECKS)
    unknown = [w for w in wanted if w not in CHECKS]
    if unknown:
        print(f"Unknown plugin(s): {unknown}. Known: {list(CHECKS)}")
        return 2

    if not (Path.home() / ".env").is_file():
        print("No ~/.env found. This check needs real credentials — see SETUP.md.")
        return 2

    print("Live check — read-only calls against the real APIs")
    for plugin in wanted:
        run_plugin(plugin, CHECKS[plugin])

    print(f"\n{'-' * 60}")
    if failures:
        print(f"{len(failures)} FAILED, {passes} passed\n")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"All {passes} checks passed against live APIs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
