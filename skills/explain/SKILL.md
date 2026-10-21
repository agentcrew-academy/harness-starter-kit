---
name: explain
description: "Re-explain the previous reply or a specified topic in plain language a high-schooler could follow, no jargon. Triggers: /explain, plain English, I don't get it, ELI5, too much jargon."
---

# Explain — Say It So a Layperson Gets It

When someone types `/explain` (with or without a topic), **re-explain** the subject to a standard of "**a high-schooler with no background in this could follow it right away**."

## What to explain

- **No topic given** (just `/explain`): explain **my own previous reply** — whatever the user didn't follow is that.
- **Topic given** (`/explain how the quote was calculated`): explain that specific thing.
- **File path given** (`/explain <file path>`): read that file first, then re-explain it following the rules below.
- If it's unclear which part is meant, pick the part the user is most likely stuck on, and open with "I'm guessing you mean X — let me know if that's not it."

## Document mode: if you have a way to delegate to another model, prefer that when the target is a file path

Skip this section when the target is **the previous reply** or an **abstract topic** with no matching file — a separate process can't see this conversation.

It only applies when the target is a **specific file path**:

1. This assumes you have some CLI tool that can run a headless prompt against another model and read a local file by absolute path (this section was originally written around `agy`, a wrapper for Google's Antigravity CLI — swap in whatever equivalent tool you actually have, or skip this entirely if you don't have one).
2. If you do, call it with a prompt that pastes in the full "Hard rules" section below verbatim (the other process can't see this file, so it needs the whole ruleset spelled out), plus the absolute path to read. For example:
   ```
   Re-explain this document in plain [language] a high-schooler could follow. Rules:
   1. No mixing languages; a genuinely untranslatable term can stay in the
      original, with a parenthetical plain-language explanation the first
      time it appears.
   2. No jargon, no abbreviations.
   3. Short sentences, one idea each.
   4. Lean on comparisons and everyday examples.
   5. Lead with the conclusion / what it means for the reader, details after.
   6. Say less and say it clearly -- don't cram in every detail.
   Structure: one-sentence summary -> plain-language breakdown (2-4 points) ->
   what it means for you -> a closing offer to go deeper if they want it.
   Read this file: <absolute path>
   ```
3. **Fall back to writing it yourself** (never hand over a rule-violating output as-is) whenever any of these hold:
   - the tool isn't installed / command not found
   - non-zero exit code, timeout, or empty output
   - the output still breaks a "Hard rules" item below (mixed languages without a parenthetical, untranslated jargon, and so on)
4. Whether the draft came from the tool or you wrote it yourself, always run the "Self-check" below before sending it.

This is optional acceleration, not a requirement — everything else in this file works the same with or without a second CLI in the loop.

## Hard rules (breaking these means the explanation failed)

1. **Reply in the language the user is using, and re-explain it in plain language a high-schooler could follow — no jargon.**
   - If a technical term genuinely has no good equivalent, or the original term is actually clearer than any translation (e.g., API, SaaS, PDF), you can keep the original term — but **immediately follow it with a plain-language explanation in parentheses** the first time it appears. Example: "API (a way for two pieces of software to talk to each other)."
   - Only explain it the first time it shows up; after that you can use it directly.
   - Don't drop jargon like "SOW," "addendum," "roster," "pipeline," or "enterprise" without explaining it — either use an everyday word instead, or add a parenthetical explanation.
   - Names of people and companies are the exception: keep them exactly as written. Don't translate, transliterate, or add titles ("John" stays "John", not "Manager John"); a changed name no longer matches the person the reader knows.
2. **No jargon, no abbreviations.** Say "spreadsheet" instead of "workbook file," say "pay part of it upfront" instead of "remit an initial installment."
3. **Short sentences.** One idea per sentence — don't cram three concepts into one sentence.
4. **Use comparisons and everyday examples.** Give an everyday analogy before anything abstract ("it's like...").
5. **Lead with the conclusion / what it means for the reader**, then the details. What the user wants to know first is "what does this mean for me — good news or bad."
6. **Don't pile on information.** Say less and say it clearly, rather than cramming in every detail. When something doesn't land, the usual cause is "too much," not "too little."
7. **No emoji by default** (unless the existing conversation is already using them).

## Suggested structure (adapt freely — not every explanation needs all four)

1. **One-sentence summary**: what this actually is / what happened.
2. **Plain-language breakdown**: 2–4 points, each with a comparison or example.
3. **What it means for you**: good news or bad, whether you need to do anything, whether it costs money, any risk.
4. **Going deeper**: if there's a more detailed layer, cover it briefly in a last short section so the reader can choose to read on. Don't end by asking "want me to go on?" — finish the explanation in one reply.

## Self-check (run through before sending)

- Any jargon or foreign-language term left unexplained? → Fix it. (Names of people and companies don't count; changing a name is the error.)
- Any sentence that requires understanding another term first? → Break it apart and explain that first.
- Could a high-schooler read this and repeat it back in their own words? → If not, simplify further.

## Before / after example

**Before (fails the bar)**:
> I converted the SOW Addendum to a PDF and sent it to Sho — it's the quotation for the recorded course, with the fee folded into the Stage 2 balance.

**After (passes the bar)**:
> I put together a supplementary contract for you, saved it as a file that's ready to print and sign, and sent it to your client Sho.
> It's about a pre-recorded online course you're offering him as an add-on — the document just spells out how much that course costs.
> He won't be billed separately for it; it gets added to the balance he still owes from before.
