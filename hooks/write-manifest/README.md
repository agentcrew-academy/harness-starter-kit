# write-manifest: a ground-truth record of which files this session touched

This isn't an interceptor. It never blocks a write and never ends a turn early. It just keeps a quiet log, every time an edit tool runs, of which file it touched and (on the Claude Code side) exactly what changed.

## Why this exists

Run more than one Claude Code or Codex session against the same repo — two terminals, a background agent plus a foreground one, a session you resumed after switching away — and a question comes up constantly: *is this uncommitted change in the working tree mine, or did another session leave it there?*

Without a record, the only evidence is `git status` at the moment you look, and that can't tell the two apart. `git add -A` on a file that was already dirty before your session touched it risks silently absorbing someone else's in-progress work into your commit.

With the manifest, a later step — a closure/checkpoint skill, or a script you write yourself — can read `~/.claude/state/write-manifests/<session-id>.list` (or the Codex equivalent under `~/.codex/state/write-manifests/`) and know exactly which paths this session is responsible for, before deciding what to stage.

## What it writes

**Claude Code build** (`claude-code/write-manifest.sh`), per `Write`/`Edit`/`MultiEdit`/`NotebookEdit` call:

- `write-manifests/<session-id>.list` — every distinct file path touched, one per line
- `edit-logs/<session-id>.jsonl` — one JSON line per edit: `{"f": "<path>", "op": "edit", "old": "...", "new": "...", "all": false}` for `Edit`/`MultiEdit`, or `{"f": "<path>", "op": "write"}` for a whole-file `Write`

**Codex build** (`codex/write-manifest.sh`), per `apply_patch`/`Write`/`Edit`/`MultiEdit` call:

- `write-manifests/<session-id>.list` only — file paths, parsed out of the patch's `*** Add/Update/Delete File:` lines. No edit-log equivalent; see the asymmetry note in the parent `hooks/README.md`.

Both are silent (no stdout) and fail open — a missing session id or file path just means nothing gets logged, not an error.

## The companion script: `stage-own-edits.sh`

Shipped with the `checkpoint` skill (`skills/checkpoint/scripts/stage-own-edits.sh`), not with this hook, because it's a consumer of the log rather than part of the recording itself.

Given a session id and a file that might also have been touched by another session, it replays this session's `old`/`new` pairs from the edit log on top of the file's `HEAD` version and writes the result straight into the git index — the working tree is never touched, so whatever the other session left there stays exactly as it was. It refuses (exits with a `hold` code) when this session used a whole-file `Write` on that path, or when an `old_string` no longer matches `HEAD` — both cases need a human to look, not an automatic merge.

## Housekeeping

Neither script prunes old manifests or edit logs. If you want to cap how much accumulates under `~/.claude/state/` or `~/.codex/state/`, add your own cleanup (for example, delete files older than N days) — that's deliberately left out here since retention needs vary by how you use sessions.
