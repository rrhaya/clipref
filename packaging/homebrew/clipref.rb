class Clipref < Formula
  desc "Save clipboard text to a file and copy its absolute path"
  homepage "https://github.com/rrhaya/clipref"
  url "https://github.com/rrhaya/clipref/archive/refs/tags/v0.3.0.tar.gz"
  sha256 "b6f0a9ed1561ed59f179c840e24664aeb1ce316464a0bd18ce1124ce3386cd3f"
  license "MIT"

  depends_on :macos

  def install
    bin.install "bin/clipref"
    chmod 0555, bin/"clipref"
    bin.install_symlink bin/"clipref" => "pbe"
  end

  test do
    assert_equal "clipref #{version}\n", shell_output("#{bin}/clipref --version")
    assert_match "Usage: clipref", shell_output("#{bin}/clipref --help")
    assert_match "Usage:", shell_output("#{bin}/pbe --help")
  end
end
