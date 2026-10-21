---
name: first-principles
description: "First-principles decomposition: ask whether the requirement should exist, strip to ground truths, rebuild the minimal solution. Triggers: first principles, first principles rethink, reason from the ground up, why should this be done this way, blind spots, unknowns inventory."
version: 0.4.0
---

# First Principles Thinking

Decompose a decision into facts that cannot be reduced further, then reason upward from them, instead of "everyone does it this way" or "we've always done it this way." Customized from awesome-skills/first-principles-skill; Phase 0 (Delete First) was added per Elon Musk's requirement-questioning mantra.

> **Explore-unknowns mode**: when the requirement is ambiguous or the domain is unfamiliar and you need to inventory the "known unknowns / unknown unknowns" four quadrants first, read [references/explore-unknowns/guide.md](references/explore-unknowns/guide.md) instead (its own references/ live in the same directory). Come back to this file for the decomposition once the unknowns are mapped.

## When to Use This Skill

- An architecture, practice, or "best practice" looks reasonable but nobody has asked why
- The current solution keeps feeling wrong and swapping approaches does not help
- Foundational decisions with long-term impact (pricing structure, service packages, system boundaries)
- Suspicion that a step or requirement should not exist at all

Not for everyday small decisions or work that already has a clear spec. The decomposition costs time; reserve it for choices that are expensive to get wrong.

## Core Process

### Phase 0: Question the Requirement Itself (Delete First)

**Opening move**: before analyzing *how* to solve something, ask whether this requirement/step/feature should exist at all. If it can be deleted, delete it — don't optimize something that shouldn't exist in the first place. If deleting it actually breaks something, add it back.

Elon Musk's mantra: "All requirements are dumb to some degree." The stupidest thing is to optimize something that shouldn't exist.

1. Try to delete the requirement entirely. Can the system work without this step?
2. If it can be deleted, delete it. Don't optimize what should be removed.
3. If deletion fails, add it back, and only then analyze.
4. Challenge who owns the requirement. Requirements from smart people are the most dangerous because you're least likely to question them. Ask: can the person who imposed it waive it?

Red flags: "We've always had this step," "Legal/compliance requires it" (verify, often outdated), "Users expect it" (asked them recently?), "It's in the spec" (who wrote it, and why?).

### Phase 1: Identify the Problem's Essence

Strip away implementation details. What exactly needs to be solved? Is this the cause or a symptom? What would be different once it is solved? If this system didn't exist, what would the user actually need?

### Phase 2: Challenge All Assumptions

List the explicit assumptions, then surface the implicit ones (conventions everyone follows without saying). For each: is this a real constraint, or just how it's always been done?

| Category | Question to Ask |
|----------|----------------|
| Technical | "Must we use this technology/pattern?" |
| Business | "Is this requirement actually fixed?" |
| Resource | "Are these constraints real or perceived?" |
| Historical | "Why was this decision made originally? Does that condition still hold?" |

Red flags: "We've always done it this way," "Industry standard says...," "Everyone uses X," "That's too simple to work."

### Phase 3: Establish Ground Truths

Keep only what cannot be decomposed further and whose violation guarantees failure. For client-facing or business decisions, ground truths usually fall into one of four kinds:

- **Contracts and commitments**: what was signed, what was promised to whom
- **Cash flow**: what was actually received, when, and who deducted what
- **The other party's own words**: what they said they want or don't want (transcripts, emails), not your paraphrase
- **Time and people**: real available hours, dates, who can actually be there

Test each: can it be decomposed further? Is it provable, or merely believed? Would violating it definitely cause failure?

### Phase 4: Reason Upward

Write the minimal solution first: the simplest thing that satisfies the ground truths and nothing more. Then add layers one at a time; each addition must justify itself.

```
Ground Truth → Minimal Solution → Justified Additions → Final Design
     ↑              ↑                    ↑
  (proven)     (sufficient)        (each defended)
```

### Phase 5: Validate the Reasoning

Can every design decision be traced to a ground truth? Where does the reasoning still rest on an assumption? What would break this solution?

## Output Format

Keep all five sections — that's what makes the output scannable at a glance. Write them in the reader's language and in plain words: no field labels like "Verdict" or "Trade-offs acknowledged," sentences instead of slots. Use a table for assumptions only when there are more than three.

```markdown
## First-Principles Decomposition: <topic>

### 0. Should this exist at all
What was tried to delete, what happened, and the verdict — keep or cut. One to three sentences.

### 1. The real problem
One sentence for the core problem, one sentence for what changes once it's solved.

### 2. Assumptions challenged
For each: what it is, why it was doubted, and whether it survived. Use a table only if there are more than three.

### 3. Ground truths
Three to five, each tagged with its kind (contract / cash flow / the other party's own words / time & people).

### 4. The solution built from those truths
What the minimal solution looks like; which layers were added on top, and why each one earned its place.

### 5. Conclusion
The recommendation, the single most important finding from this decomposition, and what tradeoff was accepted to get there. One to two sentences each.
```

## Common Patterns

- **The Complexity Trap**: the solution is more complex than the problem. Remove one component; does the core still work? If yes, that component wasn't essential. Repeat until removal breaks it.
- **The Analogy Trap**: "Company X does it this way." What problem were they actually solving? Are our constraints the same in every relevant dimension?
- **The Legacy Trap**: maintaining compatibility with decisions that no longer serve us. Why was it decided? Do those conditions still exist? What is the true cost of change versus the cost of keeping it?

## Additional Resources

- `references/elon-musk-examples.md`: real-world examples from SpaceX and Tesla
- `references/software-examples.md`: software engineering applications
- `examples/architecture-review.md`: a full first-principles analysis of a microservices decision
