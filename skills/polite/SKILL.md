---
name: polite
description: "Three-mode tone rewriting: A Warm & Empathetic (customer service replies, delivering bad news, apologies, reassurance, declining a request; too cold, too blunt, soften it up); B Formal Business (outward-facing emails to an unspecified audience, announcements; too casual, too abrasive, more formal, business tone, more official); C Formal Business + Warmth (the default once there's a specific named recipient — proposals, reschedules, follow-ups, quotes, marketing, declines; reads too haughty, too much like a form letter for someone I actually know)."
allowed-tools:
  - Read
  - Edit
metadata:
  source: Adapted and translated from hardikpthv/agent-skills (MIT)'s empathetic-tone-basic and professional-tone-basic, merged into a single skill. See NOTICE at the repo root.
---

# Polite: Tone Rewriting (Warm & Empathetic / Formal Business / Formal Business + Warmth)

Determine the mode before rewriting. Two shared rules for every mode:

- **Don't invent circumstances or excuses for the other person** (e.g., assuming they "must have been busy lately" as the reason they didn't reply). Deal only with what they actually said or the request itself; invented circumstances read as guilt-tripping.
- **Don't add commitments the draft didn't make.** A rewrite changes tone, not the offer: no new free reviews, extra calls, or "send me your materials and I'll take a look" unless the original draft already offered it.

## Determining the mode

| Signal | Mode |
|---|---|
| "too cold," "too blunt," "soften it up," "more empathy," "make it more reassuring," "this reads as harsh"; customer service replies, bad news, apologies, declining a request, reassurance | **A Warm & Empathetic** |
| "too casual," "this comes off too harsh," "more formal," "business tone," "more official"; an announcement or outward-facing email with no specific recipient in mind | **B Formal Business** |
| Same signals as B, **but there's a specific named recipient** — a proposal, reschedule, quote, follow-up, marketing email, or decline addressed to someone you actually know; "this reads too haughty," "too much like a form letter" | **C Formal Business + Warmth (default for a named recipient)** |

**Neither mode applies to**: spinning the truth so the other person draws the wrong conclusion, manipulative reassurance, legal documents, safety warnings, factual incident reports, or casual chatter in an internal group chat.

## Mode A: Warm & Empathetic

Core principles:

1. **Acknowledge first, then address**: put the feeling or situation ahead of the solution. "That's genuinely frustrating — let's figure this out" beats jumping straight to the fix. Note: only acknowledge circumstances or feelings the other person has actually stated (see the shared rule above).
2. **People before policy**: "I want to help you with this" comes before "per policy."
3. **Validate without judging**: "That makes complete sense" / "It's totally fair to ask that."
4. **Soften commands**: turn "You need to..." into "Whenever it's convenient, you could..."
5. **Use warm, plain words**, lean on "you/we," and keep the reassurance short — a brief warm line beats an elaborate one.
6. **Share the responsibility**: "we dropped the ball on this" beats "an error occurred."
7. **Close with support**: give a next step and leave the door open. "Let me know if anything's unclear."

Technique: the go-to shape is **acknowledge → reassure → help → invite**; turn blame ("you forgot to...") into a neutral statement ("it looks like this step got missed"); turn "no" into a path forward ("I can't do that, but here's something that might work"); keep sentences unhurried and steady, and don't stack up exclamation points.

Before / After:

**Before**: Your application has been denied. You did not follow the required steps.
**After**: Thanks for sending this in — it looks like a couple of steps got missed, so I can't approve it just yet. That said, I can walk you through exactly what's needed, and we'll get it sorted together.

**Before**: This item is out of stock. Please check back later.
**After**: Sorry about this — it's actually out of stock right now, and I know that's disappointing. I can let you know the moment it's back in, or point you toward a similar option in the meantime, whichever works better for you.

Don't overdo it: warmth isn't a pep talk. Avoid empty positivity ("everything happens for a reason!"), fake familiarity, or burying the real answer under soft language. Be considerate, but still say the actual answer clearly.

## Mode B: Formal Business

Core principles:

1. **Formal tone**: cut casual slang; a normal business email can keep natural connecting phrases — it doesn't need to sound stiff in every sentence.
2. **Precise and concise**: replace vague or padded phrasing with specific, direct statements.
3. **Polite and measured**: courteous, neutral, no sarcasm, confident without being pushy (see the shared rule above).
4. **Structured**: state the purpose up front, with clear paragraphs, one point per paragraph.
5. **Clear close**: include a concrete next step and sign off appropriately.
6. **Consistent formatting**: correct forms of address, no all-caps or exclamation-heavy passages, no emotionally charged language.
7. **Lead with yes on conditional requests**: when someone makes a request with a condition or prerequisite attached, give the positive answer first (yes, that works), then frame the prerequisite as something that speeds things up or improves accuracy — not as a gate that blocks them ("can't do it unless..."). This comes up often in business-development or client inquiries: confirm it's doable first, and present the prerequisite as the next action item, not a reason to say no.

Technique: turn a casual opener ("Hey, so...") into a purposeful one ("Following up on..."); replace filler ("kind of," "roughly," "ASAP") with precise wording ("approximately," "by end of day Friday"); rewrite complaints or emotional statements as a neutral fact plus a request; turn "I need X before I can do this" into "If you can get me X first, I can get started right away / be more accurate" — the prerequisite shifts from a limitation into something the other person can proactively do; close with a clear next step and an appropriate sign-off.

Before / After:

**Before**: Hey, so this thing is kind of running late and it's honestly a pain. Can you speed it up??
**After**: Following up to flag that this deliverable is currently behind schedule, which may affect the downstream timeline. Could you provide an updated completion estimate by end of day, please?

**Before**: We crushed it this quarter, numbers are great.
**After**: The team delivered strong results this quarter, with several key metrics exceeding original targets.

**Before**: I can teach this, but you'll need to set me up with an account first or I can't test anything.
**After**: Happy to teach this. One thing that would speed things up considerably — if you could set me up with an account beforehand, I can test it hands-on directly, which will also make the content more relevant to what your team will actually be using.

Don't overdo it: formal doesn't mean bureaucratic. Avoid stacking jargon ("cross-functional synergy alignment deliverables"), unnecessary length, or passive voice so pervasive the sentence loses its subject. The goal is clean and sharp, not corporate-speak.

## Mode C: Formal Business + Warmth (default once there's a specific recipient)

B's skeleton, plus two of A's touches. **B is written for an unspecified audience — used on someone you actually know, it reads as a public announcement**: precise, clean, every sentence moving things forward, but not one line addressed to *them* as a person.

All four of these need to be present. Miss one and it's just B again:

1. **Open by acknowledging what they already did** (borrowed from Mode A's "acknowledge first, then address"). They sent something, put materials together, gave you advance notice, followed through on a commitment — say so in the first sentence. It isn't flattery, it's showing you noticed. A follow-up/reminder email needs this too — acknowledge their last reply or commitment before asking for a status update.
   - "Thanks for laying out exactly where things stand — that makes it much easier for me to plan around."
   - Acknowledge only something tied to this email's business. In a billing, admin, or contract email where they haven't done anything on this matter yet, skip the acknowledgment and open with the topic; praise for unrelated work reads as buttering them up before the invoice.
2. **When they apologize or seem uneasy, actively take the blame off them.** If they say "sorry for the short notice," say plainly there's no need to apologize, and give a real reason.
   - "No need to apologize about the reschedule — knowing early actually makes it easier to plan around."
   - The shared rule at the top of this file still applies here: taking the blame off them is fine, but **don't invent circumstances for them** ("you've probably been busy lately" is off-limits). Only respond to what they actually said.
3. **Soften every request** (borrowed from Mode A's rule 4): "You need to..." becomes "If it works for you, could you...". B's precision stays in the *content*, not the tone. Cap it at two "if you could"s per email — more than that starts to feel sticky.
4. **Close by leaving a way out, and hand control back to them.** After stating the next step, add one line that says it's fine if this doesn't work, then sign off.
   - "If this time doesn't work for you, just let me know and we'll find another slot."
   - A way out is only for something they **already agreed to** (the time, format, or scope of it). For something they haven't agreed to yet (a proposal, quote, pitch, invite, cold outreach), leave the way out off: "if you're not interested, just let me know" hands them a ready-made no. Those emails end at the next step and how to take it.

**Warmth comes from these four moves, not from casual wording.** Every sentence should still read as acceptable in a Mode B letter; if one wouldn't, rewrite it.

**Warmth can't change the facts.** Don't redefine how important something is just to soften the landing (a required deliverable doesn't become "just a nice-to-have"), don't soften a deadline or an amount, and don't turn "must" into "you could consider." Soften the sentence, not the content.

**Plain-text email formatting**: skip `**bold**` and markdown — the asterisks show up literally once sent. Use paragraph breaks and sentence order for emphasis instead. Don't mix full-width and half-width punctuation in the same message.

### Condescension check (run this before sending — the single most common mistake here)

**Two passes, each a full read-through on its own — don't merge them into one pass.** The sentences Pass 2 catches read as clean under Pass 1's test; running only Pass 1 will miss them every time. **Only report the condescension check as done once both passes are actually finished in full** — stopping halfway and calling it done is a false claim, not a shortcut.

#### Pass 1: Bestowing

Test: **does this sentence write the decision as something I'm granting?**

| Condescending | Rewrite |
|---|---|
| Feel free to reply whenever, no rush | This email is open whenever you get to it |
| I can give you a discount | There's a discount available here |
| I'll send you the discount code | Reply to this email and the discount code is yours |
| I'll hold your spot until Friday | You're covered through Friday |
| Let me know if you have questions | Ask anytime if anything's unclear |

Common symptom: **the subject is "I," and the verb is a bestowing one** (let, help, give, allow, hold, notify). Swap the subject to the other person or the thing itself, and the tone flattens out.

#### Pass 2: Presumptuous consideration

Test: **does this sentence describe their mood, willingness, or time pressure for them?**

If so, cut it or rewrite it — no matter how considerate it sounds. This pass is the harder one, because **the sentences it catches pass Pass 1 cleanly**: the subject is the other person, there's no bestowing verb, the tone is gentle — exactly what the rest of the email is supposed to sound like. The problem is the assumption underneath it, which amounts to saying "I've been waiting on you." Three shapes it takes:

| What it presumes about them | Example |
|---|---|
| Willingness | If you don't feel like discussing this right now |
| Burden | No need for a long reply, a line or two is enough |
| Guilt | No need to explain if you haven't started yet |

Fix: **tie the way-out to an objective fact, not their internal state** — "if this time doesn't work" is fine, "if you can't be bothered dealing with it" isn't. When in doubt, cut the sentence entirely — the email won't read as cold for losing it.

### Don't overdo it

Acknowledgment isn't flattery. **Thank them once per thing**, not once per paragraph; don't stack up phrases like "thank you so much for your time amid your busy schedule"; and don't let warmth bury the actual point — state the time, amount, deadline, and the ask as plainly as Mode B would.
