# Checkpoint Closure Protocol

The input is a closure manifest produced by the main thread. You are the sole closure worker; don't spawn further subagents, and don't re-summarize the whole conversation.

## 1. Re-verify state

1. Confirm the manifest's date and timezone with `date`.
2. Re-run status/branch checks per repo; don't process the same path twice (your notes folder may live inside the current repo).
3. Don't guess about dirty files the manifest doesn't list: classify them with the attribution table in §4.
4. Check coverage: every changed file, and every listed external / scheduled / payment / todo action, must be classified. If you find a gap, stop and send it back to the main thread to fill in the manifest — don't guess.
5. Whether or not this session touched your notes, scan your master files for open todos that cite a commit or branch already on the remote's default branch while still saying "not pushed / not deployed / awaiting merge." Copy each hit into the `warnings` of your report. **Don't edit those todos yourself:** marking them done or rewriting the remaining steps needs the main thread to confirm with the user.

## 2. Write the daily log exactly once

Except for `git-only`, `daily_action: skip_duplicate`, or no material session, write it once following your own log-format conventions (if you have a separate logging process script, read its conventions file, but don't run the whole thing — that would duplicate the work). Use the `daily_entries` from the manifest for the content. Don't write a second entry during the reconciliation step in the same pass.

Write to notes with the Edit/Write tools, not a shell heredoc or `sed`. The write-manifest hook only records edit tools; a shell write is seen only by a later scan, and a file that was already dirty at the start of the session can be skipped and left uncommitted.

Then apply the manifest's `todo_closeouts` to your master files (not in `git-only`): when marking one done, change the checkbox **and** add the completion date in your own format; leave anything listed under warnings untouched and pass it back as-is. If the manifest has no `todo_closeouts`, send it back to the main thread rather than guessing from the daily log.

## 3. Conditional fact reconciliation

- `git-only`: skip.
- `scoped` with an empty fact list: skip, report `sync: skipped (no fact delta)`.
- Otherwise: read `<checkpoint-skill-dir>/references/sync-protocol.md` in full, passing it the manifest's mode, memory_mode, fact list, and paths.

The sync protocol only reconciles facts — it does not commit. Move to the next section once it's done.

## 4. Verify, stage, commit, push

For each repo:

1. **Attribute with a mechanism, not memory.** When the manifest's `attribution` carries this session's write-manifest, edit-log, and (if you keep one) opening-snapshot paths, look up every dirty file in this table. The snapshot is `git status --porcelain` output, with paths relative to its repo, so convert them to absolute paths before comparing.

   | Dirty file | What to do |
   |---|---|
   | In this session's write-manifest, in no other session's manifest, and clean at snapshot time | stage the whole file (`git add`) |
   | In this session's write-manifest, but **someone else may have touched it too** (it's in another manifest, it was already dirty at snapshot time, or its diff has a hunk this session can't explain) | **don't stage it whole and don't hold it yet**: run `<checkpoint-skill-dir>/scripts/stage-own-edits.sh <session-id> <file>`. It replays this session's recorded edits on top of the `HEAD` version and writes the result straight into the index, leaving the working tree alone. Exit `0` or `1` → staged. Exit `2` (this session overwrote the whole file with `Write`) or `3` (an `old_string` isn't in `HEAD`, so the changes overlap) → hold it and list it in warnings; those two need a human decision. Exit `5` (the helper or git failed) → hold it and list it in warnings with the error message |
   | A daily-log file shared by several sessions where every entry is final | stage the whole file |
   | Not in the manifest, and already dirty at snapshot time | not this session's; leave it as it is |
   | Not in the manifest, clean at snapshot time | unknown writer: stage it only if `attribution.bash_writes` lists the file along with the command that produced it; otherwise leave it and list it under preserved |

   - "Other manifests" means every `.list` that isn't this session's, in `~/.claude/state/write-manifests/` and `~/.codex/state/write-manifests/`. Count all of them, not just recent ones: an hour-old uncommitted edit is normal for someone else's session.
   - The edit-log is `~/.claude/state/edit-logs/<session-id>.jsonl`, written by the `write-manifest` hook: old → new for each edit, a whole-file marker for each `Write`.
   - No snapshot? Treat every dirty file in the manifest as the second row of the table, and run it through `stage-own-edits.sh`.
   - `attribution: conversational` (no hook was running) → fall back to judging attribution from the diff, and say in warnings that no manifest verified it.
2. Exclude `.env`, `credentials*`, `*.secret`, session dumps, lock files, and any sensitive data not authorized by the manifest.
3. Run tests proportionate to the risk of the change; at minimum `git diff --check`. If the repo has its own lint/check scripts, run those too — fixes stay scoped to what's relevant to this closure, not a full periodic-maintenance sweep.
4. Stage file by file — never a blind `git add -A`. Scan every staged diff for secret-like patterns, but don't print the matched values.
5. If the staged diff is empty, report clean — don't create an empty commit.
6. Conventional Commit subject ≤72 characters; only add `Co-Authored-By` when the system or user explicitly asked for it.
7. Stage and commit in a single shell call, after taking a per-repo lock, so that when several sessions close out the same repo at once, one session's commit doesn't sweep in what another just staged. After you get the lock and before `git add`, re-run `git status --porcelain` and confirm the table's result hasn't changed (the other session may have committed while you waited):

   ```bash
   LOCKDIR="$(git rev-parse --absolute-git-dir)/checkpoint.lock.d"
   n=0; until mkdir "$LOCKDIR" 2>/dev/null; do
     n=$((n+1)); [ "$n" -gt 90 ] && { echo "checkpoint lock timeout"; exit 1; }
     find "$LOCKDIR" -maxdepth 0 -mmin +10 -exec rmdir {} \; 2>/dev/null; sleep 2
   done
   trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT
   git status --porcelain && git add -- <whole-file list> \
     && <checkpoint-skill-dir>/scripts/stage-own-edits.sh <session-id> <mixed-author list> \
     ; git commit -m "<msg>"
   ```
   (Leave out the `stage-own-edits.sh` line if the mixed-author list is empty. Files for which it returns 2 or 3 never reach the index, so the commit contains only what is staged.)
8. Push the current branch; report failures honestly, no force push. Verify local `HEAD == origin/<branch>`. If you need live-remote evidence and network access is available, also compare against `git ls-remote`.
9. **Only after every repo has been committed and pushed, do one cleanup**: empty this session's write-manifest and edit-log (`: > <manifest>`, `: > <edit-log>`), and, if you keep an opening snapshot, rebuild it from the current `git status --porcelain` (the session may continue, so the attribution baseline moves forward). For files you held, keep their entries in the manifest and edit-log so the next closure can try again.

   **Never run this step right after one repo's commit.** The write-manifest and edit-log are one shared file per session, not per repo. If you clear them after the first repo, the second repo loses its mechanical evidence for mixed-author files, and `stage-own-edits.sh` fails because it can no longer find the edit records. The correct order for a multi-repo closure is repo A commit + push → repo B commit + push → … → cleanup, once, at the end.

When your notes folder and the current repo are different repos, commit each separately and take each one's own lock; if they overlap and can't be separated, stop on that repo rather than sweeping unknown changes in.

> `stage-own-edits.sh` replays recorded `Edit` calls only. It cannot separate a file that was written with `Write`, or changed by a shell command; those get held for a human, not merged automatically.

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
