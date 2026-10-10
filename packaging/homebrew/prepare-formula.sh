#!/bin/bash
set -euo pipefail

die() { printf 'prepare-formula: %s\n' "$*" >&2; exit 1; }
[ "$#" -eq 2 ] || die 'usage: bash prepare-formula.sh vMAJOR.MINOR.PATCH ARCHIVE.tar.gz'
tag=$1
archive=$2
[[ "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || die 'invalid release tag'
[ -f "$archive" ] && [ -r "$archive" ] || die 'archive is not a readable file'

# Extract one known member to stdout; never unpack archive paths onto disk.
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/clipref-formula.XXXXXX")
script="$work_dir/clipref"
cleanup() { rm -f -- "$script"; rmdir -- "$work_dir"; }
trap cleanup EXIT
tar -xzOf "$archive" "clipref-${tag#v}/bin/clipref" > "$script" \
  || die 'archive does not contain the requested release'
[ -s "$script" ] || die 'archive command is empty'
IFS= read -r first_line < "$script"
[ "$first_line" = '#!/bin/bash' ] || die 'archive command is not a Bash script'
/bin/bash -n "$script" || die 'archive command has invalid Bash syntax'
grep -Fxq "version=${tag#v}" "$script" || die 'command version does not match release tag'
checksum=$(shasum -a 256 "$archive")
checksum=${checksum%% *}

cat <<EOF
class Clipref < Formula
  desc "Save clipboard text to a file and copy its absolute path"
  homepage "https://github.com/rrhaya/clipref"
  url "https://github.com/rrhaya/clipref/archive/refs/tags/$tag.tar.gz"
  sha256 "$checksum"
  license "MIT"

  depends_on :macos

  def install
    bin.install "bin/clipref"
    chmod 0555, bin/"clipref"
  end

  test do
    assert_equal "clipref #{version}\\n", shell_output("#{bin}/clipref --version")
    assert_match "Usage: clipref", shell_output("#{bin}/clipref --help")
  end
end
EOF
