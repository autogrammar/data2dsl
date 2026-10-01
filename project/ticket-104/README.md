# Ticket 104: Validate Wellman source without floating build dependencies

- **ID**: ticket-104
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-01

## Goal and scope

Replace pip build resolution in the existing metadata job with a pinned,
verified checkout of dependency-free Wellman source. Keep existing triggers
and checks; disable persisted credentials. This applies the reviewed repair
from Intract to the same installation pattern here.

## Acceptance criteria

- [ ] AC-01: The checker runs with site-packages disabled and passes hosted CI.
- [ ] AC-02: Managed governance accepts the infrastructure scope.
- [ ] AC-03: Independent protected delivery merges the tested head.

## Authorization

SESSION_EXECUTION_AUTHORIZATION: the owner requested completion, testing, push
and protected merge of Wellmanifest adoption across Autogrammar repositories.
This authorizes process invocation, not trusted merge approval.

## Tracking boundary

Raw output and receipts remain private external state. Product code and
existing gates remain unchanged; no S3-S5 certification is claimed.
