# Install instructions for the AI assistant

If you're reading this file, someone has handed you this repo and asked you to install it for them.

## First, know who you're talking to

**Assume the other person can't code.** They probably just pasted a URL and said "install this for me." They don't know what a hook is, what JSON is, what an environment variable is — and they shouldn't need to.

So:

- Don't throw jargon at them. If you have to use a term, explain it in plain language first.
- Don't ask them to edit config files themselves. You edit them, and then tell them what you changed.
- Don't install four or five things and then report back all at once. Install one thing, say one sentence — "this one's installed, here's what it does" — then ask if they want to keep going.
- If they say "whatever you think" or "your call," make the call. Don't keep pressing for details. They handed you the decision.

If the person is clearly an engineer (they've used technical terms, asked implementation questions), switch to a normal technical conversation — none of the above applies.

## Ask three things before you install anything

Ask all three at once, not one at a time:

1. **What do you mainly use your computer for?** Coding, writing/note-taking, or both. This decides which pieces to install.
2. **Has AI ever told you "I'm done" when it wasn't?** If yes, claim-guard is the one they need most.
3. **Do you care if AI puts emoji in your documents?** If not, skip no-emoji-guard so it doesn't annoy them later.

## Check before you start installing

All four hooks need a small tool called `jq` (used to read data). Check whether it's already there:

```bash
which jq
```

If it's missing, on a Mac install it with:

```bash
brew install jq
```

If `brew` itself isn't installed, don't jump straight into telling them to install Homebrew — that's a big undertaking for a non-technical user. Just tell them about it, ask if they want to deal with it now, or install only the pieces that don't need `jq` (the skills don't need it).

## Installation steps

### hooks (four hooks: three interceptors, one recorder)

1. Copy the script files from `hooks/<tool-name>/**claude-code**/` into `~/.claude/hooks/`, **placed flat at the top level of that folder — don't preserve the subfolder structure from here.** Make sure you take the `claude-code/` copy, not the `codex/` one — the logic is the same but the interface code is different, and using the wrong one just won't run.
2. Make them executable: `chmod +x ~/.claude/hooks/<filename>`
3. Register them in `~/.claude/settings.json`. Use `settings-example.json` as the reference for the format.

**Registration is where things most often go wrong — watch for two things:**

- Their `settings.json` probably already has content in it. **Merge** the new entries in — don't overwrite the whole file. Overwriting will break their existing settings.
- Back up the file before you touch it, and after editing, verify the JSON is still valid with `python3 -c "import json;json.load(open('...'))"`. If the JSON is broken, Claude Code won't start — a disaster for a non-technical user.

The two claim-guard scripts have to be installed **together**. Install only one and the feature silently stops working, with no error message — the user will think they're protected when they're not.

`write-manifest` never blocks anything; it only matters once they also install `checkpoint` (lite mode needs it) or run more than one AI session against the same project.
Neither applies? Skip it, and say so.

### skills (ten ready-made skills)

Copy into `~/.claude/skills/`, keeping each one's own folder. No registration needed — drop them in and they work.

review-loop comes with a script and a template; copy the whole thing, not just SKILL.md. After installing, update the path in SKILL.md's "commands" section to match their actual install location, and run `bash skills/review-loop/examples/regression/run-test.sh` for them to watch (it should show 10 passed, 0 failed), explaining what it's testing as you go. If they don't have a "repeatedly revise a long document" need, this one can be skipped.

checkpoint and neat-freak need to be tuned to match how the user actually organizes their own files. After installing, ask where they usually keep their notes and projects, then help them edit the table in `skills/neat-freak/references/sync-matrix.md`. If they can't answer that right now, skip it for the moment — those two skills won't break without the tuning, they'll just produce inaccurate reconciliation results.
checkpoint's lite mode also needs the `write-manifest` hook above — flag that if it was skipped.

explain, polite, first-principles, info-diet, asd-ste100, iso-24495, and phantom-pushback work as-is — no tuning needed.

### claude-md-template (rules file template)

This one gets **merged**, not copied, which makes it different from the other two categories:

1. First check whether they already have a `~/.claude/CLAUDE.md`. **If they do, never overwrite it** — read through the template section by section and ask "does this apply to you," and only merge in the sections that do, checking each time whether their existing file already says the same thing (a rule should only exist once — two copies dilute each other). If they don't have one yet, copy the whole template over.
2. The template has blanks (＿＿＿) you should fill in with them on the spot: who they are, what they do, what language to reply in, their time zone. Leaving them blank means it isn't really installed.
3. For the "background" section, ask one more question: "is there anything you judge by, or prefer, that AI can't guess — but would trip you up if it guessed wrong?" Turn what they say into one or two lines and add it. If they can't think of anything, leave it blank for now and add it later when it comes up.
4. The three files in `rules/` are optional — ask about each one individually. For the ones they want, copy into `~/.claude/rules/`; if a file with the same name already exists, merge instead of overwrite, same as step 1.
5. Remind them: this template is maintained by **subtraction** — every time you're tempted to add a line later, ask "would AI get this wrong without this line?" If not, don't add it.

### One thing you must say once installation is done

**"You need to fully quit and restart Claude Code for what you just installed to take effect."**

These interceptor hooks only load at startup. Not restarting means it isn't actually installed, and the user will think it is. Say this clearly, and make sure it lands.

## If the user changes their mind

Some people find it annoying once it's installed and blocking things. That's completely normal. To remove it:

- To disable just one temporarily: delete that section from `~/.claude/settings.json` and restart. The script files can stay where they are.
- To remove everything: delete the relevant sections from `settings.json`, then delete the corresponding files under `~/.claude/hooks/` and `~/.claude/skills/`.

Don't try to talk them out of removing it just because they want to. It's their computer.

## Things to watch for yourself

- **Never claim something is installed without verifying it.** The entire point of this package is "don't trust a completion claim with no evidence" — you especially can't be the one who violates that. After copying, confirm the files are actually there. After editing JSON, confirm it's still valid.
- **Read every file yourself before you copy it.** These are scripts that intercept tool calls — you're installing something that will affect all of someone else's future work.
- If something goes wrong, say so plainly. If you get stuck partway through, say exactly where you're stuck — don't skip past it and keep installing the next thing.
