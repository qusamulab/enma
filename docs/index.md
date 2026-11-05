# Getting started with enma

enma is an Android and iOS runtime analysis toolkit powered by [Frida](https://frida.re).
Collect information while an app runs, then turn it into JSON and HTML reports.
Use it with apps you own or have permission to analyze.

This site defaults to English. Use the language menu in the header to switch to Japanese.
The switch opens the corresponding page in the other language.

## 1. Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/qusamulab/enma
cd enma
uv sync
uv run enma --help
```

## 2. Prepare your device

| Target | Preparation |
|---|---|
| Android | Install ADB and connect a rooted device or emulator. Deploy frida-server with `uv run enma setup` |
| iOS | Install frida-server on a compatible jailbroken device. Check USB connectivity and pairing |
| Gadget | Connect over TCP to an app with Frida Gadget you have prepared. Specify its OS with `--platform` |

See [Platform setup](platforms.md) for instructions and the support matrix.

## 3. Collect artifacts

List apps to find an Android package name or iOS bundle identifier.

```bash
uv run enma list
```

Start the target app, then choose the agents you need.

=== "Android"

    ```bash
    uv run enma dump com.example.game -t dex http sqlite -o ./dump --timeout 30
    ```

=== "iOS"

    ```bash
    uv run enma dump com.example.app -t ios_app ios_http sqlite -o ./dump --timeout 30
    ```

Add `--spawn` to start the app, or `--watch` to wait for it to start.
Omitting `-t` loads all agents supported on the target OS.
`coverage` and `tracer` can be expensive, so start with a small selection.

## 4. View the report

```bash
uv run enma analyze ./dump
uv run enma report ./dump
open ./dump/report.html   # macOS; on other systems, open the file in a browser
```

`analyze` and `report` work without a connected device.
`jadx`, `Il2CppDumper`, and `strings` are optional. Steps that need missing tools are skipped.
See [Output files](output-files.md) for the artifacts produced by each step.

## Next steps

- [Command reference](subcommands.md): arguments, memory operations, Unity, and UE4
- [Agent reference](agents.md): collected data and supported platforms
- [Troubleshooting](troubleshooting.md): connection, output, and documentation problems
- [Architecture](architecture.md): components and data flow
- [Development guide](development.md): validation and adding features
