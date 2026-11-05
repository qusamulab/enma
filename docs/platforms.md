# Platform setup

Connection requirements and available artifacts depend on the target OS.
enma uses Frida's OS identifier to select agents and excludes Android-only agents on iOS.
Explicitly selecting an unsupported agent fails before attaching to the app.

## Support matrix

| Feature | Android | iOS |
|---|---|---|
| App listing, PID/identifier attachment, spawning, and waiting for launch | Supported | Supported |
| USB and TCP connections | Supported | Supported |
| Memory scanning and patching | `memscan` / `mempatch` | Same |
| Code coverage and function tracing | `coverage` / `tracer` | Same |
| IL2CPP symbols and metadata | `il2cpp` | `il2cpp`, using public IL2CPP APIs in UnityFramework or another runtime module |
| File I/O and dynamic library loading | `fileio` / `dlopen` | Same, with iOS container paths and Mach-O modules |
| SQLite | Java / Room | Public SQLite C APIs; records SQL and database handles |
| HTTP | `http`: OkHttp and other libraries | `ios_http`: NSURLSession URLs and methods |
| Cryptographic operations | `crypto`: Java / OpenSSL | `ios_crypto`: CommonCrypto keys and algorithms |
| App information and module inventory | App listing | `ios_app`: bundle ID, version, and loaded modules |
| DEX, JNI, Java heap, Binder, SafetyNet, and UE4 | Supported | Not supported |
| SSL pinning, WebSocket, Protobuf, Mono, and AssetBundle collection | Android agents | Not supported |
| Automatic frida-server deployment and APK repacking | `setup` / `repack` | Not supported; no IPA resigning |
| Offline analysis, HTML reports, and Unity asset extraction | Supported | Uses the same offline processing |

This matrix describes the implementation. iOS behavior still needs validation on a real device.
Encrypted metadata, hidden symbols, and custom networking can prevent collection.
`ios_http` records task creation without request bodies or responses.
CryptoKit, custom cryptography, and iOS TLS pinning bypass are not supported.

## Android

1. Add ADB to your PATH and authorize USB debugging.
2. Check the connection with `adb devices`.
3. Run the following on a device where root access is available.

```bash
uv run enma setup
uv run enma list
uv run enma dump com.example.app -t dex http sqlite --timeout 30
```

Use `-s SERIAL` when multiple devices are connected.
For Gadget injection into an APK without root, see [repack](subcommands.md).

## iOS

1. Install frida-server in a compatible jailbreak environment using the [official Frida iOS instructions](https://frida.re/docs/ios/).
2. Match the host and device Frida versions. Check the host version with `uv run frida --version`.
3. Connect the device over USB and complete trust and pairing prompts.
4. Verify app listing with `uv run frida-ps -Uai` and `uv run enma list`.

```bash
# Attach to a running app; the OS is detected automatically
uv run enma dump com.example.iosapp -t ios_app ios_http sqlite --timeout 30

# Select a device
uv run enma dump com.example.iosapp -s DEVICE_UDID -t ios_app

# Scan memory
uv run enma memscan com.example.iosapp
```

`setup` uses Android's ADB. It does not install frida-server on iOS.
For non-jailbroken apps, prepare Gadget integration and code signing in your own app's development environment.

## TCP and Gadget

`--host` selects a frida-server or Gadget endpoint. It cannot be combined with `-s`.
Specify `--platform` if Gadget cannot provide OS information.

```bash
uv run enma list --host 127.0.0.1:27042
uv run enma dump Gadget --host 127.0.0.1:27042 --platform ios -t ios_app ios_http
```

Use the process name shown by `list` or `frida-ps`.
