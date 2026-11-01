---
name: checkpoint
description: "Close a session once: daily log, fact reconciliation (master files, project docs, memory), selective commit/push, and remote verification. Use for /checkpoint, end of session, save, push, commit and push. Full: full reconciliation, knowledge sync, memory cleanup. Lite mode: inline, no subagent, for sessions already kept in sync."
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Agent Read
---

# Checkpoint — the single closure entry point

`checkpoint` is the single closure entry point. Its fact-reconciliation engine lives in `references/sync-protocol.md` (neat-freak was merged into this skill on 2026-10-25).

## Modes

- `scoped` (default): write the daily log once; run a targeted reconciliation only if there's a fact list, then commit + push.
- `full`: the user typed `/checkpoint full`, or asked for a full reconciliation, knowledge sync, memory cleanup, or a full closure (formerly `/neat-freak`) — run the complete GATE reconciliation before commit + push.
- `lite`: the user asks for `/checkpoint lite` or lite mode, or the session qualifies for the automatic downgrade (below). **The main thread finishes it directly — no subagent, no manifest.** See §0.
- `git-only`: only when the user explicitly says no log / no sync.

## 0. Lite mode

Lite applies when the user asks for it, or automatically when the fact list is empty and 5 or fewer files are attributable to this session. A closure that small isn't worth a subagent round-trip: the main thread can finish it in a handful of commands, and delegating costs far more than it saves. **Read `references/lite.md` in full before you start**: it holds the exact criteria, the conditions that send you back to `scoped`, and the steps.

## 1. The main thread builds the closure manifest exactly once

Use the current platform's task/plan mechanism to build one closure plan, and only one.

1. Get the date and timezone with `date`.
2. Check `git status --porcelain`, `git diff --stat HEAD`, and the current branch for the current repo (and any other project roots you touched, including your notes folder).
3. Work out which files belong to this session (the `attribution` field of the manifest):
   - **Write-manifest**: if the `write-manifest` hook is installed, read `~/.claude/state/write-manifests/<session-id>.list` (the files this session's edit tools touched) and note the edit-log path `~/.claude/state/edit-logs/<session-id>.jsonl`. No hook, or an old session it never recorded → `attribution: conversational` (judge by reading diffs, and say in warnings that nothing verified it).
   - **Bash writes**: the manifest only sees edit tools. Files written by a shell heredoc, `sed -i`, `cp`, a script, or by a subagent on your behalf are not in it. Run `python3 <checkpoint-skill-dir>/scripts/bash-writes.py <session-id> [--after <time of the last checkpoint>]` to list candidates (it reads the session transcript, so the list survives context compaction). Drop false positives (a script that only read the file), and add from memory only what the script can't see, such as files written inside a script you wrote or output from an external CLI. After several compactions, memory alone will miss files. Put the result under `attribution.bash_writes`. This script reads Claude Code transcripts under `~/.claude/projects/`; on other platforms, list those files by hand.
   - **The manifest proves "I changed this", not "only I changed this."** If you keep an opening snapshot (a copy of `git status --porcelain` taken when the session began), check every candidate against it: a file that was already modified (` M`) at the start goes on a **hold list** instead of `attributable_files`. You may write to it, but you must not `git add` it whole. Without that check, a subagent following the manifest will commit another session's unfinished work along with yours. No snapshot? Treat every dirty file in the manifest as possibly shared and route it through `scripts/stage-own-edits.sh` in the closure step, which stages only this session's edits.
4. Review the whole conversation once, producing:
   - `session_summary`: 0–3 items each of what was completed / decided / any pitfalls hit.
   - `fact_list`: facts that changed → the files they affect; not just a list of touched files.
   - `daily_entries`: the condensed content to write into the daily log.
   - `todo_closeouts`: todos in your master files that this session finished or moved forward, each with what to change (mark done with today's date, rewrite the remaining step, or list it in warnings). Follow the rule in `references/lite.md` step 2. If the only thing missing is a decision from the user, ask in the conversation before closing out; don't open a new todo for it.
   - `repos`: repo, branch, attributable files (per `attribution`; memory only fills in `bash_writes`), tests run.
   - `coverage`: every changed file, and every external action / scheduled item / payment / todo change, must be tagged `fact_delta: yes` (linked to the fact list) or `fact_delta: no` (with a one-line reason). Anything left unclassified blocks delegation.
   - `lessons`: **the main thread does this before delegating**, because a worker can't see the conversation. Read `references/lessons.md` to decide whether it applies; if its triggers aren't met, write `none`. If they are, follow that file: propose first, wait for the user's approval, apply and commit, and only then delegate. Anything already saved during the conversation is listed, not redone.
5. Compare against today's daily log, recent commits, and the current file state; if another session already wrote the same content more recently, mark `daily_action: skip_duplicate` — don't duplicate or backfill it.
6. The manifest must include `mode`, `memory_mode`, `attribution`, the checkpoint skill folder, the memory folder, your notes root, and every project folder being closed out.

`memory_mode` defaults to `read-only`; it's `update` in `full` mode, or when the user explicitly asked for memory sync or memory cleanup.

## 2. Execute exactly once

Hand the manifest to a fresh-context, general-purpose bounded subagent:

- Codex: use `fork_turns: "none"`, prompt carries only the manifest and this file's path.
- Claude Code: use a fresh general-purpose Agent subagent on a small, cheap model (for example `model: "haiku"`), and **run it in the foreground** (`run_in_background: false`). When it was dispatched in the background, its final report never made it back to the main thread, and only the reply to a follow-up question did. The subagent won't see the main thread's conversation history but still loads applicable CLAUDE.md and permissions. If that model is too weak to follow the protocol, use `model: "sonnet"`. The delegation prompt carries only the manifest and this file's path.

The first instruction must tell it to read `references/closure-protocol.md` in full, and not spawn any further subagents. If the platform has no subagent support, or the task is a single-repo `git-only`, the main thread follows that protocol directly.

## 3. Main-thread verification

A subagent's report is a claim, not a fact:

1. If sync edits were made, spot-read 1–2 of the files it claims to have changed.
2. Confirm each item appears in the daily log exactly once: grep a key phrase from each `daily_entries` item in today's daily log. A worker can report the log as written while the write never happened, and the same item must not show up twice.
3. Per repo, check the reported hash, `git log -1 --oneline`, and `HEAD == origin/<current-branch>`.
4. Recheck `git status --short`: changes attributable to this session should be closed out; unrelated or concurrent changes should be left untouched and listed.

## Condensed report

```text
daily: written | skipped (<reason>)
sync: skipped | scoped | full (<GATE result>)
commit: <repo> <hash> | clean
vault: <hash> | clean | preserved unrelated changes
pushed: <branches>
lessons: none | <n> saved (where), <k> logged as repeat mistakes, <m> waiting on you
warnings: none | <items>
```

No force push; no blind `git add -A`; never sweep unattributable changes in just to make things look clean.
