# clipref

Save clipboard text to a local file and copy its absolute path.
For logs and long text you want an AI coding agent to read.

[日本語](README.ja.md)

## Requirements

macOS. Uses Bash and commands included with macOS. No network requests.

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

Piped input takes precedence over the clipboard. The default extension is `txt`.
Extensions change the filename only; they do not convert the content.
Input is preserved without trimming or adding a newline.

## Files

Each run creates a private `clipref.XXXXXX` directory in the system temp directory,
or in the directory passed to `--dir`. Files are readable and writable only by
their owner. Existing files are never overwritten.

Empty input is rejected. The clipboard changes only after the file is saved.
If copying the path fails, the file remains and its path is printed.

clipref does not delete saved files. System temp files may be removed by the OS.
Use `--dir` when you need to keep a file or place it inside an agent's workspace.

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
shellcheck --shell=bash bin/clipref install.sh
python3 -m unittest discover -s tests -v
```

Tests use fake clipboard commands; they do not access the system clipboard.
Python 3 is needed only for tests.
ShellCheck is needed only for linting; on macOS, install it with `brew install shellcheck`.

GitHub Actions runs the syntax check and tests on macOS for pushes and pull requests.
ShellCheck checks both Bash scripts on Ubuntu. Dependabot opens weekly update PRs
for GitHub Actions dependencies.

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
