"""Artifact section renderers and their dispatch table."""

from __future__ import annotations

import json
from html import escape

from enma.report.components import _badge, _kv_table, _section, _table, _ul


def _render_dex(data: dict) -> str:
    files = data.get("files", [])
    obf = data.get("obfuscation") or {}
    ratio = obf.get("obfRatioPct", 0)
    verdict = obf.get("verdict", "")
    level = "high" if ratio > 50 else "med" if ratio > 20 else "low"
    badge = _badge(level, f"{ratio}% obfuscated")
    body = "<p>Files:</p>" + _ul(files)
    body += f"<p>Verdict: <b>{escape(verdict, quote=False)}</b></p>"
    jadx = data.get("jadx") or {}
    if jadx.get("java_files"):
        body += f"<p>jadx decompiled: {jadx['java_files']:,} Java files</p>"
    return _section("DEX Files", badge, body, ratio > 20)


def _render_il2cpp(data: dict) -> str:
    methods = data.get("methods", 0)
    fields = data.get("fields", 0)
    interesting = data.get("interesting_methods", [])
    badge = _badge("info", f"{methods} methods")
    body = f"<p>Methods: {methods:,}  Fields: {fields:,}</p>"
    if interesting:
        rows = [
            [m.get("Name", "?"), m.get("Signature", "?"), m.get("Address", "?")]
            for m in interesting[:50]
        ]
        body += "<p><b>Security-relevant methods:</b></p>"
        body += _table(["Name", "Signature", "Address"], rows)
    return _section("IL2CPP Symbol Map", badge, body, bool(interesting))


def _render_jni(data: dict) -> str:
    total = data.get("total_mappings", 0)
    badge = _badge("info", f"{total} mappings")
    rows = [
        [mod, str(cnt)]
        for mod, cnt in sorted(data.get("by_module", {}).items(), key=lambda x: -x[1])
    ]
    return _section("JNI Map", badge, _table(["Module", "Mappings"], rows), total > 0)


def _render_crypto(data: dict) -> str:
    hk = data.get("hook_keys") or {}
    total = hk.get("total", 0)
    badge = _badge("high" if total > 0 else "low", f"{total} keys hooked")
    body = f"<p>Hook captures: {total}  Heap byte[] candidates: {data.get('heap_key_candidates', 0)}</p>"
    if hk.get("by_algorithm"):
        body += _kv_table(hk["by_algorithm"])
    return _section("Crypto Keys", badge, body, total > 0)


def _render_tls(data: dict) -> str:
    conns = data.get("connections", 0)
    hosts = data.get("unique_hosts", [])
    badge = _badge("info", f"{conns} connections")
    body = f"<p>Unique hosts ({len(hosts)}):</p>" + _ul(hosts)
    return _section("TLS Connections", badge, body, conns > 0)


def _render_native_strings(data: dict) -> str:
    total = sum(len(v) for v in data.values())
    badge = _badge("med" if total > 0 else "low", f"{total} interesting strings")
    rows = [[so, s] for so, strs in data.items() for s in strs[:20]]
    body = _table(["Library", "String"], rows) if rows else "<p>None found.</p>"
    return _section("Native Strings (URLs / JWTs)", badge, body, total > 0)


def _render_assets(data: dict) -> str:
    count = data.get("count", 0)
    badge = _badge("info", f"{count} bundles")
    body = f"<p>Total size: {data.get('total_bytes', 0) / 1024 / 1024:.1f} MB</p>"
    if data.get("files"):
        body += _ul(data["files"])
    return _section("Unity AssetBundles", badge, body)


def _render_http(data: dict) -> str:
    reqs = data.get("requests", 0)
    hosts = data.get("unique_hosts", [])
    badge = _badge("med" if reqs > 0 else "info", f"{reqs} requests")
    body = f"<p>Unique hosts ({len(hosts)}):</p>" + _ul(hosts)
    return _section("HTTP Traffic", badge, body, reqs > 0)


def _render_sqlite(data: dict) -> str:
    total = data.get("total_ops", 0)
    badge = _badge("info", f"{total} ops")
    return _section("SQLite", badge, _kv_table(data.get("by_op", {})), total > 0)


def _render_binder(data: dict) -> str:
    total = data.get("total", 0)
    badge = _badge("info", f"{total} events")
    return _section("Binder / IPC", badge, _kv_table(data.get("by_type", {})), total > 0)


def _render_coverage(data: dict) -> str:
    blocks = data.get("total_blocks", 0)
    badge = _badge("info", f"{blocks} blocks")
    body = f"<p>Total unique basic blocks: {blocks:,}</p>"
    if data.get("top_modules"):
        body += "<p><b>Top modules:</b></p>" + _kv_table(data["top_modules"])
    return _section("Code Coverage", badge, body, blocks > 0)


def _render_dlopen(data: dict) -> str:
    total = data.get("total_loads", 0)
    libs = data.get("unique_libs", [])
    badge = _badge("info", f"{total} loads")
    body = f"<p>Unique libraries ({len(libs)}):</p>" + _ul(libs)
    return _section("dlopen Monitor", badge, body, total > 0)


def _render_protobuf(data: dict) -> str:
    total = data.get("total", 0)
    badge = _badge("info", f"{total} messages")
    return _section("Protobuf", badge, _kv_table(data.get("by_direction", {})), total > 0)


def _render_anti_tamper(data: dict) -> str:
    total = data.get("total_bypasses", 0)
    badge = _badge("med" if total > 0 else "low", f"{total} bypasses")
    bypasses = data.get("bypasses", [])
    body = _ul(bypasses) if bypasses else "<p>None.</p>"
    return _section("Anti-Tamper Bypasses", badge, body, total > 0)


def _render_safetynet(data: dict) -> str:
    total = data.get("total", 0)
    badge = _badge("high" if total > 0 else "low", f"{total} events")
    return _section(
        "SafetyNet / Play Integrity", badge, _kv_table(data.get("by_type", {})), total > 0
    )


def _render_fileio(data: dict) -> str:
    total = data.get("total_ops", 0)
    paths = data.get("unique_paths", [])
    badge = _badge("info", f"{total} ops")
    body = f"<p>Unique paths ({len(paths)}):</p>" + _ul(paths)
    return _section("File I/O", badge, body, total > 0)


def _render_mono(data: dict) -> str:
    count = data.get("count", 0)
    badge = _badge("info", f"{count} DLLs")
    body = _ul(data.get("files", []))
    return _section("Mono DLLs", badge, body)


def _render_ue4(data: dict) -> str:
    sdk = data.get("sdk") or {}
    pak = data.get("pak_files") or []
    bp = data.get("blueprint_trace") or {}

    classes = sdk.get("classes", 0)
    functions = sdk.get("functions", 0)
    badge = _badge("info", f"{classes} classes / {functions} funcs")

    body = ""
    if sdk:
        body += (
            f"<p>Objects: {sdk.get('total_objects', 0):,}  Names: {sdk.get('total_names', 0):,}  "
        )
        body += f"Enums: {sdk.get('enums', 0)}  Structs: {sdk.get('structs', 0)}</p>"
        if sdk.get("class_names"):
            body += "<p><b>Classes (first 50):</b></p>"
            body += _ul(sdk["class_names"][:50])
        if sdk.get("function_names"):
            body += "<p><b>Functions (first 50):</b></p>"
            body += _ul(sdk["function_names"][:50])

    if pak:
        body += f"<p><b>PAK files ({len(pak)}):</b></p>"
        body += _ul([p.get("path", p.get("addr", "?")) for p in pak])

    if bp:
        total = bp.get("total_calls", 0)
        body += f"<p><b>Blueprint trace:</b> {total:,} calls"
        if bp.get("capped"):
            body += " (capped)"
        body += "</p>"
        if bp.get("top_functions"):
            body += "<p><b>Top Blueprint functions:</b></p>"
            body += _kv_table(bp["top_functions"])

    return _section("Unreal Engine 4", badge, body or "<p>No UE4 data.</p>", bool(sdk or pak or bp))


def _render_ios_app(data: dict) -> str:
    metadata = {key: data.get(key) for key in ("bundle_id", "name", "version", "build", "arch")}
    body = _table(
        ["Property", "Value"], [[key, str(value or "?")] for key, value in metadata.items()]
    )
    modules = data.get("modules", [])
    body += _table(
        ["Module", "Path"], [[mod.get("name", "?"), mod.get("path", "?")] for mod in modules[:200]]
    )
    return _section("iOS Application", _badge("info", f"{len(modules)} modules"), body, True)


def _render_generic(title: str, data: dict) -> str:
    body = (
        f"<pre>{escape(json.dumps(data, indent=2, ensure_ascii=False)[:4000], quote=False)}</pre>"
    )
    return _section(title, _badge("info", ""), body)


_RENDERERS = {
    "ios_app": _render_ios_app,
    "dex": _render_dex,
    "il2cpp": _render_il2cpp,
    "jni": _render_jni,
    "crypto": _render_crypto,
    "tls": _render_tls,
    "native_strings": _render_native_strings,
    "assets": _render_assets,
    "http": _render_http,
    "sqlite": _render_sqlite,
    "binder": _render_binder,
    "coverage": _render_coverage,
    "dlopen": _render_dlopen,
    "protobuf": _render_protobuf,
    "anti_tamper": _render_anti_tamper,
    "safetynet": _render_safetynet,
    "fileio": _render_fileio,
    "mono": _render_mono,
    "ue4": _render_ue4,
}
