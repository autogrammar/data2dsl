# ADR-005: Autonomous Agent Feedback Feeds (Doctor Diagnostic & Koru Remediation)

- **Status:** Accepted
- **Date:** 2026-08-25
- **Decision owner:** `data2dsl` ticket-045
- **Related tickets:** ticket-015, ticket-041, ticket-043, ticket-044, ticket-045

## Context and Decision Question

`data2dsl` deterministically compares multi-source observations and produces cryptographic comparison bundles containing matched, conflicting, missing, and unevaluable metrics with exact deltas.

Autonomous agents and self-healing systems across the ecosystem require specialized representations of these discrepancies:
1. **`subactor/doctor-agent` & Diagnostic Triage:** Requires prioritized discrepancy profiles where symptoms are sorted by delta magnitude, classified by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`), and summarized for rapid root-cause diagnosis.
2. **`semcod/koru` Closed-Loop Self-Healing:** Operates on the `DETECT → PLAN → EXECUTE → VERIFY → HEAL` loop and requires structured `remediation-intent/v1` manifests specifying machine-actionable repair actions (`synchronize_metric`, `restore_missing_entries`, `resolve_conflict`) with pinned pre-repair SHA-256 evidence digests.

How should `data2dsl` expose its factual comparison bundles to diagnostic agents (`doctor-agent`) and remediation controllers (`koru`) without coupling factual verification to agent-specific reasoning or mutation logic?

## Decision

`data2dsl` implements two dedicated, stateless formatting modules that project canonical comparison bundles into autonomous agent feed contracts:

1. **Diagnostic Profile Feed (`src/data2dsl_doctor.py` & CLI `feed-doctor`):**
   - **`DiagnosticProfileFormatter` / `format_diagnostic_profile()`**: Transforms comparison bundles into `new-project.diagnostic-profile/v1` documents.
   - **Symptom Extraction & Severity Classification:**
     - `CONFLICT` and `UNEVALUABLE` items are mapped to symptoms with classified severities based on delta magnitude and metric criticality.
     - Symptoms are deterministically sorted by absolute delta magnitude descending.
   - **Severity Summary & Recommendations:** Generates counts (`critical`, `high`, `medium`, `low`, `info`) and actionable diagnostic notes.
   - **Verifiable Provenance:** Includes full SHA-256 evidence digests for both observation sources.

2. **Remediation Intent Feed (`src/data2dsl_remediation.py` & CLI `feed-koru`):**
   - **`RemediationIntentFormatter` / `format_remediation_intent()`**: Transforms comparison bundles into `new-project.remediation-intent/v1` payloads for `semcod/koru`.
   - **Action Item Generation:**
     - `CONFLICT`: maps to `synchronize_metric` or `resolve_conflict` actions with target values and discrepancy magnitudes.
     - `MISSING_LEFT` / `MISSING_RIGHT`: maps to `restore_missing_entries` actions.
     - `MATCH`: classified as `SATISFIED` without requiring actions.
     - `UNEVALUABLE`: classified as `BLOCKED` with diagnostic details.
   - **Status Mapping & Pinned Preconditions:** Remediation items are marked as `PROPOSED`, `SATISFIED`, or `BLOCKED` with pinned subject URIs and evidence digests.

3. **CLI & Skill Boundary Exposure:**
   - Both feeds are accessible via dedicated CLI subcommands:
     - `data2dsl feed-doctor -b comparison_bundle.json -o diagnostic_profile.json`
     - `data2dsl feed-koru -b comparison_bundle.json -o remediation_intent.json`
   - Exposed as tool interfaces in `Data2DslSkill` and URI-based routings for orchestrators.

## Consequences

- **Strict Separation of Concerns:** `data2dsl` remains strictly factual and deterministic. It generates diagnostic symptoms and repair intentions based purely on observed deltas, leaving mutation, scheduling, and policy execution to `doctor-agent` and `koru`.
- **Closed-Loop Verification:** `koru` can invoke `data2dsl` in the `VERIFY` phase to generate a fresh diagnostic profile and remediation intent, confirming whether a prior repair succeeded.
- **Cryptographic Auditability:** Every symptom and remediation action references immutable SHA-256 evidence digests from raw observation sources.
- **Interoperability:** Standard JSON schemas allow any agent in the ecosystem (Cursor, Claude, Windsurf, doctor-agent, koru) to consume verification results seamlessly.
