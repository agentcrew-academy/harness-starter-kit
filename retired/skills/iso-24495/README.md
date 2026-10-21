# ISO 24495 Skill — Plain Language for English and Traditional Chinese

A Claude Code skill that rewrites text into plain language per
[ISO 24495-1:2023](https://www.iso.org/standard/78907.html) — the
international standard that defines plain language by reader outcome: the
intended readers can **find** what they need, **understand** it on first
reading, and **use** it.

Two things make this skill different from a one-line "write plainly" prompt:

1. **It implements the standard's actual structure** — reader-first content
   selection (relevant), document structure (findable), wording
   (understandable), and actionability (usable) — not just shorter sentences.
2. **It ships a real Traditional Chinese technique layer（繁體中文層）.**
   ISO 24495-1 is explicitly language-independent, but as of this release the
   [official translation list](https://www.iplfederation.org/standard-translations/)
   contains no East Asian language at all. The Chinese layer here is an
   original implementation of the four principles for Chinese — targeting the
   problems Chinese text actually has（歐化長句、公文腔、成語堆疊、中英夾雜、
   被字句濫用）, not a translation of the English rules.

## Before / After

| Before | After |
|---|---|
| "It is expected that the reimbursement form should be completed and submitted in a timely manner in order for processing to be initiated." | "Submit your reimbursement form by the 25th. We start processing it the day we receive it." |
| 「相關費用之核銷單據應儘速填妥並繳交，俾利後續作業之進行。」 | 「請在每月 25 日前把核銷單交給財務部的王小姐。我們收到當天就開始處理。」 |
| "The team will make a determination as to whether an implementation of the proposed solution may potentially be feasible in some circumstances." | "The team will decide whether the proposed solution is feasible." |
| 「請先 review 這份 proposal 的 scope，確認 stakeholder 的 alignment 沒問題之後，我們再 kick off 這個 project。」 | 「請先看過這份提案的範圍，確認相關的人都同意了，我們再開始做。」 |

More pairs, each naming the principle applied:
[`examples/before-after-en.md`](examples/before-after-en.md) ·
[`examples/before-after-zh.md`](examples/before-after-zh.md).

## What This Skill Does

1. Identifies the intended reader and purpose — the standard's first
   principle requires it, and every cut/keep decision follows from it.
2. Detects the text language and loads the matching technique layer:
   [`references/english-techniques.md`](references/english-techniques.md) or
   [`references/chinese-techniques.md`](references/chinese-techniques.md).
3. Rewrites against the four principles (relevant → findable →
   understandable → usable) without dropping any fact, number, condition, or
   honest hedge. Where plainness would cost precision, it keeps the
   precision and flags the trade-off.
4. Returns the rewritten text alone — no preamble, no lecture. Ask for
   "show the diff" and it returns a before/after table naming the principle
   behind each change instead.

## Architecture: one shared layer, per-language technique layers

```
SKILL.md                          shared layer (English): principles, procedure, routing
references/principles.md          the four principles, interpretation, sources
references/english-techniques.md  English techniques (in English)
references/chinese-techniques.md  中文手法（以中文撰寫）
```

The shared layer is language-independent, mirroring the standard itself.
Technique layers are written in their own language, because plain language
techniques do not translate: English fights nominalization and passive
voice; Chinese fights Europeanized long sentences and bureaucratic register.
Adding another language = adding one technique file. Contributions welcome.

## Installation

```bash
git clone https://github.com/danyuchn/iso-24495-skill ~/.claude/skills/iso-24495
```

## Usage

```
Rewrite this in plain language
Apply ISO 24495 to this announcement
把這段改成淺白中文
幫我去掉這封信的公文腔
```

You get the rewritten text back and nothing else. Add "show the diff" /
「列出改了什麼」 to see the per-change principle table.

## Scope

Built for: reader-facing text — reports, emails, documentation, UI strings,
announcements, policies, explanations, and AI output that reads as dense or
bureaucratic. Works on English and Traditional Chinese; the principles apply
to other languages but no technique layer exists for them yet.

Not built for: creative or literary writing (voice is the point there), and
not for **agent-facing** text where a machine must parse without ambiguity —
that is controlled-language territory; use the companion skill
[asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) instead.
Rule of thumb: reader is a person → this skill; reader is a machine or a
maintenance manual → STE.

## Relationship to the ISO Standard

This is an unofficial project, not affiliated with, endorsed by, or approved
by ISO. The full ISO 24495-1 text is a licensed document and is **not**
reproduced here. The skill is built from the standard's publicly documented
principle framework (ISO's published abstract and scope, and the
International Plain Language Federation's freely published materials). Every
quantitative rule in the technique files is this project's own working
proxy, not a clause of the standard. For certified conformance, buy and
consult the standard.

## Sources

- [ISO 24495-1:2023 — Plain language, Part 1](https://www.iso.org/standard/78907.html)
- [International Plain Language Federation — ISO standard](https://www.iplfederation.org/iso-standard/)
- [IPLF — national adoptions and translations](https://www.iplfederation.org/standard-translations/)
- [AccessibleEU — ISO 24495-1 summary](https://accessible-eu-centre.ec.europa.eu/content-corner/digital-library/iso-24495-12023-plain-language-part-1-governing-principles-and-guidelines_en)
- Companion controlled-language skill: [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)

## License

MIT — see [LICENSE](LICENSE). The license covers this repository's original
text; it grants no rights to any ISO publication.
