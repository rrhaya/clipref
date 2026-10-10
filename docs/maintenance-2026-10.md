# Completion audit — October 2026

Target: `rrhaya/clipref`. Preserve the macOS-only, dependency-free runtime and private local storage. Use synthetic logs; never read the user's clipboard or personal configuration. Leave pre-existing `docs/admin/` files untouched.

## Background and current state

The product saves clipboard text or stdin, then copies the absolute file path. Its purpose is to remove repeated file preparation when sharing logs with an agent that can access local files. It does not summarize logs or promise token savings.

Repository-specific GitHub reads on 2026-10-10 found:

- Open #5: document and manually validate a macOS Shortcut and keyboard shortcut.
- Open #7: publish and validate Homebrew distribution. The local formula still points to v0.1.0.
- Open #10: prepare and publish v0.2.0. The release is published; formula update and tap validation remain.
- No open pull requests. `delete_branch_on_merge` is enabled.

## Ownership and coordination

Coordinator: current agent. Local implementation, validation, and review proceed sequentially. No worker has been dispatched.
The Orca orchestration runtime is reachable, but `run-create` returned `no_active_sender_terminal`. No other terminal's identity was used. This document is the shared task and evidence record for a later authorized worker.
GitHub CLI requests were rejected by the execution approval policy (`AskForApproval=Never`). Repository reads were retrieved through the existing GitHub read connector. GitHub writes must use an authorized available tool; do not route around a rejected write.

## Task ledger

| Task | Owner | State | Acceptance |
| --- | --- | --- | --- |
| Confirm issues, PRs, release and branch deletion | Coordinator | Done | Repository-specific GitHub API results |
| Audit CLI and installer failure handling | Coordinator | Implemented locally | #12, #13, #14; regression failures reproduced before fixes |
| Refresh Homebrew packaging | Coordinator | Blocked on archive retrieval and tap setup | Archive download rejected by execution policy; do not guess checksum |
| Shortcut validation | Coordinator | Pending manual execution | Shortcuts app has no accessible window; no real clipboard or personal configuration read |
| Record improvements as Issues | Coordinator | Done | #12, #13, #14 created through existing scoped GitHub connector |
| Review next OSS opportunities | Coordinator | Done | `docs/next-oss-ideas.ja.md`; existing tools compared, demand remains unvalidated |

## Findings and implementation

- [#12](https://github.com/rrhaya/clipref/issues/12): a failed installer could overwrite the current executable, replace symlinks, and print incorrect custom-directory PATH advice. Stage in the destination directory, then rename after successful installation. Reject symlink and non-regular destinations.
- [#13](https://github.com/rrhaya/clipref/issues/13): SIGTERM during streaming input left an incomplete file. EXIT cleanup and HUP/INT/TERM handlers remove only this invocation's incomplete save. Disable cleanup after the nonempty input is saved. SIGKILL and machine crashes cannot run cleanup handlers.
- [#14](https://github.com/rrhaya/clipref/issues/14): sufficiently large history exceeded argv limits and produced an apparently successful empty list. List the directory itself and check command failure before processing entries.

Issue comments record local progress. Leave these issues open until merge; implementation on a local branch is not a published fix.

## Validation and limitations

Baseline: 38 unit tests passed. Installer, interrupted-input, and large-history regression tests each failed before their respective fixes. Final results are recorded below after validation.

Final validation: `/usr/bin/python3 -m unittest discover -s tests -q` passed all 46 tests on macOS. `/bin/bash -n bin/clipref`, `/bin/bash -n install.sh`, `shellcheck bin/clipref install.sh`, `ruby -c packaging/homebrew/clipref.rb`, and `git diff --check` all exited 0. Real clipboard contents and personal config files were not used.

Bash syntax, ShellCheck, Ruby formula syntax and `git diff --check` passed after the initial fixes. Homebrew style against the standalone Ruby path used generic Ruby rules, reported four offenses, and automatically enabled developer mode and installed its lint dependencies. Retrying with `--formula` exited 1 without diagnostics. Neither result is a successful tap formula check; no style rules were suppressed. The product gained no runtime dependencies.

`brew developer off` exited 0 to undo the automatic developer-mode change. Homebrew's installed lint dependencies were not removed.

`rrhaya/homebrew-tap` returned HTTP 404 from the scoped connector; this does not prove whether a private inaccessible repository exists. The v0.2.0 archive download was rejected before execution (`approval required by policy, but AskForApproval is set to Never`). The formula remains pinned to the verified v0.1.0 archive. No replacement checksum was invented.

Orca computer-use capabilities were available. Observing `com.apple.shortcuts` returned `window_not_found` (no accessibility window). No Shortcut or global keyboard binding was changed. Follow `docs/shortcuts.ja.md` for the remaining manual check with synthetic text.

## Remaining sequence

Local implementation commit: `adaa4b0`. Pushing `maintenance/completion-audit` was rejected before execution by the approval policy (`AskForApproval=Never`). No remote branch or PR was created. Do not substitute another upload route for the rejected push. The owner can run:

```sh
cd /Users/ryu/PJ/playground/clipref
git push -u origin maintenance/completion-audit
gh pr create --repo rrhaya/clipref --base main --head maintenance/completion-audit --title 'Fix installation failures, interrupted saves, and large history' --body-file docs/maintenance-pr.md
```

1. Push `maintenance/completion-audit` and open a PR using `docs/maintenance-pr.md`. Run required CI and merge through the protected main branch.
2. Finish #7: create or make the rrhaya tap available, obtain and verify the v0.2.0 archive checksum, update URL and checksum together, run Homebrew style/audit/install/test in the real tap, and document the verified installation route.
3. Finish #5: verify application execution and the assigned keyboard shortcut with synthetic text. Confirm saved bytes and the pasted absolute path. Record the macOS version and results in the issue.
4. Close #10 only after its remaining packaging requirements are met. Prepare a patch release for the merged bug fixes when appropriate; do not change the version just for the audit documents.
5. Validate the first next-product experiment described in `docs/next-oss-ideas.ja.md` before creating a new OSS repository.

## Completion boundary

Do not claim the product complete while distribution, GUI validation, or publishing checks remain unverified. Keep implementation and release work separate; a branch commit is not a release. Do not bump the release solely for documentation or packaging.

## Follow-up after PR #15

PR #15 was merged as `29bf48e`; #12, #13 and #14 are closed. Follow-up branch: `distribution/finish-validation`.

- Fetched the actual v0.2.0 command and installer through the existing GitHub connector. An isolated installation using those exact sources passed byte comparison, executable permissions, `--help`, `--version`, and synthetic stdin saving with `--no-copy`. The installer's curl transport was stubbed to serve the fetched source; this is not a live curl-network verification.
- SHA-256 of the fetched command: `b8ce26a779ee33c878615d886aabd85fa66221c326a7bdd3eb3130b0ac76ec31`. Installer: `15407231a8aff499af55c7720676a915c42bfa17dbd98e50cd9897c7567dac0e`. Neither is the release archive checksum.
- Added `packaging/homebrew/prepare-formula.sh`, with tests for the exact checksum, version mismatch, missing archive member, invalid Bash and invalid tag. It reads a locally downloaded archive, extracts only the command to stdout, and emits the formula after validation; it does not execute archive contents or fetch data.
- All 49 unit tests passed. ShellCheck for all three scripts, helper Bash syntax and diff checks passed. CI now includes helper syntax and ShellCheck.
- Prepared local `../homebrew-tap`, with fetch/push origin `https://github.com/rrhaya/homebrew-tap.git`, a draft README, formula and macOS CI. Its formula still pins v0.1.0; it must not be published as v0.2.0.
- Homebrew style on the tap's `Formula/clipref.rb` passed with no offenses. `brew audit --strict rrhaya/tap/clipref` exited 0. Audit by absolute path is disabled by Homebrew, so the local tap was temporarily registered using a symlink. That exact symlink was removed afterward; automatically enabled developer mode was turned off.
- No Homebrew installation/test was reported as passed. The v0.2.0 archive curl command was again rejected before execution by the approval policy. No download workaround or fabricated checksum was used.
- Shortcuts still returned `window_not_found`, including with `--restore-window` and after opening Apple's documented `shortcuts://create-shortcut` URL. The URL open exited 0, but creation and execution are unverified. No personal clipboard contents were read, and no keyboard binding was assigned.

Remaining #7: obtain the actual archive, generate the new formula, publish the prepared tap, and run installation/test before updating the main READMEs with a working brew route. Remaining #5: accessible editor and synthetic-data application/key execution. Remaining #10: live published-tag download verification plus #7's distribution requirements.

Pushing the follow-up branch was rejected before execution by the same approval policy. Owner commands for the current branch (the earlier PR #15 commands above are historical):

```sh
cd /Users/ryu/PJ/playground/clipref
git push -u origin distribution/finish-validation
gh pr create --repo rrhaya/clipref --base main --head distribution/finish-validation --title 'Prepare Homebrew formula updates and distribution checks' --body-file docs/distribution-pr.md
```

No high-impact product tradeoff required a decision in this follow-up. The remaining obstacles are execution approval, remote tap publication, and accessible Shortcut UI, rather than unresolved feature design.
