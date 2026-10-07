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
2. `clipref.rb`をtapの`Formula/clipref.rb`に配置します。
3. `brew style rrhaya/tap/clipref`と`brew audit --strict rrhaya/tap/clipref`を実行します。
4. macOSで`brew install --build-from-source rrhaya/tap/clipref`と
   `brew test rrhaya/tap/clipref`を実行します。
5. `clipref --version`を確認してから、両READMEに導入コマンドを記載します。

新しいリリースでは、`url`のタグと、ダウンロードしたアーカイブのSHA-256を更新します。
上記の検証を再実行し、リリース公開後にtapの更新を公開します。移動するブランチのURLは使いません。

検証状況: 公開アーカイブのダウンロード・チェックサム計算・Ruby構文チェックは完了しました。
一時ディレクトリでFormulaのインストール処理を動かし、実行権限・`--version`・`--help`も確認しました。
Homebrewのstyle・audit・インストール・Formulaテストはtap準備後に行います。
