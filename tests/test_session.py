from __future__ import annotations

import argparse
from types import SimpleNamespace
from unittest.mock import Mock

import frida
import pytest

from enma import mem
from enma.core import session
from enma.core.platforms import Platform


def test_numeric_target_attaches_as_pid() -> None:
    device = Mock()
    session.attach_or_spawn(device, "1234", False)
    device.attach.assert_called_once_with(1234)
    device.enumerate_applications.assert_not_called()


def test_bundle_identifier_resolves_to_running_pid() -> None:
    device = Mock()
    device.enumerate_applications.return_value = [SimpleNamespace(identifier="com.app", pid=42)]
    session.attach_or_spawn(device, "com.app", False)
    device.attach.assert_called_once_with(42)


def test_stopped_bundle_suggests_spawn_instead_of_name_attach() -> None:
    device = Mock()
    device.enumerate_applications.return_value = [SimpleNamespace(identifier="com.app", pid=0)]
    with pytest.raises(frida.ProcessNotFoundError, match="--spawn"):
        session.attach_or_spawn(device, "com.app", False)
    device.attach.assert_not_called()


def test_process_name_still_works() -> None:
    device = Mock()
    device.enumerate_applications.return_value = []
    session.attach_or_spawn(device, "Gadget", False)
    device.attach.assert_called_once_with("Gadget")


def test_remote_host_is_added_to_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = Mock()
    monkeypatch.setattr(frida, "get_device_manager", lambda: manager)
    assert (
        session.get_device(None, host="127.0.0.1:27042") is manager.add_remote_device.return_value
    )
    manager.add_remote_device.assert_called_once_with("127.0.0.1:27042")


def test_android_only_connection_rejects_ios_before_attach(monkeypatch: pytest.MonkeyPatch) -> None:
    device = Mock()
    device.query_system_parameters.return_value = {"os": {"id": "ios"}}
    monkeypatch.setattr(session, "get_device", lambda *a, **kw: device)
    args = argparse.Namespace(serial=None, target="com.app", spawn=False, watch=False)
    with pytest.raises(SystemExit, match="android only"):
        session.connect(args, platform=Platform.ANDROID)
    device.attach.assert_not_called()


def test_timeout_is_cancelled_when_session_detaches(monkeypatch: pytest.MonkeyPatch) -> None:
    timer = Mock()
    event = Mock()
    monkeypatch.setattr(session.threading, "Timer", lambda *_a: timer)
    monkeypatch.setattr(session.threading, "Event", lambda: event)
    target = Mock()
    assert session.run_until_detached(target, timeout=10) is False
    timer.start.assert_called_once()
    timer.cancel.assert_called_once()
    target.detach.assert_called_once()


def test_mempatch_detaches_after_rpc_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    target = Mock()
    rpc = Mock()
    rpc.write.return_value = {"error": "unmapped address"}
    monkeypatch.setattr(mem, "_start_agent", lambda *_a: (target, rpc))
    args = argparse.Namespace(addr="0x1", nop=0, bytes=None, value="1", type="int32", freeze=False)
    with pytest.raises(SystemExit):
        mem.run_mempatch(args)
    target.detach.assert_called_once()
