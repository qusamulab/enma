"""Shared JSON, counting and external-tool helpers for offline analysis."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _find(tool: str) -> str | None:
    return shutil.which(tool)


def _run(
    *args: str,
    capture: bool = True,
    cwd: str | None = None,
    timeout: int = 300,
) -> tuple[int, str, str]:
    result = subprocess.run(
        list(args),
        capture_output=capture,
        text=True,
        cwd=cwd,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def _load_json(path: Path) -> list | dict | None:
    """Return parsed JSON from *path*, or None if absent."""
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _count_by(data: list, key: str) -> dict:
    """Tally occurrences of data[i][key] across a list of dicts."""
    tally: dict = {}
    for entry in data:
        k = entry.get(key, "?")
        tally[k] = tally.get(k, 0) + 1
    return tally
