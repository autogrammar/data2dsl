# Ticket 072: Local re-audit and remaining work only

- **ID**: ticket-072
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-28

## Goal and scope

Re-audit local HEAD 5eb2e32c54a9858215cc770751ebc77d497e2628 after tickets
059-071, then replace docs/AUDYT_KODU_2026-08-28.md with remaining work only.
No application fixes or secret access. The subsequent user request authorizes
publication of the document and required ticket evidence through a separate PR,
without publishing the unrelated local implementation commits or merging.
SESSION_EXECUTION_AUTHORIZATION is supplied by the user's request to recheck
the local repository and update the audit.

## Acceptance criteria

- [x] AC-01: Record the audit-only request and bounded write scope.
- [x] AC-02: Re-run local checks and reproduce unresolved findings.
- [x] AC-03: Remove resolved findings and architecture/history from the audit.
- [x] AC-04: Verify document links and write scope; run and accurately record the managed governance gate, including its publication blocker.

## Result

Replaced the old audit with 11 groups of remaining work, each with evidence
and acceptance conditions. Source and tests were not changed. 127 tests pass;
ruff and contract self-test pass; mypy reports 11 actual source errors.
Isolated wheel still omits the CLI, and focused probes confirm remaining
comparison, normalization, provenance, MCP and example defects.

Final governance result: GOV-BASE-001. The local audit baseline/main is
5eb2e32, while the checker prefers origin/main at 1e7eddd (39 commits behind).
The report is locally delivered; publication validation is not passed. No
base SHA, remote ref or policy was changed to suppress this finding.

The initial delivery was local only. The subsequent push request authorizes a
documentation-only publication rebuilt from origin/main, with original audit
provenance retained. Remain IN_PROGRESS through publication and trusted review.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication preparation

Rebuilt only the document and existing ticket evidence from origin/main 1e7eddd.
The accepted delivery base now describes this real publication checkout, not the
audited source 5eb2e32. The 39 local code commits are excluded. No merge is authorized.

Latest SESSION_EXECUTION_AUTHORIZATION: user explicitly requested immediate merge of the document.
Merge is authorized only through the protected GitHub boundary; no admin bypass or self-approval.
While preparing publication, main advanced to bf98b515a144eb0cb64b65482549e396fbee036d via another PR. Merged that base into this branch, resolving only the audit conflict in favor of the updated report. Delivery base updated to this actual base; audit source remains 5eb2e32.
Read-only workspace inventory found 38 pre-existing non-default branch findings across the workspace; preserved unknown/unique data. Goal CLI is unavailable; terminal lifecycle not claimed passed.
