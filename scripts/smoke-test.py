#!/usr/bin/env python3
"""Smoke test for every plugin in this marketplace. No credentials required.

Runs in CI and locally. Checks the things that have actually broken here:
manifests drifting from disk, skills with malformed frontmatter, a `bin/`
directory creeping back in (which silently blocks claude.ai marketplace sync),
shell scripts that no longer parse, and MCP servers that fail to start or have
quietly lost a tool.

What this does NOT cover: whether a tool's request payload is still valid
against the live API. That needs real credentials — see scripts/live-check.py.
Both of the bugs fixed in keyword-planner 2.0.0 were of that kind, so run the
live check before shipping a change to how a tool builds its request.

Usage:  python3 scripts/smoke-test.py
Exit:   0 all passed, 1 one or more failures
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Tools that must exist on each server. Deliberately a critical subset rather
# than an exact list, so adding a tool doesn't fail the build but losing one does.
REQUIRED_TOOLS = {
    "google-ads": [
        "list_accounts",
        "execute_gaql_query",
        "add_negative_keywords",
        "update_budget_amount",
    ],
    "meta-ads": ["ad_account_list", "campaign_list", "insights_get"],
    "keyword-planner": [
        "generate_keyword_ideas",
        "get_historical_metrics",
        "get_keyword_forecast",
    ],
}

# Module to launch per plugin. Plugins absent here are skills-only.
SERVER_MODULES = {
    "google-ads": "mcp_google_ads",
    "meta-ads": "mcp_meta_ads",
    "keyword-planner": "mcp_keyword_planner",
}

# Enough to satisfy startup checks. Never used against a real API.
DUMMY_ENV = {
    "GOOGLE_ADS_DEVELOPER_TOKEN": "dummy",
    "GOOGLE_ADS_CLIENT_ID": "dummy",
    "GOOGLE_ADS_CLIENT_SECRET": "dummy",
    "GOOGLE_ADS_REFRESH_TOKEN": "dummy",
    "GOOGLE_ADS_CREDENTIALS_PATH": "/tmp/not-a-real-token.json",
    "GOOGLE_ADS_CUSTOMER_ID": "1234567890",
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "1234567890",
    "ACCESS_TOKEN": "dummy",
    "META_ACCESS_TOKEN": "dummy",
    "AD_ACCOUNT_ID": "act_1234567890",
    "BUSINESS_ID": "1234567890",
}

SECRET_PATTERNS = [
    (r"AIza[0-9A-Za-z_-]{30,}", "Google API key"),
    (r"ya29\.[0-9A-Za-z_-]{20,}", "Google OAuth access token"),
    (r"GOCSPX-[A-Za-z0-9_-]{20,}", "Google OAuth client secret"),
    (r"[0-9]{6,}-[0-9a-z]{32}\.apps\.googleusercontent\.com", "OAuth client ID"),
    (r"EAA[A-Za-z0-9]{60,}", "Meta access token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
]

failures: list[str] = []
passes = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passes
    if ok:
        passes += 1
        print(f"  PASS  {name}")
    else:
        failures.append(f"{name}: {detail}")
        print(f"  FAIL  {name} — {detail}")


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [line for line in out.stdout.splitlines() if line]


def plugin_dirs() -> list[str]:
    return sorted(
        p.name for p in ROOT.iterdir() if (p / ".claude-plugin" / "plugin.json").is_file()
    )


def test_marketplace() -> None:
    print("\nmarketplace manifest")
    path = ROOT / ".claude-plugin" / "marketplace.json"
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        check("marketplace.json parses", False, str(exc))
        return
    check("marketplace.json parses", True)
    check("marketplace has a name", bool(data.get("name")), "missing 'name'")

    named = {p["name"] for p in data.get("plugins", [])}
    on_disk = set(plugin_dirs())
    check(
        "every marketplace entry has a directory",
        not (named - on_disk),
        f"listed but missing: {sorted(named - on_disk)}",
    )
    check(
        "every plugin directory is registered",
        not (on_disk - named),
        f"on disk but unregistered: {sorted(on_disk - named)}",
    )

    for entry in data.get("plugins", []):
        src = entry.get("source", "")
        check(
            f"source path for '{entry.get('name')}'",
            src == f"./{entry.get('name')}",
            f"expected './{entry.get('name')}', got '{src}'",
        )


def test_plugin_manifests() -> None:
    print("\nplugin manifests")
    for name in plugin_dirs():
        path = ROOT / name / ".claude-plugin" / "plugin.json"
        try:
            data = json.loads(path.read_text())
        except Exception as exc:
            check(f"{name}/plugin.json parses", False, str(exc))
            continue
        check(f"{name}/plugin.json parses", True)
        check(
            f"{name} manifest name matches directory",
            data.get("name") == name,
            f"manifest says '{data.get('name')}'",
        )
        version = str(data.get("version", ""))
        check(
            f"{name} has a numeric version",
            bool(re.fullmatch(r"\d+\.\d+\.\d+", version)),
            f"got '{version}', expected N.N.N",
        )


def test_no_bin_directory() -> None:
    print("\nno bin/ directory")
    # claude.ai-hosted plugins may not ship bin/ executables: bin/ is added to
    # PATH on the CLI but never shown on the admin approval surface, so the org
    # sync skips the whole plugin. This silently kept keyword-planner out of the
    # marketplace for months.
    offenders = [f for f in tracked_files() if re.search(r"(^|/)bin/", f)]
    check(
        "no tracked bin/ directory",
        not offenders,
        f"would block marketplace sync: {offenders[:5]}",
    )


def test_no_secrets() -> None:
    print("\nno committed secrets")
    hits = []
    for rel in tracked_files():
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, text):
                hits.append(f"{rel} ({label})")
    check("no credential patterns in tracked files", not hits, f"found: {hits[:5]}")

    env_like = [
        f
        for f in tracked_files()
        if re.search(r"(^|/)\.env(\.|$)|\.pem$|token\.json$", f)
    ]
    check("no .env or token files tracked", not env_like, f"found: {env_like[:5]}")


def test_skills() -> None:
    print("\nskill frontmatter")
    skills = [ROOT / f for f in tracked_files() if f.endswith("SKILL.md")]
    check("at least one skill found", bool(skills), "no SKILL.md files tracked")
    for path in sorted(skills):
        rel = path.relative_to(ROOT)
        text = path.read_text()
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            check(f"{rel} frontmatter", False, "missing or malformed --- block")
            continue
        fm = match.group(1)
        name_m = re.search(r"^name:\s*(.+)$", fm, re.M)
        desc_m = re.search(r"^description:\s*(.*)$", fm, re.M)
        problems = []
        if not name_m:
            problems.append("no 'name:'")
        elif name_m.group(1).strip() != path.parent.name:
            problems.append(
                f"name '{name_m.group(1).strip()}' != directory '{path.parent.name}'"
            )
        if not desc_m:
            problems.append("no 'description:'")
        elif not desc_m.group(1).strip() and not desc_m.group(1).strip().startswith(">"):
            # A folded block scalar ('description: >') carries its text on the
            # following lines, so an empty first line is only a problem if no
            # indented continuation follows.
            after = fm[desc_m.end():]
            if not re.match(r"\n\s+\S", after):
                problems.append("empty description")
        check(f"{rel} frontmatter", not problems, "; ".join(problems))


def test_shell_syntax() -> None:
    print("\nshell script syntax")
    scripts = [f for f in tracked_files() if f.endswith(".sh")]
    check("at least one shell script found", bool(scripts), "none tracked")
    for rel in scripts:
        result = subprocess.run(
            ["bash", "-n", rel], cwd=ROOT, capture_output=True, text=True
        )
        check(f"{rel} parses", result.returncode == 0, result.stderr.strip()[:200])


def test_python_compiles() -> None:
    print("\npython syntax")
    pkgs = sorted({f.split("/")[0] + "/" + f.split("/")[1]
                   for f in tracked_files()
                   if f.endswith(".py") and f.count("/") >= 2})
    for pkg in pkgs:
        result = subprocess.run(
            [sys.executable, "-m", "compileall", "-q", pkg],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        check(f"{pkg} compiles", result.returncode == 0, result.stdout.strip()[:200])


def start_server(plugin: str, module: str):
    env = {**os.environ, **DUMMY_ENV}
    env["CLAUDE_PLUGIN_ROOT"] = str(ROOT / plugin)
    return subprocess.Popen(
        ["uv", "run", "--directory", plugin, "python", "-m", module],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )


def test_servers() -> None:
    print("\nMCP servers boot and expose their tools")
    for plugin, module in SERVER_MODULES.items():
        if not (ROOT / plugin).is_dir():
            check(f"{plugin} directory exists", False, "not found")
            continue
        proc = start_server(plugin, module)
        try:
            def send(obj):
                proc.stdin.write(json.dumps(obj) + "\n")
                proc.stdin.flush()

            def response(req_id, timeout_lines=200):
                for _ in range(timeout_lines):
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

            send({
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "smoke-test", "version": "1"},
                },
            })
            if response(1) is None:
                check(
                    f"{plugin} server starts",
                    False,
                    proc.stderr.read()[-300:].strip() or "no response to initialize",
                )
                continue
            check(f"{plugin} server starts", True)

            send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
            listing = response(2)
            if listing is None:
                check(f"{plugin} lists tools", False, "no response to tools/list")
                continue

            found = {t["name"] for t in listing["result"]["tools"]}
            check(f"{plugin} lists tools", True, "")
            missing = [t for t in REQUIRED_TOOLS.get(plugin, []) if t not in found]
            check(
                f"{plugin} exposes its required tools",
                not missing,
                f"missing: {missing}",
            )
        finally:
            try:
                proc.stdin.close()
            except Exception:
                pass
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


def main() -> int:
    print(f"Smoke test — {ROOT}")
    test_marketplace()
    test_plugin_manifests()
    test_no_bin_directory()
    test_no_secrets()
    test_skills()
    test_shell_syntax()
    test_python_compiles()
    test_servers()

    print(f"\n{'-' * 60}")
    if failures:
        print(f"{len(failures)} FAILED, {passes} passed\n")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"All {passes} checks passed.")
    print(
        "\nNote: this runs without credentials, so it cannot catch a tool whose\n"
        "request payload has gone stale against the live API. Run\n"
        "scripts/live-check.py for that."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
