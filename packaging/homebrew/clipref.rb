class Clipref < Formula
  desc "Save clipboard text to a file and copy its absolute path"
  homepage "https://github.com/rrhaya/clipref"
  url "https://github.com/rrhaya/clipref/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "e99aebf89a25c20a6c131bcc254780377fcc3234c4d0ed0a64083722bb247f0b"
  license "MIT"

  depends_on :macos

  def install
    bin.install "bin/clipref"
  end

  test do
    assert_equal "clipref #{version}\n", shell_output("#{bin}/clipref --version")
    assert_match "Usage: clipref", shell_output("#{bin}/clipref --help")
  end
end
