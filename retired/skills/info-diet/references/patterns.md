# Classification Rules: How the Five Buckets Get Sorted

The script takes a first automatic pass, and anything it can't figure out falls into
"unclassified." This file is the criteria for you (Claude) to use when working through
"unclassified" domains together with the user.

---

## Definitions of the five buckets

| Bucket | Definition | The question to ask |
|---|---|---|
| **External intake** | Bringing something in from the outside world | "Are they here to find out what other people think, or what's happening?" |
| **Watching yourself** | Watching how the world sees them | "Are they looking at their own content, their own stats, or reactions to themselves here?" |
| **Messaging** | One-on-one or group back-and-forth | "Is there a specific person or group they're talking to here?" |
| **Tools & workbench** | Used to get things done | "Are they producing something, looking something up, or handling a task here?" |
| **Unclassified** | Can't tell | None of the above four is obvious |

---

## Criteria for judging "unclassified" (ask in this order)

**1. Is this domain a search engine, cloud drive, admin dashboard, bank, shopping, or booking site?**
→ Tools & workbench. What these have in common: "a clear task, done, and they leave."

**2. Is it a news site, forum, video platform, or social network?**
→ External intake. **Local news and non-English platforms most commonly land in unclassified —
this is an inevitable gap in the built-in list, don't skip it just because you haven't seen it before.**

**3. Is it the user's own site, their own service's back end, their own company's system?**
→ Look at the path shape: checking stats, comments, order status → watching yourself;
actually editing content → tools & workbench.

**4. If you still can't tell, just ask the user.**
Keep it short: "You went to `xxx.com` N times — what is that?"
**Don't guess and then keep going as if your guess is fact** — a wrong guess tanks the credibility
of the whole report, and the user can usually answer in one second anyway.

---

## The same domain can span multiple buckets (important)

**This is the easiest place to get this tool wrong, and getting it wrong here buries the core finding.**

The script has already been rewritten to classify "per visit," not per domain. Keep that same
granularity when interpreting results with the user. For example:

| Domain | Path | Bucket |
|---|---|---|
| threads.com | `/activity` | watching yourself |
| threads.com | `/@own-handle/post` | watching yourself |
| threads.com | `/` (home feed) | external intake |
| threads.com | `/@someone-else/post` | external intake |
| threads.com | `/messages` | messaging |
| youtube.com | `/watch` | external intake |
| youtube.com | `/@own-channel` | watching yourself |
| studio.youtube.com | any path | watching yourself |

Domains marked "(mixed)" in the output are exactly this situation. **Always break it apart when
interpreting it** — just saying "you spent 2,324 visits on Threads" carries no real information.

---

## Identifying the "personal account"

The script lists candidates: an account with a visit count far higher than any other on the same
platform.

**Always confirm with the user, don't assume.** Someone might repeatedly look at a celebrity's or
rival's page and rack up just as many visits — guessing wrong here is embarrassing.

Once confirmed, **make sure to rerun** with `--self <handle>`. Without rerunning,
the "watching yourself" number will be badly understated — in practice, the gap can exceed
4 percentage points.

---

## How "scroll-without-clicking" is computed

Staying on any of these paths = still in the feed layer, hasn't clicked into any specific content:

```
/  /home  /explore  /feed  /foryou  /browse  /trending
/popular  /timeline  /following  /discover  /reels  /shorts
/search  /search_result  /results  /hot  /new  /all
```

This ratio is only computed for the "external intake" and "watching yourself" categories.
It doesn't apply to tools & workbench — nobody would call staying on Gmail's inbox "scrolling without clicking."

**Search result pages count as the feed layer**, since staying on search results without
clicking through is the same behavior as staying on a recommended feed.

---

## Judgments to avoid making

- **Don't infer someone's life situation from a domain.** Job-search sites, medical sites,
  legal consultations — treat as unseen, unless the user brings it up themselves. This tool's
  authorized scope is "analyzing attention distribution," not "interpreting someone's life."
- **Don't pass value judgment on entertainment.** Entertainment is entertainment, just label the
  category and move on. The problem was never entertainment itself — it's mistaking entertainment for learning.
- **Don't suggest cutting a domain just because it "sounds unproductive."** Ask first what role
  it plays in the user's life. Someone living abroad reading local news, someone with a hobby
  reading a hobby forum — neither needs a justification.
