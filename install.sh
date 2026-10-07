#!/bin/bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash install.sh [--bin-dir DIRECTORY] [--version TAG]

Install clipref on macOS. Default directory: ~/.local/bin
Default release: v0.2.0. Tags must have the form vMAJOR.MINOR.PATCH.
EOF
}
die() { printf 'clipref installer: %s\n' "$*" >&2; exit 1; }

bin_dir="$HOME/.local/bin"
release_tag=v0.2.0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --bin-dir)
      [ "$#" -ge 2 ] || die 'missing value for --bin-dir'
      [ -n "$2" ] || die 'install directory must not be empty'
      bin_dir=$2
      shift 2
      ;;
    --version)
      [ "$#" -ge 2 ] || die 'missing value for --version'
      release_tag=$2
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ "$(uname -s)" = Darwin ] || die 'macOS is required'
[[ "$release_tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] \
  || die 'release tag must have the form vMAJOR.MINOR.PATCH'

work_dir=$(mktemp -d "${TMPDIR:-/tmp}/clipref-install.XXXXXX")
download="$work_dir/clipref"
cleanup() {
  rm -f -- "$download"
  rmdir -- "$work_dir"
}
trap cleanup EXIT

curl -fsSL "https://raw.githubusercontent.com/rrhaya/clipref/$release_tag/bin/clipref" -o "$download" \
  || die 'download failed; existing installation was not changed'
[ -s "$download" ] || die 'download is empty'
IFS= read -r first_line < "$download"
[ "$first_line" = '#!/bin/bash' ] || die 'download is not a Bash script'
/bin/bash -n "$download" || die 'download has invalid Bash syntax'

mkdir -p -- "$bin_dir"
bin_dir=$(cd -- "$bin_dir" && pwd -P)
install -m 755 "$download" "$bin_dir/clipref"
printf 'Installed: %s/clipref\n' "$bin_dir"
case ":$PATH:" in
  *":$bin_dir:"*) printf 'Run: clipref --help\n' ;;
  *)
    printf 'Add this directory to PATH: %s\n' "$bin_dir"
    printf 'For the default directory, add to ~/.zshrc:\n'
    printf '  export PATH="$HOME/.local/bin:$PATH"\n'
    ;;
esac
