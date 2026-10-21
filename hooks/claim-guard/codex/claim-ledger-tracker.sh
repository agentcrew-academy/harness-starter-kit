#!/usr/bin/env bash
# PostToolUse: record verification, search and file-write actions for the current Codex turn.
# Each ledger's mtime is when that kind of event last happened; the Stop guard compares
# .edit against .verify to tell whether a verification still covers the current code
# (running tests and then editing one more line = that verification is stale).
set -u

ledger_dir="$HOME/.cache/codex-guard-hooks"
input="$(cat)"
if ! command -v jq >/dev/null 2>&1; then
  printf '{}\n'
  exit 0
fi

tool="$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)"
# agent_id first: subagents get their own ledger so their claims are checked against their own work
turn_id="$(printf '%s' "$input" | jq -r '.agent_id // .turn_id // .session_id // "default"' 2>/dev/null)"
verify_ledger="$ledger_dir/${turn_id}.verify"
search_ledger="$ledger_dir/${turn_id}.search"
edit_ledger="$ledger_dir/${turn_id}.edit"

case "$tool" in
  apply_patch|Write|Edit|MultiEdit|NotebookEdit)
    fp="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null)"
    mkdir -p "$ledger_dir"
    printf '%s %s %.160s\n' "$(date +%H:%M:%S)" "$tool" "$fp" >> "$edit_ledger"
    ;;
  Grep|Glob)
    mkdir -p "$ledger_dir"
    printf '%s %s\n' "$(date +%H:%M:%S)" "$tool" >> "$search_ledger"
    ;;
  WebSearch)
    query_text="$(printf '%s' "$input" | jq -r '.tool_input.query // empty' 2>/dev/null)"
    mkdir -p "$ledger_dir"
    printf '%s WebSearch %.120s\n' "$(date +%H:%M:%S)" "$query_text" >> "$search_ledger"
    ;;
  web_fetch|WebFetch)
    url_text="$(printf '%s' "$input" | jq -r '.tool_input.url // empty' 2>/dev/null)"
    mkdir -p "$ledger_dir"
    printf '%s WebFetch %.120s\n' "$(date +%H:%M:%S)" "$url_text" >> "$search_ledger"
    ;;
  Bash)
    command_text="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
    if [ -n "$command_text" ]; then
      if printf '%s' "$command_text" | grep -qE '(--version|npm (run build|test)|pytest|jest|cargo test|go test|make test|uv run|py_compile|bash -n|jq (-e |\.)|curl.*-[sI]|git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(status|diff|log)|systemctl (status|is-active)|test -[fedrwx]|grep -[qcl]|wc -[lcw]|python3 (-c|-m)|node -e|pdfinfo|cmp -s|diff -r)'; then
        mkdir -p "$ledger_dir"
        printf '%s %.120s\n' "$(date +%H:%M:%S)" "$command_text" >> "$verify_ledger"
      fi
      if printf '%s' "$command_text" | grep -qE '(^|[|;&][[:space:]]*)(grep|rg|find|ls|fd|gh api|mdfind)[[:space:]]'; then
        mkdir -p "$ledger_dir"
        printf '%s %.120s\n' "$(date +%H:%M:%S)" "$command_text" >> "$search_ledger"
      fi
    fi
    ;;
esac

printf '{}\n'
exit 0
