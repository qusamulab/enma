# Android・iOS の準備

接続方法と収集できる情報は OS によって異なります。
自動判定には Frida の OS ID を使い、Android 専用エージェントを iOS に読み込みません。
明示的に非対応のエージェントを指定すると、アタッチ前にエラーになります。

## 対応範囲

| 機能 | Android | iOS |
|---|---|---|
| アプリ一覧、PID／識別子で接続、起動・起動待ち | 対応 | 対応 |
| USB／TCP 接続 | 対応 | 対応 |
| メモリ検索・書き換え | `memscan` / `mempatch` | 同左 |
| コードカバレッジ・関数トレース | `coverage` / `tracer` | 同左 |
| IL2CPP シンボル・メタデータ | `il2cpp` | `il2cpp`。UnityFramework 等の公開 IL2CPP API を使用 |
| ファイルI/O・動的ライブラリ | `fileio` / `dlopen` | 同左。iOS コンテナーと Mach-O に対応 |
| SQLite | Java / Room | 公開 SQLite C API。SQL と DB ハンドルを記録 |
| HTTP | `http`：OkHttp 等 | `ios_http`：NSURLSession の URL とメソッド |
| 暗号処理 | `crypto`：Java / OpenSSL | `ios_crypto`：CommonCrypto のキーとアルゴリズム |
| アプリ情報・モジュール一覧 | アプリ一覧 | `ios_app`：Bundle ID、バージョン、ロード済みモジュール |
| DEX、JNI、Java ヒープ、Binder、SafetyNet、UE4 | 対応 | 非対応 |
| SSL pinning、WebSocket、Protobuf、Mono、AssetBundle の収集 | Android 用エージェント | 非対応 |
| frida-server 自動配置・APK リパック | `setup` / `repack` | 非対応。IPA の再署名は行わない |
| 収集後の解析・HTML レポート・Unity 資産の展開 | 対応 | 同じオフライン処理を利用可能 |

この対応表は実装の範囲です。iOS 実機での動作確認は別途必要です。
暗号化されたメタデータ、隠されたシンボル、独自の通信実装は取得できない場合があります。
`ios_http` は通信本文・レスポンスを取得せず、タスク作成を記録します。
CryptoKit／独自暗号や iOS の TLS pinning 回避には対応していません。

## Android

1. ADB を PATH に追加し、USB デバッグを許可する。
2. `adb devices` で端末を確認する。
3. root 権限を利用できる端末で次を実行する。

```bash
uv run enma setup
uv run enma list
uv run enma dump com.example.app -t dex http sqlite --timeout 30
```

複数端末がある場合は `-s SERIAL` を指定します。
root を使えない場合の APK への Gadget 組み込みは [repack](subcommands.md) を参照してください。

## iOS

1. 対応する脱獄環境に、[Frida 公式の iOS 手順](https://frida.re/docs/ios/)に従って frida-server を導入する。
2. ホストと端末の Frida のバージョンを合わせる。ホストは `uv run frida --version` で確認できる。
3. 端末を USB 接続し、信頼・ペアリングを済ませる。
4. `uv run frida-ps -Uai` と `uv run enma list` でアプリを確認する。

```bash
# 起動済みアプリへ接続。OS は自動判定される
uv run enma dump com.example.iosapp -t ios_app ios_http sqlite --timeout 30

# 特定の端末を選ぶ
uv run enma dump com.example.iosapp -s DEVICE_UDID -t ios_app

# メモリ検索
uv run enma memscan com.example.iosapp
```

`setup` は Android の ADB 用です。iOS の frida-server 導入は自動化しません。
非脱獄アプリへの Gadget 組み込みとコード署名は、所有するアプリの開発環境で行ってください。

## TCP／Gadget

`--host` は frida-server または Gadget の接続先です。`-s` と同時指定はできません。
Gadget で OS 情報を取得できない場合に `--platform` を指定します。

```bash
uv run enma list --host 127.0.0.1:27042
uv run enma dump Gadget --host 127.0.0.1:27042 --platform ios -t ios_app ios_http
```

接続先のプロセス名は `list` または `frida-ps` の結果に合わせてください。
