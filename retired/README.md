# Retired

Everything in this folder used to be part of the kit. It still works and you can read or copy it, but it is no longer installed by default, listed in the plugin marketplace, or updated.

| Item | Why it was retired | Where the idea lives now |
|---|---|---|
| `skills/review-loop` | Its author stopped using it, and it needs a Python script plus an HTML template to run, which is more setup than a starter kit should ask for. | The habit of answering every review comment with "what you said, where I changed it" is a single paragraph you can add to any writing skill. |
| `skills/phantom-pushback` | Its author stopped using it. | Not replaced. |
| `skills/info-diet` | It was built for one workshop and depends on that workshop's setup. | Not replaced. |
| `skills/asd-ste100` | A strict technical-English standard. Useful for manuals, too narrow for everyday writing. | `humanizer` (removes AI-sounding patterns) and `explain` (plain-language rewrite) cover most everyday needs. |
| `skills/iso-24495` | A plain-language standard. Same reason as above. | Same as above. |
| `claude-md-template` | One template cannot fit everyone, and a rules file copied from someone else tends to grow without anyone checking whether each line still matters. | The hooks in this kit enforce the rules that matter most. Writing a rules file that fits your own work is what the paid pack does. |

## Using something from here anyway

Copy the folder you want into `~/.claude/skills/` (or `~/.codex/skills/` for Codex), the same way the active skills are installed. For `claude-md-template`, read its own `README.md` first: never overwrite an existing `CLAUDE.md`, merge section by section.

Nothing here gets bug fixes. If one of these breaks after a Claude Code or Codex update, the fix is on you.
