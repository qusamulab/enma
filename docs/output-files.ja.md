# 出力ファイル

収集先は `dump -o DIR` で指定し、既定では `./dump` です。
全ファイルが毎回生成されるわけではなく、対象 API・イベントが観測されたものを保存します。

## 最初に見るもの

| ファイル | 内容 |
|---|---|
| `report.html` | `report` が生成する閲覧用 HTML |
| `report.json` | `analyze` が生成する解析結果 |
| `ios_app.json` | iOS の Bundle ID、バージョン、モジュール一覧 |
| `http_traffic.json` | HTTP 観測結果。iOS は URL・メソッドのみ |
| `sqlite_log.json` / `fileio_log.json` | SQL／ファイル操作 |

`analyze DIR` を実行してから `report DIR` を実行します。
任意の出力先は [コマンド一覧](subcommands.md) を参照してください。

## バイナリとゲーム資産

| ファイル | 内容 |
|---|---|
| `classes_N_*.dex` / `dex_obfuscation_report.json` | Android DEX／難読化の情報 |
| `libil2cpp.so` / `UnityFramework` / `*.dylib` | IL2CPP 等のメモリイメージ。OS・モジュール名で異なる |
| `global-metadata.dat` / `il2cpp_dump.json` | IL2CPP メタデータ／シンボルマップ |
| `*.dll` / `asset_*.unity3d` | Mono DLL／Unity AssetBundle |
| `dlopen_*` | 後からロードされたライブラリのメモリイメージ |
| `ue4_sdk.json` / `ue4_pak_list.json` / `ue4_pak_*.pak` | Android UE4 の SDK／PAK |
| `ue4_blueprint_trace.json` | Android UE4 の Blueprint 呼び出し |

メモリイメージは元のファイルと同一とは限らず、そのまま実行・再署名できるものではありません。

## イベントと詳細情報

| ファイル | 内容 |
|---|---|
| `crypto_keys.json` / `rsa_private_key.der` | 暗号処理の観測情報。iOS は CommonCrypto が対象 |
| `tls_connections.json` | Android の TLS SNI |
| `jni_map.json` | Android の JNI マッピング |
| `heap_*.json` | Android Java ヒープのキー・文字列・設定等 |
| `websocket_log.json` / `protobuf_log.json` / `binder_log.json` | Android の通信・IPC |
| `dlopen_log.json` / `dlsym_log.json` | 動的ライブラリ／シンボルの解決 |
| `coverage.json` / `trace.json` | コードカバレッジ／関数呼び出し |
| `anti_tamper_log.json` / `safetynet_log.json` | Android の整合性確認・端末認証関連 |

生のイベントをすべて HTML に表示するわけではありません。詳細は元の JSON を確認してください。
