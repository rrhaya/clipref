# pbe

pbe（Pasteboard Export）は、クリップボードのテキストをローカルファイルに保存し、絶対パスをコピーします。
ログや長いテキストをAIコーディングエージェントに渡すためのツールです。

既存のスクリプトやショートカットからは `clipref` でも実行できます。

[English](README.md)

## 動作環境

macOS。BashとmacOS標準コマンドを使います。
インストーラーはGitHubからダウンロードします。インストール後のコマンドはネット通信を行いません。

## インストール

### Homebrew

```sh
brew install rrhaya/tap/clipref
```

更新は`brew upgrade clipref`、削除は`brew uninstall clipref`で行えます。
シェル版も導入している場合は、`command -v pbe`で優先される実行ファイルを確認してください。

### シェルインストーラー

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/v0.3.0/install.sh | bash'
```

`v0.3.0`を`~/.local/bin`にインストールします。
シェルの設定ファイルは変更しません。`PATH`に登録されていない場合は、
次の行を`~/.zshrc`に追加して、新しいターミナルを開いてください。

```sh
export PATH="$HOME/.local/bin:$PATH"
```

新しいターミナルでインストールを確認します。

```sh
pbe --version
pbe --help
```

実行権限はインストーラーが設定します。別途`chmod`する必要はありません。

### インストール先を変更

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/v0.3.0/install.sh | bash -s -- --bin-dir "$HOME/bin"'
```

必要に応じて、指定したディレクトリを`PATH`に追加してください。
`--bin-dir`はコマンドのインストール先、`pbe --dir`はテキストの保存先を指定します。

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
if [ ! -e "$HOME/.local/bin/pbe" ] && [ ! -L "$HOME/.local/bin/pbe" ]; then
  ln -sh clipref "$HOME/.local/bin/pbe"
fi
```

3. 現在のシェルの`PATH`に追加して、コマンドを確認します。

```sh
export PATH="$HOME/.local/bin:$PATH"
pbe --help
pbe --version
```

次回以降のターミナルでも使うには、`export`の行を`~/.zshrc`に追加してください。

## 使い方

1. 保存したいログやテキストをコピーします。
2. ターミナルで実行します。

```sh
pbe
```

3. コピーされたパスをエージェントに貼り付け、調べたい内容を伝えます。

パスはターミナルにも表示されます。保存先を指定する場合は、先にディレクトリを作ります。

```sh
mkdir -p ./tmp
pbe --dir ./tmp
```

その他の指定:

```sh
pbe --dir ./tmp          # 保存先を指定（既存のディレクトリ）
pbe --ext log            # input.logとして保存
your-command 2>&1 | pbe  # コマンド出力を保存
pbe --no-copy            # クリップボードを変更せず、パスを表示
```

パイプ入力がある場合は、クリップボードより優先します。`pbe --clipboard`で
入力元を明示すると、ランチャーやショートカットからもクリップボードを読めます。
この場合、標準入力は読みません。このオプションはv0.2.0以降で利用できます。
拡張子の初期値は`txt`です。
拡張子の指定はファイル名だけを変えます。内容の変換は行いません。
`pbe --name startup-error.log`でファイル名を指定できます。
空白や日本語も使えます。パス区切り・タブ・改行は使えません。`--name`と`--ext`は併用できません。
`--name`を指定した場合は、設定ファイルの拡張子よりファイル名を優先します。
入力の空白や改行はそのまま保存します。末尾に改行を追加しません。

## 設定ファイル

v0.2.0以降で利用できます。`~/.config/clipref/config`
（`XDG_CONFIG_HOME`を指定した場合はその下の`clipref/config`）を作成します。

```text
dir=~/logs
ext=log
```

保存先は先に作成してください。値に引用符は付けません。シェル式は実行せず、
先頭の`~/`だけをホームディレクトリに置き換えます。保存先は絶対パスか`~/`で指定します。
空行と`#`で始まる行は無視します。優先順位はCLI指定、設定ファイル、初期値の順です。
未知のキー・重複したキー・不正な値はエラーになります。

## 保存ファイル

キー操作で実行する場合は[macOSショートカットの設定手順](docs/shortcuts.ja.md)を参照してください。

v0.3.0では、実行ごとに `20261126170042-Ab3xY7/input.txt` のようなパスを作ります。
フォルダ名の先頭14桁は保存を始めた現地時刻（年月日時分秒）です。
末尾のランダムな6文字で同じ秒に保存したファイルを区別します。
ファイルは所有者だけが読み書きできます。

標準の保存先は `${TMPDIR:-/tmp}/clipref-<ユーザーID>` です。
設定ファイルの `dir` または `--dir` を使う場合は、指定先に日時付きフォルダが作られます。

空の入力はエラーになります。保存が成功してからクリップボードを変更します。
パスのコピーに失敗した場合もファイルは残り、パスはターミナルに表示されます。

標準の保存先をまとめて片付けるには、保存処理が終わってから、
保存時と同じ `TMPDIR` でフォルダをゴミ箱へ移動します。

```sh
/usr/bin/trash "${TMPDIR:-/tmp}/clipref-$(id -u)"
```

`/usr/bin/trash` が使えない場合は、Finder に対象を表示して `⌘ Delete` を押します。

```sh
open -R "${TMPDIR:-/tmp}/clipref-$(id -u)"
```

次の既定保存時にフォルダが再作成されます。移動したファイルは履歴で `missing` と表示されます。
従来の `clipref.XXXXXX` フォルダは元の場所に残ります。
一時ファイルはOSによって削除される場合があります。残しておきたいファイルには `--dir` を使ってください。

## 履歴

v0.2.0以降で利用できます。

```sh
pbe list --limit 10  # 直近のパスとexists/missingを表示
pbe last            # 直近の保存パスを表示・コピー
pbe last --no-copy  # クリップボードを変えずに表示
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
bash -n packaging/homebrew/prepare-formula.sh
shellcheck --shell=bash bin/clipref install.sh packaging/homebrew/prepare-formula.sh
python3 -B -m unittest discover -s tests -v
ruby -c packaging/homebrew/clipref.rb
```

テストはダミーのクリップボードコマンドを使います。実際のクリップボードにはアクセスしません。
Python 3はテストにのみ必要です。
ShellCheckは静的検査にのみ必要です。macOSでは`brew install shellcheck`で導入できます。

GitHub Actionsでも、pushとpull request時にmacOS上で構文チェックとテストを実行します。
ShellCheckでBashスクリプトをUbuntu上で検査します。
DependabotはGitHub Actionsの依存を確認し、週次で更新PRを作成します。

ローカルのコマンドを手動で確認するには、リポジトリのルートで以下を実行します。
ダミー入力を使い、保存先・設定・履歴を一時ディレクトリに分けます。

```sh
(
  clipref_smoke=$(mktemp -d "${TMPDIR:-/tmp}/clipref-smoke.XXXXXX") || exit 1
  export TMPDIR="$clipref_smoke" XDG_CONFIG_HOME="$clipref_smoke/config"
  export XDG_STATE_HOME="$clipref_smoke/state"
  mkdir "$clipref_smoke/custom"
  printf 'sample log\n' | bash bin/pbe --no-copy
  printf 'custom log\n' | bash bin/pbe --no-copy --dir "$clipref_smoke/custom" --name sample.log
  bash bin/pbe list
  bash bin/pbe last --no-copy
)
```

1件目は `clipref-<ユーザーID>`、2件目は `custom` 配下に保存されます。
`list` には両方が `exists` と表示され、`last --no-copy` は2件目の絶対パスを表示します。

## 更新

インストーラーに使いたいバージョンのタグを指定します。

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/main/install.sh | bash -s -- --version v0.3.0'
```

## アンインストール

```sh
if [ "$(readlink "$HOME/.local/bin/pbe" 2>/dev/null)" = clipref ]; then
  rm "$HOME/.local/bin/pbe"
fi
rm "$HOME/.local/bin/clipref"
```

保存ファイルは残ります。不要になったファイルは別途削除してください。

## ライセンス

MIT。
