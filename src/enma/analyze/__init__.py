"""Offline dump analysis pipeline. Public entry point: analyze_dump."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from enma.analyze.binaries import (
    _analyze_assets,
    _analyze_dex,
    _analyze_il2cpp,
    _analyze_mono,
    _analyze_native_strings,
)
from enma.analyze.events import (
    _analyze_anti_tamper,
    _analyze_binder,
    _analyze_coverage,
    _analyze_crypto,
    _analyze_dlopen,
    _analyze_fileio,
    _analyze_http,
    _analyze_ios_app,
    _analyze_jni,
    _analyze_protobuf,
    _analyze_safetynet,
    _analyze_sqlite,
    _analyze_tls,
)
from enma.analyze.helpers import _find, _run
from enma.analyze.ue4 import analyze_ue4_dump as _analyze_ue4

logger = logging.getLogger(__name__)

_ANALYZERS = [
    _analyze_ios_app,
    _analyze_dex,
    _analyze_il2cpp,
    _analyze_jni,
    _analyze_crypto,
    _analyze_assets,
    _analyze_mono,
    _analyze_native_strings,
    _analyze_tls,
    _analyze_http,
    _analyze_sqlite,
    _analyze_binder,
    _analyze_coverage,
    _analyze_dlopen,
    _analyze_protobuf,
    _analyze_anti_tamper,
    _analyze_safetynet,
    _analyze_fileio,
    _analyze_ue4,
]


def analyze_dump(dump_dir: str, output: str | None = None) -> None:
    path = Path(dump_dir).resolve()
    if not path.is_dir():
        logger.error("Directory not found: %s", path)
        sys.exit(1)

    logger.info("Analyzing dump: %s", path)
    report: dict = {
        "dump_dir": str(path),
        "tool_versions": {
            "jadx": _run("jadx", "--version")[1].strip() if _find("jadx") else None,
            "apktool": _run("apktool", "--version")[1].strip() if _find("apktool") else None,
        },
    }

    for fn in _ANALYZERS:
        fn(path, report)

    out_path = Path(output) if output else path / "report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    logger.info("Report saved: %s", out_path)
