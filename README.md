# clipref

Save clipboard text to a local file and copy its absolute path.
For logs and long text you want an AI coding agent to read.

Starting with v0.3.0, run the command as `pbe`. The `clipref` name also works.

[日本語](README.ja.md)

## Requirements

macOS. Uses Bash and commands included with macOS.
The installer downloads from GitHub. The installed command makes no network requests.

## Install

### Homebrew

```sh
brew install rrhaya/tap/clipref
```

Use `brew upgrade clipref` to update and `brew uninstall clipref` to remove it.
If you also used the shell installer, run `command -v pbe` to check which copy runs.

### Shell installer

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/v0.3.0/install.sh | bash'
```

Installs `v0.3.0` to `~/.local/bin`.
The installer does not edit your shell configuration. If the directory is not in
your `PATH`, add this line to `~/.zshrc` and open a new terminal:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

Check the installation in the new terminal:

```sh
pbe --version
pbe --help
```

The installer sets executable permissions. No separate `chmod` step is needed.

### Choose an install directory

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/v0.3.0/install.sh | bash -s -- --bin-dir "$HOME/bin"'
```

Add the chosen directory to your `PATH` if needed.
`--bin-dir` sets where the command is installed; `pbe --dir` sets where text is saved.

### From source

1. Get the source:

```sh
git clone https://github.com/rrhaya/clipref.git
cd clipref
```

2. Install the command:

```sh
mkdir -p "$HOME/.local/bin"
install -m 755 bin/clipref "$HOME/.local/bin/clipref"
if [ ! -e "$HOME/.local/bin/pbe" ] && [ ! -L "$HOME/.local/bin/pbe" ]; then
  ln -sh clipref "$HOME/.local/bin/pbe"
fi
```

3. Add the install directory to your current shell's `PATH` and check the command:

```sh
export PATH="$HOME/.local/bin:$PATH"
pbe --help
pbe --version
```

For future terminal sessions, add the `export` line to `~/.zshrc`.

## Use

1. Copy the log or text you want to save.
2. Run `pbe` in a terminal:

```sh
pbe
```

3. Paste the copied path into your agent and describe what to investigate.

The path is also printed in the terminal. To choose a save directory, create it first:

```sh
mkdir -p ./tmp
pbe --dir ./tmp
```

Other options:

```sh
pbe --dir ./tmp          # Choose an existing save directory
pbe --ext log            # Save as input.log
your-command 2>&1 | pbe  # Save command output
pbe --no-copy            # Print the path without changing the clipboard
```

Piped input takes precedence over the clipboard. Use `pbe --clipboard` to
read the clipboard explicitly, including from launchers or Shortcuts. It ignores
stdin. Available since v0.2.0.
The default extension is `txt`.
Extensions change the filename only; they do not convert the content.
Use `pbe --name startup-error.log`
to choose a filename. Names may contain spaces and Japanese characters, but must
not contain path separators, tabs, or line breaks. `--name` and `--ext` cannot be combined.
A filename supplied with `--name` takes precedence over the configured extension.
Input is preserved without trimming or adding a newline.

## Configuration

Available since v0.2.0. Create
`~/.config/clipref/config` (or `$XDG_CONFIG_HOME/clipref/config`):

```text
dir=~/logs
ext=log
```

Create the save directory first. Values are literal text, without quotes or shell
expansion; only a leading `~/` expands to your home directory. Blank lines and
lines starting with `#` are ignored. Use an absolute directory path or `~/`.
Command-line options override configuration, which overrides built-in defaults.
Unknown keys, duplicate keys, and invalid values are errors.

## Files

For keyboard access, see [macOS Shortcut setup](docs/shortcuts.md).
Requires v0.2.0 or later.

In v0.3.0, each run creates a path like `20261126170042-Ab3xY7/input.txt`. The first 14 digits
give the local date and time when the save began, down to the second. The random
suffix keeps saves in the same second separate. Only the owner can read and write
the files.

The default destination is `${TMPDIR:-/tmp}/clipref-<user-id>`. When `dir` is set
in configuration or supplied with `--dir`, the timestamped folder is created
under that destination.

Empty input is rejected. The clipboard changes only after the file is saved.
If copying the path fails, the file remains and its path is printed.

To clear the default destination, wait for any saves to finish and move the
folder to the Trash using the same `TMPDIR` as when you saved the files.

```sh
/usr/bin/trash "${TMPDIR:-/tmp}/clipref-$(id -u)"
```

If `/usr/bin/trash` is unavailable, reveal the folder in Finder and press
Command-Delete.

```sh
open -R "${TMPDIR:-/tmp}/clipref-$(id -u)"
```

The next save to the default destination recreates the folder. History marks
moved files as `missing`.
Older `clipref.XXXXXX` folders remain in their original locations. The OS may
remove temporary files. Use `--dir` when you need to keep a file.

## History

Available since v0.2.0:

```sh
pbe list --limit 10  # Recent paths, marked exists or missing
pbe last            # Print and copy the newest saved path
pbe last --no-copy  # Print it without changing the clipboard
```

List output quotes paths for the shell. `last` copies the original absolute path.
If the latest file is gone, `last` reports an error rather than selecting another file.
History follows record modification times, newest first; simultaneous saves may tie.

Each successful save records only its path, including saves with `--dir`.
Records are private and stored in `~/.local/state/clipref/history`, or
`$XDG_STATE_HOME/clipref/history` when set. Configuration defaults do not change
the history location. Missing files remain listed; no files are deleted automatically.
If recording history fails, the saved file and path copying still work and a warning is printed.

## Using it with an agent

The agent must be able to access the saved file. A local path alone will not make
the file available to an agent on another machine.

Saving text to a file does not by itself reduce token usage. Ask the agent to
search and read relevant sections instead of loading the entire file:

```text
Log: /absolute/path/to/input.log
Find the cause of the startup failure. Start with the last 100 lines,
then search for errors and read the surrounding lines as needed.
```

## Development

```sh
bash -n bin/clipref
bash -n install.sh
bash -n packaging/homebrew/prepare-formula.sh
shellcheck --shell=bash bin/clipref install.sh packaging/homebrew/prepare-formula.sh
python3 -B -m unittest discover -s tests -v
ruby -c packaging/homebrew/clipref.rb
```

Tests use fake clipboard commands; they do not access the system clipboard.
Python 3 is needed only for tests.
ShellCheck is needed only for linting; on macOS, install it with `brew install shellcheck`.

GitHub Actions runs the syntax check and tests on macOS for pushes and pull requests.
ShellCheck checks the Bash scripts on Ubuntu. Dependabot opens weekly update PRs
for GitHub Actions dependencies.

For a manual check, run this from the repository root. It uses sample input and
stores the files, configuration, and history under a temporary directory.

```sh
(
  clipref_smoke=$(mktemp -d "${TMPDIR:-/tmp}/clipref-smoke.XXXXXX") || exit 1
  export TMPDIR="$clipref_smoke" XDG_CONFIG_HOME="$clipref_smoke/config"
  export XDG_STATE_HOME="$clipref_smoke/state"
  mkdir "$clipref_smoke/custom"
  printf 'sample log\n' | bash bin/pbe --no-copy
  printf 'custom log\n' | bash bin/pbe --no-copy --dir "$clipref_smoke/custom" --name sample.log
  bash bin/pbe list
  bash bin/pbe last --no-copy
)
```

The first file is saved under `clipref-<user-id>` and the second under `custom`.
`list` marks both paths as `exists`, and `last --no-copy` prints the second path.

## Update

Use the installer with the release tag you want:

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/main/install.sh | bash -s -- --version v0.3.0'
```

## Uninstall

```sh
if [ "$(readlink "$HOME/.local/bin/pbe" 2>/dev/null)" = clipref ]; then
  rm "$HOME/.local/bin/pbe"
fi
rm "$HOME/.local/bin/clipref"
```

Saved files are kept. Remove them separately when you no longer need them.

## License

MIT.
