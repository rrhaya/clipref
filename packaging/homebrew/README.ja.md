# Homebrew Formula

公開済みv0.1.0のアーカイブを使うFormulaです。Bashコマンドをインストールし、
クリップボードに触れずに`--version`と`--help`をテストします。

tapの公開は未完了です。`rrhaya/homebrew-tap`を作成し、`Formula/clipref.rb`を
配置して検証した後に、次のコマンドで導入・更新・削除できるようになります。

```sh
brew install rrhaya/tap/clipref
brew upgrade clipref
brew uninstall clipref
```

アンインストールしても保存ファイルは残ります。install.shでも導入した場合は、
`command -v clipref`でどちらが使われているか確認してください。

## 公開・検証手順

1. 作成の承認後に、公開リポジトリ`rrhaya/homebrew-tap`を作成します。
2. 公開アーカイブを取得し、以下の手順で`Formula/clipref.rb`を生成します。同梱のFormulaはまだv0.1.0です。
3. `brew style rrhaya/tap/clipref`と`brew audit --strict rrhaya/tap/clipref`を実行します。
4. macOSで`brew install --build-from-source rrhaya/tap/clipref`と
   `brew test rrhaya/tap/clipref`を実行します。
5. `clipref --version`を確認してから、両READMEに導入コマンドを記載します。

新しいリリースでは、`url`のタグと、ダウンロードしたアーカイブのSHA-256を更新します。
上記の検証を再実行し、リリース公開後にtapの更新を公開します。移動するブランチのURLは使いません。

cliprefのチェックアウトから実行します。tapは隣の`homebrew-tap`に配置してください。
各コマンドの成功を確認してから、次へ進んでください。

```sh
clipref_archive=$(mktemp -t clipref-release)
curl -fsSL https://github.com/rrhaya/clipref/archive/refs/tags/v0.2.0.tar.gz -o "$clipref_archive"
mkdir -p ../homebrew-tap/Formula
bash packaging/homebrew/prepare-formula.sh v0.2.0 "$clipref_archive" > ../homebrew-tap/Formula/clipref.rb.new &&
  mv ../homebrew-tap/Formula/clipref.rb.new ../homebrew-tap/Formula/clipref.rb
rm "$clipref_archive"
```

補助スクリプトはアーカイブ内の実行ファイル、Bash構文、バージョンを確認し、
実際のバイト列からチェックサムを計算します。配布者の署名を検証するものではありません。
Formulaの差分を確認してコミットし、tapを公開した後、上記のHomebrew検証を行います。

検証状況: 公開アーカイブのダウンロード・チェックサム計算・Ruby構文チェックは完了しました。
一時ディレクトリでFormulaのインストール処理を動かし、実行権限・`--version`・`--help`も確認しました。
Homebrewのstyle・audit・インストール・Formulaテストはtap準備後に行います。
