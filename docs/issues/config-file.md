Title: Support a configuration file for save directory and extension

Allow users to set the default save directory and file extension in a configuration file.

Current behavior requires --dir and --ext on each invocation.

Scope:
- Decide and document the configuration location and format.
- Support save directory and extension defaults.
- Apply precedence: command-line options > configuration > built-in defaults.
- Treat configuration as data. Do not source or execute it.
- Report invalid configuration with a clear error.
- Keep the current behavior when no configuration file exists.
- Update both READMEs and add tests for precedence and invalid values.

No configuration format or path has been selected yet.
