# Change-impact matrix (fact → files)

Check this table when you're unsure which files a given fact-level change should sync to.

**This is a template, not a spec.** The left column is "something that happens in your work"; the right column is "which files go stale once that happens." The rows below are generic starting points — replace them with your own fact types and file layout. This table is only useful once it matches your actual file structure.

## Fact-level changes → file-level changes

| What happened in this conversation | Files to update |
|---|---|
| Project progress advanced | progress section of the corresponding project master file · one-line summary in the log |
| Something sent externally (proposal / quote / deliverable / PR) | "next steps" in that client's master file, noting "awaiting reply, follow up by when" · log entry noting it was sent |
| Reply received / confirmed / declined by the other party | status line in that client's master file · if closed, archive it and update the index |
| Schedule set or rescheduled | date in the master file · **sync the external system (calendar / scheduling tool) — a local-only change doesn't count as done** · rescheduling should also trigger a check of other affected todos |
| Amount / contract / terms changed | the corresponding finance or contract file · sync any existing conclusions that the change affects |
| A new opportunity or work item first takes shape | create a single source-of-truth (SSOT) file for it · the top-level rollup file gets only a one-line summary + link |
| A decision is finalized | mark the decision file as finalized · **delete the superseded old conclusion, don't just annotate it** |
| Technical approach changed | docs next to the code · README · related statements in rule files (CLAUDE.md / AGENTS.md) |
| A rule or process changed | the rule file itself · check whether any hook/script is still running the old rule |
| A remembered fact went stale, a relative date ("today", "recently") got saved, or the same fact sits in two memory files | the memory file and its index line: rewrite relative dates as `YYYY-MM-DD`, merge duplicates into one, delete finished todos, overturned decisions, and one-session context |

## Operating principles

1. **A fact lives in exactly one place.** The same thing written in two files will eventually drift into two contradicting versions. Top-level rollup files hold only a summary and a link — never a copy of the content.
2. **State changes take priority over new content.** The point of reconciliation is "which existing statements are now wrong," not "what more can be added."
3. **Whether an external system counts as synced depends on the external system.** If the local file changed but the calendar/scheduling tool didn't, the sync isn't done.
4. **Deletion is a legitimate action.** Stale conclusions, superseded decisions, and completed todos left in place only give the next reader (or your future self) the wrong answer.
5. **Check where else the one-line version lives.** A status often exists in full in one file and as a one-line summary in another (a rollup line, a daily log, a memory note). When it changes, update both, and grep the old conclusion's keywords across files that cite it.
