# clipref

クリップボードのテキストをローカルファイルに保存し、絶対パスをコピーします。
ログや長いテキストをAIコーディングエージェントに渡すためのツールです。

[English](README.md)

## 動作環境

macOS。BashとmacOS標準コマンドを使います。ネット通信は行いません。

## インストール

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/main/install.sh | bash'
```

現在の`main`のコードを`~/.local/bin`にインストールします。更新も同じコマンドで行えます。
シェルの設定ファイルは変更しません。`PATH`に登録されていない場合は、
次の行を`~/.zshrc`に追加して、新しいターミナルを開いてください。

```sh
export PATH="$HOME/.local/bin:$PATH"
```

### ソースからインストール

1. ソースを取得します。

```sh
git clone https://github.com/rrhaya/clipref.git
cd clipref
```

2. コマンドをインストールします。

```sh
mkdir -p "$HOME/.local/bin"
install -m 755 bin/clipref "$HOME/.local/bin/clipref"
```

3. 現在のシェルの`PATH`に追加して、コマンドを確認します。

```sh
export PATH="$HOME/.local/bin:$PATH"
clipref --help
```

次回以降のターミナルでも使うには、`export`の行を`~/.zshrc`に追加してください。

## 使い方

1. 保存したいログやテキストをコピーします。
2. ターミナルで実行します。

```sh
clipref
```

3. コピーされたパスをエージェントに貼り付け、調べたい内容を伝えます。

パスはターミナルにも表示されます。保存先を指定する場合は、先にディレクトリを作ります。

```sh
mkdir -p ./tmp
clipref --dir ./tmp
```

その他の指定:

```sh
clipref --dir ./tmp             # 保存先を指定（既存のディレクトリ）
clipref --ext log               # input.logとして保存
your-command 2>&1 | clipref     # コマンド出力を保存
clipref --no-copy               # クリップボードを変更せず、パスを表示
```

パイプ入力がある場合は、クリップボードより優先します。拡張子の初期値は`txt`です。
拡張子の指定はファイル名だけを変えます。内容の変換は行いません。
入力の空白や改行はそのまま保存します。末尾に改行を追加しません。

## 保存ファイル

実行ごとに、システムの一時ディレクトリまたは`--dir`で指定した場所に
`clipref.XXXXXX`ディレクトリを作ります。ファイルは所有者だけが読み書きできます。
既存ファイルは上書きしません。

空の入力はエラーになります。保存が成功してからクリップボードを変更します。
パスのコピーに失敗した場合もファイルは残り、パスはターミナルに表示されます。

cliprefは保存ファイルを削除しません。システムの一時ファイルはOSによって削除される場合があります。
残しておきたい場合や、エージェントのワークスペース内に置きたい場合は`--dir`を使ってください。

## エージェントへの渡し方

エージェントが保存ファイルにアクセスできる必要があります。
別マシンのエージェントにローカルパスだけを渡しても、ファイルは読めません。

ファイルに保存するだけでトークン消費が減るわけではありません。
全文を読み込む代わりに、必要な箇所を検索して読むように伝えます。

```text
ログ: /absolute/path/to/input.log
起動失敗の原因を調べてください。まず末尾100行を確認し、
エラーを検索して、必要に応じてその前後を読んでください。
```

## 開発

```sh
bash -n bin/clipref
bash -n install.sh
python3 -m unittest discover -s tests -v
```

テストはダミーのクリップボードコマンドを使います。実際のクリップボードにはアクセスしません。
Python 3はテストにのみ必要です。

GitHub Actionsでも、pushとpull request時にmacOS上で構文チェックとテストを実行します。

## 更新

ソースを取得したディレクトリで実行します。

```sh
git pull --ff-only
install -m 755 bin/clipref "$HOME/.local/bin/clipref"
```

## アンインストール

```sh
rm "$HOME/.local/bin/clipref"
```

保存ファイルは残ります。不要になったファイルは別途削除してください。

## 今後の予定

保存先と拡張子の初期値を設定ファイルで指定できるようにします。
現在は`--dir`と`--ext`を使ってください。

## ライセンス

MIT。
