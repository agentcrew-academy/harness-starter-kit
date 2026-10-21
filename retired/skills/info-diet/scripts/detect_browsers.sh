#!/usr/bin/env bash
# detect_browsers.sh — find the browser profile the user actually uses
#
# Important: this script "only" looks at file size and modification time —
# it never opens or reads a single history entry.
# Its only output is a candidate list plus one copy command.
#
# Why not just read it directly? Two reasons:
#   1. Chrome locks the History file while it's running; reading it directly
#      would get incomplete or locked data.
#   2. Reading browsing history runs into a permission guard. Most setups
#      just pop a confirmation dialog (the user clicks allow and it's fine),
#      but a strict setup (e.g. an auto-mode classifier) will hard-block it
#      without even asking — this has happened in practice. So the flow has
#      to handle both: the AI runs the copy first, and if that gets blocked,
#      ask the user to run it themselves instead.
#
# Usage: bash detect_browsers.sh [output dir]
#   output dir defaults to ~/.info-diet/

set -uo pipefail

OUTDIR="${1:-$HOME/.info-diet}"

echo "=== Looking for browsers (file size and time only, no content read) ==="
echo

# Chromium family: identical schema, one parser handles all of them
# Format: display name|user data root
CHROMIUM_ROOTS=(
  "Chrome|$HOME/Library/Application Support/Google/Chrome"
  "Chrome Beta|$HOME/Library/Application Support/Google/Chrome Beta"
  "Chrome Canary|$HOME/Library/Application Support/Google/Chrome Canary"
  "Edge|$HOME/Library/Application Support/Microsoft Edge"
  "Brave|$HOME/Library/Application Support/BraveSoftware/Brave-Browser"
  "Vivaldi|$HOME/Library/Application Support/Vivaldi"
  "Arc|$HOME/Library/Application Support/Arc/User Data"
  "Opera|$HOME/Library/Application Support/com.operasoftware.Opera"
  "Chrome (Linux)|$HOME/.config/google-chrome"
  "Chromium (Linux)|$HOME/.config/chromium"
  "Brave (Linux)|$HOME/.config/BraveSoftware/Brave-Browser"
  "Edge (Linux)|$HOME/.config/microsoft-edge"
)

TMP_LIST="$(mktemp)"
trap 'rm -f "$TMP_LIST"' EXIT

for entry in "${CHROMIUM_ROOTS[@]}"; do
  name="${entry%%|*}"
  root="${entry#*|}"
  [ -d "$root" ] || continue
  # A Chromium profile is always a first-level folder under root, containing a file called History
  while IFS= read -r -d '' hist; do
    prof="$(basename "$(dirname "$hist")")"
    # Get byte size and mtime epoch with stat; macOS and Linux use different syntax
    if stat -f '%z %m' "$hist" >/dev/null 2>&1; then
      read -r bytes mtime <<<"$(stat -f '%z %m' "$hist")"      # macOS / BSD
    else
      read -r bytes mtime <<<"$(stat -c '%s %Y' "$hist")"      # Linux / GNU
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$mtime" "$bytes" "$name" "$prof" "$hist" >>"$TMP_LIST"
  done < <(find "$root" -maxdepth 2 -name History -type f -print0 2>/dev/null)
done

if [ ! -s "$TMP_LIST" ]; then
  echo "No Chromium-family browser history found (Chrome / Edge / Brave / Arc / Vivaldi)."
  echo
  echo "STATUS=none"
  exit 0
fi

# The sort order decides which one we recommend, so the criteria matter:
#   - Sorting by time alone: a profile someone accidentally opened today
#     would jump to the top and bury the real main profile.
#   - Sorting by size alone: an old profile that was heavily used years ago
#     but abandoned since would jump to the top.
# So "touched within the last 45 days" is the qualifying bar; among those
# that qualify, sort by size; only fall back to pure size when none qualify.
# A lesson learned the hard way: "Default" is often an empty shell, and the
# one actually in use is something like "Profile 1" — never hardcode Default.
NOW_EPOCH="$(date +%s)"
RECENT_CUTOFF=$((NOW_EPOCH - 45 * 86400))

awk -F'\t' -v cut="$RECENT_CUTOFF" '{ print (($1 >= cut) ? 1 : 0) "\t" $0 }' "$TMP_LIST" \
  | sort -k1,1nr -k3,3nr -k2,2nr \
  | cut -f2- >"$TMP_LIST.sorted"
mv "$TMP_LIST.sorted" "$TMP_LIST"

echo "Found these browser profiles, most likely main one listed first:"
echo
printf '   %-16s %-12s %10s   %s\n' "Browser" "Profile" "Size" "Last used"
printf '   %s\n' "--------------------------------------------------------------------"

i=0
BEST_PATH=""
BEST_DESC=""
while IFS=$'\t' read -r mtime bytes name prof path; do
  i=$((i + 1))
  # human-readable size
  if [ "$bytes" -ge 1048576 ]; then
    human="$((bytes / 1048576)) MB"
  else
    human="$((bytes / 1024)) KB"
  fi
  if date -r "$mtime" '+%Y-%m-%d %H:%M' >/dev/null 2>&1; then
    when="$(date -r "$mtime" '+%Y-%m-%d %H:%M')"          # macOS / BSD
  else
    when="$(date -d "@$mtime" '+%Y-%m-%d %H:%M')"         # Linux / GNU
  fi
  mark="  "
  if [ "$i" -eq 1 ]; then
    mark="->"
    BEST_PATH="$path"
    BEST_DESC="$name / $prof"
  fi
  printf ' %s %-16s %-12s %10s   %s\n' "$mark" "$name" "$prof" "$human" "$when"
done <"$TMP_LIST"

echo
echo "The arrow points to the most recently used, most data-rich profile — usually that's the main one."
echo "(Note: one called \"Default\" isn't necessarily the one in use — for a lot of people the main one is actually \"Profile 1\".)"
echo

# Other browsers: not supported in this version, but must be stated clearly so the user doesn't assume they were scanned
OTHERS=""
[ -f "$HOME/Library/Safari/History.db" ] && OTHERS="${OTHERS}Safari "
if find "$HOME/Library/Application Support/Firefox/Profiles" -maxdepth 2 -name places.sqlite -print -quit 2>/dev/null | grep -q . ; then
  OTHERS="${OTHERS}Firefox "
fi
if [ -n "$OTHERS" ]; then
  echo "Also detected: $OTHERS"
  echo "This version doesn't support them yet (different data format; Safari also needs Full Disk Access)."
  echo "If the Chromium-family data above looks too small, the main usage may be here instead, and this run's results would be skewed."
  echo
fi

mkdir -p "$OUTDIR"
echo "=== Next: copy the history out (the original is locked while Chrome is running) ==="
echo
echo "cp \"$BEST_PATH\" \"$OUTDIR/history.db\""
echo
echo "Tell the user before running this. Most people will just see a confirmation dialog and can click allow."
echo "If it gets blocked outright by permission settings, ask the user to run this line themselves, prefixed with !."
echo

echo "BEST_PATH=$BEST_PATH"
echo "BEST_DESC=$BEST_DESC"
echo "OUTDIR=$OUTDIR"
echo "STATUS=ok"
