# Lite mode

**Purpose**: the session has already synced its master files item by item, the daily log was written as you went, and most changes are already committed and pushed. Running the full flow now would redo finished work and add a subagent round-trip.

**When to use it** (any one set is enough):
- The user explicitly asks for lite mode.
- **Automatic downgrade**: the fact list is empty, and 5 or fewer files are attributable to this session. Delegating a closure that small means paying for a whole subagent trip to do what the main thread can do in a few commands.
- All three hold: (1) master files were updated as you went; (2) the daily log is already written in the conversation and needs at most a line or two; (3) there's no cross-file fact reconciliation to do.

Fall back to `scoped` if there's a fact list, more than 5 attributable files, or a mixed-author file that needs a judgment call beyond what `scripts/stage-own-edits.sh` can make on its own.

**Steps** (main thread, inline, no subagent at any point):
1. `git status --porcelain` + `git log -1` across every repo this session touched.
2. Fill in whatever is still missing from the daily log; don't rewrite what's there, and don't backfill. Reconcile todos at the same time: for each thing this session finished or moved forward, grep the matching master file for its open item (`- [ ]` or your in-progress marker).
   - Finished, with a receipt (a commit, a sent message, a payment) → mark it done **and** add the completion date in your own format. Both edits, every time.
   - Only partly done → rewrite the item to say what's left.
   - Can't tell → put it in warnings and ask the user.
3. **Stage only the files attributable to this session.** The sources are the `write-manifest` hook's list plus whatever `scripts/bash-writes.py <session-id>` reports (shell and subagent writes). List them one by one; never `git add -A`. A file that was already modified before this session touched it (per your opening snapshot, if you keep one), or that another session's manifest also lists, doesn't get `git add`-ed whole: run `scripts/stage-own-edits.sh <session-id> <file>` so only this session's edits go into the index. Exit code `2` or `3` means hold the file and report it.
4. Commit + push, and verify `HEAD == origin/<branch>` per repo.
5. Check for stale todos: for open items in your master files that mention a commit or branch which is already on the remote's default branch while the item still says "not pushed / not deployed / awaiting merge", copy each one into warnings. Don't edit them yourself; marking them done needs the user's confirmation.
6. Report using the condensed format in `SKILL.md`, with `sync:` set to `lite (inline)`.

**What lite skips**: the closure manifest, coverage classification, fact-list reconciliation, memory writes, and subagent delegation and verification. Needing any one of those means it isn't lite. **The exception is `lessons`**: follow the trigger rules in `references/lessons.md`, and if they're met, do it even in lite mode.
