<!-- gate:allow install guide read once by the installing AI, not an always-on rules file -->
# Notes for Codex

Read `CLAUDE.md` in this same folder first. Everything in it about talking to someone who can't code, the questions to ask before installing, and the restart reminder applies here too.

This file only covers where Codex differs. Codex has no plugin marketplace for this kit, so it always uses the by-hand route.

## hooks

Every hook has a Codex build under `hooks/<name>/codex/`, with the same logic as the Claude Code build and the interface already adapted.

1. Copy the scripts from `hooks/<name>/codex/` into `~/.codex/hooks/`, then `chmod +x`.
2. Merge the blocks you need from `codex-hooks-example.json` into `~/.codex/hooks.json`. If an event name already exists, add to its `hooks` array.
3. Confirm `~/.codex/config.toml` has `hooks = true`.
4. Codex asks the user to trust each hook the first time it runs.
5. Restart the session.

**After installing, trigger each hook once and confirm it fires.** No error is not proof it works.

Two Codex-specific notes:

- `write-manifest` on Codex records which paths were touched, not the edit content, so there is no Codex version of `stage-own-edits.sh`. See the asymmetry note in `hooks/README.md`.
- `block-outgoing-comms` matches tool names containing send, reply, forward, broadcast, publish, schedule or push. Codex has no "ask" decision, so every send attempt is blocked, retries included: the model shows the draft and the user sends it themselves. Tell the user this before installing it.

The interface differences between the two platforms are in the table in `hooks/README.md`.

## skills

The six folders under `skills/` are plain-text instructions and work in Codex as-is. Copy them into `~/.codex/skills/` (the `.agents/skills/` links in this repo point at the same folders).

`checkpoint` and `neat-freak` mention a "subagent"; use whatever Codex calls its equivalent.

## Don't pretend it's installed

Say clearly what couldn't be installed and what you rewrote, and only say something works once you've tested it.
