# Command reference

Start with [Getting started](index.md) for the basic workflow.
Run `uv run enma COMMAND --help` for all arguments.
`--verbose` is available on every command, before or after the command name.

## Shared connection options

These options apply to `dump`, `ue4`, `memscan`, and `mempatch`.

| Option | Meaning |
|---|---|
| `TARGET` | Android package, iOS bundle identifier, process name, or PID |
| `-s ID` / `--serial ID` | Frida device ID: Android serial or iOS UDID |
| `--host HOST:PORT` | TCP frida-server or Gadget endpoint; cannot be combined with `-s` |
| `--platform auto/android/ios` | Auto-detect the OS by default; override when needed for Gadget |
| `--spawn` | Start the app and attach |
| `--watch` | Wait for the app to start, then attach |

`list` supports `-s` and `--host`. See [Platform setup](platforms.md) for OS limitations.

## list — List apps

```bash
uv run enma list
uv run enma list -s DEVICE_ID
uv run enma list --host 127.0.0.1:27042
```

Prints the identifier, app name, and PID if the app is running.

## dump — Collect runtime artifacts

```bash
uv run enma dump com.example.app -t dex http -o ./dump --timeout 30
uv run enma dump com.example.iosapp -t ios_app ios_http sqlite -o ./ios-dump
```

| Option | Meaning |
|---|---|
| `-t TYPE [TYPE …]` | Agents to run; defaults to all agents supported on the OS |
| `-o DIR` | Output directory; defaults to `./dump` |
| `--timeout SECONDS` | Stop after the given duration; `0` (default) runs until Ctrl+C |
| `--retry` | Reconnect after the target exits; Ctrl+C and timeout stop the session |

Interact with the app while collecting. See [Output files](output-files.md) for saved artifacts
and [Agent reference](agents.md) for each agent's behavior.

## analyze — Offline analysis

```bash
uv run enma analyze ./dump
uv run enma analyze ./dump -o ./analysis.json
```

Analyzes collected files and writes `report.json` in the dump directory by default.
No device connection is needed. Steps that require missing optional tools are skipped.

## report — HTML report

```bash
uv run enma report ./dump
uv run enma report ./dump --json ./analysis.json -o ./report.html
```

Reads `./dump/report.json` and writes `./dump/report.html` by default.
CSS and JavaScript are embedded, so the report is a single file.

## memscan — Search memory

Works on Android and iOS. Opens an interactive prompt for the target.

```bash
uv run enma memscan com.example.app
```

```text
scan 100 int32
filter 90 eq
results 20
read 0x12345678 int32
info
reset
quit
```

Types include signed and unsigned integers, `float`, `double`, and `bytes`.
Filters include `eq`, `ne`, `gt`, `lt`, `gte`, `lte`, `changed`, and `unchanged`.

## mempatch — Read and write memory

Works on Android and iOS. Here, `-v` means the value to write.
Use the long form `--verbose` for debug logging.

```bash
uv run enma mempatch com.example.app 0x12345678 -t int32
uv run enma mempatch com.example.app 0x12345678 -t int32 -v 100
uv run enma mempatch com.example.app 0x12345678 --bytes DE AD BE EF
uv run enma mempatch com.example.app 0x12345678 --nop 4
uv run enma mempatch com.example.app 0x12345678 -v 100 --freeze --interval 100
```

`--freeze` repeatedly writes the value at the specified interval in milliseconds.
Press Ctrl+C to stop.

## setup — Deploy frida-server (Android)

```bash
uv run enma setup
uv run enma setup -s ANDROID_SERIAL --force
```

Downloads the server for the device ABI, deploys it to `/data/local/tmp/frida-server`
using ADB and `su`, and starts it. `--force` forces redeployment.
Downloads are cached in `~/.cache/enma/`. See [iOS setup](platforms.md#ios) for iOS.

## repack — Inject Gadget into an APK (Android)

```bash
uv run enma repack app.apk --arch arm64 -o app-gadget.apk
```

Requires `apktool`, `zipalign`, `keytool`, and either `apksigner` or `jarsigner`.
Decodes the APK, injects Gadget, and signs it with a debug key.
`--arch` accepts `arm64`, `arm`, `x86_64`, or `x86`. Use `--keep-workdir` to retain intermediate files.
The original signature is not preserved. IPA repacking is not supported.

## unity — Extract AssetBundles

```bash
uv sync --extra unity
uv run enma unity ./dump -o ./extracted
```

Uses UnityPy to read collected `.unity3d` files and extract images, text, audio, and other assets.
The default output directory is `unity_extracted/` inside the dump directory.

## ue4 — Analyze Unreal Engine 4 (Android)

```bash
uv run enma ue4 com.example.game -t ue4_sdk ue4_pak -o ./dump
```

Omitting `-t` loads all UE4 agents. Supply known addresses with
`--gnames`, `--gobjects`, and `--process-event`.
`--extract-pak` uses `u4pak` after collection to extract PAK files accessible on the host.
A device-side path alone does not make the file accessible from the host.
