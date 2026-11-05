# コマンド一覧

迷ったら [使い始める](index.md) の手順を実行してください。
全引数は `uv run enma COMMAND --help` で確認できます。
`--verbose` は全コマンドで利用でき、コマンドの前後どちらにも指定できます。

## 接続の共通オプション

`dump`、`ue4`、`memscan`、`mempatch` に共通です。

| オプション | 意味 |
|---|---|
| `TARGET` | Android パッケージ、iOS Bundle ID、プロセス名、または PID |
| `-s ID` / `--serial ID` | Frida の端末 ID。Android シリアルまたは iOS UDID |
| `--host HOST:PORT` | TCP の frida-server／Gadget。`-s` と同時指定不可 |
| `--platform auto/android/ios` | 既定は OS 自動判定。Gadget 等で必要なときに上書き |
| `--spawn` | アプリを起動して接続 |
| `--watch` | アプリが起動するまで待って接続 |

`list` は `-s` と `--host` に対応します。OS の制約は [対応範囲](platforms.md) を参照してください。

## list — アプリ一覧

```bash
uv run enma list
uv run enma list -s DEVICE_ID
uv run enma list --host 127.0.0.1:27042
```

識別子、アプリ名、実行中の場合は PID を表示します。

## dump — ランタイム情報の収集

```bash
uv run enma dump com.example.app -t dex http -o ./dump --timeout 30
uv run enma dump com.example.iosapp -t ios_app ios_http sqlite -o ./ios-dump
```

| オプション | 意味 |
|---|---|
| `-t TYPE [TYPE …]` | 使用するエージェント。省略時は OS に対応する全種類 |
| `-o DIR` | 収集先。既定は `./dump` |
| `--timeout SECONDS` | 指定秒数で終了。既定の `0` は Ctrl+C まで実行 |
| `--retry` | 対象プロセス終了後に再接続を試みる。Ctrl+C／タイムアウトでは終了 |

収集中にアプリを操作してください。結果は [出力ファイル](output-files.md) に保存します。
エージェントごとの内容は [エージェント一覧](agents.md) を参照してください。

## analyze — オフライン解析

```bash
uv run enma analyze ./dump
uv run enma analyze ./dump -o ./analysis.json
```

収集済みファイルを解析し、既定では収集先に `report.json` を生成します。
端末への接続は不要です。任意の外部ツールがない場合は該当処理をスキップします。

## report — HTML レポート

```bash
uv run enma report ./dump
uv run enma report ./dump --json ./analysis.json -o ./report.html
```

既定では `./dump/report.json` を読み、`./dump/report.html` に出力します。
CSS・JavaScript は HTML に含まれるため、単一ファイルで閲覧できます。

## memscan — メモリ値の検索

Android・iOS 共通です。対象を指定すると対話プロンプトが開きます。

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

型は整数、符号なし整数、`float`、`double`、`bytes`。
絞り込みは `eq`、`ne`、`gt`、`lt`、`gte`、`lte`、`changed`、`unchanged` です。

## mempatch — メモリの読み書き

Android・iOS 共通です。`-v` はこのコマンドでは書き込み値です。
詳細ログには長い形式の `--verbose` を使ってください。

```bash
uv run enma mempatch com.example.app 0x12345678 -t int32
uv run enma mempatch com.example.app 0x12345678 -t int32 -v 100
uv run enma mempatch com.example.app 0x12345678 --bytes DE AD BE EF
uv run enma mempatch com.example.app 0x12345678 --nop 4
uv run enma mempatch com.example.app 0x12345678 -v 100 --freeze --interval 100
```

`--freeze` は指定値をミリ秒単位の間隔で書き戻します。Ctrl+C で停止します。

## setup — frida-server の配置（Android）

```bash
uv run enma setup
uv run enma setup -s ANDROID_SERIAL --force
```

ABI に合うサーバーを取得し、ADB と `su` で `/data/local/tmp/frida-server` に配置して起動します。
`--force` は再配置を強制します。キャッシュは `~/.cache/enma/` です。
iOS の準備は [iOS](platforms.md#ios) を参照してください。

## repack — APK への Gadget 組み込み（Android）

```bash
uv run enma repack app.apk --arch arm64 -o app-gadget.apk
```

`apktool`、`zipalign`、`keytool`、`apksigner` または `jarsigner` が必要です。
APK を展開して Gadget を組み込み、デバッグキーで再署名します。
`--arch` は `arm64`、`arm`、`x86_64`、`x86`。`--keep-workdir` で中間ファイルを残せます。
元の署名は引き継がれません。IPA のリパックには対応していません。

## unity — AssetBundle の展開

```bash
uv sync --extra unity
uv run enma unity ./dump -o ./extracted
```

収集済みの `.unity3d` ファイルを UnityPy で読み、画像・テキスト・音声等を展開します。
既定の出力先は収集ディレクトリ内の `unity_extracted/` です。

## ue4 — Unreal Engine 4 の解析（Android）

```bash
uv run enma ue4 com.example.game -t ue4_sdk ue4_pak -o ./dump
```

`-t` を省略すると UE4 エージェントをすべて読み込みます。
`--gnames`、`--gobjects`、`--process-event` で既知のアドレスを指定できます。
`--extract-pak` は収集後にホストで読み出せる PAK を `u4pak` で展開します。
デバイス上のパスだけでは、ホストからファイルを読めません。
