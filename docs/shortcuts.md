# Run clipref with a keyboard shortcut

[日本語](shortcuts.ja.md)

Requires macOS Shortcuts and a clipref build with `--clipboard` (not v0.1.0).
Install that build first and run `clipref --help` to check the option is available.

1. Open Shortcuts and create a shortcut named “Save clipboard with clipref”.
2. Add the **Run Shell Script** action. Select `/bin/bash` as the shell.
3. Enter this script for the default install directory:

```sh
"$HOME/.local/bin/clipref" --clipboard
```

4. Open the shortcut details and assign a keyboard shortcut with **Add Keyboard Shortcut**.
5. Copy some sample text and run the shortcut. Paste into a text editor to check
   that the clipboard contains an absolute path. Open the file to check its contents.

For another install directory, replace the executable path. Do not rely on your
terminal's `PATH`: Shortcuts does not load your interactive shell configuration.

To keep files in a chosen directory, create it once in Terminal:

```sh
mkdir -p "$HOME/Documents/clipref"
```

Then use this script:

```sh
"$HOME/.local/bin/clipref" --clipboard --dir "$HOME/Documents/clipref" --ext log
```

The clipboard changes only after saving. Empty clipboard text or an inaccessible
save directory makes the action fail. Check the error in Shortcuts; if copying
the path fails after saving, the action's output still contains the saved path.

The keyboard shortcut must be unused by the current app. If it does not run, test
with Shortcuts' Run button first, then choose another key combination.

Validation: the shell command is covered by CLI tests with non-terminal stdin.
The Shortcuts UI and keyboard binding still need a manual check on macOS.
