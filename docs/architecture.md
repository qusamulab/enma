# Architecture

enma consists of Python on the host and JavaScript agents inside the target app.
The CLI handles arguments and dispatch, keeping device operations separate from offline analysis.

```text
CLI
 ├─ dump / mem / ue4 → core/session → Frida → JS agents in the target app
 │                                 ↓ messages
 │                              dump directory
 ├─ analyze → binaries / events / ue4 → report.json
 └─ report → sections / components / assets → report.html
```

## Responsibilities

| Location | Responsibility |
|---|---|
| `cli.py` | Argument parsing and lazy imports; no device connections or analysis logic |
| `core/platforms.py` | Android/iOS detection and explicit overrides for Gadget |
| `core/agents.py` | Single registry of agent names, categories, and supported platforms |
| `core/scripts.py` | Frida 17 Java/Objective-C bridges and shared JavaScript bootstrap |
| `core/session.py` | USB/TCP connections, attachment, script loading, and flushing on shutdown |
| `dump.py` / `mem.py` / `ue4.py` | Runtime operations |
| `frida_server.py` / `repack.py` | Android server deployment and APK processing |
| `analyze/` | Analysis of collected files without device or Frida dependencies |
| `report/` | HTML generation, with CSS/JavaScript under `assets/` |
| `agents/` | JavaScript executing inside the target process, separately from Python |

Dependencies flow from `CLI → features → core`. The core layer does not import the CLI or feature modules.
`--help`, `analyze`, and `report` do not need to import Frida or UnityPy.

## Platform selection

1. Select a device using a Frida device ID, USB, or `--host`.
2. Read the OS from `query_system_parameters().os.id`.
3. Filter default `dump` agents by platform support.
4. Reject explicitly selected incompatible agents before attachment.

`--platform` overrides detection for endpoints such as Gadget that cannot provide OS information.
`ue4` is Android-only; available functionality differs between platforms.
See the [support matrix](platforms.md).

## Agent output

```javascript
send({ event: "log", message: "status" });
send({ event: "file", name: "output.bin" }, arrayBuffer);
send({ event: "json", name: "result.json", data: { key: "value" } });
```

The host displays logs and saves files in the dump directory.
Agents exposing `flush()` also attempt to save buffered events on Ctrl+C or timeout.
Forced termination or a crash can lose buffered events.

`memscan` and `mempatch` expose `rpc.exports` so Python can invoke scans, reads, and writes.
They are not part of the default `dump` agent set.

## Offline analysis

`analyze_dump()` runs analyzers in order and collects results for available files in `report.json`.
UE4 artifact analysis lives in `analyze/ue4.py`, so it does not require a device connection.
Steps that require missing optional external tools are skipped.

`generate_html()` dispatches each result key to a section renderer.
Unknown keys use a generic JSON view. CSS and JavaScript are embedded in a single HTML file.
