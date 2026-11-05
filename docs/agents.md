# Agent reference

Select agents with `dump -t NAME`. Omitting `-t` runs all agents supported on the target OS.
`memscan` and `mempatch` use dedicated commands and are not included in `dump`.
See also the [support matrix](platforms.md) and [output files](output-files.md).

## Shared Android and iOS agents

### `il2cpp` — Unity IL2CPP

Detects modules exposing public IL2CPP APIs and saves a symbol map to `il2cpp_dump.json`.
Supports Android's `libil2cpp.so` and iOS modules such as UnityFramework, including modules loaded later.
Attempts to capture the in-memory binary and `global-metadata.dat`.
Memory images are not complete reconstructions of on-disk executables.
Encryption, relocated metadata, or stripped symbols can prevent collection.

### `coverage` — Code coverage

Uses Frida Stalker to collect executed basic blocks in `coverage.json`.
Instrumentation can be expensive; use short sessions.

### `tracer` — Function tracing

Hooks exported functions in target modules and records arguments, return values,
and thread information in `trace.json`. The default matches many functions and
records up to 5,000 events, which can add substantial overhead.

### `sqlite` — SQL observation

Observes SQLiteDatabase, SQLiteStatement, and Room on Android.
On iOS, observes `sqlite3_exec`, `sqlite3_prepare_v2`, and `sqlite3_prepare_v3`.
Saves events to `sqlite_log.json`. iOS events contain database handles and SQL,
without bound values or result rows.

### `fileio` — File operations

Monitors native `open`, `write`, and `unlink`, plus Java file APIs on Android.
Records relevant Android data paths and iOS container or Documents paths in `fileio_log.json`.

### `dlopen` — Library loading

Observes `dlopen` and `dlsym`, saving events to `dlopen_log.json` and `dlsym_log.json`.
May also save in-memory images of newly loaded modules as `dlopen_*` files.

### `memscan` — Memory scanning

Use `enma memscan TARGET` to search, filter, and read memory interactively.
Supports signed and unsigned integers, floating-point values, and byte patterns.

### `mempatch` — Memory patching

Use `enma mempatch TARGET ADDR` to write values, bytes, or NOP instructions,
or repeatedly restore a value. NOP instructions match the target architecture.

## iOS agents

### `ios_app` — App information

Reads the bundle identifier, name, version, and build from NSBundle.
Saves them with the architecture and loaded module inventory to `ios_app.json`,
which also appears in the HTML report.

### `ios_http` — NSURLSession

Observes NSURLSession data, download, and upload task creation.
Saves URLs and HTTP methods to `http_traffic.json`.
Does not capture request bodies, responses, or WebSocket messages.
Requests can appear more than once when internal calls pass through multiple observed APIs.

### `ios_crypto` — CommonCrypto

Records algorithms, operations, and keys from `CCCrypt`, `CCCryptorCreate`, and
`CCCryptorCreateWithMode` in `crypto_keys.json`.
Does not cover CryptoKit or custom cryptographic implementations.

## Android agents

### `dex` — DEX extraction

Uses class loaders, ART, and memory scanning to save `classes_N_*.dex`
and `dex_obfuscation_report.json`.

### `assets` — Unity AssetBundles

Detects AssetBundles through IL2CPP, file access, UnityFS and other magic values,
and AssetManager. Saves bundles as `.unity3d` files.

### `mono` — Mono DLLs

Uses Mono embedding APIs and load hooks to find managed assemblies and save `.dll` files.

### `heap` — Java heap

Collects keys, SharedPreferences, URLs, strings, and high-entropy byte arrays into `heap_*.json`.

### `jni` — JNI mappings

Hooks RegisterNatives and related paths to record Java-to-native method mappings in `jni_map.json`.

### `ssl` — Android TLS verification

Intercepts verification paths in TrustManager, OkHttp CertificatePinner, and native SSL.
Saves observed SNI hostnames to `tls_connections.json`. Does not support iOS pinning.

### `crypto` — Android cryptographic operations

Collects keys from Java Crypto, OpenSSL APIs, and memory candidates into `crypto_keys.json`
and related artifacts.

### `anti_detect` — Detection checks

Targets root, emulator, and debugger detection APIs and `/proc` access.

### `anti_tamper` — Integrity checks

Observes or intercepts signature checks, ptrace, map access, and CRC-related operations.
Records events in `anti_tamper_log.json`.

### `safetynet` — SafetyNet and Play Integrity

Records device attestation API calls and related information in `safetynet_log.json`.
Does not guarantee successful server-side attestation verification.

### `http` — Android HTTP

Observes OkHttp, HttpURLConnection, and Volley and saves `http_traffic.json`.
Available bodies and status information depend on the library and hook used.

### `websocket` — WebSocket

Saves OkHttp and javax.websocket send/receive events to `websocket_log.json`.

### `protobuf` — Protobuf

Observes protobuf-java, Wire, and relevant OkHttp bodies.
Saves events and basic decoding results to `protobuf_log.json`.

### `binder` — Binder and IPC

Records Intent, ContentProvider, and native Binder operations in `binder_log.json`.

### `ue4_sdk` — UE4 SDK information

Reads GNames/FNamePool and GUObjectArray to reconstruct classes, functions, and related data
in `ue4_sdk.json`. Targets UE4.23–4.27 layouts.
Use the `ue4` command to supply addresses when detection fails.

### `ue4_pak` — UE4 PAK files

Detects PAK paths and memory and saves `ue4_pak_list.json` and `ue4_pak_*.pak`.

### `ue4_blueprint` — Blueprint tracing

Observes UObject::ProcessEvent and saves `ue4_blueprint_trace.json`.
Supply the address with the `ue4` command's `--process-event` option.
