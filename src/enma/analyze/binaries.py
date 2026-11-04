"""Offline analysis of binaries."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from enma.analyze.helpers import _find, _load_json, _run

logger = logging.getLogger(__name__)


def _analyze_dex(dump_dir: Path, report: dict) -> None:
    dex_files = sorted(dump_dir.glob("*.dex"))
    if not dex_files:
        return

    report["dex"] = {"files": [f.name for f in dex_files], "jadx": None, "obfuscation": None}

    obf = _load_json(dump_dir / "dex_obfuscation_report.json")
    if obf:
        report["dex"]["obfuscation"] = obf

    jadx = _find("jadx")
    if not jadx:
        logger.warning("jadx not found — skipping DEX decompilation")
        return

    out_dir = dump_dir / "jadx_out"
    logger.info("Running jadx on %d DEX file(s) -> %s", len(dex_files), out_dir)
    rc, _, stderr = _run(
        jadx,
        "--output-dir",
        str(out_dir),
        "--threads-count",
        "4",
        *[str(f) for f in dex_files],
        capture=True,
        timeout=600,
    )
    report["dex"]["jadx"] = {
        "exit_code": rc,
        "output_dir": str(out_dir),
        "error": stderr[:2000] if rc != 0 else None,
    }
    if rc == 0:
        java_files = list(out_dir.rglob("*.java"))
        report["dex"]["jadx"]["java_files"] = len(java_files)
        logger.info("jadx: %d Java files decompiled", len(java_files))
    else:
        logger.error("jadx failed (exit %d)", rc)


def _analyze_il2cpp(dump_dir: Path, report: dict) -> None:
    il2cpp_so = next(
        (
            dump_dir / name
            for name in ("libil2cpp.so", "UnityFramework", "GameAssembly.dylib", "libil2cpp.dylib")
            if (dump_dir / name).exists()
        ),
        dump_dir / "libil2cpp.so",
    )
    metadata = dump_dir / "global-metadata.dat"
    dump_json = dump_dir / "il2cpp_dump.json"

    if not il2cpp_so.exists() and not dump_json.exists():
        return

    section: dict = {
        "libil2cpp_size": il2cpp_so.stat().st_size if il2cpp_so.exists() else None,
        "metadata_size": metadata.stat().st_size if metadata.exists() else None,
    }
    report["il2cpp"] = section

    data = _load_json(dump_json)
    if data:
        section["methods"] = len(data.get("ScriptMethod", []))
        section["fields"] = len(data.get("ScriptMetadata", []))
        logger.info("IL2CPP: %d methods, %d fields", section["methods"], section["fields"])

        keywords = re.compile(
            r"(auth|login|token|secret|key|password|encrypt|decrypt|hash|sign|verify)",
            re.IGNORECASE,
        )
        interesting = [
            m for m in data.get("ScriptMethod", []) if keywords.search(m.get("Name", ""))
        ]
        section["interesting_methods"] = interesting[:50]
        if interesting:
            logger.info("IL2CPP: %d security-related method(s) flagged", len(interesting))

    il2cpp_dumper = _find("Il2CppDumper") or _find("il2cppdumper")
    if il2cpp_dumper and il2cpp_so.exists() and metadata.exists():
        out_dir = dump_dir / "il2cppdumper_out"
        out_dir.mkdir(exist_ok=True)
        logger.info("Running Il2CppDumper -> %s", out_dir)
        rc, _, _ = _run(il2cpp_dumper, str(il2cpp_so), str(metadata), str(out_dir), timeout=120)
        section["il2cppdumper"] = {"exit_code": rc, "output_dir": str(out_dir)}


def _analyze_assets(dump_dir: Path, report: dict) -> None:
    bundles = sorted(dump_dir.glob("*.unity3d"))
    if not bundles:
        return
    report["assets"] = {
        "count": len(bundles),
        "total_bytes": sum(f.stat().st_size for f in bundles),
        "files": [f.name for f in bundles],
    }
    logger.info("Assets: %d bundle(s)", len(bundles))


def _analyze_mono(dump_dir: Path, report: dict) -> None:
    dlls = list(dump_dir.glob("*.dll"))
    if not dlls:
        return

    report["mono"] = {"count": len(dlls), "files": [f.name for f in dlls]}
    logger.info("Mono: %d DLL(s)", len(dlls))

    jadx = _find("jadx")
    if not jadx:
        return

    out_dir = dump_dir / "jadx_mono_out"
    logger.info("Running jadx on %d DLL(s) -> %s", len(dlls), out_dir)
    rc, _, _ = _run(jadx, "--output-dir", str(out_dir), *[str(d) for d in dlls], timeout=600)
    report["mono"]["jadx"] = {"exit_code": rc, "output_dir": str(out_dir)}


def _analyze_native_strings(dump_dir: Path, report: dict) -> None:
    so_files = sorted(set(dump_dir.glob("lib*.so")) | set(dump_dir.glob("*.dylib")))
    if (dump_dir / "UnityFramework").is_file():
        so_files.append(dump_dir / "UnityFramework")
    if not so_files:
        return

    strings_bin = _find("strings")
    if not strings_bin:
        return

    url_re = re.compile(r"https?://[^\s\"'<>]{8,}")
    jwt_re = re.compile(r"ey[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
    all_interesting: dict[str, list[str]] = {}

    for so in so_files:
        rc, out, _ = _run(strings_bin, "-n", "6", str(so), timeout=30)
        if rc != 0:
            continue
        text = "\n".join(out.splitlines())
        interesting = url_re.findall(text) + jwt_re.findall(text)
        if interesting:
            all_interesting[so.name] = interesting[:100]

    if all_interesting:
        report["native_strings"] = all_interesting
        total = sum(len(v) for v in all_interesting.values())
        so_count = len(all_interesting)
        logger.info("Native strings: %d URL/JWT found across %d .so file(s)", total, so_count)
