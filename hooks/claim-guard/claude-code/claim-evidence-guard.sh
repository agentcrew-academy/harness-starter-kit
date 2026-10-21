#!/bin/bash
# claim-evidence-guard.sh
#
# This one runs when the AI is about to end this turn, and reconciles the
# ledger against what was said.
#
# It checks two things:
#   1. It claimed "I tested it" / "verification passed" / "confirmed working"
#      → the ledger must have a real record of a verification command being run
#   2. It claimed "not found" / "doesn't exist"
#      → the ledger must have a real record of a search being performed
# If it doesn't add up, the turn is blocked from ending, and it's told what's
# missing.
#
# The ledger is written by the neighboring claim-ledger-tracker.sh — the two
# must be installed together, or this one stops working.
#
# Why this is needed: saying "I tested it" costs the AI almost nothing. It can
# say that in exactly the same tone whether or not it actually ran anything,
# and you can't tell the difference. Rather than trust the claim, check the
# record.
#
# Only small local commands run here — no AI calls, no cost.
#
# When the data can't be read or the format is wrong, it always lets the turn
# through — better to miss a block than to block wrongly. It only intervenes
# when the claim was made explicitly AND the ledger has zero matching records.
#
# Adapted from AlethiaQuizForge/no-hallucination's (MIT licensed) verify-guard
# and claim-guard, merged into one hook with Chinese trigger phrases added.

LEDGER_DIR="$HOME/.cache/claude-guard-hooks"

INPUT=$(cat)
# Also wired to SubagentStop: agent_id keys the subagent's own ledger
SID=$(echo "$INPUT" | jq -r '.agent_id // .session_id // "default"' 2>/dev/null) || exit 0

VERIFY_LEDGER="$LEDGER_DIR/${SID}.verify"
SEARCH_LEDGER="$LEDGER_DIR/${SID}.search"
EDIT_LEDGER="$LEDGER_DIR/${SID}.edit"

cleanup() { rm -f "$VERIFY_LEDGER" "$SEARCH_LEDGER" "$EDIT_LEDGER"; }

# Second pass (already blocked once this turn): let it through and clear the ledger
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)
if [[ "$STOP_ACTIVE" == "true" ]]; then
    cleanup
    exit 0
fi

LAST_MSG=$(echo "$INPUT" | jq -r '.last_assistant_message // empty' 2>/dev/null)
# SubagentStop may omit the message: read the last assistant text from the subagent transcript
if [[ -z "$LAST_MSG" ]]; then
    TP=$(echo "$INPUT" | jq -r '.agent_transcript_path // empty' 2>/dev/null)
    [[ -f "$TP" ]] && LAST_MSG=$(jq -rs '[.[] | select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text] | last // empty' "$TP" 2>/dev/null)
fi
[[ -z "$LAST_MSG" ]] && exit 0
# Quoted text is a mention, not a claim: drop 「…」 and `…` spans before matching
LAST_MSG=$(printf '%s' "$LAST_MSG" | LC_ALL=en_US.UTF-8 sed -E 's/「[^」]*」//g; s/`[^`]*`//g')

# A) Verification claims (English + Chinese)
VERIFY_TRIGGERS='verified|confirmed|all passing|tests? pass|build passes|all green|works now|working now|deployed and verified|驗證通過|測試通過|驗證無誤|實測通過|實測有效|全數通過|建置通過|跑通|已驗證|確認無誤'
if echo "$LAST_MSG" | grep -iqE "$VERIFY_TRIGGERS"; then
    if [[ ! -s "$VERIFY_LEDGER" ]]; then
        cleanup
        cat << 'EOF'
{
  "decision": "block",
  "reason": "CLAIM-EVIDENCE GUARD: You claimed 'verified / tests pass / confirmed working', but this session's ledger has no record of any verification-type command (test, build, status, diff, live run). A completion claim is a factual claim — run the verification command first, then state the result; if it genuinely can't be verified automatically, rephrase as 'not yet verified, needs manual confirmation'."
}
EOF
        exit 0
    fi
    # Stale verification: files were edited after the last verification command
    if [[ -s "$EDIT_LEDGER" && "$EDIT_LEDGER" -nt "$VERIFY_LEDGER" ]]; then
        LAST_EDIT=$(tail -1 "$EDIT_LEDGER"); LAST_VERIFY=$(tail -1 "$VERIFY_LEDGER")
        cleanup
        jq -cn --arg e "$LAST_EDIT" --arg v "$LAST_VERIFY" '{decision: "block", reason: ("CLAIM-EVIDENCE GUARD (stale verification): you claimed verified / tests pass, but files were edited after the last verification command, so it did not cover the current code.\n  Last verification: " + $v + "\n  Later edit: " + $e + "\nRe-run the verification before claiming it; if this change needs no test (docs, comments), say edited, not re-verified.")}'
        exit 0
    fi
fi

# B) Negative existence assertions (English + Chinese)
NEG_TRIGGERS="doesn't exist|does not exist|not found|no such|couldn't find|cannot find|can't find|nothing matching|no evidence|there is no|不存在|找不到|沒有找到|查無|沒有任何(相關|紀錄|檔案)|從未出現"
if echo "$LAST_MSG" | grep -iqE "$NEG_TRIGGERS"; then
    if [[ ! -s "$SEARCH_LEDGER" ]]; then
        cleanup
        cat << 'EOF'
{
  "decision": "block",
  "reason": "CLAIM-EVIDENCE GUARD: You asserted something 'doesn't exist / can't be found', but this session's ledger has no record of any search action (Grep/Glob/find/ls). A negative assertion requires an exhaustive search first — search, then say it doesn't exist."
}
EOF
        exit 0
    fi
fi

cleanup
exit 0
