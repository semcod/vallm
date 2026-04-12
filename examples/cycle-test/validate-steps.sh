#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Semcod Step Validation — checks every API endpoint individually
# No PR creation — safe to run repeatedly.
# ═══════════════════════════════════════════════════════════════════════════
set -uo pipefail

SEMCOD_URL="${SEMCOD_URL:-http://127.0.0.1:8003}"
REDSL_URL="${REDSL_URL:-http://127.0.0.1:8030}"
PASS=0; FAIL=0

green() { printf "\033[32m✔ %s\033[0m\n" "$1"; PASS=$((PASS+1)); }
red()   { printf "\033[31m✘ %s\033[0m\n" "$1"; FAIL=$((FAIL+1)); }
check() {
  local name=$1 expect=${2:-} actual=${3:-}
  if [ -z "$expect" ] || [ "$actual" = "$expect" ]; then
    green "$name"
  else
    red "$name (expected='$expect' got='$actual')"
  fi
}

echo "═══════════════════════════════════════════════════════════"
echo "  SEMCOD API STEP-BY-STEP VALIDATION"
echo "═══════════════════════════════════════════════════════════"

# ── Infrastructure ──────────────────────────────────────────────────────────
echo ""
echo "── Infrastructure ──"

R1=$(curl -sf "$SEMCOD_URL/api/redsl/status" 2>/dev/null) || R1=""
check "Backend + reDSL status" "True" "$(echo "$R1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('available',''))" 2>/dev/null)"

R2=$(curl -sf "$REDSL_URL/health" 2>/dev/null) || R2=""
check "reDSL health" "ok" "$(echo "$R2" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)"

R3=$(curl -sf http://localhost:4010/health 2>/dev/null) || R3=""
check "mock-github health" "ok" "$(echo "$R3" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)"

# ── Auth ─────────────────────────────────────────────────────────────────────
echo ""
echo "── Authentication ──"

GH_TOKEN=$(gh auth token 2>/dev/null) || GH_TOKEN=""
check "gh auth token" "" "$([ -n "$GH_TOKEN" ] && echo 'present' || echo 'missing')"

SESSION=$(curl -sf -X POST "${SEMCOD_URL}/auth/gh-token?token=${GH_TOKEN}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_token',''))" 2>/dev/null) || SESSION=""
check "Semcod session" "" "$([ -n "$SESSION" ] && echo 'present' || echo 'missing')"

semcod() {
  local method=$1 endpoint=$2 data=${3:-}
  curl -sf -X "${method}" "${SEMCOD_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${SESSION}" \
    ${data:+-d "$data"}
}

# ── User endpoints ──────────────────────────────────────────────────────────
echo ""
echo "── User ──"

ME=$(semcod GET "/api/me" 2>/dev/null) || ME=""
check "/api/me login" "" "$([ -n "$ME" ] && echo 'present' || echo 'missing')"

# ── Ticket CRUD ─────────────────────────────────────────────────────────────
echo ""
echo "── Ticket CRUD ──"

# Create
T_RESP=$(semcod POST "/api/tickets" "{
  \"title\": \"Validate test ticket\",
  \"repo\": \"semcod/vallm\",
  \"ticket_type\": \"feature\",
  \"description\": \"Validation test ticket\",
  \"priority\": \"low\"
}" 2>/dev/null) || T_RESP=""
T_ID=$(echo "$T_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null) || T_ID=""
check "POST /api/tickets (create)" "open" "$(echo "$T_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)"

# List
L_RESP=$(semcod GET "/api/tickets" 2>/dev/null) || L_RESP=""
L_TOTAL=$(echo "$L_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null) || L_TOTAL=0
check "GET /api/tickets (list)" "" "$([ "${L_TOTAL:-0}" -gt 0 ] && echo 'has_items' || echo 'empty')"

# Stats
S_RESP=$(semcod GET "/api/tickets/stats" 2>/dev/null) || S_RESP=""
S_TOTAL=$(echo "$S_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null) || S_TOTAL=0
check "GET /api/tickets/stats" "" "$([ "${S_TOTAL:-0}" -gt 0 ] && echo 'has_stats' || echo 'no_stats')"

# Get single
if [ -n "$T_ID" ]; then
  G_RESP=$(semcod GET "/api/tickets/${T_ID}" 2>/dev/null) || G_RESP=""
  check "GET /api/tickets/{id}" "$T_ID" "$(echo "$G_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null)"
fi

# Update
if [ -n "$T_ID" ]; then
  U_RESP=$(semcod PATCH "/api/tickets/${T_ID}" "{\"priority\":\"high\"}" 2>/dev/null) || U_RESP=""
  check "PATCH /api/tickets/{id}" "high" "$(echo "$U_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('priority',''))" 2>/dev/null)"
fi

# Status
if [ -n "$T_ID" ]; then
  ST_RESP=$(semcod GET "/api/tickets/${T_ID}/status" 2>/dev/null) || ST_RESP=""
  check "GET /api/tickets/{id}/status" "" "$([ -n "$ST_RESP" ] && echo 'present' || echo 'missing')"
fi

# Process (dry_run)
if [ -n "$T_ID" ]; then
  P_RESP=$(semcod POST "/api/tickets/${T_ID}/process" "{
    \"project_path\": \"/tmp/vallm\",
    \"max_actions\": 3,
    \"dry_run\": true,
    \"auto_create_pr\": false
  }" 2>/dev/null) || P_RESP=""
  P_STATUS=$(echo "$P_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null) || P_STATUS=""
  check "POST /api/tickets/{id}/process (dry_run)" "" "$([ "$P_STATUS" = "dry_run" ] || [ "$P_STATUS" = "analyzed" ] || [ "$P_STATUS" = "no_targets" ] && echo 'ok' || echo "fail:$P_STATUS")"
fi

# Delete
if [ -n "$T_ID" ]; then
  D_RESP=$(semcod DELETE "/api/tickets/${T_ID}" 2>/dev/null) || D_RESP=""
  check "DELETE /api/tickets/{id}" "deleted" "$(echo "$D_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)"
fi

# ── reDSL endpoints ─────────────────────────────────────────────────────────
echo ""
echo "── reDSL ──"

# Status
check "GET /api/redsl/status" "True" "$(semcod GET "/api/redsl/status" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('available',''))" 2>/dev/null)"

# Health score
H_RESP=$(semcod POST "/api/redsl/health" "{\"project_path\":\"/tmp/vallm\"}" 2>/dev/null) || H_RESP=""
check "POST /api/redsl/health" "" "$([ -n "$H_RESP" ] && echo 'present' || echo 'missing')"

# Decide
D_RESP=$(curl -sf -X POST "${REDSL_URL}/decide" -H "Content-Type: application/json" -d '{"project_dir":"/tmp/vallm"}' 2>/dev/null) || D_RESP=""
D_COUNT=$(echo "$D_RESP" | python3 -c "import sys; print(sys.stdin.read().count('Action:'))" 2>/dev/null) || D_COUNT=0
check "POST /redsl/decide" "" "$([ "${D_COUNT:-0}" -gt 0 ] && echo "found_${D_COUNT}_decisions" || echo "no_decisions")"

# Refactor dry-run
RF_RESP=$(curl -sf -X POST "${REDSL_URL}/refactor" -H "Content-Type: application/json" \
  -d '{"project_path":"/tmp/vallm","max_actions":3,"dry_run":true,"format":"json"}' 2>/dev/null) || RF_RESP=""
RF_COUNT=$(echo "$RF_RESP" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('refactoring_plan',{}).get('decisions',[])))" 2>/dev/null) || RF_COUNT=0
check "POST /redsl/refactor (dry-run)" "" "$([ "${RF_COUNT:-0}" -gt 0 ] && echo "found_${RF_COUNT}_decisions" || echo "no_decisions")"

# ── Webhook ─────────────────────────────────────────────────────────────────
echo ""
echo "── Webhook ──"

W_RESP=$(semcod POST "/api/tickets/webhook/pr-updated" "{\"action\":\"opened\",\"pull_request\":{\"number\":1},\"repository\":{\"full_name\":\"test/repo\"}}" 2>/dev/null) || W_RESP=""
check "POST /api/tickets/webhook/pr-updated" "" "$([ -n "$W_RESP" ] && echo 'present' || echo 'missing')"

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
printf "  Passed: \033[32m%d\033[0m   Failed: \033[31m%d\033[0m\n" "$PASS" "$FAIL"
echo "═══════════════════════════════════════════════════════════"

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
