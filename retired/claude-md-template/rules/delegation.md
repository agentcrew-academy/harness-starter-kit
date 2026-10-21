# Delegation Judgment (Optional Rules File)

<!-- Keep only judgment calls the model won't apply by default, where getting it wrong costs something. Each item comes with a reason; extrapolate the situation yourself. -->

- Route grunt work — collecting, reading files, formatting — to a cheaper model; save the expensive model for judgment calls where a mistake is costly. Why: grunt work barely varies in quality across models but varies a lot in cost.
- Hand verification to an independent conversation or agent that had no part in producing the work, and give it only the raw data and the result — not the reasoning behind it. Why: whoever made something is bound to grade it favorably, and a verifier that only reads a summary just copies the same mistake forward.
- When accepting an agent's work, look at the actual deliverable and the command history — don't take its summary at face value; only cite its conclusions after spot-checking them. Why: an agent's report is a claim, just like your own self-report, not a fact.
- When an unexpected change turns up, confirm who made it from version history and file timestamps before attributing it. Why: the user is often working in parallel with you, so "the agent overstepped" is an accusation that needs evidence, not the default explanation.
