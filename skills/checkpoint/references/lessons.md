# Lessons: turn the user's corrections into better rules

Run this at closure, or whenever the user asks mid-conversation to "review the corrections I made." The main thread does it itself, because a delegated worker can't see the conversation.

## Whether to run it (any one is enough; lite mode too)

- The user corrected the same piece of work 2 or more times (including having it rejected or being interrupted so you'd change course).
- A deliverable going to other people went through 2 or more review rounds, in text or by voice.
- The user showed the right way themselves (wrote the reply themselves, dictated how it should read).
- The user said something like "review my corrections," "fix the rules," or "update the spec."
- The user ruled item by item on a list of open questions, and some of those rulings generalize. Log them as in step 3; promote them as in step 5, into the rule file that already covers that area, not a separate table of precedents.

None of these → write `lessons: none` and stop. A one-off ruling about one person or one client is not a trigger.

## Steps

1. **Collect the corrections.** If the conversation was compacted, have a read-only subagent read the full transcript and pull out the user's own words; don't rely on a summary. Also read any review recordings or meeting transcripts from this session: the heaviest corrections are often spoken, not typed.
2. **Find where each wrong output came from.** For each correction, find the rule, template, or example that led the model to write it that way, cite `path:line`, and label it as one of:
   - the rule doesn't exist
   - the rule exists but points the wrong way, or is worded so that it gets misread
   - the rule exists and the model didn't follow it

   If a rule points the wrong way, fix that rule itself. Don't write a separate memory note or patch to paper over it: a rule that was wrong at the source will cause the same mistake again. If the model just didn't follow a correct rule, you usually don't need to change the rule; say so honestly in the report.
3. **Keep one-off rulings apart from rules that generalize.** A one-off ruling stays in that case's own file. A correction that might generalize goes into a mistakes log first, not straight into a skill or rule file.
   - The mistakes log is a feedback note in your memory folder. First grep it for the same kind of entry using 2 or 3 keywords. Found one → append a line at the end, `Seen: YYYY-MM-DD (case name)`. Keep the existing `Seen` lines as they are, because overwriting them loses the count; when you're back-filling, write the date it actually happened. None found → start a new entry: the rule in one sentence, a **Why:** line, a **How to apply:** line, and a final `Seen:` line. Keep the quoted words and the story of what happened in the conversation record; don't copy them in.
   - **Promotion threshold: `Seen` on 2 different days, or the user says it's a general rule.** Then go to step 4 and turn it into a proper rule in a skill or rule file. Choose the layer using the questions below. Once promoted, delete the log entry and its index line so there aren't two copies.
   - Exception: if step 2 found "the rule points the wrong way," skip the count and go straight to step 4. That is a defect in the rule, not a pattern still being watched.
4. **Propose first; change nothing until the user approves.** The proposal covers only two things: entries that reached the promotion threshold, and rules whose source is wrong. Write it as a table the user can strike rows from: the correction in their words → the source and its state (`path:line`) → how to change it → where it lands. Add a final row listing what you are not changing and why. Entries newly logged but still below the threshold stay out of the proposal; list them in the report.
5. **After approval, apply it.** Before writing, grep the old wording of the same topic (see question 5 below). If it exists, change or delete it. After changing a project's rules, run that project's own lint or check, if it has one. Then commit, and continue with the rest of the checkpoint.

## Five quick questions for placing a rule

1. **How many projects does it affect?** All of them → your global instructions or a shared skill. One → that project's instruction file or memory. A trap specific to one project's API → that project's "common mistakes" section.
2. **Rule or fact?** Rules, procedures and prohibitions go in the instruction file; facts, fixes and technical findings go in a skill or a memory topic file. Temporary session state isn't recorded anywhere.
3. **How strong a guard?** Take the highest one you can actually build: (1) make the mistake impossible (one source of truth, delete the old path that keeps getting copied); (2) a hook or lint that blocks it, with an error message that names the file or command to use instead; (3) a test or check script; (4) only then, a sentence in a rule file, and only for things that need judgment. Before a new hook or lint goes live, feed it the real command or wording from the incident and confirm it would have blocked it. A rule that already exists, with no mechanism enforcing it, and the mistake happens again: go one layer up in the same change.
4. **How long is it?** 1-3 lines → an index line in your memory file; 5 or more lines → its own file, with only a pointer in the index.
5. **Is it already written somewhere?** Before writing, grep 2 or 3 keywords from the new rule across your rules, skills, instruction files, memory and the current project's docs. If an old version exists, change or remove it first, then decide whether you still need a new one. When a new rule overturns an old one, remove the old one in the same change. Adding without removing is how rules drift. If the corrected output was following some rule, fix that rule instead of adding a patch on top.

## Optional: a monthly sweep for mistakes nobody has corrected yet

The steps above only collect mistakes that were corrected. To catch ones made twice but never called out:

1. **Look at the evidence.** Over the last 30 days: reverted commits, `fix(` commits, comments marked workaround / temporary / hack, and the "pitfalls" section of your daily logs.
2. **Only a class that appears twice counts.** Propose raising it a layer as in step 4. Feed any new hook or lint the real commands or wording from both incidents.
3. **Exemptions need a reason and an expiry date.** Lint exemptions, hook allow-markers and "don't block this one for now" notes each get both. Ones with no expiry are listed for the user to decide on during the monthly sweep; none stays permanent by default.

## Report

In the checkpoint report, the `lessons:` line reads: `<n> saved (where), <k> logged as repeat mistakes (Seen count), <m> waiting on you`. When you run this on its own mid-conversation, report with the step-4 proposal table instead.
