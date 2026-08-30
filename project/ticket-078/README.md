# Ticket 078: Expose bounded operational attributes and bottleneck queries

- **ID**: ticket-078
- **Owner**: founder:tom-sapletta-com
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-30

## Goal and scope

Make the experimental explicit-source data graph useful for operational
bottleneck analysis without widening discovery authority. Entity nodes may
carry only an allowlisted, bounded set of non-secret scalar attributes, and a
query may select a bounded list of terms using deterministic OR semantics.

## Acceptance criteria

- [x] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the Founder's
  active request to continue autonomy repair.
- [x] AC-02: Entity nodes expose only allowlisted operational scalar
  attributes with deterministic size and value bounds.
- [x] AC-03: A string query remains backward compatible and a bounded list of
  terms selects the union of matching nodes plus their immediate graph context.
- [x] AC-04: Secret-shaped, reference and arbitrary scalar values never become
  node attributes; invalid or oversized queries fail closed.
- [x] AC-05: Positive, negative, full-stack and governance checks pass.

## Validation evidence

- `repositories[]` and `pull_requests[]` now become bounded entity nodes; the
  scalar projection is restricted to 32 code-owned operational keys and
  160-character, finite, non-secret values.
- String queries remain compatible; lists accept at most 16 non-empty terms of
  at most 80 characters and use deterministic OR semantics.
- A live read-only PR-controller projection produced 11 failing entities plus
  their source node (12 nodes, 11 edges), instead of the full cycle payload.
- Complete suite: 144 passed; focused Ruff, governance and whitespace gates
  pass. The existing jsonschema deprecation warning remains unchanged.
- Protected Validator run `33305042438` approved exact head
  `bdd913252a7a03ecd820e9c6a1e8767b39b01e65`; PR #71 merged it as
  `98aa427f707880ee31fbfc743192d9e1d5c0f374`.
- The wheel built from integrated `main` was installed into the Subactor
  runtime venv. Live installed-CLI readback returned 12 current bottleneck
  entities in a 13-node, 12-edge graph.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
