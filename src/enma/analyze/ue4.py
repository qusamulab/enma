"""Offline UE4 artifact analysis; no device or Frida imports."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def analyze_ue4_dump(dump_dir: Path, report: dict) -> None:
    """Analyze UE4 dump artifacts and add findings to report dict."""
    sdk_file = dump_dir / "ue4_sdk.json"
    pak_file = dump_dir / "ue4_pak_list.json"
    bp_file = dump_dir / "ue4_blueprint_trace.json"

    section: dict = {}

    if sdk_file.exists():
        sdk = json.loads(sdk_file.read_text())
        stats = sdk.get("stats", {})
        section["sdk"] = {
            "total_objects": stats.get("totalObjects", 0),
            "total_names": stats.get("totalNames", 0),
            "classes": stats.get("classes", 0),
            "functions": stats.get("functions", 0),
            "enums": stats.get("enums", 0),
            "structs": stats.get("structs", 0),
            "class_names": sdk.get("classes", [])[:200],
            "function_names": sdk.get("functions", [])[:200],
        }
        logger.info(
            "UE4 SDK: %d classes, %d functions",
            stats.get("classes", 0),
            stats.get("functions", 0),
        )

    if pak_file.exists():
        pak_list = json.loads(pak_file.read_text())
        section["pak_files"] = pak_list
        logger.info("UE4 PAK: %d PAK location(s)", len(pak_list))

    if bp_file.exists():
        bp = json.loads(bp_file.read_text())
        total = bp.get("total", 0)
        entries = bp.get("entries", [])
        func_counts: dict = {}
        for e in entries:
            k = e.get("func", "?")
            func_counts[k] = func_counts.get(k, 0) + 1
        top = dict(sorted(func_counts.items(), key=lambda x: -x[1])[:50])
        section["blueprint_trace"] = {
            "total_calls": total,
            "capped": bp.get("capped", False),
            "top_functions": top,
        }
        logger.info("UE4 Blueprint: %d call(s) traced", total)

    if section:
        report["ue4"] = section
