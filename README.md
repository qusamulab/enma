# enma

English | [日本語](README.ja.md)

An Android and iOS runtime analysis toolkit powered by [Frida](https://frida.re).
Collect runtime artifacts from apps and turn them into JSON and HTML reports.
Use it with apps you own or have permission to analyze.

**[Documentation](https://qusamulab.github.io/enma/) · [Platform setup](docs/platforms.md) · [Command reference](docs/subcommands.md)**

The documentation defaults to English. Use the language menu to switch between
English and [日本語](https://qusamulab.github.io/enma/ja/).

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/qusamulab/enma
cd enma
uv sync
```

For Android, install ADB, connect a rooted device or emulator, and run `uv run enma setup`.
For iOS, use a Frida-compatible jailbroken device or an app with Gadget that you have prepared yourself.
Start with the [platform setup and support matrix](docs/platforms.md).

## Collect artifacts and generate a report

```bash
uv run enma list

# Android: attach to a running app
uv run enma dump com.example.app -t dex http sqlite -o ./dump --timeout 30

# iOS: select the agents you need
uv run enma dump com.example.iosapp -t ios_app ios_http sqlite -o ./dump --timeout 30

uv run enma analyze ./dump
uv run enma report ./dump
# Open ./dump/report.html in a browser
```

The OS is detected automatically. Omitting `-t` runs all agents supported on that OS.
iOS HTTP collection captures NSURLSession URLs and methods, without bodies or responses.
DEX, APK repacking, and UE4 support are Android-only. iOS behavior still needs device testing.

## Development and documentation

```bash
uv sync --group docs
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest
node --test tests/agents.test.cjs
uv run mkdocs build --strict
uv run mkdocs serve
```

[Development guide](docs/development.md) · [Architecture](docs/architecture.md) · [Troubleshooting](docs/troubleshooting.md)

Collected files can contain sensitive material such as cryptographic keys. Handle them appropriately.
[MIT License](LICENSE)
