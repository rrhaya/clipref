# Homebrew Formula

公開済みの v0.3.0 アーカイブを使い、`pbe` と `clipref` をインストールします。

```sh
brew install rrhaya/tap/clipref
pbe --version
brew upgrade clipref
brew uninstall clipref
```

アンインストールしても保存ファイルは残ります。install.shでも導入した場合は、
`command -v pbe` でどちらが使われているか確認してください。

## 公開・検証手順

リリース公開後に、clipref のチェックアウトからタグ付きアーカイブで Formula を生成します。

```sh
curl -fL https://github.com/rrhaya/clipref/archive/refs/tags/v0.3.0.tar.gz -o /tmp/clipref-v0.3.0.tar.gz
bash packaging/homebrew/prepare-formula.sh v0.3.0 /tmp/clipref-v0.3.0.tar.gz
```

生成結果を確認し、`rrhaya/homebrew-tap` の `Formula/clipref.rb` と、このリポジトリの
`packaging/homebrew/clipref.rb` を更新します。補助スクリプトはアーカイブ内の実行ファイルの
Bash 構文とバージョンを確認し、取得したアーカイブの SHA-256 を計算します。

更新前に macOS で次を確認します。

```sh
brew style rrhaya/tap/clipref
brew audit --strict rrhaya/tap/clipref
brew install --build-from-source rrhaya/tap/clipref
brew test rrhaya/tap/clipref
pbe --version
```
