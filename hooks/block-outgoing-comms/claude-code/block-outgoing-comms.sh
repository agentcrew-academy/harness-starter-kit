#!/bin/bash
# Purpose: stop before any MCP tool that sends something out (email, chat, social posts)
#   and make the user confirm the draft first: draft -> show -> confirm -> send.
# Event: PreToolUse. Which tools it stops is decided by the matcher in the plugin
#   registration (send / reply / forward / broadcast / publish / schedule / push in the
#   tool name); this script itself names no tools and asks for any tool it receives.
# Decision: ask (permissionDecision "ask" raises a confirmation prompt, even in auto mode).
# Requires: jq. Without jq it prints nothing and the call proceeds normally.

INPUT=$(cat)
command -v jq >/dev/null 2>&1 || exit 0
TOOL=$(printf '%s' "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null)

jq -n \
  --arg tool "$TOOL" \
  '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: ("Outgoing message: " + $tool + ". Check the draft (recipient, wording, attachments) before allowing it to send.")
    }
  }'

exit 0
