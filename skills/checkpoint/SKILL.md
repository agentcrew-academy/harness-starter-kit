---
name: checkpoint
description: "Close a session once: daily log, optional fact sync, selective commit/push, and remote verification. Use for /checkpoint, end of session, save, push, commit and push, or checkpoint + neat-freak. Lite mode: inline, no subagent, for sessions already kept in sync."
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Agent Read
---

# Checkpoint — the single closure entry point

`checkpoint` is the public closure entry point; `neat-freak` is the fact-reconciliation engine it can optionally call. When both are named at once, run exactly one closure flow — don't summarize, delegate, write the daily log, or verify twice.

## Modes

- `scoped` (default): write the daily log once; run a targeted reconciliation only if there's a fact list, then commit + push.
- `full`: the user explicitly named `neat-freak`, knowledge sync, memory cleanup, or a full closure — run the complete GATE reconciliation before commit + push.
- `lite`: the user asks for `/checkpoint lite` or lite mode. **The main thread finishes it directly — no subagent, no manifest.** See §0 below.
- `git-only`: only when the user explicitly says no log / no sync.

## 0. Lite mode

**When to use it**: mid-session, you've already been syncing changes into your notes as you went, the daily log is mostly written, and most changes are already committed and pushed. Running the full flow at that point just repeats work that's already done, plus adds another subagent round-trip.

**Trigger** (any one of these is enough):
- The user explicitly asks for lite mode.
- **Automatic downgrade**: the fact list is empty, and 5 or fewer files are attributable to this session. Delegating a closure like that just spends a whole subagent round-trip (measured at roughly 190k tokens in one real case) redoing something the main thread could finish in a handful of commands.
- All three hold at once: (1) your notes were updated as you went, not batched at the end; (2) the daily log is already written in-conversation and needs at most a line or two more; (3) there's no cross-file fact reconciliation to do.

Fall back to `scoped` if there's a fact list, more than 5 attributable files, or a mixed-author file that needs a judgment call beyond what `stage-own-edits.sh` can make on its own.

**How to do it** (main thread, inline, no subagent at any point):
1. `git status --porcelain` + `git log -1` across every repo this session touched.
2. Fill in whatever's still missing from the daily log. Don't rewrite what's already there, and don't backfill entries.
3. **Stage only the files attributable to this session** — per the `write-manifest` hook's record (see `hooks/write-manifest/`) — listed one by one, never `git add -A`. For a file that was already modified before this session touched it, or that another session's manifest also lists, don't `git add` the whole file: run `scripts/stage-own-edits.sh <session-id> <file>` instead, so only this session's edits get staged (an exit code of `2` or `3` means hold it and report, don't force it through).
4. Commit + push, and verify `HEAD == origin/<branch>` per repo.
5. Report using the condensed format below, with `sync:` set to `lite (inline)`.

**What lite skips**: the closure manifest, coverage classification, fact-list reconciliation, memory writes, and subagent delegation/verification. Needing any one of those means it isn't lite — fall back to `scoped`.

## 1. The main thread builds the closure manifest exactly once

Use the current platform's task/plan mechanism to build one closure plan; don't build a second one for neat-freak.

1. Get the date and timezone with `date`.
2. Check `git status --porcelain`, `git diff --stat HEAD`, and the current branch for the current repo (and any other project roots listed in the manifest).
3. Review the whole conversation once, producing:
   - `session_summary`: 0–3 items each of what was completed / decided / any pitfalls hit.
   - `fact_list`: facts that changed → the files they affect; not just a list of touched files.
   - `daily_entries`: the condensed content to write into the daily log.
   - `repos`: repo, branch, attributable files, tests run.
   - `coverage`: every changed file, and every external action / scheduled item / payment / todo change, must be tagged `fact_delta: yes` (linked to the fact list) or `fact_delta: no` (with a one-line reason). Anything left unclassified blocks delegation.
4. Compare against today's daily log, recent commits, and the current file state; if another session already wrote the same content more recently, mark `daily_action: skip_duplicate` — don't duplicate or backfill it.
5. The manifest must include `mode`, `memory_mode`, the folder for whichever process scripts are currently in use, the memory folder, the knowledge base root, and every project folder being closed out.

`memory_mode` defaults to `read-only`; it's only `update` when the user explicitly asked for neat-freak, memory sync, or memory cleanup.

## 2. Execute exactly once

Hand the manifest to a fresh-context, general-purpose bounded subagent:

- Codex: use `fork_turns: "none"`, prompt carries only the manifest and this file's path.
- Claude Code: use a fresh general-purpose Agent/Task subagent with `model: sonnet`; it won't see the main thread's conversation history but still loads applicable CLAUDE.md / permissions. The delegation prompt carries only the manifest and this file's path.

The first instruction must tell it to read `references/closure-protocol.md` in full, not spawn any further subagents, and not separately invoke neat-freak. If the platform has no subagent support, or the task is a single-repo `git-only`, the main thread follows that protocol directly.

## 3. Main-thread verification

A subagent's report is a claim, not a fact:

1. If sync edits were made, spot-read 1–2 of the files it claims to have changed.
2. Confirm each item appears in the daily log exactly once.
3. Per repo, check the reported hash, `git log -1 --oneline`, and `HEAD == origin/<current-branch>`.
4. Recheck `git status --short`: changes attributable to this session should be closed out; unrelated or concurrent changes should be left untouched and listed.

## Condensed report

```text
daily: written | skipped (<reason>)
sync: skipped | scoped | full (<GATE result>)
commit: <repo> <hash> | clean
vault: <hash> | clean | preserved unrelated changes
pushed: <branches>
warnings: none | <items>
```

No force push; no blind `git add -A`; never sweep unattributable changes in just to make things look clean.
