# Checkpoint Closure Protocol

The input is a closure manifest produced by the main thread. You are the sole closure worker; don't spawn further subagents, and don't re-summarize the whole conversation.

## 1. Re-verify state

1. Confirm the manifest's date and timezone with `date`.
2. Re-run status/branch checks per repo; don't process the same vault path twice.
3. Treat dirty files not listed in the manifest as concurrent or someone else's changes; read the diff to judge attribution — if you can't safely separate them, leave them in place and flag a warning.
4. Check coverage: every changed file, and every listed external / scheduled / payment / todo action, must be classified. If you find a gap, stop and send it back to the main thread to fill in the manifest — don't guess.

## 2. Write the daily log exactly once

Except for `git-only`, `daily_action: skip_duplicate`, or no material session, read:

Write it once following your own log-format conventions (if you have a separate logging process script, read its conventions file, but don't run the whole thing — that would duplicate the work). Use the `daily_entries` from the manifest for the content. Don't write a second entry during the reconciliation step in the same pass.

## 3. Conditional fact reconciliation

- `git-only`: skip.
- `scoped` with an empty fact list: skip, report `sync: skipped (no fact delta)`.
- Otherwise: read `<neat-freak-skill-dir>/references/sync-protocol.md` in full, passing it the manifest's mode, memory_mode, fact list, and paths.

The sync protocol only reconciles facts — it does not commit. Move to the next section once it's done.

## 4. Verify, stage, commit, push

For each repo:

1. Read status and diff to confirm attributable files; exclude `.env`, `credentials*`, `*.secret`, session dumps, lock files, and any sensitive data not authorized by the manifest.
2. Run tests proportionate to the risk of the change; at minimum `git diff --check`. If the repo has its own lint/check scripts, run those too — fixes stay scoped to what's relevant to this closure, not a full periodic-maintenance sweep.
3. Stage file by file — never a blind `git add -A`. For a file listed in this session's write-manifest that was also dirty before this session touched it (or that another session's manifest also lists), don't stage the whole file: run `<checkpoint-skill-dir>/scripts/stage-own-edits.sh <session-id> <file>`. It replays this session's recorded edits on top of `HEAD` and writes the result straight into the index, without touching the working tree, so the other session's uncommitted content stays exactly where it is. Exit code `0` or `1` means it staged cleanly; `2` (this session used a whole-file `Write` on it) or `3` (an edit's `old_string` no longer matches `HEAD` — overlapping change) means hold that file and report it — those two need a human call, not an automatic merge. Scan every staged diff for secret-like patterns, but don't print the matched values.
4. If the staged diff is empty, report clean — don't create an empty commit.
5. Conventional Commit subject ≤72 characters; only add `Co-Authored-By` when the system or user explicitly asked for it.
6. Push the current branch; report failures honestly, no force push.
7. Verify local `HEAD == origin/<branch>`. If you need live-remote evidence and network access is available, also compare against `git ls-remote`.

When the vault and the current repo differ, commit each separately; only include files attributable to this session. If they overlap and can't be separated, stop on that repo rather than sweeping unknown changes in.

## 5. Report back

```text
daily: written | skipped (<reason>)
sync: skipped | scoped | full (<gate summary>)
repos:
- <path> <hash|clean> pushed=<branch|no>
preserved:
- <unrelated dirty file>
warnings:
- <item>
```

Attach the final enumerate evidence once; don't repost the full diff or the protocol text.
