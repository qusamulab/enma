# Troubleshooting

## Device not found

- Android: check `adb devices`, authorize USB debugging, and run `uv run enma setup`.
- iOS: check pairing, USB connectivity, and frida-server. `setup` is Android-only.
- Both: verify connectivity with `uv run frida-ps -Uai` and match the host and server Frida versions.
- TCP: use `--host HOST:PORT`. It cannot be combined with the device ID option `-s`.

## Cannot attach to an app

Find the identifier with `uv run enma list`, then start the app.
Use `--spawn` if it is stopped, or `--watch` to wait for a manual launch.
Numeric targets are treated as PIDs. For Gadget, use the process name from the listing.

## OS detection fails or an agent is unsupported

Use `--platform android` or `--platform ios` when endpoints such as Gadget cannot provide OS information.
Android agents such as `dex`, `jni`, and `http` cannot run on iOS.
Use `ios_http` for iOS networking. See [Platform setup](platforms.md) for the support matrix.

## Few artifacts or missing JSON files

Interact with the app after loading the agents to trigger networking, file access, or other operations.
Some JSON files are only created when matching events occur.
Most agents save periodically, and Ctrl+C or `--timeout` attempts to flush before detaching.
Crashes or forced termination can lose buffered events.
iOS `ios_http` observes NSURLSession task creation without bodies or responses.

## report.json not found

Analyze the same directory before generating a report.

```bash
uv run enma analyze ./dump
uv run enma report ./dump
```

Missing optional tools such as `jadx` only skip the relevant analysis step.
An empty dump directory can still produce HTML, but it will not contain collected-data sections.

## Documentation returns 404

The current URL is [https://qusamulab.github.io/enma/](https://qusamulab.github.io/enma/).
Update bookmarks pointing to the old `ykus4.github.io` domain.

Administrators should check **Actions → Deploy documentation** and **Settings → Pages** on GitHub.
The source should be GitHub Actions. A successful build alone does not publish the site;
the Pages deployment must also succeed.
Preview locally with `uv sync --group docs` and `uv run mkdocs serve`.

## Switch the documentation language

Use the language menu in the site header to choose English or 日本語.
English is available at the site root, and Japanese is under `/ja/`.
The switch preserves the page you are reading. Local `mkdocs serve` previews support both languages too.
