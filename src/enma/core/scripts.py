"""Prepare agents for Frida 17, including lazy Java and Objective-C bridges."""

from __future__ import annotations

from functools import cache
from importlib.resources import files


@cache
def _bridge(name: str) -> str:
    return files("frida_tools").joinpath(f"bridges/{name.lower()}.js").read_text(encoding="utf-8")


def prepare_source(source: str) -> str:
    bootstrap = files("enma.agents").joinpath("_runtime.js").read_text(encoding="utf-8")
    for name in ("Java", "ObjC"):
        if f"{name}." not in source:
            continue
        bootstrap += f"""
if (typeof globalThis.{name} === 'undefined') {{
    Object.defineProperty(globalThis, '{name}', {{
        configurable: true,
        get() {{
            const value = (function () {{ {_bridge(name)}\nreturn bridge; }})();
            Object.defineProperty(globalThis, '{name}', {{ value, configurable: true }});
            return value;
        }}
    }});
}}
"""
    return (
        bootstrap
        + "\n"
        + source
        + "\nif (typeof flush === 'function') rpc.exports.flush = flush;\n"
    )
