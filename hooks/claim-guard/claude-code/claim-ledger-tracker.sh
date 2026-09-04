#!/bin/bash
# claim-ledger-tracker.sh
#
# This one works like a dashcam: every time the AI runs a command, it quietly
# logs an entry beside it — no noise, no interruption.
#
# It only logs two kinds of things:
#   1. Which verification-type commands were run (tests, builds, version checks, etc.)
#   2. Which searches were performed (finding files, finding keywords, WebSearch, WebFetch)
#
# What gets logged is used by the neighboring claim-evidence-guard.sh, which
# checks this ledger at the end of the turn to see whether "what it just said"
# is actually backed by evidence. The two hooks must be installed together.
#
# The ledger lives in a cache folder under the user's home directory, kept
# separate per conversation, so it never pollutes your project.
#
# Adapted from AlethiaQuizForge/no-hallucination's (MIT licensed) verify-tracker
# and search-tracker, merged into one hook with an isolated ledger path.

LEDGER_DIR="$HOME/.cache/claude-guard-hooks"

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
SID=$(echo "$INPUT" | jq -r '.session_id // "default"')

VERIFY_LEDGER="$LEDGER_DIR/${SID}.verify"
SEARCH_LEDGER="$LEDGER_DIR/${SID}.search"

case "$TOOL" in
    Grep|Glob)
        mkdir -p "$LEDGER_DIR"
        echo "$(date +%H:%M:%S) $TOOL" >> "$SEARCH_LEDGER"
        ;;
    WebSearch)
        QUERY=$(echo "$INPUT" | jq -r '.tool_input.query // empty')
        mkdir -p "$LEDGER_DIR"
        echo "$(date +%H:%M:%S) WebSearch ${QUERY:0:120}" >> "$SEARCH_LEDGER"
        ;;
    WebFetch)
        URL=$(echo "$INPUT" | jq -r '.tool_input.url // empty')
        mkdir -p "$LEDGER_DIR"
        echo "$(date +%H:%M:%S) WebFetch ${URL:0:120}" >> "$SEARCH_LEDGER"
        ;;
    Bash)
        CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
        [[ -z "$CMD" ]] && exit 0
        # Verification-type: tests, builds, status, health checks, diff, lint, live-run scripts
        if echo "$CMD" | grep -qE '(--version|npm (run build|test)|pytest|jest|cargo test|go test|make test|uv run|vault-lint|visual-drift-lint|py_compile|bash -n|jq (-e |\.)|curl.*-[sI]|git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(status|diff|log)|systemctl (status|is-active)|test -[fedrwx]|grep -[qcl]|wc -[lcw]|python3 (-c|-m)|node -e|pdfinfo|cmp -s|diff -r)'; then
            mkdir -p "$LEDGER_DIR"
            echo "$(date +%H:%M:%S) ${CMD:0:120}" >> "$VERIFY_LEDGER"
        fi
        # Search-type: grep/rg/find/ls/gh api lookups
        if echo "$CMD" | grep -qE '(^|[|;&][[:space:]]*)(grep|rg|find|ls|fd|gh api|mdfind)[[:space:]]'; then
            mkdir -p "$LEDGER_DIR"
            echo "$(date +%H:%M:%S) ${CMD:0:120}" >> "$SEARCH_LEDGER"
        fi
        ;;
    *) exit 0 ;;
esac

exit 0
