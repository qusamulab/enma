# エージェント一覧

`dump -t NAME` で収集処理を選びます。省略時は対応 OS の全種類を実行します。
`memscan` と `mempatch` は専用コマンドから操作し、`dump` には含まれません。
[OS別の対応表](platforms.md) と [出力ファイル](output-files.md) も参照してください。

## Android・iOS 共通

### `il2cpp` — Unity IL2CPP

公開 IL2CPP API を持つモジュールを検出し、シンボルマップを `il2cpp_dump.json` に保存します。
Android の `libil2cpp.so` と iOS の UnityFramework 等に対応し、後からロードされるモジュールも監視します。
メモリ上のバイナリと `global-metadata.dat` の取得を試みます。メモリイメージはディスク上の実行ファイルの完全な復元ではありません。
暗号化・配置変更・シンボル削除によって取得できない場合があります。

### `coverage` — コードカバレッジ

Frida Stalker で実行された基本ブロックを収集し、`coverage.json` に保存します。
実行負荷が高いため、短いセッションで使ってください。

### `tracer` — 関数トレース

対象モジュールの公開関数をフックし、引数・戻り値・スレッド情報を `trace.json` に保存します。
既定では多数の関数を対象にし、最大5,000件を記録します。アプリの実行に負荷がかかります。

### `sqlite` — SQL の観測

Android は SQLiteDatabase／SQLiteStatement／Room、iOS は
`sqlite3_exec`／`sqlite3_prepare_v2`／`sqlite3_prepare_v3` を観測します。
`sqlite_log.json` に保存します。iOS は DB ハンドルと SQL が対象で、バインド値・結果行は含みません。

### `fileio` — ファイル操作

ネイティブの `open`／`write`／`unlink` と、Android では Java のファイル API を監視します。
Android のアプリデータ領域、iOS のコンテナーや Documents 等のパスを `fileio_log.json` に記録します。

### `dlopen` — ライブラリのロード

`dlopen` と `dlsym` を観測し、`dlopen_log.json`／`dlsym_log.json` に保存します。
後からロードされたモジュールのメモリイメージを `dlopen_*` に保存する場合があります。

### `memscan` — メモリ検索

`enma memscan TARGET` の対話操作で、値の検索・絞り込み・読み取りを行います。
整数、符号なし整数、浮動小数点、バイト列に対応します。

### `mempatch` — メモリ書き換え

`enma mempatch TARGET ADDR` で値・バイト列・NOP の書き込み、定期的な値の書き戻しを行います。
対象アーキテクチャに合わせて NOP を生成します。

## iOS 専用

### `ios_app` — アプリ情報

NSBundle から Bundle ID、名前、バージョン、ビルドを読み取り、アーキテクチャと
ロード済みモジュール一覧を `ios_app.json` に保存します。HTML レポートにも表示します。

### `ios_http` — NSURLSession

NSURLSession のデータ・ダウンロード・アップロードタスク作成を観測し、URL と HTTP メソッドを
`http_traffic.json` に保存します。通信本文・レスポンス・WebSocket は対象外です。
内部で複数の API を経由する場合、同じリクエストの記録が重複することがあります。

### `ios_crypto` — CommonCrypto

`CCCrypt`、`CCCryptorCreate`、`CCCryptorCreateWithMode` のアルゴリズム・操作・キーを
`crypto_keys.json` に記録します。CryptoKit や独自の暗号実装は対象外です。

## Android 専用

### `dex` — DEX の抽出

クラスローダー、ART、メモリスキャンを利用し、`classes_N_*.dex` と
`dex_obfuscation_report.json` を保存します。

### `assets` — Unity AssetBundle

IL2CPP、ファイルアクセス、UnityFS 等のマジック値、AssetManager から
AssetBundle を検出し、`.unity3d` として保存します。

### `mono` — Mono DLL

Mono の埋め込み API とロード処理から管理アセンブリを探し、`.dll` を保存します。

### `heap` — Java ヒープ

キー、SharedPreferences、URL、文字列、高エントロピーのバイト列等を収集し、`heap_*.json` に保存します。

### `jni` — JNI マッピング

RegisterNatives 等をフックし、Java メソッドとネイティブ関数の対応を `jni_map.json` に記録します。

### `ssl` — Android の TLS 検証

TrustManager、OkHttp の CertificatePinner、ネイティブ SSL 等の検証処理に介入します。
取得した SNI ホスト名は `tls_connections.json` に保存します。iOS の pinning には対応しません。

### `crypto` — Android の暗号処理

Java Crypto、OpenSSL API、メモリ上の候補からキーを収集し、`crypto_keys.json` 等に保存します。

### `anti_detect` — 検出処理への介入

root、エミュレーター、デバッガー等の確認 API と `/proc` の参照を対象にします。

### `anti_tamper` — 整合性確認

署名確認、ptrace、マップ参照、CRC 等を観測・処理し、`anti_tamper_log.json` に記録します。

### `safetynet` — SafetyNet／Play Integrity

端末認証 API と関連情報を `safetynet_log.json` に記録します。
端末認証のサーバー側検証を通過できることを保証するものではありません。

### `http` — Android の HTTP

OkHttp、HttpURLConnection、Volley を観測し、`http_traffic.json` に保存します。
収集できる本文やステータスは、使用するライブラリとフックに依存します。

### `websocket` — WebSocket

OkHttp と javax.websocket の送受信イベントを `websocket_log.json` に保存します。

### `protobuf` — Protobuf

protobuf-java、Wire、OkHttp の対象ボディを観測し、簡易デコード結果を `protobuf_log.json` に保存します。

### `binder` — Binder／IPC

Intent、ContentProvider、ネイティブ Binder の操作を `binder_log.json` に記録します。

### `ue4_sdk` — UE4 の SDK 情報

GNames／FNamePool と GUObjectArray からクラス・関数等を読み、`ue4_sdk.json` に保存します。
UE4.23–4.27 のレイアウトが対象です。検出できない場合は `ue4` コマンドでアドレスを指定します。

### `ue4_pak` — UE4 の PAK

PAK のパスやメモリを検出し、`ue4_pak_list.json` と `ue4_pak_*.pak` に保存します。

### `ue4_blueprint` — Blueprint トレース

UObject::ProcessEvent を観測し、`ue4_blueprint_trace.json` に保存します。
`ue4` コマンドの `--process-event` でアドレスを指定できます。
