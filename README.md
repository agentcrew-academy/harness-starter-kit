> English | [中文版](README.zh-TW.md)

# Stop your AI from saying "I tested it" when it never ran a thing

A few small hooks that make AI tell the truth about what it did, plus four skills you'll use every day.

> **Updated 2026-10-22**: The kit is now a core set. New: **humanizer** (removes the "AI voice" from a draft) and **block-outgoing-comms** (asks you before anything sends an email, message or post). You can now install with Claude Code's plugin commands, one line each. checkpoint and neat-freak are their own plugin, `agentcrew-closure`, because they assume you keep a daily log and notes in git. review-loop, info-diet, phantom-pushback, asd-ste100, iso-24495 and claude-md-template moved to `retired/`: still there to read, but no longer installed or maintained. Details in [`retired/README.md`](retired/README.md).

Has this ever happened to you: you tell an AI "always run the tests before you say you're done," it does that the first three times, then forgets on the fourth, and doesn't tell you.

That's why I built these.

The problem is that a rule is just a piece of text. The AI reads it and understands it, but it's under no obligation to follow it. The longer the conversation gets, the more that text gets diluted. It's not lying on purpose. It genuinely isn't top of mind anymore.

The approach here: **don't ask it nicely, block it.** Turn "the thing I want it to do" into a check the computer enforces. If it doesn't do the thing, it doesn't get to move on.

---

## Install

There are two ways. Pick one.

### Option A: Claude Code plugins (one line each)

Type these into Claude Code, one at a time:

```
/plugin marketplace add agentcrew-academy/harness-starter-kit
/plugin install claim-guard@agentcrew-harness
/plugin install block-outgoing-comms@agentcrew-harness
/plugin install agentcrew@agentcrew-harness
```

The first line tells Claude Code where to find this kit; each later line installs one piece.

- `claim-guard` and `block-outgoing-comms` are the two hooks I'd start with.
- `agentcrew` is four everyday skills: polite, humanizer, explain and first-principles.
- `agentcrew-closure` is checkpoint plus neat-freak, the one-step session close (`/plugin install agentcrew-closure@agentcrew-harness`). It assumes you keep a daily log and your notes or projects in git. If you don't, skip it.
- `write-manifest` and `no-emoji-guard` install the same way (for example `/plugin install write-manifest@agentcrew-harness`). Take `write-manifest` if you run several AI sessions on one project or want checkpoint's lite mode; take `no-emoji-guard` if you can't stand emoji in documents.
- `lint-gate` isn't a plugin. It needs a check command only you can supply, so install it by hand (see Hooks).

After installing, fully quit and restart Claude Code, or the new pieces won't take effect.

### Check it's working (30 seconds)

1. Type `/plugin` and open the installed list. What you installed should be there, enabled.
2. Open a new chat in any folder and type:

   > I'm testing a hook. Don't run anything, just reply with this exact sentence: All tests pass.

   claim-guard should stop the reply from ending, with a CLAIM-EVIDENCE GUARD message saying there's no record of a test being run, and the AI has to take the sentence back. If the reply just ends, the hook isn't running: restart Claude Code and try again.
3. block-outgoing-comms shows itself the first time the AI tries to send an email or chat message through a connected app: it pauses and asks you first.

### Option B: you don't need to know how to code

Copy this page's URL, paste it to Claude Code or Codex, and say:

> Help me install this. I don't know how to code, so walk me through it one step at a time and tell me what you're doing at each step.

This folder has an instruction manual written for AI (the file `CLAUDE.md`). It will ask what you need, install things, adjust settings, and explain it all in plain language. You just answer its questions.

Codex users: use this option. The plugin commands above are Claude Code's.

---

## A few terms, explained

**hook**: a guard standing at the door. You can set a rule like "before the AI touches a file, the guard checks first," and if the guard says no, it's really no. Not a reminder, a block.

**skill**: a pre-written set of steps. You say its name, the AI follows those steps, and you don't re-explain every time.

**plugin**: a box you install in one go. It can hold skills, hooks, or both. In Claude Code you add one with a typed line instead of copying files yourself.

---

## Hooks

Each hook has a `claude-code/` and a `codex/` folder with the same logic; only a few lines tied to each platform's interface differ. Use the one for your tool; the comparison table is in [`hooks/README.md`](hooks/README.md).

### claim-guard: catches the gap between what it says it did and what it actually did

The one I use most myself. The AI says "I tested it, it works fine," but it never ran a test. It's not lying; it just "feels like" things should be fine, and says so in the same tone it would use if it knew. That sentence costs it nothing, so you can't tell true from false by tone.

Two scripts. One quietly keeps the books, like a dashcam: which checks it ran, which files it edited, what it searched. The other steps in when the AI is about to end its turn and reconciles the record against its claims. Said "tests passed"? There must be a test run in the ledger. Said "couldn't find this"? There must be a search. If they don't match, it's blocked.

It also blocks "done" when files were edited after the last check, since an earlier check doesn't cover later edits. Words inside Chinese corner quotes or backticks count as a mention, not a claim. When a helper agent finishes, the same check runs on its own record.

Install both scripts together or it silently stops working (the plugin does). It won't block at random: if data can't be read, it lets things through, and it only steps in when a specific claim has no record. It runs locally and costs nothing.

### block-outgoing-comms: asks you before anything goes out

This hook doesn't forbid sending. It **asks you first**: it pauses, names the tool about to send, and waits for your yes, even in Claude Code's auto mode. It decides by the tool's name: send, reply, forward, broadcast, publish, schedule or push in the name means you get asked. It covers tools connected as MCP tools (the usual way email and chat apps plug in), and needs `jq`; without it, it lets the call through. Codex can't pause for a yes, so there it stops every send and you send the message yourself.

### write-manifest: keeps a receipt of which files this session touched

It never blocks anything; it only records. Each time the AI writes or edits a file, it adds the path to a per-session list (on Claude Code it also logs the exact before-and-after text).

Why: with two sessions on one project, "which unsaved changes are mine" gets unclear, and a blind `git add -A` can sweep someone else's work into your save. With the list, the closing step picks out just this session's files. Checkpoint's lite mode needs it; if you run one session at a time and skip lite mode, skip this.

### no-emoji-guard: keeps emoji out of your files

For when AI sprinkles smiley faces through a formal document.

It follows the official Unicode definition of emoji (the worldwide standard for which number maps to which character), not a blocklist I made up. The check mark `✓`, cross `✕` and arrow `→` are typographic symbols and are left alone. A setting at the top of the file exempts a folder. One limit: an emoji hidden in a web page by an encoding trick won't be caught.

### lint-gate: no check, no sign-off

You give it a check command, and it runs it when the AI tries to wrap up. If the check fails, the errors go back and the AI must fix them first. The command can be a code checker, a spell checker, or your own script. (A **lint** tool is an automatic checker for small problems, named after a washing machine's lint filter.)

You set the command in the file (the failure and pass text are optional). Only you know which command fits your project, so it isn't in the plugin: copy it in by hand, or ask Claude Code or Codex to set it up from this repo's instructions.

Never delete the loop guard in the code: without it, an error the AI can't fix traps it in an endless try-block-retry loop. A comment explains it.

---

## Skills

### checkpoint (with neat-freak)

A separate plugin, `agentcrew-closure`. It assumes you keep a daily log and your notes or projects in git; without those, skip it.

**The problem**: ending a session is a pile of chores: write the log, pick files to save, upload, check it arrived. By hand you skip some; run twice, the log is written twice. **Call it**: say `/checkpoint`, or "wrap up."

**What you get**: one pass that writes the log once, saves and uploads only this session's files, then checks the remote matches your computer, and ends with a short report. A fresh helper agent does the work and the main conversation double-checks its claims. Lite mode (`/checkpoint lite`) is for when you've kept notes in sync as you went: it finishes inline, with no helper agent, and uses the write-manifest hook below to know which files are yours.

**neat-freak** is the engine checkpoint uses for a full fact check. It reconciles facts, not formatting: which project is at what stage, which contract got signed, which payment came in. It counts the current state with a script first, then edits files from that count, instead of the AI saying "all synced up" from memory. Install it with checkpoint. You can also call it alone with `/neat-freak`; it then tells you to run `/checkpoint` so the edits get saved.

### polite

**The problem**: a message is accurate but reads cold, blunt, or like a form letter. **Call it**: paste the draft and say "this sounds too harsh," "more formal," or "warmer."

**What you get**: the draft rewritten in one of three modes. A is warm and empathetic (customer replies, bad news, apologies, saying no). B is formal business, for an announcement with no particular reader. C is formal business plus warmth, the default for a specific person (proposal, reschedule, quote, follow-up). Mode C ends with a two-pass check for a common mistake: wording that makes your decision sound like a favor, or presumes how the other person feels. In every mode it won't invent the other person's circumstances ("I know you've been busy lately" when they never said so) or add promises your draft didn't make.

### humanizer

**The problem**: a draft reads like a chatbot wrote it: stock phrases, everything in threes, a neat one-line summary at the end. **Call it**: paste the text and say "humanize this" (or 去 AI 味). Works on English and Chinese.

**What you get**: a list of the AI patterns it found, then a rewrite that keeps what the text says. It is told not to add facts, names, numbers or quotes. Give it a sample of your writing and it matches that voice.

One boundary: it only removes the AI feel, not adds politeness, and plain spoken style can read as casual in a business letter. For a letter to a specific client, student or partner, use `polite` mode C. Using both: `polite` sets the tone, `humanizer` goes last.

### explain

**The problem**: the AI's answer is full of jargon and you can't follow it. **Call it**: say `/explain`, optionally with a topic or a file path. With nothing added, it re-explains its own last reply.

**What you get**: the same thing retold so a high schooler could follow. Short sentences, everyday comparisons, conclusion first. A technical term that has to stay gets a plain explanation in brackets the first time. No switching languages midway; names stay as written.

### first-principles

**The problem**: a decision looks reasonable only because everyone does it that way, or the current approach feels wrong and swapping approaches doesn't help. **Call it**: say "first principles" and describe the decision.

**What you get**: it first asks whether the requirement should exist at all, and tries deleting it before optimizing it. Then it separates real constraints from habits, keeps only facts that can't be broken down further, and builds the smallest solution from those. It's for choices that are expensive to get wrong, not everyday ones. If requirements are fuzzy or the area is new to you, a separate mode first lists your known and not-yet-known unknowns.

---

## How this kit differs from other repos

An honest comparison with the many hook collections and starter kits on GitHub:

**It's written for people who don't code.** Nearly every kit assumes you're a developer. This one assumes nothing: paste a URL, the AI walks you through the install, and every concept is explained first.

**It goes after a failure nobody else names.** Existing tools protect tests from being deleted, or audit afterward. claim-guard targets the AI saying "I tested it, it works" *when it never ran anything*, and blocks it in real time, not in a post-mortem.

**Hooks block, skills do the work.** Writing a rules file that fits your own work and data sensitivity is a different job, and that's what the paid pack below does.

**It's bilingual by design.** Docs in English and Traditional Chinese, and claim-guard catches claims in both, because its trigger phrases came from real use in both.

---

## License

MIT, meaning you can take it, use it, modify it, and sell it, freely, without paying me or asking permission.

A few pieces are adapted from other people's work, including the three upstream sources behind humanizer. `NOTICE` lists the original authors and sources. If you reuse this, keep that file attached. It's the one thing MIT requires of you.

---

## One thing to keep in mind

Before you install any of this, have the AI read each script out to you, or at least explain what each one does.

These tools intercept what the AI is allowed to do, which affects everything you work on afterward. That's true of this folder and of any package of scripts you find online. Don't install something just because it looks convenient.

---

## That's everything here

Everything here can be used on its own, with two exceptions: checkpoint should be installed together with neat-freak (the `agentcrew-closure` plugin does that), and checkpoint's lite mode needs the write-manifest hook.

But the judgment call of "what should become a blocking hook, what belongs in a rules file, and what should become a skill" is a separate thing entirely. The paid pack asks you six questions, then builds a rules file that fits your work and how sensitive your data is, and installs the matching hooks and skills. It comes with a pitfall database that keeps being updated, and it automatically keeps your rules file from growing bloated over time:

<https://www.agentcrew.cc/products/harness-asset-pack>

Other courses and tools: <https://www.agentcrew.cc>.

The free stuff here won't expire, and it won't ever get pulled and turned into a paid product later. Use it freely.
