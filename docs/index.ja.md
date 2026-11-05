# enma を使い始める

enma は [Frida](https://frida.re) を使う Android・iOS 向けランタイム解析ツールです。
アプリを動かしながら情報を収集し、JSON と HTML レポートにまとめます。
自分が所有する、または解析の許可を得たアプリを対象にしてください。

このサイトの標準言語は英語です。ヘッダーの言語メニューで English／日本語を切り替えられます。
切り替えると、同じ内容のページへ移動します。

## 1. インストール

Python 3.12 以降と [uv](https://docs.astral.sh/uv/) が必要です。

```bash
git clone https://github.com/qusamulab/enma
cd enma
uv sync
uv run enma --help
```

## 2. 端末を準備する

| 対象 | 準備 |
|---|---|
| Android | ADB と root 化済み端末／エミュレーター。`uv run enma setup` で frida-server を配置 |
| iOS | Frida に対応した脱獄端末に frida-server を導入。USB 接続とペアリングを確認 |
| Gadget | 自分で組み込んだ Frida Gadget に TCP 接続。OS は `--platform` で指定 |

具体的な手順と対応機能は [Android・iOS の準備](platforms.md) を参照してください。

## 3. アプリから収集する

まずアプリ一覧で Android のパッケージ名、または iOS の Bundle ID を調べます。

```bash
uv run enma list
```

対象アプリを起動してから、必要なエージェントを選んで実行します。

=== "Android"

    ```bash
    uv run enma dump com.example.game -t dex http sqlite -o ./dump --timeout 30
    ```

=== "iOS"

    ```bash
    uv run enma dump com.example.app -t ios_app ios_http sqlite -o ./dump --timeout 30
    ```

アプリを起動する場合は `--spawn`、起動を待つ場合は `--watch` を追加します。
`-t` を省略すると、その OS に対応する全エージェントを読み込みます。
`coverage` と `tracer` は負荷が高いため、最初は必要なものだけを選ぶことを勧めます。

## 4. レポートを見る

```bash
uv run enma analyze ./dump
uv run enma report ./dump
open ./dump/report.html   # macOS。ほかのOSではブラウザーで開く
```

`analyze` と `report` は端末に接続せずに使えます。
`jadx`、`Il2CppDumper`、`strings` は任意です。未導入の解析処理はスキップします。
生成されるファイルの意味は [出力ファイル](output-files.md) にまとめています。

## 次に読む

- [コマンド一覧](subcommands.md)：引数、メモリ操作、Unity・UE4 の使い方
- [エージェント一覧](agents.md)：収集内容と対応 OS
- [トラブルシューティング](troubleshooting.md)：接続・出力・公開サイトの問題
- [構成とデータの流れ](architecture.md)：コードを読むための全体像
- [開発ガイド](development.md)：検証手順と機能の追加方法
