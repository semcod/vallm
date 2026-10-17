# GEMINI.md

<!-- wellmanifest:source-links:v1 -->
## Managed standard sources

- Local adoption manifest: [.governance/manifest.json](.governance/manifest.json)
- Host contract: [.governance/agent-hosts.json](.governance/agent-hosts.json)

<!-- end wellmanifest:source-links:v1 -->

This file is the Gemini / Antigravity entry; the same rules are in `AGENTS.md`.

This repository follows the `wellmanifest/new-project` policy-as-code standard.
Fail-closed. Do not write code until this contract is followed.

1. Read `AGENTS.md` and `.governance/manifest.json`.
2. Allocate tickets only through `./project/new-ticket.sh`. Never commit on `main` or a dirty primary checkout.
3. Work in a canonical worktree v5 (`.worktrees/ticket-NNN--slug`).
4. Stay inside that ticket's `intent.json` `allowedPaths`.
5. Run `./project/governance-check.sh` before claiming done.
