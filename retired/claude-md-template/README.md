# A Starter Rules File (CLAUDE.md Template)

This is a "how we work together" template for the AI to read. Once it's installed, you don't have to re-explain "show me the draft before sending" or "get evidence before reporting done" every single conversation — it reads this on its own every time it starts working.

## What's inside

- `CLAUDE.md`: the main template, in three parts — **Background** (things only you know), **Hard gates** (a handful of things that must never go wrong, each with a reason), and **Judgment context** (the reasoning spelled out so the model can extrapolate on its own).
- `rules/`: three optional add-ons — verification discipline, delegation judgment, risk boundaries. Install whichever you need; skipping any of them doesn't affect the main template.

## How to install

Paste this folder's URL to Claude Code and say:

> Help me install claude-md-template. Go through it section by section and ask me whether each one applies — drop what doesn't. If I already have a CLAUDE.md, merge in the sections that apply instead of overwriting the whole file.

Or do it by hand: fill in the blanks in `CLAUDE.md` and put it at `~/.claude/CLAUDE.md` (global) or in your project's root folder (project-only); put whichever files you want from `rules/` into `~/.claude/rules/`.

## Why this template is so short

Because a rules file is written for the model, not for people, and the guidance from the newest generation of models (the Claude 5 line, the GPT-5.6 line) all points the same direction: **fewer rules is better — write down only what the model doesn't already know.** Anthropic cut Claude Code's own system prompt by more than 80% without losing capability; OpenAI has found in testing that leaner rules actually raise scores. So every line in this template has to pass one test:

> "If I remove this line, will the model get it wrong? If not, delete it."

Use the same test when you add your own content. Two more principles:

- **Turn hard constraints into reasoning.** Instead of writing "never do X," write "do Y before X, because…" Once the model knows the reason, it can apply the same judgment in situations you never anticipated. The real exceptions are irreversible actions (sending an email, deleting a file) — keep those as absolute statements, but still give the reason.
- **Don't hardcode numbers that will go stale.** Limits, model names, and tool settings all change across versions. Instead of hardcoding a number that'll be wrong in six months, write "check the current official docs first."

## A few reminders

- The blanks in the template (`___`) need to be filled in with your own information — leaving them blank means it isn't actually installed.
- A rules file can't stop the model from "forgetting." For anything that truly must never slip (like requiring a human look before an email goes out), you need the interceptor tools in this repo's `hooks/` folder — that's the only thing that's actually enforced.
- After installing, fully quit and restart Claude Code for it to take effect.
