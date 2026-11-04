from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_offline_pipeline_never_imports_frida_or_unitypy(tmp_path: Path) -> None:
    source = """
import sys, shutil
sys.modules['frida'] = None
sys.modules['UnityPy'] = None
shutil.which = lambda *_a, **_kw: None
from enma.cli import _build_parser
from enma.analyze import analyze_dump
from enma.report import render_report
_build_parser()
analyze_dump(sys.argv[1])
render_report(sys.argv[1])
"""
    result = subprocess.run(
        [sys.executable, "-c", source, str(tmp_path)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "report.html").is_file()
