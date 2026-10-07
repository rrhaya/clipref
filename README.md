# clipref

Save clipboard text to a local file and copy its absolute path.
For logs and long text you want an AI coding agent to read.

[日本語](README.ja.md)

## Requirements

macOS. Uses Bash and commands included with macOS.
The installer downloads from GitHub. The installed command makes no network requests.

## Install

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/v0.1.0/install.sh | bash'
```

Installs `v0.1.0` to `~/.local/bin`.
The installer does not edit your shell configuration. If the directory is not in
your `PATH`, add this line to `~/.zshrc` and open a new terminal:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

Check the installation in the new terminal:

```sh
clipref --version
clipref --help
```

The installer sets executable permissions. No separate `chmod` step is needed.

### Choose an install directory

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/v0.1.0/install.sh | bash -s -- --bin-dir "$HOME/bin"'
```

Add the chosen directory to your `PATH` if needed.
`--bin-dir` sets where the command is installed; `clipref --dir` sets where text is saved.

### From source

1. Get the source:

```sh
git clone https://github.com/rrhaya/clipref.git
cd clipref
git checkout v0.1.0
```

2. Install the command:

```sh
mkdir -p "$HOME/.local/bin"
install -m 755 bin/clipref "$HOME/.local/bin/clipref"
```

3. Add the install directory to your current shell's `PATH` and check the command:

```sh
export PATH="$HOME/.local/bin:$PATH"
clipref --help
clipref --version
```

For future terminal sessions, add the `export` line to `~/.zshrc`.

## Use

1. Copy the log or text you want to save.
2. Run `clipref` in a terminal:

```sh
clipref
```

3. Paste the copied path into your agent and describe what to investigate.

The path is also printed in the terminal. To choose a save directory, create it first:

```sh
mkdir -p ./tmp
clipref --dir ./tmp
```

Other options:

```sh
clipref --dir ./tmp             # Choose an existing save directory
clipref --ext log               # Save as input.log
your-command 2>&1 | clipref     # Save command output
clipref --no-copy               # Print the path without changing the clipboard
```

Piped input takes precedence over the clipboard. Use `clipref --clipboard` to
read the clipboard explicitly, including from launchers or Shortcuts. It ignores
stdin. This option is available in the development source, after v0.1.0.
The default extension is `txt`.
Extensions change the filename only; they do not convert the content.
In the development source after v0.1.0, use `clipref --name startup-error.log`
to choose a filename. Names may contain spaces and Japanese characters, but must
not contain path separators, tabs, or line breaks. `--name` and `--ext` cannot be combined.
Input is preserved without trimming or adding a newline.

## Configuration

Available in the development source after v0.1.0. Create
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
Requires the development build with `--clipboard`.

Each run creates a private `clipref.XXXXXX` directory in the system temp directory,
or in the directory passed to `--dir`. Files are readable and writable only by
their owner. Existing files are never overwritten.

Empty input is rejected. The clipboard changes only after the file is saved.
If copying the path fails, the file remains and its path is printed.

clipref does not delete saved files. System temp files may be removed by the OS.
Use `--dir` when you need to keep a file or place it inside an agent's workspace.

## History

Available in the development source after v0.1.0:

```sh
clipref list --limit 10  # Recent paths, marked exists or missing
clipref last            # Print and copy the newest saved path
clipref last --no-copy  # Print it without changing the clipboard
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
python3 -m unittest discover -s tests -v
```

Tests use fake clipboard commands; they do not access the system clipboard.
Python 3 is needed only for tests.

GitHub Actions runs the syntax check and tests on macOS for pushes and pull requests.

## Update

Use the installer with the release tag you want:

```sh
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rrhaya/clipref/main/install.sh | bash -s -- --version v0.1.0'
```

## Uninstall

```sh
rm "$HOME/.local/bin/clipref"
```

Saved files are kept. Remove them separately when you no longer need them.

## License

MIT.
