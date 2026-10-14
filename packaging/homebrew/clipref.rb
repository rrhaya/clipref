class Clipref < Formula
  desc "Save clipboard text to a file and copy its absolute path"
  homepage "https://github.com/rrhaya/clipref"
  url "https://github.com/rrhaya/clipref/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "23f2642c68a6befc4ccdee8fc8d681f2a89a7a31c64b92826d22a6ce39459268"
  license "MIT"

  depends_on :macos

  def install
    bin.install "bin/clipref"
    chmod 0555, bin/"clipref"
  end

  test do
    assert_equal "clipref #{version}\n", shell_output("#{bin}/clipref --version")
    assert_match "Usage: clipref", shell_output("#{bin}/clipref --help")
  end
end
