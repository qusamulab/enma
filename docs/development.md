# Development guide

## Project layout

```text
src/enma/
├── cli.py                 # Argument parsing and dispatch
├── core/                  # Connections, platforms, registry, script preparation
├── dump.py / mem.py       # Shared runtime operations
├── ue4.py                 # Android UE4 runtime operations
├── frida_server.py        # Android setup
├── repack.py              # Android APK Gadget injection
├── unity.py               # Offline AssetBundle extraction
├── analyze/
│   ├── __init__.py        # analyze_dump() and analyzer order
│   ├── helpers.py         # JSON, counting, external tools
│   ├── binaries.py        # DEX, IL2CPP, DLLs, native strings
│   ├── events.py          # Network, storage, app metadata
│   └── ue4.py             # Offline UE4 analysis
├── report/
│   ├── __init__.py        # generate_html() / render_report()
│   ├── components.py      # Shared HTML components
│   ├── sections.py        # Section renderers and registry
│   └── assets/            # Report CSS and JavaScript
└── agents/                # JavaScript executing inside the target app
    ├── _runtime.js        # Shared Frida API compatibility
    └── ios/               # iOS-specific agents
```

Public entry points remain `enma.analyze.analyze_dump` and
`enma.report.generate_html` / `render_report`.
See [Architecture](architecture.md) for the component boundaries and dependency direction.

## Validation

```bash
uv sync --group docs
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest
node --test tests/agents.test.cjs
uv run mkdocs build --strict
```

Python tests do not need a device. Fixtures replace external tool lookups, network access,
and the home directory so tests do not touch real device connections or Frida caches.
JavaScript tests use Node.js 22+ and mocked Frida APIs to verify hook behavior.
Differences between actual OS and API versions require separate device testing.

## Add an agent

1. Create `agents/{category}/{name}_agent.js`.
2. Register the name, category, tags, and supported platforms in `core/agents.py`.
3. Add an analyzer to the appropriate `analyze/` module and register it in `_ANALYZERS`.
4. Add a renderer in `report/sections.py` and register it in `_RENDERERS`.
5. Update both translations of [Agent reference](agents.md) and [Platform setup](platforms.md).
6. Verify hook behavior, incompatible-platform rejection, and analysis results using mocked APIs and artifacts.

```python
_a("example", "ios", TAG_DUMP, platforms=(Platform.IOS,)),
```

`TAG_DUMP` is for `dump`, `TAG_UE4` for `ue4`, and `TAG_MEM` for memory operations.
Tests check the registry against JavaScript files and agent headings in both documentation languages.
Let `core/scripts.py` provide runtime bridges instead of copying Java or Objective-C bridges into agents.

## Edit and publish documentation

```bash
uv sync --group docs
uv run mkdocs serve
uv run mkdocs build --strict
```

Configuration lives in `mkdocs.yml`, and pages live in `docs/`.
Keep the README short and place detailed instructions in the relevant guide.

English is the default language. Each page has two source files:

| Source | Published path |
|---|---|
| `docs/index.md` | `/enma/` |
| `docs/index.ja.md` | `/enma/ja/` |
| `docs/platforms.md` | `/enma/platforms/` |
| `docs/platforms.ja.md` | `/enma/ja/platforms/` |

The `mkdocs-static-i18n` plugin builds both languages and provides the Material language menu.
Switching languages opens the corresponding page. Navigation labels are translated in `mkdocs.yml`.
Update both versions when a page changes. Use relative links such as `platforms.md` in both
languages; the plugin resolves them to the active language, so do not add `.ja` to page links.

GitHub Actions builds documentation and configuration changes on `main` and deploys them to GitHub Pages.
For initial setup, select **GitHub Actions** as the repository's Pages source.
The site is published at [qusamulab.github.io/enma](https://qusamulab.github.io/enma/).
