# Run pbe with a keyboard shortcut

[日本語](shortcuts.ja.md)

Install pbe v0.3.0 or later and run `pbe --help` to check that `--clipboard` is available.
With v0.2.0, use the `clipref` executable in the examples.

In Shortcuts, open **Settings → Advanced** and enable **Allow Running Scripts**.
This is an app-wide setting. Enable it only if you want Shortcuts to run scripts;
turn it off in the same place to undo the change. If the shell action says scripting
actions are disabled, check this setting before running the shortcut.
See [Apple's instructions](https://support.apple.com/en-gb/guide/shortcuts-mac/apdfeb05586f/mac).

1. Open Shortcuts and create a shortcut named “Save clipboard with pbe”.
2. Add the **Run Shell Script** action. Use `/bin/zsh` (the macOS default) or `/bin/bash` as the shell.
3. Enter this script for the default install directory:

```sh
"$HOME/.local/bin/pbe" --clipboard
```

4. Open the shortcut details and assign a keyboard shortcut with **Add Keyboard Shortcut**.
5. Copy some sample text and run the shortcut. Paste into a text editor to check
   that the clipboard contains an absolute path. Open the file to check its contents.

For another install directory, replace the executable path. Do not rely on your
terminal's `PATH`: Shortcuts does not load your interactive shell configuration.

For a Homebrew installation, run `command -v pbe` and use that absolute path.
It is usually `/opt/homebrew/bin/pbe` on Apple Silicon or `/usr/local/bin/pbe`
on Intel Macs.


To keep files in a chosen directory, create it once in Terminal:

```sh
mkdir -p "$HOME/Documents/pbe"
```

Then use this script:

```sh
"$HOME/.local/bin/pbe" --clipboard --dir "$HOME/Documents/pbe" --ext log
```

The clipboard changes only after saving. Empty clipboard text or an inaccessible
save directory makes the action fail. Check the error in Shortcuts; if copying
the path fails after saving, the action's output still contains the saved path.

The keyboard shortcut must be unused by the current app. If it does not run, test
with Shortcuts' Run button first, then choose another key combination.

On macOS, a shortcut using the Homebrew `clipref` executable and `/bin/zsh` was
tested with both the Run button and Control–Option–Command–C. Both saved the
sample text, copied the absolute path, and created a file with mode `600`.
Choose an unused key combination on your Mac; the example may conflict with other apps.
