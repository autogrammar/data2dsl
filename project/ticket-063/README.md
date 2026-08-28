# Ticket 063: Fix evidence digest computation across adapters to ensure cryptographic integrity (F06)

- **ID**: ticket-063
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-28

## Goal and scope

Fix audit finding F06:
Several adapters had weaknesses in SHA-256 evidence digest calculation:
1. `OqlTelemetryAdapter`: used `val_obj.get("value", "")` which returned `""` for string-set metrics (pins, buses), producing identical digests when pins or buses differed.
2. `DetaAdapter`: computed `f"topology:{response.manifest_path}"`, ignoring actual services and ports.
3. `IntentContractAdapter`: omitted parties and obligations from contract digest.
4. `GitHubDiagitAdapter`: hashed arbitrary parameters when pagination evidence was present instead of page content digests.

SESSION_EXECUTION_AUTHORIZATION recorded from user prompt.

## Acceptance criteria

- [x] AC-01: Scope is approved (SESSION_EXECUTION_AUTHORIZATION recorded).
- [x] AC-02: `OqlTelemetryAdapter` produces distinct digests for differing string-set values (pins, buses).
- [x] AC-03: `DetaAdapter` produces distinct digests when services or ports differ.
- [x] AC-04: `IntentContractAdapter` produces distinct digests when parties, obligations, or deliverables differ.
- [x] AC-05: Unit tests in `tests/test_evidence_digests.py` verify cryptographic distinction.
- [x] AC-06: Full pytest suite passes (112/112) and `governance-check.bat` reports GOV-PASS.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
