"""Mobile platform detection without importing the Frida runtime."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol


class Platform(StrEnum):
    ANDROID = "android"
    IOS = "ios"


class SystemDevice(Protocol):
    def query_system_parameters(self) -> dict: ...


def detect_platform(device: SystemDevice, requested: str = "auto") -> Platform:
    """Use Frida's OS identifier, or an explicit override for Gadget sessions."""
    if requested != "auto":
        return Platform(requested)
    try:
        os_info = device.query_system_parameters().get("os", {})
        identifier = os_info.get("id", "").lower()
    except Exception as exc:
        raise ValueError("Cannot detect device OS; specify --platform android or ios") from exc
    if identifier in ("android", "ios"):
        return Platform(identifier)
    raise ValueError(
        f"Unsupported device OS: {identifier or 'unknown'}; "
        "use --platform android or ios for a mobile Gadget session"
    )
