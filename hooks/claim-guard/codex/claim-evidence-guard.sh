#!/usr/bin/env bash
# Stop: block unsupported verification claims and unsupported negative assertions.
set -u

ledger_dir="$HOME/.cache/codex-guard-hooks"
input="$(cat)"
if ! command -v jq >/dev/null 2>&1; then
  printf '{}\n'
  exit 0
fi

# agent_id first: a subagent keeps its own ledger, matching the tracker
turn_id="$(printf '%s' "$input" | jq -r '.agent_id // .turn_id // .session_id // "default"' 2>/dev/null)" || {
  printf '{}\n'
  exit 0
}
verify_ledger="$ledger_dir/${turn_id}.verify"
search_ledger="$ledger_dir/${turn_id}.search"
edit_ledger="$ledger_dir/${turn_id}.edit"
cleanup() { rm -f "$verify_ledger" "$search_ledger" "$edit_ledger"; }

stop_active="$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)"
if [ "$stop_active" = "true" ]; then
  cleanup
  printf '{}\n'
  exit 0
fi

last_message="$(printf '%s' "$input" | jq -r '.last_assistant_message // empty' 2>/dev/null)"
if [ -z "$last_message" ]; then
  printf '{}\n'
  exit 0
fi
# Quoted text is mention, not claim: drop 「…」 and `…` spans before matching
last_message="$(printf '%s' "$last_message" | LC_ALL=en_US.UTF-8 sed -E 's/「[^」]*」//g; s/`[^`]*`//g')"

verify_triggers='verified|confirmed|all passing|tests? pass|build passes|all green|works now|working now|deployed and verified|驗證通過|測試通過|驗證無誤|實測通過|實測有效|全數通過|建置通過|跑通|已驗證|確認無誤'
if printf '%s' "$last_message" | grep -iqE "$verify_triggers" && [ ! -s "$verify_ledger" ]; then
  cleanup
  jq -n '{decision:"block",reason:"CLAIM-EVIDENCE GUARD: The reply claims verification or tests passed, but no verification-type command was recorded this turn. Verify it for real first; if it genuinely cannot be verified automatically, mark it explicitly as not yet verified."}'
  exit 0
fi
# Stale verification: a verification ran, but the last file write happened after it,
# so that verification does not cover the current code.
if printf '%s' "$last_message" | grep -iqE "$verify_triggers" && [ -s "$edit_ledger" ] && [ "$edit_ledger" -nt "$verify_ledger" ]; then
  last_edit="$(tail -1 "$edit_ledger")"
  last_verify="$(tail -1 "$verify_ledger")"
  cleanup
  jq -cn --arg e "$last_edit" --arg v "$last_verify" '{
    decision: "block",
    reason: ("CLAIM-EVIDENCE GUARD (stale verification): the reply claims verification or tests passed, but the last file write came after the last verification, so that verification does not cover the current code.\n  Last verification: " + $v + "\n  Write after it: " + $e + "\nRe-run the verification before claiming; if this change needs none (docs or comments only), say \"changed, not re-verified\" instead.")
  }'
  exit 0
fi

negative_triggers="doesn't exist|does not exist|not found|no such|couldn't find|cannot find|can't find|nothing matching|no evidence|there is no|不存在|找不到|沒有找到|查無|沒有任何(相關|紀錄|檔案)|從未出現"
if printf '%s' "$last_message" | grep -iqE "$negative_triggers" && [ ! -s "$search_ledger" ]; then
  cleanup
  jq -n '{decision:"block",reason:"CLAIM-EVIDENCE GUARD: The reply asserts something does not exist or cannot be found, but no search action was recorded this turn. Search exhaustively first before making a negative assertion."}'
  exit 0
fi

cleanup
printf '{}\n'
exit 0
