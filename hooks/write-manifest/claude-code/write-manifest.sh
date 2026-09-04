#!/bin/bash
# write-manifest.sh
#
# This one is ground truth for a question that comes up constantly in a
# multi-session workflow: "which files did *this* conversation actually
# touch?" It writes two records every time the AI writes or edits a file:
#
#   1. write-manifests/<session-id>.list  -- every file path this session's
#      Write/Edit/MultiEdit tools touched
#   2. edit-logs/<session-id>.jsonl       -- for Edit/MultiEdit, the exact
#      old_string/new_string pairs; for Write, a marker that the whole file
#      was rewritten
#
# Why this exists: when you run more than one Claude Code session against
# the same repo at once, or resume a session after a break, "what did I
# change" and "what changed while I wasn't looking" get mixed up. A file
# already dirty before this session touched it might be someone else's
# in-progress work, not yours to stage. The write-manifest tells a later
# checkpoint/closure step exactly which paths this session is responsible
# for, and the edit log lets it reconstruct *only this session's edits* on
# top of HEAD for a file another session also modified -- see the neighboring
# stage-own-edits.sh script, which replays this log instead of staging (and
# silently overwriting) the whole file.
#
# Silent by design: no stdout, zero context cost. Fails open (missing
# session_id or file_path just means "nothing to log," not an error).

INPUT=$(cat)
SID=$(printf '%s' "$INPUT" | jq -r '.session_id // ""')
FP=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // ""')
TOOL=$(printf '%s' "$INPUT" | jq -r '.tool_name // ""')
[ -z "$SID" ] && exit 0
[ -z "$FP" ] && exit 0

STATE="$HOME/.claude/state"
mkdir -p "$STATE/write-manifests" "$STATE/edit-logs"
LIST="$STATE/write-manifests/$SID.list"
LOG="$STATE/edit-logs/$SID.jsonl"

grep -qxF -- "$FP" "$LIST" 2>/dev/null || printf '%s\n' "$FP" >> "$LIST"

case "$TOOL" in
  Edit)
    printf '%s' "$INPUT" | jq -c '{f: .tool_input.file_path, op: "edit",
      old: .tool_input.old_string, new: .tool_input.new_string,
      all: (.tool_input.replace_all // false)}' >> "$LOG"
    ;;
  MultiEdit)
    printf '%s' "$INPUT" | jq -c '.tool_input.file_path as $f | .tool_input.edits[]? |
      {f: $f, op: "edit", old: .old_string, new: .new_string, all: (.replace_all // false)}' >> "$LOG"
    ;;
  Write|NotebookEdit)
    printf '%s' "$INPUT" | jq -c '{f: (.tool_input.file_path // .tool_input.notebook_path), op: "write"}' >> "$LOG"
    ;;
esac
exit 0
