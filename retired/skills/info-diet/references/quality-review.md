# Quality Mode: Judging Whether What They're Taking In Is Any Good

> Only reached after the user gives **separate consent**. Basic mode doesn't look at content.
> This section is the part of the tool closest to the original source material — Clay Johnson's
> whole argument was that "the problem isn't quantity, it's whether you're selecting well," and
> basic mode can measure quantity but not selection.

---

## First, be clear about exactly what's being authorized

Before getting consent, say this plainly, don't hand-wave it:

> **"The numbers so far tell you where your attention went, but they can't tell you whether what
> you looked at was any good — a serious in-depth report and a headline designed to make you
> angry look identical in the numbers.**
>
> **If you want, I can go one step further: look at the actual titles of articles you clicked into
> and read, then talk with you about the quality of what you're taking in.**
>
> **But I need to ask you separately for this one, because a title reveals a lot more than a site
> name does — a site name only tells you they went to some news site, a title tells you what
> specific thing they were paying attention to.**
>
> **Whether you do this part or not is entirely up to you. If you skip it, everything before this
> point stands complete as-is."**

**Don't open this without a clear yes.** Agreeing to the basic analysis earlier does not mean
agreeing to this part too.

---

## What this mode can and can't see

**Can see**: the **article titles** of pages they clicked into and read (only collects "external
intake" visits that click into a single item — feed-layer visits aren't collected).

**Can't see**: article body text. This tool doesn't go online or fetch pages — it only uses
titles the browser has already stored.

**One limitation you have to know about**: **titles on social platforms carry almost no
judgment value.** An X title looks like "Someone (@handle) / X"; Threads and Instagram are
similar. The title only tells you who they were looking at, not what that content said.

So quality judgment needs two different approaches depending on the source:

| Source type | Is the title useful | Look at instead |
|---|---|---|
| News, blogs, newsletters, forums | Useful, read the title directly | the title itself |
| Social platforms (X/Threads/IG) | Not useful | **look at "who they're reading" instead** |

---

## Criterion 1: article-type sources — read the titles

Look for these patterns across the set of titles. **Every point must be traceable to a specific title to be worth saying:**

**1. Emotional intensity.** How many titles are anger, fear, shock, or conflict?
If eight out of ten titles in someone's reading list are designed to make them angry,
that's not information, that's an emotion supply.

Worth quoting Johnson directly here: the media industry discovered that "affirmation sells
better than information" — what people want is "proof that I was right," not "something I didn't know."

**2. Clickbait level.** How much of it is structured like "shocking," "what you didn't know,"
"you have to see this," "roundup"?

**3. Topic breadth.** Is everything clustered around the same subject, or spread wide?
Both extremes can be a problem: too concentrated is an echo chamber, too scattered has no
throughline. **Don't assume which one is correct** — just ask them: "Which one is what you actually want?"

**4. How much of it takes real time.** Is there anything that clearly needs twenty focused
minutes to read? If there's nothing like that at all, that's a finding in itself — their
information intake is entirely fragmented.

---

## Criterion 2: social sources — look at "who they're reading"

Titles aren't useful, but the report has account names, and that itself is a quality signal:

- **Are they reading accounts they chose, or accounts the algorithm pushed at them?**
  The same account showing up repeatedly = they're actively following it; a bunch of
  one-off strangers = the algorithm is feeding them. This maps directly to Johnson's point about
  "choosing before you consume" — actively following is choosing, being fed is not.
- **Pair this with the scroll-without-clicking ratio** (already computed in basic mode):
  a high feed-layer ratio plus scattered accounts = their social intake is almost entirely
  algorithm-determined.

---

## Rules for how to talk about this

**1. No moral judgment.** Entertainment, gossip, binge-watching — label the category and move
on. The problem was never entertainment — it's **mistaking entertainment for learning.** You can
say this directly to the learner.

**2. Don't decide what "good" means for them.** Your job is to point out the pattern and let
them say whether it's what they want. Phrase it as "your reading list has X articles that are
..., is that the ratio you want?" — not "you should read more ..."

**3. Never evaluate political stance.** For political-leaning titles, do exactly two things:
report the **diversity** of viewpoints (are they all from one side), and don't comment on the
stance itself. This is what the original author actually cared about — echo chambers, not which side someone's on.

**4. Treat anything private as unseen.** Even with consent, the authorization covers
"judging information quality," not "interpreting someone's life." Health, relationships,
financial hardship, job-search-related titles — even if some slip through, don't bring them up.

**5. If the sample's too small, say so.** If they have very few single-article clicks to begin
with, titles won't be enough to judge — say "there isn't enough single-article reading in your
data to judge quality — and that absence is itself the answer: you're almost entirely
scrolling, not reading."

---

## Wrap-up

Quality mode's output **doesn't go into the baseline file**, and isn't part of next month's re-check metrics.

Reason: quality is a judgment call, not a measurement. Turning it into a number to track would
turn it into just another "higher is better" score — exactly the thing this tool decided from
the start not to do.
