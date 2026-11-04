# enma

[Frida](https://frida.re) を使う Android・iOS ランタイム解析ツール。
アプリから実行時の情報を収集し、JSON と HTML レポートにまとめます。
所有する、または解析の許可を得たアプリを対象にしてください。

**[ドキュメント](https://qusamulab.github.io/enma/) · [Android・iOS の準備](docs/platforms.md) · [コマンド一覧](docs/subcommands.md)**

## インストール

Python 3.12 以降と [uv](https://docs.astral.sh/uv/) が必要です。

```bash
git clone https://github.com/qusamulab/enma
cd enma
uv sync
```

Android は ADB と root 化済み端末／エミュレーターを用意し、`uv run enma setup` を実行します。
iOS は Frida 対応の脱獄端末、または自分で Gadget を組み込んだアプリを用意します。
[OS 別の手順と対応範囲](docs/platforms.md) を先に確認してください。

## 収集してレポートを見る

```bash
uv run enma list

# Android：起動済みアプリから収集
uv run enma dump com.example.app -t dex http sqlite -o ./dump --timeout 30

# iOS：必要なエージェントを選択
uv run enma dump com.example.iosapp -t ios_app ios_http sqlite -o ./dump --timeout 30

uv run enma analyze ./dump
uv run enma report ./dump
# ./dump/report.html をブラウザーで開く
```

OS は自動判定します。`-t` を省略すると、その OS に対応する全エージェントを実行します。
iOS の HTTP 収集は NSURLSession の URL・メソッドが対象で、本文・レスポンスは含みません。
DEX、APK リパック、UE4 などは Android 専用です。iOS 実機での検証は別途必要です。

## 開発・ドキュメント

```bash
uv sync --group docs
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest
node --test tests/agents.test.cjs
uv run mkdocs build --strict
uv run mkdocs serve
```

[開発ガイド](docs/development.md) · [構成とデータの流れ](docs/architecture.md) · [困ったとき](docs/troubleshooting.md)

収集ファイルには暗号キー等の機密情報が含まれる場合があります。適切に管理してください。
[MIT License](LICENSE)
