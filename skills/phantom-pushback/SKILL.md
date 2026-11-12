---
name: phantom-pushback
description: "Use when a reply or document carries caveats that attribute a belief, assumption, expectation, or worry to the reader ('you may be assuming...', 'one honest caveat...', 'this plan treats X as...') and each one needs checking against what was actually said or written — typically a closing paragraph that argues with something nobody wrote. Triggers: phantom pushback, invented objection, strawman caveat, manufactured disagreement, it's arguing with something I never said, why does it always end with 'one thing I'd push back on', audit this for invented assumptions. Not for removing real disagreement — see Boundaries."
version: 0.2.0
---

# Phantom Pushback

A **phantom pushback** is a passage that disagrees with a position nobody took. The writer needs to close on a note of independent judgment, has nothing genuine to disagree with, and so invents a belief, attributes it to someone, and corrects it.

It is a normal failure mode of instruction-tuned models, and it survives most editing passes because the passage looks like good writing: it has a viewpoint, it has structure, it is not sycophantic. Only a reader who knows what they actually said can tell that its target does not exist.

Typical shape:

> You asked to change the payment terms to two installments.
>
> Done. **One thing I'd gently push back on: you may be assuming installments are always friendlier to cash flow, but they push out your receipt date and widen the window for non-payment.**

The reader never said installments were friendlier to cash flow. They asked for an edit. The belief was manufactured to fill the slot.

## What this is not

Three neighboring problems get confused with this one. Fixing the wrong one makes this one worse.

| Problem | What it is | Why the fix differs |
|---|---|---|
| Verbosity | Too many words for the content | A length rule cuts it. Phantom pushback survives a length rule, because the passage carries apparent content. |
| Sycophancy | Agreeing with everything, praising the input | The usual fix — "always give the strongest counterargument" — **causes** phantom pushback. See Interaction With Anti-Sycophancy Rules. |
| Real disagreement, badly placed | A genuine objection buried in a closing caveat | The fix is to move it to the top and state it plainly, not to delete it. |

## The Test

For any passage that attributes a belief to a person — what they think, assume, expect, want, or worry about — ask one question:

**Can you point at material that person produced, which they would recognize as stating this?**

Two sources count:

1. **Their words** — anywhere in the conversation or document, not only the last few turns. A position stated early and later contradicted is still sourced.
2. **Their artifact** — code, plan, spec, or draft they wrote. A belief evidenced by their own work is sourced even when they never said it aloud. Reply text asserting "you seem to be relying on MD5 being adequate for passwords" is sourced if their code calls MD5.

What does not count: inference from tone, from their situation, or from what a person in their position would plausibly believe. That is the line — **invention, not literal wording**.

- **Can point at it** — sourced. Keep it. Disagreeing with something the reader actually holds is the job.
- **Cannot point at it** — apply one of the three outcomes below.

**Third parties count too.** "Your client may be assuming the installment plan protects them" is the same move aimed at an absent person, and it is worse because the reader may relay it. It is sourced only if the record contains the reader reporting that belief.

## The discriminator

The most useful separation between a phantom pushback and real criticism: **what is the target?**

- Target is a **property of the artifact** — this query has no index, this endpoint is not idempotent, this clause has no termination date. Not a belief claim. It needs no quotation from anyone, because the artifact is the source.
- Target is a **belief held by a person** — "you may be assuming", "you might be worried", "it sounds like you want". The Test applies.

A reviewer who forgets this strips out legitimate technical criticism and leaves the manufactured part intact, because the manufactured part is the one that sounds considerate.

**Two ways artifact-framing hides a phantom.** Do not treat the artifact side as an automatic exemption.

1. **Laundered attribution.** "This plan treats the migration as reversible", "your approach assumes idempotency", "the schedule expects two weeks of slack" are belief claims about the artifact's author, who is usually the reader. Run the Test on them, sourcing from the artifact's own text.
2. **Referent-free artifact claims.** A real objection can name what it responds to: a line, a number, a clause. A claim about an artifact that points at nothing specific is a candidate, not an exemption. Locate the referent in the artifact or treat the claim as unsourced.

## Signature phrasings

These openers are where the behavior lives. Their presence triggers the Test; it is not a verdict, since each has a legitimate use when the target is sourced.

English: "One thing I'd gently push back on" / "One honest caveat" / "My honest take is" / "It's worth noting that you may be" / "I want to flag a tension" / "To be clear, I'm not saying" / "You might be thinking" / "This may feel like X, but".

Traditional Chinese: 「不過有一點我想溫和地提出」／「必須誠實說」／「你可能會覺得……但實際上」／「值得留意的是，你或許」／「這裡有個張力想指出」.

These are language-specific examples, not a closed list. In any other language, scan directly for belief-attribution clauses rather than for wording.

Two structural tells, independent of wording:

1. **Position in the text.** Phantom pushbacks cluster in the final paragraph. This carries real signal in a document, where a real objection appears next to the thing it objects to. It carries little signal in a short chat reply, where the work is delivered first and a genuine objection also lands at the end.
2. **Absence of a referent.** A real objection can name what it responds to. A phantom one describes a mental state instead, because there is nothing on the page to point at.

## Three outcomes

When the Test fails, pick one by this rule:

Rows are ordered. Apply the first that matches.

| Outcome | When |
|---|---|
| **Promote** | Acting on the request as delivered causes concrete harm the reader has not accepted. |
| **Re-attribute** | The fact changes how the delivered work behaves or how it should be used. |
| **Cut** | The fact is true but concerns something the request never touched. |

1. **Cut.** The passage exists only to fill the closing slot. Delete it. Do not soften it, hedge it, or relocate it to a footnote. A reply that ends on its result is complete.
2. **Re-attribute.** Strip the attribution and state the point as a fact about the work, keeping the strength of any hedge — turning "may be slower" into "is slower" is a different claim, not a re-attribution: "you may be expecting this to help across the board, but it only helps above 50 MB" becomes "It reduces memory only for files above 50 MB." **The re-attributed sentence may contain only material already present in the passage or the record.** If stating it as a fact requires a number, cause, or mechanism the text does not supply, cut instead — inventing one is the same fabrication this skill removes.
3. **Promote.** Move the objection to the top, state it directly, and name its actual target. Do not soften it to compensate for having moved it.

## Two Modes

**Self-check** — run against your own draft before sending. Scan the closing paragraph and every belief attribution, apply the Test, apply the outcome, send the corrected text with no report that the check ran. This mode does not fire on its own; it runs when something invokes the skill — a standing instruction in CLAUDE.md, a hook, or the user asking for it directly.

**Review** — run against a supplied text with the conversation or source artifact available. Every candidate gets classified and reported.

Review mode requires the source record. Without the conversation or artifact that produced the text, "nobody said this" is unverifiable, and the honest answer is that classification is not possible. Say that instead of guessing.

## Process

1. **Locate candidates.** Scan for the signature phrasings, then for every clause attributing a belief to any person — the reader or a third party. The phrasings are not exhaustive and the behavior does not require them. Include artifact-framed attributions ("this plan assumes", "your approach treats X as").
2. **Separate artifact claims.** A claim that attributes no belief and asserts a property of the artifact, naming the specific line, number, or clause it responds to, is not a candidate; leave it alone. Belief attributions from step 1 never exit here, whatever they name. A claim with no locatable referent stays on the list.
3. **Search the record.** For each candidate, look for the person's own words, or their own artifact, evidencing the attributed position. Search the whole conversation and the full artifact.
4. **Classify.**
   - **Sourced** — quotable in their words. Keep unchanged.
   - **Implied** — not stated, but evidenced by their own artifact. Keep, and name the evidence so the reader can check it.
   - **Generalizable** — unsourced as a belief, but true and useful independent of who holds it. Re-attribute, and point at what makes it true: the record, the artifact, or the passage's own unhedged content. A passage whose only content is a hedged perception establishes no fact and is cut, not re-attributed.
   - **Phantom** — unsourced, and interesting only as a correction of this person. Cut.
   - **Misattributed objection** — unsourced belief-framing wrapped around a real objection. Promote. The phantom part is the wrapper, not the objection.
5. **Apply the outcome** and reread the result. A text that has had its closing caveat removed usually needs no replacement ending. Resist writing one.
6. **Report** according to Output Format.

## Interaction With Anti-Sycophancy Rules

Rules of the form "always give the strongest counterargument", "never affirm the user's premise", "never apologize for disagreeing" are a known cause of this behavior. They make disagreement mandatory per response, so when a response has nothing to disagree with, the only way to comply is to invent something.

If an audit finds a high rate in one context, check that context's standing instructions before treating it as a model problem. The fix is to make disagreement **permitted and unhedged** rather than **required**: remove the per-response quota, keep the licence to object.

The inverse rule is equally wrong. "Never push back" produces agreement with broken plans. What this skill enforces is neither quota nor prohibition: **object when there is something to object to, and stop when there is not.**

## Output Format

**Self-check mode: the corrected text, nothing else.** No announcement that the check ran, no count, no summary of what was removed.

**Review mode: one table, then the corrected text.**

```markdown
| Passage | Attributed position | Verdict | Action |
|---|---|---|---|
| "you may be assuming installments are friendlier to cash flow" | reader believes installments help cash flow | Phantom — nothing in the record states it | Cut |
| "you mentioned wanting this shipped before the audit" | reader wants it before the audit | Sourced — turn 3, "has to be in before the auditors come" | Keep |
| "you seem to treat env vars as a security boundary" | reader believes env vars are a boundary | Implied — their config stores the API key there | Keep, name the evidence |
| "the parser only helps for files above 50 MB, though you may be expecting it everywhere" | reader expects it to help everywhere | Generalizable — the threshold is stated in the passage | Re-attribute: "It reduces memory only above 50 MB." |
| "you may be assuming retries are harmless here" | reader believes retries are safe | Misattributed objection — the endpoint is not idempotent | Promote |
```

When nothing fires, say so in one line. Do not manufacture a finding to justify the pass — that failure mode is the one this skill is named after.

## Worked examples

**Cut.** The request touched the config format; nothing in it touched security.

> Before: I've updated the config. One honest caveat: you might be treating environment variables as a security boundary, but anyone with shell access can read them.
>
> After: I've updated the config.

**Re-attribute.** The 50 MB threshold is in the original passage, so it survives; the expectation attributed to the reader does not. Nothing is added.

> Before: Switched to the streaming parser. I want to flag a tension: you may be expecting this to reduce memory usage across the board, but it only helps for files above about 50 MB.
>
> After: Switched to the streaming parser. It reduces memory usage only for files above about 50 MB.

**Promote.** Shipping the requested change as delivered can double-charge a customer. That is concrete harm the reader has not accepted, so the objection leads.

> Before: Added the retry loop as requested. One thing I'd gently push back on: you may be assuming retries are harmless here, but this endpoint is not idempotent, so a retry can double-charge.
>
> After: Added the retry loop, but it is not safe to ship — this endpoint is not idempotent, so a retry can double-charge. The loop is in place if you still want it after that.

**No action, sourced.** Quotable, so it stays.

> You said earlier you wanted to keep the sync version around for the CLI. That conflicts with removing the sync entry point in step 3.

**No action, artifact claim with a referent.** No belief is attributed to anyone; the referent is nameable.

> The `charge()` call in step 3 has no idempotency key, so the retry path can bill twice.

## Boundaries

**Will:**
- Find passages attributing a belief to any person and check each against that person's words or their own artifact.
- Cut invented ones, keep sourced and implied ones, preserve useful content by re-attributing it, and promote real objections out of closing caveats.
- Name the evidence when it keeps an implied attribution, so the reader can check the call.
- Say when the source record is missing and classification is therefore not possible.

**Will not:**
- Remove disagreement that has a real target. Criticism of code, plans, numbers, or reasoning stays, however it is phrased.
- Add a fact while re-attributing. If the point needs a number, cause, or mechanism the text does not contain, it cuts instead.
- Soften a promoted objection to compensate for having moved it.
- Treat a signature phrasing as sufficient evidence, or treat artifact framing as an automatic exemption. The Test is the record.
- Classify a position as phantom because the person implied rather than stated it. An implication their own words or artifact carries is sourced; the line is invention, not literal wording.
- Require a closing caveat, or supply a replacement ending for one it removed.
- Convert an audit into a rewrite. It touches the flagged passages and leaves everything else as written.
- Verify a belief attribution when the conversation or artifact that would source it is unavailable. It reports that limit rather than guessing.
