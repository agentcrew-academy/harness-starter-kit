> English | [中文版](README.zh-TW.md)

# Three small tools that keep AI honest, ten ready-made skills, and a starter rules file

> **Updated 2026-08-09**: Both interceptor hooks now ship in a Claude Code version and a Codex version, with the same underlying logic. Added the review-loop skill, bringing the total to six.
> **Updated 2026-08-12**: Added info-diet (works out where your attention is actually going), bringing the total to seven.
> **Updated 2026-08-21**: Added phantom-pushback (catches the AI inventing an opinion you never held, then correcting you for it), bringing the total to ten.
> **Updated 2026-08-14**: Added claude-md-template — a starter CLAUDE.md written to match the official guidance for the fifth-generation models, plus three optional rules files.

Has this ever happened to you: you tell an AI "always run the tests before you say you're done," it does exactly that for the first three times, then forgets on the fourth — and doesn't tell you it forgot.

That's why I built these.

The problem is that a rule is just a piece of text. You write it down, the AI reads it, the AI understands it — but it's under no obligation to actually follow it. The longer the conversation gets, the more that text gets diluted. It's not lying to you on purpose. It genuinely isn't top of mind anymore.

The approach here is: **don't ask it nicely — block it.** Turn "the thing I want it to do" into a check the computer enforces automatically. If it doesn't do the thing, it doesn't get to move on.

---

## You don't need to know how to code to install this

You don't have to do any of this by hand. Copy this page's URL, paste it to Claude Code or Codex, and say:

> Help me install this. I don't know how to code, so walk me through it one step at a time and tell me what you're doing at each step.

This folder includes an instruction manual written for AI (the file called `CLAUDE.md`). It will follow those instructions to ask you what you need, install things, adjust settings, and explain everything in plain language. All you have to do is answer its questions.

It'll start by asking you three things — roughly: "what do you mainly use your computer for," "has an AI ever told you something was done when it wasn't," and "do you mind if AI puts emoji in your documents." Just answer honestly — there's no wrong answer, and you can always add or remove pieces later.

**The one thing to remember**: after installing, fully quit and restart Claude Code. The new pieces won't take effect until you do.

---

## A few terms, explained

**Claude Code**: an AI assistant that can write code and edit files directly on your computer. This whole package is built for it.

**hook**: think of it as a guard standing at the door. You can set a rule like "before the AI touches a file, have the guard check first" — and if the guard says no, it's really no. This isn't a reminder. It's a block.

**skill**: a pre-written set of steps for doing something. You say its name, and the AI follows those exact steps, so you don't have to re-explain yourself every time.

**lint**: a tool that automatically catches small problems for you. The name comes from a washing machine's lint filter — the thing that catches the fuzz off your clothes. Code has an equivalent: extra whitespace, variables that got declared but never used, names that don't follow the project's convention. None of that will necessarily break the program, but it makes the code messier and harder to read. A lint tool runs once and hands you a list: "line 12 has trailing whitespace, line 40 declares a variable nobody uses."

---

## Three interceptor hooks

**Both platforms are covered.** Each tool has a `claude-code/` folder and a `codex/` folder underneath it, and the logic inside is identical — the only difference is the handful of lines tied to each platform's interface. Install whichever one matches the tool you use; if you use both, install both. The ledgers are kept separate, so they won't collide.

For exactly where the two versions differ, and what to change if you want to port another hook yourself, see the comparison table in [`hooks/README.md`](hooks/README.md).


### claim-guard: catches the gap between what it says it did and what it actually did

This is the one I use the most myself.

Here's the situation: the AI tells you "I tested it, it works fine." But it never ran a test. It's not lying to you — it just "feels like" things should be fine, and says so in exactly the same tone it would use if it actually knew. That sentence costs it nothing to say, which is exactly why you can't tell true from false by the tone alone.

So this tool does two things.

One script quietly keeps the books in the background, logging which checks it actually ran and what it actually searched for during the conversation. Think of it as a dashcam — always recording, never saying a word.

The other script steps in right when the AI is about to end the conversation and reconciles the record against what it's claiming. Said "tests passed"? There'd better be a test run in the ledger. Said "couldn't find this feature"? There'd better be a search in the ledger. If the two don't match, it gets blocked — no wrapping up.

Both scripts have to be installed together. Install just one, and the whole thing silently stops working.

It won't block things at random. If the data can't be read or is malformed, it lets things through by default. It only steps in when the AI made a specific claim with zero record behind it. The whole thing runs as a small local program — it won't cost you a cent.

### no-emoji-guard: keeps emoji out the door

If you can't stand it when AI sprinkles smiley faces and checkmarks through a formal document, this one's for you.

It isn't a blocklist I threw together by feel — it's based on the official Unicode definition (Unicode is the standard the whole world agreed on for "which number maps to which character"). Whatever the official spec calls an emoji, this blocks.

A few things look similar but aren't: the checkmark `✓`, the cross `✕`, the arrow `→`. Those are typographic symbols, and they're deliberately left alone.

If you've got a whole folder you want to exempt, there's a setting at the top of the file for that. In my own notes app, some of these symbols do real work — deleting them would break my to-do tracking — so I whitelisted that entire folder.

One honest limitation up front: if an emoji is hidden inside a web page using some special encoding trick, this won't catch it.

### lint-gate: no check, no sign-off

The simplest of the three. You give it a check command, and it runs that command whenever the AI tries to wrap up. If the check fails, it hands the errors back and makes the AI fix them before it's allowed to finish.

It's not limited to code checks. Whatever command you point it at is what it runs — a spelling checker, or a script you wrote yourself to check whether a document's formatting is correct. I personally use it to check my notes' formatting.

Two settings, and you can drop it into any project.

There's a piece of logic in the code you should never delete. Without it, if the AI hits an error it can't fix, it gets stuck in a loop — try to finish, get blocked, try to finish again, get blocked again — forever. That's the single easiest trap to fall into if you build a tool like this yourself, so I left a comment explaining it.

---

## Ten skills

**explain**: call `/explain` and it retells whatever was just said in terms a high schooler could follow. No jargon, no slipping into another language mid-explanation. Use it when you can't follow what the AI is saying.

**polite**: rewrites the tone of a message for you. Two modes — one warm and empathetic (for customer replies, breaking bad news, turning someone down), and one formal-business (for outbound emails, proposals, chasing payment). There's one rule in here I added on purpose: never invent the other person's circumstances for them. Something like "I know you've probably been really busy lately" — if they never said that, don't put it in their mouth. It reads as manipulative.

**first-principles**: rethink something from the ground up instead of copying how someone else did it. The core question, before you ever ask "how should I do this," is "should this even be done at all." It comes with a process for mapping out your unknowns, which works well when the requirements are still fuzzy or you're new to the whole area.

**checkpoint**: finishes everything that needs doing at the end of a session, in one pass — writing the work log, choosing what to save, uploading it, and then double-checking it actually made it up there. The point is doing it in one pass; doing the same thing twice logs it twice.

**neat-freak**: does the reconciliation. Not formatting — facts. Which project is at what stage, which contract got signed, which payment came in, which to-do actually got finished a while ago. It first runs a script that mechanically counts up the current state — numbers that can't be faked — and only then edits files based on that count. Instead of letting the AI say "all synced up" from memory.

**review-loop**: you ask AI to write something long — a proposal, a spec, a report. You read it, give feedback, it produces a second draft. You read that, give more feedback, it produces a third. By the fourth draft, you notice a section is just gone. You never asked for it to be cut. It never said it cut it.

This is what stops that. Every section of the document gets a permanent ID, and the computer does the counting: ten sections in the last version, only nine findable in this one — it flags it and tells you exactly which one vanished. The moment you say "this section's approved," its content gets locked, and any further edit to it gets blocked too. It also turns the document into a web page with a comment box next to each section, where you pick "approve / revise / question / discuss," fill it in, and copy the whole thing back to the AI in one click. Don't feel like typing — talk it out, transcribe the recording, and paste that back instead.

It ships with a regression suite: a fictional planning spec that reproduces three real bugs this tool has actually hit in the past. Run `bash skills/review-loop/examples/regression/run-test.sh` to verify it yourself.

**info-diet**: works out where your attention is actually going. It reads the browsing history on your own computer and sorts it into four buckets — information you're taking in from outside, you looking at yourself (notifications, your own posts, your own dashboards), talking to people, and getting things done. Most people assume their problem is too much information; what actually turns up is usually something else — the time isn't going toward looking at the world, it's going toward watching how the world is looking at you.

It only runs on your own computer — no network access, nothing uploaded. The organized results get saved to a file first, and the AI doesn't see them yet; it asks you if there's anything you'd rather it not see, you give it keywords, and it deletes based on those keywords — **while it still hasn't looked at the file**. Medical, job-hunting, dating, legal, and gambling categories get hidden automatically during the sorting step, no exceptions needed. If you want to go a step further and have it look at the titles of articles you actually read to judge information quality, that needs a separate, explicit authorization from you.

The limitations are stated plainly, not hidden: it can't see your phone, it only supports browsers in the Chrome family, and it can't judge the quality of social media posts (all it gets there is an account name as the title).

The first three are ready to use as-is. checkpoint and neat-freak need to be adjusted to match how you actually organize your own files before the numbers mean anything. The comparison table inside is a template — swap the left column for the things that actually happen in your work, and the right column for your own folder names. Copying mine won't help you; my folders don't look like yours.

review-loop is a bit different from the others: it only works once you've reformatted a document into its tagged format. That's an extra step, but it's the only way to actually catch content disappearing without a trace. The first time you use it, try it on the included example before you run it on a real document.

**asd-ste100**: a Simplified Technical English rewrite. Use it for English text that's going to be read directly by a machine, or by another AI, where a misread has a real cost — tool descriptions, error messages, instructions passed between agents. The core move is stripping out ambiguous words and multi-clause sentences.

**iso-24495**: an ISO 24495-1 plain-language rewrite, with dedicated techniques for both English and Traditional Chinese. Use it for reports, letters, documentation — text where the goal is for the intended reader to understand it in one pass and know what to do next.

**phantom-pushback**: you ask the AI to change the payment terms to two installments. It makes the change, then adds: "one thing I'd gently push back on — you may be assuming installments are always friendlier to cash flow, but..." You never said that. It needed to end on a note of independent judgment, had nothing to disagree with, so it invented an opinion, put it in your mouth, and corrected you for it.

This is not the same as the AI being long-winded, and telling it to be brief won't fix it — the paragraph looks like real content, which is why it survives editing. The test this skill applies is one question: can you point at something you actually said, or something you actually wrote, where you hold that position? If not, the passage goes. Real objections stay: criticism of your code, your numbers, or your plan is never touched, and a genuine warning buried in a closing caveat gets moved to the top instead of deleted.

Worth knowing why this happens: rules of the form "always give me the strongest counterargument" are a likely cause. They make disagreement compulsory, so when there's nothing to disagree with, the only way to comply is to make something up. The skill says so, and refuses to write the opposite rule either.

---

## How this kit differs from other repos

There are plenty of Claude Code hook collections and starter kits on GitHub. Before deciding whether this one is for you, here's an honest comparison:

**It's written for people who don't code.** Nearly every kit out there assumes you're a developer — the docs talk about test suites, CI, and architecture decision records. This one assumes nothing: you paste a URL, the AI walks you through the install in plain language, and every concept (hook, skill, lint) gets explained in one paragraph before it's used.

**It goes after a failure nobody else names.** Existing tools protect tests from being deleted, or audit the work after the fact. claim-guard targets something different: the AI saying "I tested it, it works" *when it never ran anything*. A ledger records what actually happened; a reconciliation gate blocks the wrap-up when the claims and the record don't match — in real time, not in a post-mortem.

**It covers all three layers in one place.** Enforcement (hooks), workflows (skills), and a lean rules-file template written to the current generation of models' official guidance. Most kits give you one of the three and stop there.

**It's bilingual by design.** Docs in English and Traditional Chinese, and the hooks catch claims in both languages out of the box — because the trigger patterns were built from real usage in both.

---

## A starter rules file (claude-md-template)

Earlier I said "a rule is just a piece of text, and the AI has no obligation to follow it" — that doesn't mean a rules file is useless. It means the file needs to be **short, and correct**. `claude-md-template/` is a starter CLAUDE.md written to match the official guidance for the newest generation of models: just three sections (your background, a small number of hard gates each backed by a reason, and reasoning context that lets it generalize on its own), plus three optional rules files for verification, delegation, and risk.

Every line in it had to pass the same test to earn its place: "if you deleted this line, would the AI get something wrong? If not, delete it." Use that same test when you add your own rules later. For how to install it and why it's this short, see [`claude-md-template/README.md`](claude-md-template/README.md).

The rules file handles "suggestions"; this repo's hooks handle "enforcement." They're meant to work together, not as an either-or choice.

---

## License

MIT — meaning you can take it, use it, modify it, and sell it, freely, without paying me or asking permission.

A few pieces here are adapted from other people's work; the original authors and sources are listed in the `NOTICE` file. If you redistribute or reuse this, keep that file attached — it's the one thing MIT actually requires of you.

---

## One thing to keep in mind

Before you install any of this, have the AI read each script out loud to you, or at minimum have it explain what each one does.

These tools intercept what the AI is allowed to do, and that affects everything you work on afterward. That's true of this folder, and it's true of any package of scripts you find anywhere online. Don't install something just because it looks convenient.

---

## That's everything here

Everything above can be used on its own — none of it depends on anything else.

But the judgment call of "what should become an interceptor hook, what belongs in a rules file, and what should become a skill" — that's a separate thing entirely. I've written up that decision method, along with the mistakes I've made along the way, into a paid resource pack:

<https://www.agentcrew.cc/products/harness-asset-pack>

Other courses and tools live at <https://www.agentcrew.cc>.

The free stuff here won't expire, and it won't ever get pulled and turned into a paid product later. Use it freely.
