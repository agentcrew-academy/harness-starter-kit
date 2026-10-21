<!-- gate:allow install guide read once by the installing AI, not an always-on rules file -->
# Install instructions for the AI assistant

If you're reading this file, someone has handed you this repo and asked you to install it for them.

## First, know who you're talking to

**Assume the other person can't code.** They probably just pasted a URL and said "install this for me." They don't know what a hook is, what JSON is, what an environment variable is — and they shouldn't need to.

So:

- Don't throw jargon at them. If you have to use a term, explain it in plain language first.
- Don't ask them to edit config files themselves. You edit them, and then tell them what you changed.
- Install one thing, say one sentence — "this one's installed, here's what it does" — then ask if they want to keep going.
- If they say "whatever you think" or "your call," make the call. They handed you the decision.

If the person is clearly an engineer, switch to a normal technical conversation — none of the above applies.

## What's in the kit

| Piece | What it does | Needs |
|---|---|---|
| skills `checkpoint` + `neat-freak` | Close a work session in one step: log what happened, reconcile notes, commit only this session's changes | plugin `agentcrew-closure` installs both; lite mode also needs `write-manifest`. Only for users who keep a daily log and notes or projects in git |
| skill `polite` | Rewrite a draft in a warmer or more formal tone | nothing |
| skill `humanizer` | Remove AI-sounding patterns from a draft, English or Chinese | nothing |
| skill `explain` | Re-explain the last answer (or a file) in plain words | nothing |
| skill `first-principles` | Break a decision down, starting with "should this exist at all" | nothing |
| hook `claim-guard` | Stops the AI from saying "verified" or "not found" when it ran no check or search, or edited files after its last check | `jq` |
| hook `block-outgoing-comms` | Asks the user to confirm before any tool sends an email, chat message or post | `jq` |
| hook `write-manifest` | Silently records which files this session edited; never blocks | `jq` |
| hook `no-emoji-guard` | Blocks file writes that contain emoji | `python3` |
| hook `lint-gate` | Runs a check command the user names before the AI may end its turn | `jq`, plus a check command |

Everything under `retired/` is no longer installed. Only install from there if the user asks for a specific item, and read `retired/README.md` with them first.

## Ask these before you install anything

Ask all at once, not one at a time:

1. **What do you mainly use the AI for?** Coding, writing and admin, or both.
2. **Has the AI ever told you "done" or "checked" when it wasn't?** If yes, `claim-guard` is the one they need most.
3. **Is the AI connected to your email, chat or social accounts?** If yes, install `block-outgoing-comms`.
4. **Do you mind emoji in your documents?** If not, skip `no-emoji-guard`.

The four everyday skills (`agentcrew`) suit almost everyone; install them unless the user says no. Install `agentcrew-closure` (checkpoint + neat-freak) only if they keep a daily log and notes or projects in git. `lint-gate` is only for people who write code and already have a check command (`npm run lint`, `pytest`, and so on).

## Check before you start

Most hooks need a small tool called `jq`. Check with `which jq`. If it's missing, on a Mac: `brew install jq`.

If `brew` itself isn't installed, don't push them into installing Homebrew. Tell them, ask if they want to deal with it now, or install only the pieces that don't need `jq` (all the skills, and `no-emoji-guard`).

## Route A: plugin install (Claude Code, preferred)

This repo is a plugin marketplace named `agentcrew-harness`. From a terminal:

```bash
claude plugin marketplace add agentcrew-academy/harness-starter-kit
claude plugin install claim-guard@agentcrew-harness
claude plugin install block-outgoing-comms@agentcrew-harness
claude plugin install agentcrew@agentcrew-harness            # polite, humanizer, explain, first-principles
claude plugin install agentcrew-closure@agentcrew-harness    # checkpoint + neat-freak, only if they keep a daily log / notes in git
claude plugin install write-manifest@agentcrew-harness        # if they use checkpoint lite mode
claude plugin install no-emoji-guard@agentcrew-harness        # if they said yes to question 4
```

Inside Claude Code the same lines work as `/plugin marketplace add ...` and `/plugin install ...`.
Plugins don't touch `settings.json`, so there is nothing to merge or break.
Updates: `claude plugin marketplace update agentcrew-harness`.

`lint-gate` is not in the marketplace because it needs the user's own check command. Install it by hand (Route B) and set `LINT_CMD` and `FAIL_PATTERN` with them.

If the plugin commands fail (old Claude Code version, no network to GitHub), fall back to Route B and say so.

## Route B: by hand

### hooks

1. Copy the scripts from `hooks/<name>/claude-code/` into `~/.claude/hooks/`, flat, without the subfolders.
   Take the `claude-code/` copy, not `codex/`: the logic is the same but the interface code differs.
2. Make them executable: `chmod +x ~/.claude/hooks/<filename>`
3. Register them in `~/.claude/settings.json`, using `settings-example.json` as the reference.

**Registration is where things most often go wrong:**

- Their `settings.json` probably already has content. **Merge** the new entries in — never overwrite the whole file. If an event name already exists, add to its `hooks` array.
- Back up the file first. After editing, check the JSON is still valid with `python3 -c "import json;json.load(open('...'))"`. Broken JSON stops Claude Code from starting.

The two `claim-guard` scripts have to be installed **together**. With only one, the feature silently stops working and the user thinks they're protected when they're not.

### skills

Copy each folder under `skills/` into `~/.claude/skills/`, keeping the folder. No registration needed.

## After installing the skills

`checkpoint` and `neat-freak` work better once they know where the user keeps notes and projects.
Ask, then help them edit the table in `skills/neat-freak/references/sync-matrix.md` (plugin installs keep it under `~/.claude/plugins/cache/`; a plugin update replaces that copy, so keep a backup of the edited table).
If they can't answer now, skip it; the skills still run, the reconciliation is just less accurate.

## One thing you must say once installation is done

**"You need to fully quit and restart Claude Code for what you just installed to take effect."**

Hooks only load at startup, and `/clear` does not reload them. Not restarting means it isn't actually installed.

## If the user changes their mind

- Plugin install: `claude plugin uninstall <name>@agentcrew-harness` (or `claude plugin disable` to pause it).
- Hand install: delete that section from `~/.claude/settings.json` and restart; delete the files under `~/.claude/hooks/` and `~/.claude/skills/` to remove them fully.

Don't try to talk them out of removing something. It's their computer.

## Things to watch for yourself

- **Never claim something is installed without verifying it.** This kit exists to stop unproven completion claims; don't be the one who makes one.
  Confirm the files are there and the JSON is valid, and after the restart trigger one hook once to see it fire.
- **Read every file yourself before you install it.** These scripts intercept tool calls and will affect all of someone's future work.
- If something goes wrong, say so plainly and say exactly where you got stuck. Don't skip past it and keep installing.
