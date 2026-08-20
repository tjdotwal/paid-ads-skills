"""Thin wrapper around the local `meta ads` CLI binary.

Every MCP tool eventually flows through `run_meta()`. It builds an argv list,
shells out, and returns parsed JSON or raises with the CLI's stderr.

We deliberately do NOT re-implement the Marketing API client here. Meta's CLI
already handles auth, pagination, retries, and rate-limit backoff. Our job is
to expose its surface area to Claude as structured tools.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any


class MetaCliError(RuntimeError):
    """Raised when the `meta ads` CLI exits non-zero or returns unparseable output."""

    def __init__(self, returncode: int, stderr: str, argv: list[str]):
        self.returncode = returncode
        self.stderr = stderr
        self.argv = argv
        super().__init__(
            f"meta ads {' '.join(argv)} failed (exit {returncode}): {stderr.strip()}"
        )


def _resolve_binary() -> str:
    """Find the `meta` binary on PATH. Fail loudly if missing."""
    binary = shutil.which("meta")
    if binary is None:
        raise MetaCliError(
            returncode=127,
            stderr=(
                "The `meta` CLI is not on PATH. Install it with "
                "`pip install meta-ads` (Python 3.12+) or via `uv tool install meta-ads`."
            ),
            argv=[],
        )
    return binary


def run_meta(
    argv: list[str],
    *,
    output: str = "json",
    timeout: int = 60,
    extra_env: dict[str, str] | None = None,
) -> Any:
    """Run `meta ads <argv...>` and return the parsed result.

    Args:
        argv: CLI args AFTER `meta ads`. e.g. ["campaign", "list", "--limit", "10"].
        output: One of "json" | "table" | "plain". We default to json so the
            caller gets structured data back.
        timeout: Hard cap in seconds.
        extra_env: Optional env vars to layer on top of the inherited environment
            (e.g. per-call overrides). Tokens come from the inherited env.

    Returns:
        Parsed JSON if output=="json" and the CLI emitted valid JSON,
        otherwise the raw stdout string.

    Raises:
        MetaCliError: non-zero exit code, with stderr attached.
    """
    binary = _resolve_binary()
    # `--output` is a GLOBAL flag on `meta` itself (must come BEFORE `ads`),
    # not a subcommand flag. Confirmed via `meta ads campaign list --help`
    # which shows the example: `meta --output json ads campaign list`.
    full_argv = [binary, "--output", output, "ads", *argv]

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    try:
        proc = subprocess.run(
            full_argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise MetaCliError(
            returncode=-1,
            stderr=f"Timed out after {timeout}s",
            argv=argv,
        ) from e

    if proc.returncode != 0:
        raise MetaCliError(
            returncode=proc.returncode,
            stderr=proc.stderr or proc.stdout,
            argv=argv,
        )

    if output == "json":
        stdout = proc.stdout.strip()
        if not stdout:
            return {}
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            # Some commands (e.g. create operations) may print a confirmation
            # line before/after JSON. Fall back to raw text.
            return {"_raw": stdout}
    return proc.stdout
