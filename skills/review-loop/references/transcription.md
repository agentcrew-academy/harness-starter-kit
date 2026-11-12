# Recorded review: two rules that keep it from breaking

This skill **doesn't provide a transcription tool**, and doesn't care which one
you use -- local model, cloud API, an online service, or a transcript you
already made yourself.

But the two rules below apply regardless of tooling. Both come from having
actually hit them, not from general common sense.

## 1. Before transcribing, confirm the audio actually has sound in it

Give a multimodal model a silent file and **it won't say "this is empty" -- it
will fabricate an entire transcript that looks completely normal**: speaker
labels, timestamps, coherent content, all of it invented.

Adding "if the file is silent, report no speech, don't make anything up" to
the prompt **doesn't stop this**. Tested it -- the model confabulates again on
the second attempt, just with different fabricated content.

So measure the volume programmatically before feeding it to the model:

```bash
ffmpeg -i input.m4a -vn -af volumedetect -f null /dev/null 2>&1 | grep mean_volume
```

`mean_volume` above roughly -40 dB means there's something there. Close to
-90 dB is effectively silence -- **stop and ask the user**, don't send it for
transcription.

How to spot a transcript that's already been fabricated: **no proper nouns
anywhere in it.** No names, no places, no product names, no specific
numbers. A real hour of review feedback from a real person can't possibly
contain zero proper nouns.

## 2. Past ten minutes, split it and run the segments in parallel

Feed in one long audio file and the model will give up partway through, then
turn the rest into a summary to fill the gap -- and it won't tell you it gave
up. What you get back looks like a complete transcript; the back half is
actually a paraphrase.

Split into five-minute chunks and process them in parallel:

```bash
ffmpeg -v error -i input.m4a -vn -ac 1 -ar 16000 -b:a 48k \
  -f segment -segment_time 300 out%02d.m4a
```

After transcribing, **check the timestamp at the end of every segment**: the
last line's timestamp should be close to that segment's actual length. A
five-minute segment that only transcribes up to 2:30 gave up partway --
rerun that one.

Real numbers: two recordings, 24 minutes and 17 minutes long, split into 9
segments total -- **2 of them failed on the first pass**, and only came out
complete after a rerun. Skip the check and you'll silently lose a big chunk
of feedback.

When merging, remember to convert each segment's timestamps into the whole
recording's global timeline, or citations won't line up.

## 3. Treat every proper noun as unconfirmed

Even a successful transcription still mishears names, product names, and
project codenames -- and it mishears them in ways that sound plausible
(homophones).

How to handle it: **file the transcript exactly as transcribed, don't edit
it.** Then attach a correction table at the end of the file: "what the audio
sounds like / what it actually is / how you know." That keeps the raw
record honest while still citing the right names elsewhere.

Write down how you know -- found it in a specific file, or confirmed with
the person. Don't guess from context and then treat the guess as settled
fact.
