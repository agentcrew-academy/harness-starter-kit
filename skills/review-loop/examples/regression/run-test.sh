#!/usr/bin/env bash
# Regression test: three versions of one real-world case, proving this tool
# catches the three kinds of drift it originally missed.
#
# The fixture is a fictional community tool-library launch spec, but all
# three failure modes are copied from one real incident. That was a long
# spec that went through four review rounds with none of this tooling in
# place, and:
#   1. A whole section disappeared between revisions and nobody noticed --
#      not even the independent AI review dispatched afterward to diff the
#      versions, which only found 9 smaller omissions.
#   2. Section numbers shifted across the board -- "Section 4" in v1 and
#      "Section 4" in v2 were completely different content.
#   3. A section that had already been verbally approved ("01: Approve")
#      got its heading changed, a new subsection inserted, and was
#      renumbered afterward, with the approver never finding out.
#
# All three should be caught. If they aren't, this tool doesn't do what it
# claims to.

set -u
cd "$(dirname "$0")"
RL="python3 ../../scripts/review_loop.py"
pass=0; fail=0

ok()   { echo "  PASS  ${1}"; pass=$((pass+1)); }
bad()  { echo "  FAIL  ${1}"; fail=$((fail+1)); }
step() { echo; echo "── $1"; }

rm -f spec.md spec.review-state.json spec-review-v*.html feedback.txt

step "Version 1: nine sections, first render"
cp v1.md spec.md
$RL render spec.md -o spec-review-v1.html >/dev/null 2>&1 \
  && ok "rendered fine" || bad "render failed"
grep -q '"first-principles"' spec.review-state.json \
  && ok "the first-principles section got registered" || bad "it wasn't registered"

step "Version 2: reproduce what actually happened -- delete a whole section, say nothing"
cp v2.md spec.md
out=$($RL check spec.md 2>&1); rc=$?
echo "$out" | sed 's/^/     /'
if [ $rc -ne 0 ]; then ok "blocked (insufficient coverage)"; else bad "not blocked -- this is the one case that most has to be caught"; fi
echo "$out" | grep -q "first-principles" \
  && ok "named exactly which section vanished" || bad "didn't name the section -- still doesn't tell anyone what to look for"

step "Version 3: leave a proper tombstone, declaring these two sections removed"
cp v2.md spec.md
cat >> spec.md <<'EOF'

<!-- @block first-principles removed: the deletion-test conclusion now lives in trial and inventory, no longer its own section -->

<!-- @block shape removed: merged into process; the borrow/return skeleton is now written in the process section -->
EOF
out=$($RL check spec.md 2>&1)
if echo "$out" | grep -q "ok   coverage 1.000"; then
  ok "coverage is back to 100% once it's declared (the tool isn't stopping you from removing things, it wants you to say so)"
else echo "$out" | sed 's/^/     /'; bad "declared it and coverage is still short -- the logic is wrong"; fi
$RL render spec.md -o spec-review-v2.html >/dev/null 2>&1
grep -q "Removed" spec-review-v2.html \
  && ok "removed sections still show up on the review page (greyed out, struck through)" || bad "removed sections didn't stay on the page"

step "Version 4: the reviewer approves the trial section"
cat > feedback.txt <<'EOF'
## Review feedback
[trial] Approve
[space] Revise — two zones instead of three is enough
[materials] Approve
EOF
$RL apply spec.md feedback.txt 2>&1 | sed 's/^/     /'
python3 -c "
import json;d=json.load(open('spec.review-state.json'))
import sys;sys.exit(0 if d['blocks']['trial'].get('approved_hash') else 1)" \
  && ok "the approval got frozen as a hash" || bad "the approval wasn't recorded"

step "Version 5: the approved section gets quietly edited (what actually happened)"
cp v3.md spec.md
cat >> spec.md <<'EOF'

<!-- @block first-principles removed: the deletion-test conclusion now lives in trial and inventory, no longer its own section -->

<!-- @block shape removed: merged into process; the borrow/return skeleton is now written in the process section -->
EOF
out=$($RL check spec.md 2>&1); rc=$?
echo "$out" | sed 's/^/     /'
if [ $rc -ne 0 ]; then ok "blocked"; else bad "not blocked -- approval would be meaningless"; fi
echo "$out" | grep -q "Approved blocks changed after approval" \
  && ok "made clear this is approval-tampering, not an ordinary edit" || bad "didn't make clear what kind of problem this is"

step "Extra: implicit-inheritance phrasing"
cp v1.md spec2.md
cat >> spec2.md <<'EOF'

<!-- @block pointer-bug -->
## Equipment source
Same as v2, can be skipped.
EOF
rm -f spec2.review-state.json
$RL render spec2.md -o /dev/null >/dev/null 2>&1
out=$($RL check spec2.md 2>&1)
echo "$out" | grep -q "implicit inheritance\|points to another version" \
  && ok "caught wording like \"same as v2, can be skipped\" that rots later" || bad "missed the implicit inheritance"

echo
echo "────────────────────────────"
echo "passed ${pass}   failed ${fail}"
rm -f spec.md spec2.md spec*.review-state.json spec-review-v*.html feedback.txt
[ $fail -eq 0 ] || exit 1
