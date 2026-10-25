# Dev-repo add-on process (conditionally loaded)

**Load condition**: this session touched a repo with an API / environment variables / database / package release (e.g. PDT-learning). Docs-only sessions (the common case) don't need this file.

## Code-level changes → doc-level changes

| What happened in this conversation | Files to update (by audience) |
|---|---|
| New API / route added | project-root markdown route list · `docs/integration-guide.md` API quick-reference · `docs/architecture.md` Routes section |
| Environment variable added / renamed | project-root markdown env-var table · `docs/operator-runbook.md` env-var section · `docs/integration-guide.md` (if downstream needs to configure it) |
| Database table / column added | project-root markdown database tables · `docs/architecture.md` Data Model |
| User flow added / changed | project-root markdown user flows · README command-line examples · `docs/handoff.md` What Exists Today |
| Major feature added (spans multiple files) | all of the above + new section in `docs/architecture.md` + updated completed list in `docs/handoff.md` |
| New terminology / renamed concept | glossary in `docs/integration-guide.md` (if present) + project-wide search-and-replace of the old term |
| Deployment parameters / infra change | `docs/operator-runbook.md` · project-root markdown deployment section |
| Downstream project's integration method changed | downstream project's `docs/<integration>.md` · upstream project's `integration-guide.md` |

## Dev-project GATE add-on checklist

Dev-project-specific items for step 2 GATE in SKILL.md:

- [ ] New API route: **appears in both integration-guide and architecture**
- [ ] New environment variable: **appears in both the runbook and the project-root markdown**
- [ ] New database table: **appears in both architecture's Data Model and the project-root markdown**
- [ ] README's install / run steps match the code
- [ ] Paths / commands / tools / environment variables mentioned in CLAUDE.md / AGENTS.md actually exist in the code

## Cross-project impact check (dev version)

The scenarios most likely to get missed:

- **Upstream API changed → downstream SDK docs**: protocol changes must be aligned on both sides
- **Shared subdomain / route / environment variable changed → setup docs of every consumer project**
- **Auth middleware changed → integration guide of every consuming app**
- **Shared component / infra upgraded → any operator-runbook that mentions a version number**

How to judge: does this change touch an SDK, a subdomain, shared config, or a cross-process protocol? If so, search every dependent project for docs that mention it.

## General doc-structure convention

The standard move when adding a capability (an API, a flow, a feature) is to **touch all four places**:

1. **integration-guide / external-facing docs**: how to use it (curl / SDK examples / error-code table)
2. **architecture**: how it works (data flow, state machine, design tradeoffs)
3. **runbook**: how to operate it (smoke-test commands, troubleshooting, environment variables)
4. **handoff / CHANGELOG**: what's done

API quick-reference tables, env-var tables, and glossaries are high-frequency lookups — they **must stay current at all times**.

> Note: many repos already have their own mechanical gates (`validate_docs.py`, `spec_lint.py`, PostToolUse hooks). Where a gate exists, defer to its output; treat this table as a supplementary checklist.
