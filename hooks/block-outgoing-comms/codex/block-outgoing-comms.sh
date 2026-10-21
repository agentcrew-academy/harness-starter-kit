#!/usr/bin/env bash
# Purpose: stop before any MCP tool that sends something out and make the user confirm
#   the draft first (Codex build).
# Event: PreToolUse; which tools it stops is decided by the matcher in hooks.json.
# Decision: Codex PreToolUse has no field known to match Claude Code's
#   permissionDecision "ask", so this build blocks every send attempt (fails closed) and
#   tells the model to show the draft; the user sends it themselves. Not a native prompt.
#   Trigger it once in a real Codex session before relying on it.
# Requires: jq. Without jq it allows the call.

set -uo pipefail

if ! command -v jq >/dev/null 2>&1; then
  printf '{}\n'
  exit 0
fi

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

jq -n --arg tool "$TOOL" \
  '{decision:"block",reason:("Outgoing comms intercepted: " + $tool + " — this needs a human to confirm the draft content before it goes out. Codex cannot pause for a yes, so every send attempt is stopped, retries included. Show the user the full draft; the user sends it themselves.")}'
exit 0
