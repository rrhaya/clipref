# clipref

クリップボードのテキストをローカルファイルに保存し、絶対パスをコピーします。
ログや長いテキストをAIコーディングエージェントに渡すためのツールです。

[English](README.md)

## 動作環境

macOS。BashとmacOS標準コマンドを使います。ネット通信は行いません。

## インストール

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/v0.1.0/install.sh | bash'
```

`v0.1.0`を`~/.local/bin`にインストールします。
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
git checkout v0.1.0
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
clipref --version
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

パイプ入力がある場合は、クリップボードより優先します。`clipref --clipboard`で
入力元を明示すると、ランチャーやショートカットからもクリップボードを読めます。
この場合、標準入力は読みません。このオプションはv0.1.0以降の開発ソースで利用できます。
拡張子の初期値は`txt`です。
拡張子の指定はファイル名だけを変えます。内容の変換は行いません。
v0.1.0以降の開発ソースでは、`clipref --name startup-error.log`でファイル名を指定できます。
空白や日本語も使えます。パス区切り・タブ・改行は使えません。`--name`と`--ext`は併用できません。
入力の空白や改行はそのまま保存します。末尾に改行を追加しません。

## 保存ファイル

実行ごとに、システムの一時ディレクトリまたは`--dir`で指定した場所に
`clipref.XXXXXX`ディレクトリを作ります。ファイルは所有者だけが読み書きできます。
既存ファイルは上書きしません。

空の入力はエラーになります。保存が成功してからクリップボードを変更します。
パスのコピーに失敗した場合もファイルは残り、パスはターミナルに表示されます。

cliprefは保存ファイルを削除しません。システムの一時ファイルはOSによって削除される場合があります。
残しておきたい場合や、エージェントのワークスペース内に置きたい場合は`--dir`を使ってください。

## 履歴

v0.1.0以降の開発ソースで利用できます。

```sh
clipref list --limit 10  # 直近のパスとexists/missingを表示
clipref last            # 直近の保存パスを表示・コピー
clipref last --no-copy  # クリップボードを変えずに表示
```

一覧のパスはシェル用に引用します。`last`は元の絶対パスをコピーします。
直近のファイルが消えている場合は、別のファイルを選ばずエラーにします。
記録ファイルの更新日時が新しい順に表示します。同時保存では順序が前後する場合があります。

保存に成功するとパスだけを記録します。`--dir`で保存したファイルも対象です。
記録は所有者だけがアクセスできる`~/.local/state/clipref/history`に置きます。
`XDG_STATE_HOME`を指定した場合は、その下の`clipref/history`を使います。
保存先の設定は履歴の場所には影響しません。消えたファイルも一覧に残り、自動削除はしません。
記録に失敗しても保存ファイルは残り、パスのコピーを行って警告を表示します。

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

インストーラーに使いたいバージョンのタグを指定します。

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/main/install.sh | bash -s -- --version v0.1.0'
```

## アンインストール

```sh
rm "$HOME/.local/bin/clipref"
```

保存ファイルは残ります。不要になったファイルは別途削除してください。

## ライセンス

MIT。
