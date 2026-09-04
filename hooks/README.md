# Four hooks: three interceptors, one recorder — two versions each

Each one has two folders underneath it:

```
hooks/<tool-name>/
├── claude-code/   for Claude Code
└── codex/         for Codex
```

**The logic is identical on both sides.** What gets blocked, what gets let through, how evidence gets counted — it's the same set of rules. The only difference is the handful of lines tied to each platform's interface.

Three of the four (`claim-guard`, `no-emoji-guard`, `lint-gate`) are interceptors: they can block a write or hold up the end of a turn. The fourth, `write-manifest`, never blocks anything — it silently records which files this session's edit tools touched and, on the Claude Code side, the exact before/after content of each edit. Nothing reads that record on its own; it exists so a later step (a `/checkpoint`-style closure skill, or your own script) can answer "which files is *this* session responsible for" instead of guessing from what's currently dirty in the working tree. See `write-manifest/README.md` for what it's for and how to use the log.

Install whichever one matches the tool you use. If you use both, install both — the ledger and state directories are kept separate per platform (`~/.cache/claude-guard-hooks` vs `~/.cache/codex-guard-hooks`, `~/.claude/state` vs `~/.codex/state`), so they won't interfere with each other.

## How to configure it

- Claude Code → merge into `~/.claude/settings.json`; the example is `settings-example.json` at the repo root
- Codex → merge into `~/.codex/hooks.json`; the example is `codex-hooks-example.json`, and `~/.codex/config.toml` also needs `hooks = true`

## Where the two actually differ

The event names are **the same** (`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `UserPromptSubmit`), and the `matcher` + `hooks` structure is the same too. The real differences come down to the five points below — use this table if you're porting another hook.

| | Claude Code | Codex |
|---|---|---|
| Where config lives | the `hooks` block in `settings.json` | a separate `~/.codex/hooks.json`, and `config.toml` needs `hooks = true` |
| This turn's identifier | `session_id` | **`turn_id`** (safest to write `.turn_id // .session_id` and try both) |
| Tool names in the matcher | `Write`/`Edit`/`MultiEdit`/`Bash`/`WebFetch` | editing a file is `apply_patch`, running a command is `exec`/`shell`/`exec_command`, fetching a page is `web_fetch` |
| Project directory | env var `CLAUDE_PROJECT_DIR` | doesn't exist — read `cwd` from the payload instead |
| What to output when allowing something | just exit quietly | **print `{}`** — printing nothing gets treated as an anomaly |
| How to express a block | `exit 2` + a message to stderr | print `{"decision":"block","reason":"..."}` |
| Trust mechanism | none | a hook has to be trusted before it runs; the first activation needs confirmation |

Codex also has `PostCompact`; Claude Code has `PreCompact`, `SessionEnd`, and `Notification`. Each side has events the other doesn't — check that the one you want actually exists before you wire it up.

`stop_hook_active`, `last_assistant_message`, `tool_name`, and `tool_input` share the same field names on both sides, so you can reuse those directly.

## Porting another hook yourself

The table above is the whole story. The core logic doesn't need to change — `claim-ledger-tracker`, excluding comments, is 26 lines in one version and 32 in the other; the extra six lines are all defensive checks like "skip if `jq` isn't available." The comparison expression that actually does the judging hasn't changed by a single character.

**After porting, always trigger it once for real to confirm it actually fires.** Don't assume it's working just because it didn't error — that's exactly the failure mode the three interceptors above exist to catch.

## One known asymmetry: `write-manifest` isn't 1:1 across platforms

Every other hook here has identical logic on both sides. `write-manifest` doesn't, and it's worth knowing why before you rely on it.

On Claude Code, `Edit`/`MultiEdit` payloads hand you a clean `old_string`/`new_string` pair, so the hook can log the exact edit and a companion script (`stage-own-edits.sh`, shipped with the `checkpoint` skill) can replay just this session's edits on top of `HEAD` — useful when another session touched the same file. On Codex, `apply_patch` hands you a unified-diff-shaped patch instead, which needs more parsing to split "this session's hunks" back out. The Codex build here only tracks *which paths* were touched, not the edit content, so there's no Codex equivalent of `stage-own-edits.sh` yet. If a file is dirty from another session on the Codex side, the safe move is still to hold it for a human, not to stage it.
