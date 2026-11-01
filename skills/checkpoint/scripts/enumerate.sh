#!/bin/bash
# checkpoint fact reconciliation, step 1: mechanical enumeration script — produces unforgeable inventory evidence.
# Usage: enumerate.sh [--memory <memory-dir>] [--vault <kb-root>] [<project-root> ...]
# --vault: notes-folder reconciliation (daily-log <-> master-file done-marker cross-check, missing tags, fake dates, cross-file duplicate todos)
# --memory: memory health check (broken index links, relative-time references)
# <project-root>: pass this only for dev repos (docs/README enumeration)
# The output is pasted verbatim into the final summary's "step-1 inventory evidence" section — never hand-type or rewrite the numbers.
set -uo pipefail

MEMORY_DIR=""
VAULT=""
ROOTS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --memory) MEMORY_DIR="${2:-}"; shift 2 ;;
    --vault) VAULT="${2:-}"; shift 2 ;;
    *) ROOTS+=("$1"); shift ;;
  esac
done

# Adjust the patterns below to match your own todo-format conventions, or override via env vars.
REL_TIME_PATTERN="${REL_TIME_PATTERN:-today|yesterday|just now|recently|last week}"
# Your todo category tags; if you don't have a tag system, set this to a string that never matches to skip the check.
TAG_PATTERN="${TAG_PATTERN:-#(work|life|admin)}"
TODAY=$(date '+%Y-%m-%d')
# Completion marker used by your daily-log / master-file convention (e.g. a checkmark symbol, "[DONE]", etc). Override via DONE_MARKER.
DONE_MARKER="${DONE_MARKER:-✅}"
# Due-date marker used in your master files, appearing as "<DATE_MARKER> YYYY-MM-DD". Override via DATE_MARKER.
DATE_MARKER="${DATE_MARKER:-📅}"

echo "=== checkpoint sync enumeration @ $(date '+%Y-%m-%d %H:%M %z') ==="

if [[ -n "$MEMORY_DIR" ]]; then
  if [[ -d "$MEMORY_DIR" ]]; then
    echo "--- memory: $MEMORY_DIR ---"
    md_count=$(find "$MEMORY_DIR" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')
    echo "md files: $md_count"
    for t in user feedback project reference; do
      c=$(grep -l "type: $t" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
      echo "  type=$t: $c"
    done
    if [[ -f "$MEMORY_DIR/MEMORY.md" ]]; then
      echo "MEMORY.md lines: $(wc -l < "$MEMORY_DIR/MEMORY.md" | tr -d ' ')"
      broken=0
      while IFS= read -r f; do
        if [[ ! -f "$MEMORY_DIR/$f" ]]; then
          echo "  BROKEN index link: $f"
          broken=$((broken + 1))
        fi
      done < <(grep -o '([A-Za-z0-9_.-]*\.md)' "$MEMORY_DIR/MEMORY.md" | tr -d '()' | sort -u)
      echo "broken index links: $broken"
    else
      echo "MEMORY.md: MISSING"
    fi
    rel=$(grep -rEc "$REL_TIME_PATTERN" "$MEMORY_DIR"/*.md 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
    echo "relative-time hits in memory: $rel"
    [[ "$rel" -gt 0 ]] && grep -rEn "$REL_TIME_PATTERN" "$MEMORY_DIR"/*.md 2>/dev/null | head -10
  else
    echo "--- memory: $MEMORY_DIR --- NOT FOUND"
  fi
fi

if [[ -n "$VAULT" ]]; then
  if [[ -d "$VAULT" ]]; then
    echo "--- vault: $VAULT ---"
    MAIN_DIRS=()
    # Your notes folder's "master file" subfolders; override with VAULT_MAIN_DIRS (space-separated). Missing ones are skipped automatically.
    for d in ${VAULT_MAIN_DIRS:-pillars projects decisions personal notes}; do
      [[ -d "$VAULT/$d" ]] && MAIN_DIRS+=("$VAULT/$d")
    done

    # 1. daily log <-> master-file done-marker cross-check (heuristic: if the two counts don't line up, check item by item)
    daily_file="$VAULT/daily/$TODAY.md"
    if [[ -f "$daily_file" ]]; then
      echo "daily note today: daily/$TODAY.md"
      echo "  '$DONE_MARKER $TODAY' in daily note: $(grep -Fc "$DONE_MARKER $TODAY" "$daily_file" 2>/dev/null)"
    else
      latest=$(ls "$VAULT/daily" 2>/dev/null | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' | sort | tail -1)
      echo "daily note today: MISSING (daily/$TODAY.md; latest = ${latest:-none})"
    fi
    done_main=$(grep -rFc --include='*.md' "$DONE_MARKER $TODAY" "${MAIN_DIRS[@]}" 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
    echo "'$DONE_MARKER $TODAY' in master files (${VAULT_MAIN_DIRS:-default folders}): $done_main"

    # 2. open todos missing a category tag (see TAG_PATTERN at the top of this file)
    miss=$(grep -rn --include='*.md' '^- \[ \]' "${MAIN_DIRS[@]}" 2>/dev/null | grep -v '_TEMPLATE' | grep -Ev "$TAG_PATTERN" | wc -l | tr -d ' ')
    echo "open todos missing tag: $miss"
    [[ "$miss" -gt 0 ]] && grep -rn --include='*.md' '^- \[ \]' "${MAIN_DIRS[@]}" 2>/dev/null | grep -v '_TEMPLATE' | grep -Ev "$TAG_PATTERN" | sed "s|$VAULT/||" | head -10

    # 3. fake dates (date marker not followed by an actual date)
    fake=$(grep -rEn --include='*.md' "${DATE_MARKER} *[^0-9 ]" "${MAIN_DIRS[@]}" 2>/dev/null | grep -v '_TEMPLATE' | wc -l | tr -d ' ')
    echo "fake dates (date marker followed by non-date): $fake"
    [[ "$fake" -gt 0 ]] && grep -rEn --include='*.md' "${DATE_MARKER} *[^0-9 ]" "${MAIN_DIRS[@]}" 2>/dev/null | grep -v '_TEMPLATE' | sed "s|$VAULT/||" | head -10

    # 4. cross-file duplicate open todos (SSOT violation: the same task text living in two files)
    dup=$(grep -rh --include='*.md' --exclude='_TEMPLATE.md' '^- \[ \]' "${MAIN_DIRS[@]}" 2>/dev/null \
      | sed -E "s/^- \[ \] +//; s/ *${DATE_MARKER} [0-9-]+//; s/ *#[^ ]+//g; s/ +\$//" \
      | grep -v '〈' | grep -v '^$' | LC_ALL=C sort | LC_ALL=C uniq -d)
    if [[ -n "$dup" ]]; then
      echo "duplicate open todos (normalized text, cross-file): $(printf '%s\n' "$dup" | wc -l | tr -d ' ')"
      printf '%s\n' "$dup" | head -5 | sed 's/^/  DUP: /'
    else
      echo "duplicate open todos (normalized text, cross-file): 0"
    fi

    # 5. relative time in master files -- only scan open-todo lines and status lines (a progress-log quote of someone saying "today" is historical record, doesn't count)
    rel=$(grep -rEn --include='*.md' '^(- \[[ /]\]|> \*\*Status)' "${MAIN_DIRS[@]}" 2>/dev/null | grep -Ec "$REL_TIME_PATTERN")
    echo "relative-time hits in master-file todo/status lines: $rel"
    [[ "$rel" -gt 0 ]] && grep -rEn --include='*.md' '^(- \[[ /]\]|> \*\*Status)' "${MAIN_DIRS[@]}" 2>/dev/null | grep -E "$REL_TIME_PATTERN" | sed "s|$VAULT/||" | head -10

    # 6. stray date-named md files at the vault root (left behind when a logging tool has the wrong path configured)
    stray=$(ls "$VAULT" 2>/dev/null | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' | wc -l | tr -d ' ')
    echo "stray date-named md at vault root: $stray"
    [[ "$stray" -gt 0 ]] && ls "$VAULT" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' | sed 's/^/  STRAY: /'
  else
    echo "--- vault: $VAULT --- NOT FOUND"
  fi
fi

for ROOT in "${ROOTS[@]+"${ROOTS[@]}"}"; do
  if [[ ! -d "$ROOT" ]]; then
    echo "--- project: $ROOT --- NOT FOUND"
    continue
  fi
  echo "--- project: $ROOT ---"
  echo "root entries: $(ls "$ROOT" | wc -l | tr -d ' ')"
  echo "root md files:"
  find "$ROOT" -maxdepth 1 -name '*.md' -exec basename {} \; | sed 's/^/  /'
  if [[ -d "$ROOT/docs" ]]; then
    echo "docs/ md files: $(find "$ROOT/docs" -name '*.md' | wc -l | tr -d ' ')"
    find "$ROOT/docs" -name '*.md' | sed "s|$ROOT/||; s/^/  /"
  else
    echo "docs/: does not exist"
  fi
  if [[ -d "$ROOT/.claude/rules" ]]; then
    echo ".claude/rules/ md files: $(find "$ROOT/.claude/rules" -name '*.md' | wc -l | tr -d ' ')"
  else
    echo ".claude/rules/: does not exist"
  fi
  if [[ -d "$ROOT/.claude/skills" ]]; then
    echo ".claude/skills/ dirs: $(find "$ROOT/.claude/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
  fi
  echo "md files (maxdepth 2, excl node_modules/.git): $(find "$ROOT" -maxdepth 2 -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l | tr -d ' ')"
  rel=0
  for f in "$ROOT/README.md" "$ROOT/CLAUDE.md" "$ROOT/AGENTS.md"; do
    [[ -f "$f" ]] && rel=$((rel + $(grep -Ec "$REL_TIME_PATTERN" "$f" || true)))
  done
  if [[ -d "$ROOT/docs" ]]; then
    d=$(grep -rEc "$REL_TIME_PATTERN" "$ROOT/docs" --include='*.md' 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
    rel=$((rel + d))
  fi
  echo "relative-time hits in README/CLAUDE/AGENTS/docs: $rel"
done

echo "=== enumeration end ==="
