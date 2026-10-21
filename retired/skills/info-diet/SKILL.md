---
name: info-diet
description: "Information diet check-in: reads the user's own browsing history and works out where their attention is actually going — external intake, watching themselves, messaging, tools/workbench, how much is scroll-without-clicking, and time-of-day distribution — then names an archetype and gives one verifiable action. Fully local, no network access, sensitive categories auto-redacted, and the user can name exclusions that the AI deletes without ever having read them. There's also an opt-in quality mode that judges the actual titles of articles read. Built for zero-technical-background workshop learners to run themselves during hands-on time, explained entirely in plain language. Triggers: information diet, audit my attention, where does my time go, am I information overloaded, browsing habit analysis, attention check-up."
---

# info-diet — Information Diet Check-In

> This skill is meant for hands-on workshop time. The user has zero technical background
> and runs it themselves inside Claude Code.
> The instructor will be circulating and adding commentary, so **every step needs plain language**.
> The first time any jargon shows up, check `references/glossary.md` for the plain-language version first.

## What this tool does (say this to open)

> **Tell the user: "What you look at every day is the same kind of thing as what you eat every day —
> both build up over time, both affect you. The difference is you know what you're eating,
> but you don't really know what you're looking at.**
>
> **This tool reads the browsing history on your own computer and works out three things:
> where your attention is actually going, whether you're reading things or just scrolling past them,
> and what time of day you're online. Then it tells you which archetype you fall into.**
>
> **It's not telling you to quit anything. It's a scale, not a personal trainer — it just gives you
> the numbers. What you do with them, or whether you do anything at all, is up to you."**

---

## Step 0: Say exactly what you'll touch, then get consent

**This step can't be skipped, can't be shortened, can't be waved through with "let me just analyze this real quick."**

You're about to touch one of the most private files on this person's computer. Browsing history
can reveal someone's health condition, job search, financial situation, relationship status.
**Don't read a single byte before they've explicitly said yes.**

Say this:

> **"Before we start, I want to be clear about exactly what I'm going to touch and how I'll protect it.**
>
> **What I'm going to read is your Chrome browsing history — the full list of sites you've visited.
> This is one of the most private things on your computer, so there are three rules:**
>
> **First, this all runs on your own computer. No network access, no upload, nothing gets written back to your browser.**
>
> **Second, full URLs never enter my view. A program will process the data on your computer first.
> What I get to see is: the site name, the type of page, and how many times you visited. For example,
> I might see "you visited the notifications page of some social network 800 times" or "you visited
> some account's page 100 times" — I will see that account's name. But what you actually looked at on
> those pages, the actual content, I can't see.**
>
> **Third, the processed results get saved to a file first — they don't come straight to me.
> Before I read it, I'll ask you if there's anything you don't want me to see — you name the keywords,
> I delete those lines, and I do that deletion without having read the content first.
> So "what you deleted, I never saw" is literally true, not just something I'm promising you.**
>
> **Also, categories like medical, job search, dating, legal, and gambling are already auto-redacted
> by the program during processing — you don't need to call those out separately.**
>
> **Fourth, I'll tell you before I touch any file. If a permission dialog pops up asking whether to
> allow it, that's what's happening — the decision is yours.**
>
> **Does that work for you? It's completely fine to skip this — you can watch what a classmate gets instead."**

**The second point — "I'll see the account name" — can't be left out.** An account someone
repeatedly visits could be an ex, a competitor, or anyone they don't want known to be watching.
This needs to be said clearly before they agree, not discovered after they see the report.

**The third point is the design core of this skill, not just talk.** In Claude Code,
anything printed to the terminal is in the AI's context the instant it prints —
if "you look first, I'll delete what you don't want" depends on a flow where
"the AI runs it first, then prints the result," that promise is literally false the moment it happens.
So the script has to use `--report` to write results to a file instead.

**If the user hasn't clearly said yes, stop here.** Hesitation, silence, "I guess that's fine" —
none of those count as consent. Ask again, or skip it. One person feeling their privacy was
violated during a workshop is far worse to clean up than ten people finishing successfully.

---

## Step 1: Find out which browser they actually use

```bash
bash <this skill's directory>/scripts/detect_browsers.sh
```

(Use the path where you actually loaded this SKILL.md from for `<this skill's directory>`.
If you can't find it, locate it with
`find ~ -path "*/info-diet/scripts/detect_browsers.sh" 2>/dev/null | head -1`.)

This script **only checks file size and modification time — it never opens any history.**

**Read the output list and describe it to the user in plain language**, don't paste the whole
terminal output. For example:

> **"Found it — your Chrome has four accounts. Looks like the one you actually use is Profile 1,
> with 39 MB of history and last used today. The other three haven't been touched in a while."**

**There's a pitfall to mention here**: the one called `Default` is **not necessarily**
the one actually in use. In practice we've seen `Default` be a 2 MB empty shell while the real
main profile was `Profile 1`. Picking the wrong one leads to an absurd conclusion like
"you barely go online." **So confirm with the user**:

> **"Which Google account do you normally log into when you're browsing? Is the one I picked the right one?"**

`STATUS=none`, or every profile only having a few hundred KB, → check section A of `references/troubleshooting.md`.

---

## Step 2: Make a copy of the history

While Chrome is open that file is locked, so you need to copy it out before you can read it.
The script prints that `cp` command as its last line.

**Say something before you touch anything** (don't silently go poking at files):

> **"I'm going to make a copy of that history now — the original won't be touched, it's just locked
> while Chrome is open, so we need a copy. If a permission dialog pops up, that's this step — go ahead and allow it."**

Then **you run that `cp` command yourself.** Most people's settings will pop up a confirmation
dialog and they just click allow — that's a lot easier than having them paste a long command themselves.

**If it gets blocked** (people with stricter permission settings get denied outright, no dialog at all),
have them run it themselves instead. In Claude Code, the user can run a command directly by prefixing
it with `!` in the input box:

> **"Your settings are stricter, it got blocked. Could you paste that line yourself and run it —
> just add an exclamation mark at the very front of the input box. This is actually better anyway —
> you pressing enter yourself confirms exactly which file I'm touching."**

Copy failure (`Operation not permitted`, `No such file`) → section B of `references/troubleshooting.md`.

---

## Step 3: First analysis pass

```bash
python3 <this skill's directory>/scripts/extract.py \
  --db ~/.info-diet/history.db \
  --days 30 \
  --report ~/.info-diet/report.txt \
  --out ~/.info-diet/baseline-$(date +%Y-%m-%d).json
```

**`--report` cannot be omitted.** With it, the report gets written to a file and the terminal
only prints one status line — meaning **you (Claude) haven't seen any content yet at this point.**
This is exactly where the promise from step 0's third point gets kept.

This program aggregates the data on the user's own computer: **full URLs are read into memory
and discarded once used; what's written out is only the domain, path shape (IDs replaced with
`:id`, but handles kept), counts, and time of day.**

Search keywords are **not output by default** — of all the raw data, that's the single most
revealing thing about someone's life situation. Only add `--with-search` if the user explicitly
asks to see it, and confirm again before doing so.

---

## Step 4: They tell you what to delete, you delete it without looking, then you read

**The order can't be reversed. Reverse it, and step 0's promise becomes a lie.**

**First thing: ask what they want removed, then you delete it — without looking.**

**Don't have them open the file editor themselves.** Someone with zero technical background may
not be able to open a file, find a line, and save it — if ten people all get stuck on this step,
the class is derailed. The right approach is **they say it out loud, you do the deleting.**

> **"The report's saved, over a hundred lines, I haven't looked at it yet.**
>
> **Before I look: is there anything — any site, or any category of thing — you don't want me to see?**
>
> **Just tell me keywords, like "anything hospital-related," "this one site," "job-search stuff."
> I'll delete those lines exactly as you say — and I'll be doing it without having seen the content,
> so I will never know what got deleted.**
>
> **Also, some categories (medical, job search, dating, legal, gambling) are already auto-redacted
> when the report gets generated — you don't need to mention those."**

Run whatever they say to run:

```bash
python3 <this skill's directory>/scripts/redact.py \
  --report ~/.info-diet/report.txt \
  --terms "their keywords, comma separated"
```

This script **only reports how many lines were removed, never what was in them** — so running it doesn't count as you having seen it.

If they say "nothing," skip this step.

**Second thing: once deletion is done, that's the first time you Read the report file.**

Don't peek early just to save a round of conversation. The entire promise rests on this order.

**Third thing: confirm which account is actually theirs.**

The report has a "likely personal account candidates" section. **Always ask, don't assume** —
someone might repeatedly view a rival's or a celebrity's page and get just as many visits.
(If they already deleted those lines, that means they don't want to discuss it —
**don't push**, just skip this step and note when interpreting results that the
"watching yourself" number will be understated.)

> **"Is your Threads handle @xxx?"**

Once confirmed, **make sure to rerun** with `--self`:

```bash
python3 <this skill's directory>/scripts/extract.py \
  --db ~/.info-diet/history.db --days 30 \
  --self "threads.com:@their_handle,youtube.com:@their_channel" \
  --report ~/.info-diet/report.txt \
  --out ~/.info-diet/baseline-$(date +%Y-%m-%d).json
```

Writing it as `platform:@handle` is more accurate than just `@handle` — the same name could be
someone else on a different platform.

**Rerunning overwrites the report file, so whatever was just deleted comes back.**
Pass the keywords they just gave you into `--exclude` at the same time, so the report never
contains that content in the first place — you won't need to delete it again:

```bash
  --exclude "the keywords they just gave you, comma separated"
```

**This step can't be skipped.** Without `--self`, the "watching yourself" number will be badly
understated — in practice, the gap has exceeded 4 percentage points, and that's precisely the
single most core number this tool produces.

---

## Step 5: Sort out "unclassified"

The output will include an "unclassified" section of domains. **This is expected, not broken** —
local news, non-English platforms, niche forums, and internal company systems can never be fully
covered by a built-in list.

Following the criteria in `references/patterns.md`, read out the top dozen or so and ask the
user what each one is.

**This part is itself the best conversation material.** Users will often catch themselves
mid-sentence when hearing a domain read out loud: "Wait, why did I go there that many times?" —
that one sentence does more work than any analysis you could give.

---

## Step 6: Ask if they want quality mode (optional, needs a separate go-ahead)

**This step is optional, but must always be asked.** Everything computed so far measures
"where attention went" — it can't tell "whether what they took in was any good." A serious
in-depth report and an infuriating headline look identical in the numbers. This is exactly
where this tool differs most from the original concept it's based on.

The way to fill that gap is to look at **the titles of articles they actually clicked into and
read** (the browser already stores these — no network fetch needed).

**But this needs separate consent.** Agreeing to the basic analysis earlier does not mean they've
agreed to this — titles reveal a lot more than site names do. The full script and criteria are in
`references/quality-review.md`; follow that.

Only after they agree, rerun with `--with-titles`:

```bash
python3 <this skill's directory>/scripts/extract.py \
  --db ~/.info-diet/history.db --days 30 \
  --self "<confirmed handle>" --exclude "<their earlier keywords>" \
  --with-titles \
  --report ~/.info-diet/report.txt
```

**After rerunning, ask again "anything you want removed" before reading**, because titles are
new this time and there might be something they hadn't thought to exclude before.

If they decline, skip it entirely — the earlier analysis stands complete as-is.
**Don't push, and don't imply that skipping it makes the analysis incomplete.**

---

## Step 7: Name the archetype and interpret it

Following `references/archetypes.md`, determine **one** primary archetype, then interpret it.

**Three rules for interpretation:**

1. **Lead with the number, then give the meaning.** "You had 802 visits to the notifications page,
   averaging 27 a day" is a hundred times more useful than "you're a bit too focused on others' feedback."
2. **Give only one archetype per person.** Giving two or more loses focus.
3. **The clean archetype must be given honestly when it applies.** A tool that finds "you have a
   problem" no matter who runs it gets found out as a fortune-teller by the third run. If it's
   genuinely healthy, say it's healthy.

**When someone asks "am I information-overloaded"**, borrow the original author's line
(this works great in the room):

> **"According to the person who came up with this concept, the problem isn't actually 'overload.'
> Having a lot of information available isn't your fault — just like there being a lot of food in
> the world doesn't make you gain weight; what matters is whether you're choosing. So instead of
> looking at how much you consumed, we look at where your attention actually went."**

Finally, **pick one action**, only one, and it has to be something verifiable by numbers on a rerun next month.

- Good: "check the notifications page three times a day," "no browsing after midnight"
- Not good: "read more substantive content," "use social media less" (unverifiable, might as well not give one)

**Don't suggest blocking sites or installing blocking software.** That turns this tool from a
scale into a disciplinary tool — a completely different thing, and the user hasn't authorized that.

---

## Step 8: Wrap up

**Always remind the user to clean up the copied-out history file.**

> **"One last thing: that browsing history you copied out earlier is still on your computer,
> and it's just as sensitive as the original data in your browser. Leaving it there is extra risk for no reason."**

Give them the command to run **themselves**:

```
rm ~/.info-diet/history.db ~/.info-diet/report.txt
```

The report file (`report.txt`) should be deleted too — it contains site names and account handles.

**Keep the baseline file (`baseline-DATE.json`)**, it's needed for next month's re-check.
It only contains site names and numbers, no full URLs, no account handles.
Make this distinction clear, otherwise they'll delete the baseline too and have nothing to compare against next month.

---

## Re-check mode (when the user says "I already ran this before")

Don't rerun the entire flow from scratch. The value of the first check-in comes from
"seeing your own numbers for the first time"; the value of every check-in after that is
only "did anything move."

Walk through steps 1 to 3 again to produce a new baseline, then:

```bash
python3 <this skill's directory>/scripts/compare.py \
  --old ~/.info-diet/baseline-<previous date>.json \
  --new ~/.info-diet/baseline-<this date>.json
```

Five lines of numbers, and that's it. **If nothing moved, say nothing moved — don't invent excuses for the user.**

---

## Security boundaries (apply throughout the entire flow)

- **Read-only.** This skill never writes to any of the user's existing files, start to finish.
  It only ever produces two new files: the report `report.txt` and the baseline `baseline-DATE.json`.
- **Never read the baseline JSON directly.** It gets written before the user has reviewed it,
  and contains the top 30 domain names — even domains the user removed from the report are
  still in that JSON. Its only purpose is to be fed into `compare.py` next month to compute
  the difference. Always look at the user-reviewed `report.txt` for content.
- **No network access.** No step in this flow ever needs the internet. Say so clearly if asked.
- **No content reading.** Only domains and path shapes are examined. Which site someone visited
  is in scope; what they looked at there is not.
- **Don't interpret someone's life.** Job-search sites, medical sites, legal consultations,
  relationship-related content — treat as unseen unless the user brings it up themselves.
  This tool's authorized scope is "attention distribution," and nothing beyond that.
- **When the user says stop, stop.** No persuading, no asking why, no final pitch.
  Then hand them the deletion command to run themselves.
- **Only run this on the user's own computer.** If someone brings in someone else's browsing
  history to run this on, decline, no matter the stated reason.

## Known limitations (be honest when asked)

- **Basic mode measures the "distribution" of attention, not the "quality" of information.**
  The core argument of Clay Johnson's book is **choosing your sources** — he explicitly argues
  against the "information overload" framework, saying the problem isn't too much quantity, it's
  a lack of selection; he also calls after-the-fact critical-thinking filtering "intellectual
  bulimia" — the right move is to choose well before consuming. Basic mode doesn't look at
  content, so **it can't distinguish in-depth reporting from echo-chamber comfort food** — the
  two look identical in the numbers. **Step 6's quality mode fills this gap**, but it requires
  separate user consent; without it, the gap stays unfilled, and that should be stated honestly
  rather than pretending the numbers can answer a quality question.
- **Quality mode is nearly useless on social platforms.**
  It relies on page titles, and on X/Threads/Instagram the title is just "Someone (@handle)" —
  it can't tell you what the content actually said. For social platforms, quality has to be
  judged instead by "who they're reading" — criteria in `references/quality-review.md`.
- **Can't see the phone.** For someone who mostly scrolls on their phone, this report will
  badly understate their attention usage.
- **Chromium-family browsers only** (Chrome/Edge/Brave/Arc/Vivaldi). Safari and Firefox use
  different data formats that this version can't read.
- **Anyone who clears history regularly or uses incognito mode heavily** will get skewed results.
- **"Visit count" doesn't mean "number of times looked at."** Clicking a link, hitting back,
  refreshing — each counts as a separate visit. Look at proportions, not absolute numbers.
- **Time-on-page isn't available.** Chrome does record a duration field, but it counts a tab
  sitting open unattended too — in practice the totals come out to way more than 24 hours a
  day, so this tool never uses it at all.
