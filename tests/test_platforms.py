from __future__ import annotations

from types import SimpleNamespace

import pytest

from enma.core.agents import TAG_DUMP, TAG_MEM, select_agents
from enma.core.platforms import Platform, detect_platform


@pytest.mark.parametrize("identifier", ["android", "ios", "iOS"])
def test_detects_frida_os_identifier(identifier: str) -> None:
    device = SimpleNamespace(query_system_parameters=lambda: {"os": {"id": identifier}})
    assert detect_platform(device) == identifier.lower()


@pytest.mark.parametrize("parameters", [{}, {"os": {"id": "macos"}}])
def test_unknown_os_requires_explicit_override(parameters: dict) -> None:
    device = SimpleNamespace(query_system_parameters=lambda: parameters)
    with pytest.raises(ValueError, match="Unsupported device OS"):
        detect_platform(device)


def test_explicit_gadget_platform_does_not_query_device() -> None:
    assert detect_platform(object(), "ios") is Platform.IOS


def test_query_failure_has_actionable_message() -> None:
    def fail() -> dict:
        raise RuntimeError("not supported")

    with pytest.raises(ValueError, match="--platform"):
        detect_platform(SimpleNamespace(query_system_parameters=fail))


def test_ios_defaults_exclude_android_agents() -> None:
    selected = select_agents(TAG_DUMP, Platform.IOS)
    assert {"ios_app", "ios_http", "ios_crypto", "il2cpp", "fileio", "sqlite"} <= set(selected)
    assert not {"dex", "jni", "heap", "ssl", "http", "ue4_sdk"} & set(selected)


def test_android_defaults_exclude_ios_agents() -> None:
    selected = select_agents(TAG_DUMP, Platform.ANDROID)
    assert "dex" in selected
    assert not any(name.startswith("ios_") for name in selected)


def test_explicit_incompatible_agent_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported agents for ios: dex"):
        select_agents(TAG_DUMP, Platform.IOS, ["ios_app", "dex"])


@pytest.mark.parametrize("platform", list(Platform))
def test_memory_agents_are_available_on_both_platforms(platform: Platform) -> None:
    assert select_agents(TAG_MEM, platform) == ["memscan", "mempatch"]
