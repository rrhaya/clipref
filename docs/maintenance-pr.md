## Changes

Failed installer writes could corrupt an existing executable, symlink destinations were replaced, and custom installation directories received incorrect PATH advice. The installer now stages the executable before replacement, rejects non-regular destinations, and prints a usable PATH command for the chosen directory.

Interrupted input now removes incomplete saves. Completed files remain available if history or clipboard copying fails. History listing avoids the command argument limit and reports listing failures instead of treating them as empty results.

Closes #12
Closes #13
Closes #14

## Validation

- Regression tests reproduce installer failures, streaming-input interruption, and history beyond macOS's argument limit.
- All 46 unit tests, Bash syntax, ShellCheck, Ruby formula syntax, and diff checks passed locally on macOS; see `docs/maintenance-2026-10.md` for results.
- Real Shortcut execution and Homebrew tap installation remain pending in #5 and #7. #10 retains the unfinished packaging work.
- No release version changed. The published v0.2.0 installer does not include these fixes.
