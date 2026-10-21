# Check Here When Something's Stuck

> For use during the workshop. Every entry follows the format: **symptom → cause → what to do
> (what to say to the learner).**
> The instructor can read these directly out loud while circulating too.

---

## A. Can't find a browser

### A1. `detect_browsers.sh` prints `STATUS=none`

**Cause**: this computer doesn't have a Chromium-family browser installed (Chrome/Edge/Brave/Arc/Vivaldi).

**What to do**:

> "Is your main browser Safari or Firefox? This version can't read those yet.
> If you have Chrome installed but don't actually use it, that won't help either — no data means nothing to analyze.
> For now, watch what a classmate gets — the process is the same."

**Don't do this**: don't have the learner install Chrome and use it for a week just to have
something to run. This is a workshop, not homework.

### A2. It found browsers, but every profile is only a few hundred KB

**Cause**: two possibilities — (1) their main browser is Safari/Firefox; (2) they clear their
browsing history regularly.

**What to do**: ask about the second possibility first.

> "Do you clear your browsing history regularly? Or use incognito mode a lot?"

If yes, explain directly: this run's results will be badly skewed, since what's visible is only
the short window since the last clear.

---

## B. Copying the file fails

### B1. `cp` says `Operation not permitted`

**Cause**: macOS's privacy protection (TCC) is blocking terminal access to that folder.

**What to do**:

> "This is Mac's privacy protection blocking it. Go to System Settings → Privacy & Security →
> Full Disk Access, and enable the terminal app you're currently using, then **fully quit and
> reopen the terminal.** It won't take effect without a restart."

### B2. `cp` says `No such file or directory`

**Cause**: usually a space in the path not being wrapped in quotes (`Application Support` has a space in it).

**What to do**: have the learner **paste the entire line fresh**, don't type it manually and
don't remove the quotes.

### B3. Copy succeeds, but `extract.py` says `database is locked` or `unreadable`

**Cause**: Chrome is currently writing to that file, and the copy caught it mid-write.

**What to do**:

> "Quit Chrome completely (not just close the window, fully quit the app), then copy it again."

On Mac, fully quitting is Cmd+Q, or "Quit Google Chrome" from the menu bar.

---

## C. The numbers coming out look off

### C1. `STATUS=empty`, says there's no history in this window

**Cause**: wrong profile picked (most common), or this computer genuinely doesn't get much browser use.

**What to do**: go back to `detect_browsers.sh`'s list and try the second one down.
**Especially watch for: the one called Default is often an empty shell.**

### C2. "Unclassified" share is over 40%

**Cause**: this person's information sources fall heavily outside the built-in list —
non-English platforms, local news, niche forums, internal company systems. **This is expected, not broken.**

**What to do**: read out the top dozen or so unclassified domains and ask the user what each one
is and which category it belongs to. This part is itself great conversation material —
**users will often catch themselves right here: "Wait, why did I go there that many times?"**

### C3. "Watching yourself" is 0% or very low, but the user obviously scrolls social media a lot

**Cause**: their personal account hasn't been confirmed yet. The script can identify a
notifications page, but not "this account is you."

**What to do**: look at the "likely personal account candidates" section, ask the user which one
is theirs, then rerun with `--self <handle>`. This step can't be skipped — skipping it makes the core number wrong.

### C4. Total visit count looks absurdly high (e.g. thousands in a day)

**Cause**: this is normal. One "visit" is one page load, not one "opened it and looked at it."
Clicking a link, hitting back, refreshing — each counts separately.

**What to do**: explain this clearly to the learner, **don't let them think they scrolled their
phone a thousand times in a day.** What matters is the proportion, not the raw number.

### C5. Someone asks "what about my phone?"

**Cause**: good question, and the honest answer is a genuine limitation of this tool.

**What to do**: answer honestly.

> "This tool can only see this computer's browser. It has no visibility into your phone at all.
> So if you mostly scroll on your phone, this report will understate you.
> For the phone side, iPhone's 'Screen Time' and Android's 'Digital Wellbeing' have their own
> stats you can look at alongside this."

---

## D. Privacy questions that come up in the room

### D1. "Will this data get sent anywhere?"

> "No. The script runs on your computer, and when it's done it writes the results to a file that
> stays on your computer — I don't see it yet at that point. Before I read it, I'll ask if there's
> anything you don't want me to see, you name the keywords, I delete them, and I do that without
> having seen the content first. No step here goes online, uploads anything, or writes back to
> your browser. And what I get to read is only the site name, page type, and count — the full URL
> already got dropped inside the script; the AI never sees which exact page you visited."

### D2. "Will you see what I looked at?"

Answer honestly, don't hedge. **Especially the part about account names — that can't be left out.**

> "I'll see which **sites** you visited, how many times, and the page type — for example
> 'checked the notifications page 800 times,' 'visited some account's page 100 times,' **and I
> will see that account's name.** I won't see which specific piece of content you looked at on
> those sites. But even a site name alone can reveal things — so before I read it, tell me any
> keywords you don't want seen and I'll delete them first. Categories like medical, job search,
> dating, legal, and gambling are already auto-redacted by the program, you don't need to mention those separately."

**If they follow up with "can you judge whether what I read was any good"** — that's step 6's
quality mode, which needs separate consent; the script is in `quality-review.md`.
**Don't pitch this mode before they ask about it.**

### D3. The learner changes their mind partway through

**Stop immediately, don't try to talk them back into it.**

> "No problem, we'll stop here. The file you copied out earlier is at OO path — go ahead and
> delete it yourself, I won't touch it."

Then give them the `rm` command to run **themselves**. No exceptions here — a tool that leaves
someone regretting it does far more damage than a tool that just didn't finish running.

---

## E. Things to do at wrap-up

Once finished, remind the learner to clean up the copied-out file:

> "One last thing: that browsing history you copied out earlier is still on your computer, and
> it's just as sensitive as the original data in your browser. Leaving it there is extra risk for no reason."

Give them this line to run themselves (adjust the path to match reality):

```
rm ~/.info-diet/history.db ~/.info-diet/report.txt
```

Delete both: the history file itself, and the report (it contains site names and account handles).

**Keep the baseline file (`baseline-DATE.json`)**, it's needed for next month's re-check.
It only contains site names and numbers, no full URLs, no account handles.
Make this distinction clear to the learner, otherwise they'll delete everything and have nothing to compare against next month.
