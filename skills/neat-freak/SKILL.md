---
name: neat-freak
description: "Deep fact reconciliation for KB masters, project docs, and authorized memory. Use for /neat-freak, full reconciliation, knowledge sync, doc sync, memory cleanup. With checkpoint, enable full mode instead of a second run; a standalone run ends with /checkpoint."
---

# Neat Freak — the fact-reconciliation engine

This skill reconciles "facts": client status, contract versions, schedules, payments, todos, and dev docs. It does not write the daily log, and it does not git commit / push.

## When combined with checkpoint

If the same user instruction names `checkpoint` too:

1. Don't build a second plan, don't run Fact Detection separately, don't spawn a separate subagent.
2. Tell checkpoint's manifest to use `mode: full`, `memory_mode: update`.
3. Let checkpoint's single closure worker read this skill's `references/sync-protocol.md`.

That way the daily log, reconciliation, staging, push, and verification each happen exactly once.

## When run standalone

### 1. Fact Detection

The main thread reviews the whole conversation once, producing a `fact_list` (facts → the files they affect), and resolves the active skill dir, memory dir, vault, and project roots. Only read `references/sync-matrix.md` when the mapping is unclear.

Even with an empty fact list, explicitly naming neat-freak still means `mode: full` — but rely on the enumerate results and recently-relevant files for progressive disclosure; don't load the whole vault or rollout summaries.

### 2. One fresh-context run

Use a bounded subagent that doesn't inherit the main thread's long conversation; Codex should explicitly set `fork_turns: "none"`, Claude Code should use a fresh general-purpose Agent/Task with `model: sonnet`. The prompt carries only:

- `mode: full`
- `memory_mode: update`
- the full fact list
- the active neat-freak skill dir, memory dir, vault, project roots

The first instruction must tell it to read `references/sync-protocol.md` in full and follow it. It must not write the daily log, commit, or push. If no subagent is available, the main thread executes it directly.

### 3. Verification

The main thread spot-reads 1–2 of the files claimed to have been changed, confirms the enumerate final output and the GATE result, patches any failures that can be safely fixed, and finally reports only the sync evidence, the changes made, and anything left unresolved.

### 4. Always follow up with checkpoint

A standalone `neat-freak` run only edits files — it never commits. Run `/checkpoint` right after reconciling (lite mode is fine once the fact list is empty); otherwise these edits sit dirty in the working tree, and the next session has no way to tell them apart from someone else's in-progress work, so they never get closed out. This applies to memory files too — if `memory_mode: update` wrote to them, they need the same closure step as everything else.

## Boundaries

- Writing the daily log: that's a running record, not reconciliation — leave it to your logging process.
- `/checkpoint`: the single entry point for full closure; this skill is one segment of it.
- Periodic maintenance (format checks, archiving, index rebuilds): schedule separately, don't fold it in here.

Without a final enumerate output, neat-freak isn't done.
