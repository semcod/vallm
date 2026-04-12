#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Semcod Full Cycle Test — ticket → reDSL decide → reDSL refactor → PR → merge
# Each step is validated; exits on first failure.
# ═══════════════════════════════════════════════════════════════════════════
set -uo pipefail

SEMCOD_URL="${SEMCOD_URL:-http://127.0.0.1:8003}"
REDSL_URL="${REDSL_URL:-http://127.0.0.1:8030}"
REPO="${REPO:-semcod/vallm}"
PASS=0; FAIL=0; STEP=0

green() { printf "\033[32m✔ %s\033[0m\n" "$1"; }
red()   { printf "\033[31m✘ %s\033[0m\n" "$1"; }
step()  { STEP=$((STEP+1)); printf "\n━━━ Step %d: %s ━━━\n" "$STEP" "$1"; }
ok()    { PASS=$((PASS+1)); green "$1"; }
fail()  { FAIL=$((FAIL+1)); red "$1"; }

# ── Step 1: Verify services are up ─────────────────────────────────────────
step "Check services"
for svc in "Backend|$SEMCOD_URL/api/redsl/status" "reDSL|$REDSL_URL/health"; do
  name="${svc%%|*}"; url="${svc##*|}"
  resp=$(curl -s --max-time 10 "$url" 2>/dev/null) || true
  if [ -n "$resp" ]; then
    ok "$name is up"
  else
    fail "$name is DOWN ($url)"
  fi
done

# ── Step 2: Authenticate via gh token ──────────────────────────────────────
step "Authenticate"
GH_TOKEN=$(gh auth token 2>/dev/null) || { fail "gh not authenticated"; exit 1; }
ok "gh token obtained"

SEMCOD_SESSION=$(curl -sf --max-time 10 -X POST "${SEMCOD_URL}/auth/gh-token?token=${GH_TOKEN}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_token',''))" 2>/dev/null) || true

if [ -n "$SEMCOD_SESSION" ] && [ "$SEMCOD_SESSION" != "" ]; then
  ok "Semcod session token obtained"
else
  fail "Semcod session token FAILED"
  exit 1
fi

# Helper
semcod() {
  local method=$1 endpoint=$2 data=${3:-}
  curl -sf --max-time 15 -X "${method}" "${SEMCOD_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${SEMCOD_SESSION}" \
    ${data:+-d "$data"}
}

# ── Step 3: Verify /api/me ─────────────────────────────────────────────────
step "Verify identity"
ME=$(semcod GET "/api/me") || true
ME_LOGIN=$(echo "$ME" | python3 -c "import sys,json; print(json.load(sys.stdin).get('login',''))" 2>/dev/null) || true
if [ -n "$ME_LOGIN" ]; then
  ok "Logged in as: ${ME_LOGIN}"
else
  fail "/api/me failed — response: ${ME}"
fi

# ── Step 4: Check reDSL availability ───────────────────────────────────────
step "reDSL availability"
REDSL_STATUS=$(semcod GET "/api/redsl/status") || true
REDSL_AVAIL=$(echo "$REDSL_STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('available',False))" 2>/dev/null) || true
if [ "$REDSL_AVAIL" = "True" ]; then
  ok "reDSL available"
else
  fail "reDSL unavailable — status: ${REDSL_STATUS}"
fi

# ── Step 5: Create ticket ──────────────────────────────────────────────────
step "Create ticket"
TICKET_RESP=$(semcod POST "/api/tickets" "{
  \"title\": \"Cycle test: split high-CC module\",
  \"repo\": \"${REPO}\",
  \"ticket_type\": \"feature\",
  \"description\": \"Automated cycle test — identify and refactor high-CC module\",
  \"priority\": \"medium\"
}") || true

TICKET_ID=$(echo "$TICKET_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null) || true
TICKET_STATUS=$(echo "$TICKET_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null) || true

if [ -n "$TICKET_ID" ] && [ "$TICKET_STATUS" = "open" ]; then
  ok "Ticket created: ${TICKET_ID} (status=open)"
else
  fail "Ticket creation failed — response: ${TICKET_RESP}"
fi

# ── Step 6: reDSL decide (direct call) ──────────────────────────────────────
step "reDSL decide"
DECIDE_RESP=$(curl -sf --max-time 30 -X POST "${REDSL_URL}/decide" \
  -H "Content-Type: application/json" \
  -d '{"project_dir":"/tmp/vallm"}') || true

DECISIONS_COUNT=$(echo "$DECIDE_RESP" | python3 -c "
import sys
text = sys.stdin.read()
# decide returns explanation string, count lines with 'Action:'
count = text.count('Action:')
print(count)
" 2>/dev/null) || true

if [ "${DECISIONS_COUNT:-0}" -gt 0 ]; then
  ok "reDSL decide found ${DECISIONS_COUNT} decisions"
else
  fail "reDSL decide returned 0 decisions"
fi

# ── Step 7: reDSL refactor (dry_run) ───────────────────────────────────────
step "reDSL refactor (dry-run)"
REFACTOR_RESP=$(curl -sf --max-time 60 -X POST "${REDSL_URL}/refactor" \
  -H "Content-Type: application/json" \
  -d '{"project_path":"/tmp/vallm","max_actions":5,"dry_run":true,"format":"json"}') || true

REFACTOR_DECISIONS=$(echo "$REFACTOR_RESP" | python3 -c "
import sys,json
data = json.load(sys.stdin)
plan = data.get('refactoring_plan', {})
decisions = plan.get('decisions', [])
print(len(decisions))
" 2>/dev/null) || true

if [ "${REFACTOR_DECISIONS:-0}" -gt 0 ]; then
  ok "reDSL refactor (dry-run) returned ${REFACTOR_DECISIONS} decisions"
else
  fail "reDSL refactor (dry-run) returned 0 decisions"
fi

# ── Step 8: Process ticket via API ─────────────────────────────────────────
step "Process ticket via Semcod API"
PROCESS_RESP=$(semcod POST "/api/tickets/${TICKET_ID}/process" "{
  \"project_path\": \"/tmp/vallm\",
  \"max_actions\": 5,
  \"dry_run\": true,
  \"auto_create_pr\": false
}") || true

PROCESS_STATUS=$(echo "$PROCESS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null) || true

if [ "$PROCESS_STATUS" = "dry_run" ] || [ "$PROCESS_STATUS" = "analyzed" ]; then
  ok "Ticket processed: status=${PROCESS_STATUS}"
else
  fail "Ticket process failed — status=${PROCESS_STATUS}, response: ${PROCESS_RESP}"
fi

# ── Step 9: Check ticket status ────────────────────────────────────────────
step "Check ticket status"
STATUS_RESP=$(semcod GET "/api/tickets/${TICKET_ID}/status") || true
TICKET_CUR_STATUS=$(echo "$STATUS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null) || true

if [ -n "$TICKET_CUR_STATUS" ]; then
  ok "Ticket status: ${TICKET_CUR_STATUS}"
else
  fail "Could not get ticket status"
fi

# ── Step 10: List tickets ──────────────────────────────────────────────────
step "List tickets"
LIST_RESP=$(semcod GET "/api/tickets") || true
TOTAL=$(echo "$LIST_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null) || true

if [ "${TOTAL:-0}" -gt 0 ]; then
  ok "Tickets listed: total=${TOTAL}"
else
  fail "No tickets found"
fi

# ── Step 11: Get ticket stats ──────────────────────────────────────────────
step "Ticket statistics"
STATS_RESP=$(semcod GET "/api/tickets/stats") || true
STATS_TOTAL=$(echo "$STATS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null) || true

if [ "${STATS_TOTAL:-0}" -gt 0 ]; then
  ok "Stats: total=${STATS_TOTAL}"
else
  fail "Stats returned 0"
fi

# ── Step 12: Create PR via gh ──────────────────────────────────────────────
step "Create PR via gh"
BRANCH="cycle-test-$(date +%s)"
COMMIT_FILE="cycle_test_$(date +%s).txt"
DEFAULT_BRANCH=$(gh api "repos/${REPO}" --jq '.default_branch' 2>/dev/null) || DEFAULT_BRANCH="main"
SHA=$(gh api "repos/${REPO}/git/refs/heads/${DEFAULT_BRANCH}" --jq '.object.sha' 2>/dev/null) || true

if [ -n "$SHA" ]; then
  gh api "repos/${REPO}/git/refs" -f ref="refs/heads/${BRANCH}" -f sha="${SHA}" >/dev/null 2>&1 || true
  COMMIT_RESULT=$(gh api "repos/${REPO}/contents/${COMMIT_FILE}" -X PUT \
    -f message="cycle test: automated commit" \
    -f content="$(echo -n "Cycle test OK at $(date)" | base64)" \
    -f branch="${BRANCH}" 2>&1) || true
  COMMIT_SHA=$(echo "$COMMIT_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('sha',''))" 2>/dev/null) || true
  if [ -n "$COMMIT_SHA" ]; then
    ok "Commit created: ${COMMIT_SHA:0:8}"
  else
    fail "Commit failed — response: ${COMMIT_RESULT}"
  fi
  PR_URL=$(gh pr create --repo "${REPO}" --head "${BRANCH}" --base "${DEFAULT_BRANCH}" \
    --title "cycle test: automated PR" \
    --body "Automated PR from cycle test. Ticket: ${TICKET_ID}" 2>&1) || true

  if echo "$PR_URL" | grep -q 'github.com'; then
    ok "PR created: ${PR_URL}"
    PR_NUM=$(echo "$PR_URL" | grep -oP '\d+$') || true
  else
    fail "PR creation failed: ${PR_URL}"
  fi
else
  fail "Could not get repo SHA"
fi

# ── Step 13: Merge PR ──────────────────────────────────────────────────────
step "Merge PR"
if [ -n "${PR_NUM:-}" ]; then
  gh pr merge "${PR_NUM}" --repo "${REPO}" --merge --delete-branch >/dev/null 2>&1 || true
  MERGED_AT=$(gh api "repos/${REPO}/pulls/${PR_NUM}" --jq '.merged_at' 2>&1) || true
  if [ -n "$MERGED_AT" ] && [ "$MERGED_AT" != "null" ]; then
    ok "PR #${PR_NUM} merged at ${MERGED_AT}"
  else
    fail "PR #${PR_NUM} not merged — merged_at: ${MERGED_AT}"
  fi
else
  fail "No PR number to merge"
fi

# ── Step 14: Update ticket status ──────────────────────────────────────────
step "Update ticket to merged"
if [ -n "${PR_URL:-}" ]; then
  UPDATE_RESP=$(semcod PATCH "/api/tickets/${TICKET_ID}" "{
    \"status\": \"merged\",
    \"pr_url\": \"${PR_URL}\",
    \"pr_branch\": \"${BRANCH}\"
  }") || true
  UPDATED_STATUS=$(echo "$UPDATE_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null) || true
  if [ "$UPDATED_STATUS" = "merged" ]; then
    ok "Ticket updated to merged"
  else
    fail "Ticket update failed — status: ${UPDATED_STATUS}"
  fi
else
  fail "No PR URL to update ticket"
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  FULL CYCLE TEST RESULTS"
echo "═══════════════════════════════════════════════════════════"
printf "  Passed: \033[32m%d\033[0m   Failed: \033[31m%d\033[0m   Steps: %d\n" "$PASS" "$FAIL" "$STEP"
echo "  Ticket: ${TICKET_ID}"
echo "  PR: ${PR_URL:-N/A}"
echo "═══════════════════════════════════════════════════════════"

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
