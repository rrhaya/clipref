# Homebrew formula

The formula pins the published v0.2.0 archive. It installs only the Bash command.

```sh
brew install rrhaya/tap/clipref
brew upgrade clipref
brew uninstall clipref
```

Saved files are kept after uninstalling. If you also used `install.sh`, run
`command -v clipref` to check which installation your shell uses.

## Release updates

After publishing a new release, download its archive and generate the formula:

```sh
curl -fL https://github.com/rrhaya/clipref/archive/refs/tags/v0.2.0.tar.gz -o /tmp/clipref-v0.2.0.tar.gz
bash packaging/homebrew/prepare-formula.sh v0.2.0 /tmp/clipref-v0.2.0.tar.gz
```

Review the output and copy it to `Formula/clipref.rb` in `rrhaya/homebrew-tap`.
Keep this repository's `packaging/homebrew/clipref.rb` in sync.
The helper checks the expected archive member, Bash syntax, and command version.
It calculates a checksum from the downloaded bytes; it does not verify a publisher signature.
Use a release tag, never a moving branch, for the formula URL.

Run these checks on macOS before publishing the formula:

```sh
brew style rrhaya/tap/clipref
brew audit --strict rrhaya/tap/clipref
brew install --build-from-source rrhaya/tap/clipref
brew test rrhaya/tap/clipref
```

Local verification: the v0.2.0 archive was downloaded from GitHub; its SHA-256 is
`23f2642c68a6befc4ccdee8fc8d681f2a89a7a31c64b92826d22a6ce39459268`.
Style, strict audit, source installation, and formula tests passed on macOS.
The tap used for that verification was registered from the local checkout;
public tap creation and an installation from its GitHub URL remain to be verified.
