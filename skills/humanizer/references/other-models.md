# Drafts from GPT (Codex) or Gemini

Load this only when the draft came from Codex, another GPT model, or a Gemini model. Each row is what that model's own vendor says its release does at the sentence level. Use it as a checklist for that draft, never to guess from the prose which model wrote it (reading is not a reliable classifier). The rows apply to non-fiction text.

Source: Nanako0129/sepia, model-fingerprints reference (MIT), quoting OpenAI and Google prompting guides as re-read 2026-09-23.

## GPT-6 Astra (and other GPT-6 releases as a weaker prior)

- **Heavy formatting by default**: "tends to use lists, tables and Markdown to make responses scannable." Turn a list back into paragraphs unless the items are truly parallel or sequential.
- **Recurring phrases**, named by OpenAI's own instruction, verbatim:

```text
Avoid using slop words or phrases like "Bottom Line:" in conclusions, "delve," "foster," "leverage," "it's worth noting," "importantly," "Question? Answer." or "This isn't about X. It's about Y.", "genuinely" or hyphenated compound descriptions and adjectives. Do not use concluding summary statements such as "In short:..", "The simplest mental model is:...".

State the intended action directly. Avoid adding what you won't do, what will remain unchanged, or how you'll separate or categorize results. Do not use contrastive framing such as "X, not Y" or "X—not Y" that introduces an unprompted alternative that the user didn't ask about. Avoid invented compound labels like "exact-head checks" and "editorial-row layouts", vague qualifiers, and canned transitions; use plain verbs and prepositions to state the actual relationship directly.
```

- In Chinese drafts the same habits show as: 自問自答（「為什麼？因為……」）、沒人問的對比（「是 X，不是 Y」）、結尾標籤（「總結：」「一句話說：」）、沒人要求的「以下不會改動……」、生造的複合標籤。

## GPT-5.6

- **Too brief in both directions**: more concise than GPT-5.5, and brevity instructions can make it drop a required caveat or the next action. Check that nothing needed was cut.
- **Expected residue** the vendor tells users to trim: introductions, repetition, generic reassurance, optional background, generic praise, sign-offs.
- **Editing drift**: the vendor warns against "adding new claims, sections, or a more promotional tone" when editing. Compare against the source for added claims and a more promotional register.

## Gemini 3 and 3.1 (Gemini 3.5 / 3.8 as a weaker prior)

- **Terse by default**: "By default, Gemini 3 is less verbose and prefers providing direct, efficient answers." Brevity is not evidence of a human here. Check the other direction: caveats and next steps dropped for efficiency.
