# Notes for Codex

Read the `CLAUDE.md` file in this same folder first — that's the primary install instructions, and everything in it about "how to talk to someone who can't code," "what three things to ask before installing," and "remind them to restart when you're done" applies here too.

This file only covers where Codex differs from Claude Code.

## hooks now have a Codex version

They're under `hooks/<tool-name>/codex/`. All four are there, with the exact same logic as the Claude Code version.
The interface parts are already adapted, so you can **copy them straight into `~/.codex/hooks/` without porting anything yourself.**
One exception: `write-manifest`'s Codex build only tracks which paths were touched, not the before/after content.
There's no Codex equivalent of `stage-own-edits.sh` yet — see the asymmetry note in `hooks/README.md`.

Install steps:

1. Copy the scripts from `hooks/<tool-name>/codex/` into `~/.codex/hooks/`, then `chmod +x`
2. Merge the blocks you need from the repo root's `codex-hooks-example.json` into `~/.codex/hooks.json` (if the same event name already exists, add to its hooks array — don't overwrite the whole section)
3. Confirm `~/.codex/config.toml` has `hooks = true`
4. Codex has a trust mechanism for hooks — the first time one runs, it needs to be confirmed
5. Restart the session

**After installing, actually trigger it once and confirm it fires** — don't claim it's installed just because it didn't error out.

For the interface differences between the two platforms, and what to change if you want to port another hook yourself, see the comparison table in `hooks/README.md`. Short version: the event names are the same on both sides — what changes is `session_id` → `turn_id`, the matcher needs `apply_patch`/`exec`/`shell` added, there's no `CLAUDE_PROJECT_DIR` so read `cwd` from the payload instead, allowing something through means printing `{}`, and blocking means returning `{"decision":"block","reason":...}` instead of `exit 2`.

## skills work as-is

All ten folders under `skills/` are plain-text instructions, not tied to any platform.
Just put them somewhere Codex can read them.

review-loop is a partial exception: the SKILL.md itself is generic, but it ships with a Python script and an HTML template — copy the whole thing, and update the path in SKILL.md's "commands" section to match the actual install location. The script only uses the standard library, so it doesn't care which assistant is running it.

The "subagent" that checkpoint and neat-freak refer to has an equivalent concept in Codex, just under a different name — adjust to match your own conventions.

## Don't pretend it's installed

The entire theme of this package is "don't trust a completion claim with no evidence behind it." You especially can't be the one to break that rule while installing it for someone.

Say clearly what couldn't be installed, say clearly what you rewrote, and only say something works once you've actually tested it.
