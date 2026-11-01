# Checkpoint Sync Protocol (fact reconciliation)

Your input is a manifest containing:

- `mode: scoped | full`
- `memory_mode: read-only | update`
- `fact_list` (facts → the files they affect)
- the active checkpoint skill dir, memory dir, vault, project roots

This protocol only reconciles facts; it does not write the session daily log, commit, or push.

## 1. Enumeration and load routing

First run `<checkpoint-skill-dir>/scripts/enumerate.sh`:

```bash
<enumerate.sh> --memory <memory-dir> --vault <vault> [<project-root> ...]
```

Keep the output. If you make edits afterward, re-run it when done; the final summary should paste only the last run's output verbatim. Without final enumerate evidence, the task isn't done.

Load only what's necessary:

- Both modes: the master files a fact touches, today's daily log, and the corresponding repo instructions.
- `scoped`: additionally read only files hit by enumerate and memory-index entries matched by fact-list keywords.
- `full`: additionally read the memory index, today's relevant master/project docs, and files hit by enumerate; if the fact list is empty, start from files modified recently in this session and today's daily log.
- Read `agent-paths.md` only when a path can't be resolved.
- Read `sync-matrix.md` only when the impact mapping is unclear.
- Read `dev-mode.md` only for API, env, DB, deployment, or cross-project interface changes.

Never bulk-read rollout summaries, the entire memory topic tree, the whole vault, or every repo's docs. Locate with `rg` first, then read the matched sections.

Produce an internal file list, tagging each file `checked | edit | skip`.

## 2. GATE

Judge each item before editing; report using the codes, collapsing passing ranges (e.g. `G1-G10 pass; G11 skip`), but expand evidence for any failure:

- G1 every file in the file list has been judged.
- G2 completed items in the daily log match the master file's `- [x] ... ✅ YYYY-MM-DD (or your own DONE_MARKER)` marker.
- G3 reschedules/cancellations have updated the master file's date or status.
- G4 new todos exist only in a single source-of-truth file (SSOT), and follow your own todo-format conventions.
- G5 each open todo has exactly one SSOT.
- G6 external commitments reflect "next step, whose ball it is, follow-up date."
- G7 memory index links resolve.
- G8 memory descriptions read match their content, with no identifiable contradictions.
- G9 todos/status lines contain no relative time references.
- G10 stakeholder identities have been verified against a master file or classification rule.
- G11 dev-repo API/env/DB/docs add-on check; skip if not applicable.

If anything fails, read more or fix it before producing the final output.

## 3. Actual sync

Order:

1. KB master files: update status, todos, dates, next steps.
2. Daily-log reconciliation: the caller has already written the daily log; only verify consistency, don't add a second entry.
3. Memory:
   - `read-only`: check and report only, don't write.
   - `update`: update per the current platform's memory policy; for Codex, only add a small extension note — don't directly edit the runtime-generated `MEMORY.md` / rollout summaries; for Claude, only edit memory files that were passed in and confirmed to belong to this project.
4. Dev-repo docs: only handle these when dev-mode is triggered.

If a dev repo is missing root-level README/AGENTS/CLAUDE docs: if it already has working code, add the root file the current platform needs; if it's still prototype/vibe-coding stage, this can be skipped — but note it under unresolved.

Principles:

- Prefer updating existing entries over appending; prefer deleting superseded interim conclusions over keeping them.
- Always verify dates with `date` and write the absolute `YYYY-MM-DD`.
- Master files don't copy the daily log's running record; actionable todos don't belong in the daily log.
- When the same fact exists across multiple files, use `rg` to find all references and align them.
- Only edit global instructions when the user explicitly stated a cross-project principle.
- For schedule/meeting changes that require touching an external system, only do so when this session was explicitly authorized to; otherwise list it as unresolved — don't pass off a local edit as complete.
- If you discover a past sync was missed, fix only the items caught by this scoped/full review — don't expand into unrelated maintenance.
- Check master-file todos by actually grepping: take 2–3 keywords from this session's work (a person's name, a feature, a page) and search the matching master files for open items (`- [ ]`). Never say "there's no matching todo" from memory.
- Don't fake the run. "Memory descriptions match their content" (G8) means you actually read the affected memory files. Better to read the 3–5 that really changed than to run only an `ls` count and declare it done. A summary left over from before a context compaction that says "GATE ticked" doesn't count as having run it this time.

## 4. Final verification and report

If you modified any files, re-run enumerate. Report:

```text
enumeration:
<final enumerate.sh output>

gate: G1-Gn pass; <skip/fail details>
grep: <keyword -> files -> conclusion>
memory: read-only | updated <files> | unchanged
docs:
- <file>: <change>
unresolved:
- <item and reason>
```

List only actual changes and failure details; don't restate the whole protocol.
