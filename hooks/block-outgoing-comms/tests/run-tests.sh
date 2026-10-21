#!/bin/bash
# Dry-run test: the plugin matcher catches real send tools and skips readers,
# and both builds stop the call (Claude Code: ask, Codex: block).
#   bash hooks/block-outgoing-comms/tests/run-tests.sh
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
FAIL=0

MATCHER=$(jq -r '.plugins[] | select(.name=="block-outgoing-comms") | .hooks.PreToolUse[0].matcher' "$ROOT/.claude-plugin/marketplace.json")
[ -n "$MATCHER" ] && [ "$MATCHER" != null ] || { echo "FAIL no matcher in marketplace.json"; exit 1; }
for N in mcp__google-workspace__gmail_send mcp__claude_ai_Slack__slack_send_message mcp__line-bot__push_text_message mcp__x__gmail_reply; do
  echo "$N" | grep -Eq "$MATCHER" || { echo "FAIL matcher misses $N"; FAIL=1; }
done
for N in mcp__claude_ai_Slack__slack_read_channel mcp__x__get_sender_info mcp__gmail__list_sent Bash; do
  echo "$N" | grep -Eq "$MATCHER" && { echo "FAIL matcher wrongly catches $N"; FAIL=1; }
done

PAYLOAD='{"tool_name":"mcp__example-email__send_message","tool_input":{"to":"someone@example.com","body":"hi"}}'
OUT=$(echo "$PAYLOAD" | bash "$DIR/claude-code/block-outgoing-comms.sh")
echo "$OUT" | jq -e '.hookSpecificOutput.permissionDecision == "ask"' >/dev/null 2>&1 || { echo "FAIL claude-code: expected ask, got: $OUT"; FAIL=1; }
OUTC=$(echo "$PAYLOAD" | bash "$DIR/codex/block-outgoing-comms.sh")
echo "$OUTC" | jq -e '.decision == "block"' >/dev/null 2>&1 || { echo "FAIL codex: expected block, got: $OUTC"; FAIL=1; }

[ $FAIL -eq 0 ] && echo "PASS block-outgoing-comms"
exit $FAIL
