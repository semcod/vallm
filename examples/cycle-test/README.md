# Cycle Test — pełny cykl ticket → reDSL → PR

Skrypty do walidacji krok po kroku całego cyklu Semcod.

## Skrypty

| Skrypt | Opis | Tworzy PR? |
|--------|------|------------|
| `validate-steps.sh` | Sprawdza każdy endpoint API osobno | Nie — bezpieczny do powtarzania |
| `full-cycle.sh` | Pełny cykl: auth → ticket → reDSL → PR → merge | Tak |

## Szybki start

```bash
# 1. Walidacja endpointów (bez PR)
cd examples/cycle-test
chmod +x validate-steps.sh full-cycle.sh
./validate-steps.sh

# 2. Pełny cykl z PR
./full-cycle.sh
```

## Kroki walidowane przez validate-steps.sh

1. **Infrastructure** — Backend, reDSL, mock-github health
2. **Authentication** — gh token → Semcod session JWT
3. **User** — GET /api/me
4. **Ticket CRUD** — POST create, GET list, GET stats, GET single, PATCH update, GET status, POST process (dry_run), DELETE
5. **reDSL** — GET status, POST health, POST decide, POST refactor (dry-run)
6. **Webhook** — POST /api/tickets/webhook/pr-updated

## Kroki pełnego cyklu (full-cycle.sh)

1. Check services
2. Authenticate (gh → Semcod JWT)
3. Verify identity (/api/me)
4. Check reDSL availability
5. Create ticket
6. reDSL decide
7. reDSL refactor (dry-run)
8. Process ticket via Semcod API
9. Check ticket status
10. List tickets
11. Ticket statistics
12. Create PR via gh
13. Merge PR
14. Update ticket to merged

## Zmienne środowiskowe

| Zmienna | Default | Opis |
|---------|---------|------|
| `SEMCOD_URL` | http://localhost:8003 | Backend API |
| `REDLS_URL` | http://localhost:8030 | reDSL engine |
| `REPO` | semcod/vallm | Target repo |
