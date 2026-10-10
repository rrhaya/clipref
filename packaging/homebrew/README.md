# Homebrew formula

The formula targets the published v0.1.0 archive. It installs the Bash command
and tests `--version` and `--help` without accessing the clipboard.

Publishing a tap is still pending. The following commands are for after
`rrhaya/homebrew-tap` exists and contains `Formula/clipref.rb`:

```sh
brew install rrhaya/tap/clipref
brew upgrade clipref
brew uninstall clipref
```

Saved files are kept after uninstalling. If you also installed clipref with
install.sh, use `command -v clipref` to check which installation your shell uses.

## Publish and verify

1. Create the public repository `rrhaya/homebrew-tap` after authorization.
2. Download the published archive and generate `Formula/clipref.rb` using the commands below. The checked-in formula still targets v0.1.0; do not publish it as v0.2.0.
3. Run `brew style rrhaya/tap/clipref` and `brew audit --strict rrhaya/tap/clipref`.
4. Run `brew install --build-from-source rrhaya/tap/clipref` and
   `brew test rrhaya/tap/clipref` on macOS.
5. Verify `clipref --version`, then add the install commands to the main READMEs.

For a new release, update the tag in `url` and replace `sha256` with the SHA-256
of the downloaded archive. Re-run the checks above and publish the tap change
after the release is available. Do not use a moving branch as the formula URL.

From the clipref checkout, with the tap checked out beside it:

```sh
clipref_archive=$(mktemp -t clipref-release)
curl -fsSL https://github.com/rrhaya/clipref/archive/refs/tags/v0.2.0.tar.gz -o "$clipref_archive"
mkdir -p ../homebrew-tap/Formula
bash packaging/homebrew/prepare-formula.sh v0.2.0 "$clipref_archive" > ../homebrew-tap/Formula/clipref.rb.new &&
  mv ../homebrew-tap/Formula/clipref.rb.new ../homebrew-tap/Formula/clipref.rb
rm "$clipref_archive"
```

Run each command only after the preceding command succeeds. The helper validates
the archive member, Bash syntax and command version before emitting a formula.
It computes the checksum from the downloaded bytes; it does not verify a publisher signature.
Review and commit the formula, publish the tap, then run the Homebrew checks above.

Validation so far: downloaded the release archive and computed its checksum;
checked Ruby syntax and the formula's installation phase in an isolated directory,
including executable permissions, `--version`, and `--help`.
Full Homebrew style, audit, installation, and formula tests remain
pending until the tap is set up.
