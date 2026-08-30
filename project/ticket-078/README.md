# Ticket 078: Expose bounded operational attributes and bottleneck queries

- **ID**: ticket-078
- **Owner**: founder:tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-30

## Goal and scope

Make the experimental explicit-source data graph useful for operational
bottleneck analysis without widening discovery authority. Entity nodes may
carry only an allowlisted, bounded set of non-secret scalar attributes, and a
query may select a bounded list of terms using deterministic OR semantics.

## Acceptance criteria

- [ ] AC-01: SESSION_EXECUTION_AUTHORIZATION is recorded from the Founder's
  active request to continue autonomy repair.
- [ ] AC-02: Entity nodes expose only allowlisted operational scalar
  attributes with deterministic size and value bounds.
- [ ] AC-03: A string query remains backward compatible and a bounded list of
  terms selects the union of matching nodes plus their immediate graph context.
- [ ] AC-04: Secret-shaped, reference and arbitrary scalar values never become
  node attributes; invalid or oversized queries fail closed.
- [ ] AC-05: Positive, negative, full-stack and governance checks pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
