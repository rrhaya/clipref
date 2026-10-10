Add a release-archive-to-formula helper so a release update changes the URL and checksum together. It checks the archive member, command version and Bash syntax before producing any formula output. Tests cover invalid archives and verify the emitted checksum against the input bytes. CI now checks the helper as well.

The Homebrew instructions explain how to generate and publish the formula. Actual tap-style and strict-audit checks passed on the local v0.1.0 formula; all 49 unit tests and ShellCheck passed.

Related to #7 and #10. Neither issue is closed by this PR: the v0.2.0 archive download, tap publication and Homebrew install/test remain unverified. The isolated published-tag source check used fetched GitHub sources with stubbed curl transport. Shortcut GUI/key execution remains under #5. See docs/maintenance-2026-10.md for evidence and limitations.
