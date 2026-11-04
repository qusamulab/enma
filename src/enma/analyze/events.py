"""Offline analysis of events."""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

from enma.analyze.helpers import _count_by, _load_json

logger = logging.getLogger(__name__)


def _analyze_ios_app(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "ios_app.json")
    if data is not None:
        report["ios_app"] = data


def _analyze_jni(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "jni_map.json")
    if data is None:
        return

    modules: dict = {}
    for entry in data:
        mod = entry.get("module", "?")
        modules[mod] = modules.get(mod, 0) + 1

    report["jni"] = {"total_mappings": len(data), "by_module": modules}
    logger.info("JNI: %d mappings across %d module(s)", len(data), len(modules))


def _analyze_crypto(dump_dir: Path, report: dict) -> None:
    section: dict = {}
    report["crypto"] = section

    keys = _load_json(dump_dir / "crypto_keys.json")
    if keys is not None:
        section["hook_keys"] = {"total": len(keys), "by_algorithm": _count_by(keys, "algorithm")}
        logger.info("Crypto hooks: %d key event(s)", len(keys))

    byte_cands = _load_json(dump_dir / "heap_bytes.json")
    if byte_cands is not None:
        section["heap_key_candidates"] = len(byte_cands)
        logger.info("Heap: %d high-entropy byte[] candidate(s)", len(byte_cands))


def _analyze_tls(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "tls_connections.json")
    if data is None:
        return
    hosts = sorted({e.get("sni", "") for e in data if e.get("sni")})
    report["tls"] = {"connections": len(data), "unique_hosts": hosts}
    logger.info("TLS: %d connections to %d unique host(s)", len(data), len(hosts))


def _analyze_http(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "http_traffic.json")
    if data is None:
        return
    hosts = sorted({urlparse(e["url"]).netloc or "?" for e in data if e.get("url")})
    report["http"] = {"requests": len(data), "unique_hosts": hosts}
    logger.info("HTTP: %d request(s) to %d host(s)", len(data), len(hosts))


def _analyze_sqlite(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "sqlite_log.json")
    if data is None:
        return
    report["sqlite"] = {"total_ops": len(data), "by_op": _count_by(data, "op")}
    logger.info("SQLite: %d operation(s)", len(data))


def _analyze_binder(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "binder_log.json")
    if data is None:
        return
    report["binder"] = {"total": len(data), "by_type": _count_by(data, "type")}
    logger.info("Binder: %d event(s)", len(data))


def _analyze_coverage(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "coverage.json")
    if data is None:
        return
    summary = data.get("summary", {})
    top = dict(sorted(summary.items(), key=lambda x: -x[1])[:10])
    report["coverage"] = {"total_blocks": data.get("totalBlocks", 0), "top_modules": top}
    logger.info("Coverage: %d unique basic blocks", data.get("totalBlocks", 0))


def _analyze_dlopen(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "dlopen_log.json")
    if data is None:
        return
    libs = sorted({e.get("path", "?") for e in data if e.get("path") not in ("<null>", "?", None)})
    report["dlopen"] = {"total_loads": len(data), "unique_libs": libs}
    logger.info("dlopen: %d load(s), %d unique lib(s)", len(data), len(libs))


def _analyze_protobuf(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "protobuf_log.json")
    if data is None:
        return
    report["protobuf"] = {"total": len(data), "by_direction": _count_by(data, "direction")}
    logger.info("Protobuf: %d message(s)", len(data))


def _analyze_anti_tamper(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "anti_tamper_log.json")
    if data is None:
        return
    bypasses = [e.get("bypass", "?") for e in data]
    report["anti_tamper"] = {"total_bypasses": len(bypasses), "bypasses": bypasses[:50]}
    logger.info("Anti-tamper: %d detection bypass(es) triggered", len(bypasses))


def _analyze_safetynet(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "safetynet_log.json")
    if data is None:
        return
    report["safetynet"] = {"total": len(data), "by_type": _count_by(data, "type")}
    logger.info("SafetyNet: %d attestation event(s)", len(data))


def _analyze_fileio(dump_dir: Path, report: dict) -> None:
    data = _load_json(dump_dir / "fileio_log.json")
    if data is None:
        return
    paths = sorted({e.get("path", "?") for e in data if e.get("path")})
    report["fileio"] = {"total_ops": len(data), "unique_paths": paths[:50]}
    logger.info("File I/O: %d operation(s) on %d path(s)", len(data), len(paths))
