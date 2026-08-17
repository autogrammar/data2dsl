# ADR-001: Twin `Observation` and `EvidenceRef` compatibility

- **Status:** Accepted for planning
- **Date:** 2026-08-17
- **Decision owner:** `data2dsl` ticket-002
- **Inspected repository:** `subactor/twin`
- **Pinned revision:** `a3a8b759dc87bc4398f86bf8df25a16f1309314e`

## Decision question

Can `data2dsl` reuse the current `subactor/twin` `Observation` and
`EvidenceRef` contracts as its neutral input and evidence boundary without
copying them, depending on the Twin runtime, or inventing incompatible
semantics?

## Verdict

EXTEND

The existing messages are the preferred lineage and a strong foundation, but
they are not sufficient as-is for deterministic, language-neutral data
comparison. `data2dsl` must not fork or silently reinterpret them. A later,
separately authorized contract ticket must define an additive, versioned and
effect-free extension or profile before comparator implementation begins.

This decision does not authorize a change to `subactor/twin`, a dependency on
its runtime, a final DSL, an adapter, or product implementation.

## Evidence baseline

All evidence below was inspected from one clean checkout at the pinned
revision. Git blob identifiers make each artifact independently verifiable.

| Evidence class | Artifact | Git blob |
| --- | --- | --- |
| Protobuf contract | `proto/twin/v1/twin.proto` | `03cd991fd42c9e57bc587dcac403b466b60e5e6e` |
| Normative standard | `spec/TWIN_STANDARD.md` | `78e87890c6b4937840930aa059b079402095b192` |
| Reference profile | `profiles/generic-twin.json` | `167e6560660d53a56aa47ecb9ef1014941c97ffe` |
| Validator/generator | `src/twin_standard.py` | `dbc3919bbe47be0fe4b4dae2ac67898b8571e97e` |
| Tests | `tests/test_twin_standard.py` | `a6cbec3febc8ee3c1938764b0a958ce3ad5ad877` |
| Package metadata | `pyproject.toml` | `1df981ce8f924da1cdca17a3201cf2125c255211` |
| Maturity statement | `README.md` | `f759b2af7eb34c9f25163e9e4bd5577d41b028bb` |
| Version marker | `VERSION` | `0d4d1249434dba8d7fcb8949a2e361f70308cc48` |

The package is currently `0.1.0.dev0` / `0.1.0-dev`, and its README says the
initial contract is under review. This is evidence of contract maturity, not a
reason to discard the lineage.

## Implemented contract

### Protobuf

`EvidenceRef` contains `evidence_id`, `aggregate_id`, `target_uri`,
`media_type`, and `digest_sha256` as bytes.

`Observation` contains `observation_id`, `aggregate_id`, `target_uri`,
`metric`, `ObservationStatus status`, `google.protobuf.Any value`,
`observed_at` and `expires_at` timestamps, and repeated `EvidenceRef evidence`.

`ObservationStatus` distinguishes `OBSERVED`, `UNEVALUABLE` and `EXPIRED`.
Publishing is exposed as `PublishObservationCommand` and an RPC that emits
`ObservationPublished`; that command path is part of the state-changing Twin
model, not a neutral library boundary for `data2dsl`.

### Standard and profile

Section 2.3 of the standard requires observations to join to an aggregate and
target URI, carry observed time and expiry, and carry evidence with the same
join keys. Missing or unavailable measurements are `UNEVALUABLE` and must not
be treated as healthy. Reporting evidence is explicitly separate from an
enforcing decision.

The reference profile reinforces this with `evidenceRequired: true`, join
keys `aggregate_id` and `target_uri`, `unevaluableState: UNEVALUABLE`, and
`UNEVALUABLE` excluded from healthy states. Those invariants align with
reuse-first provenance and with the required separation between source
observation state and comparison result.

### Validator and tests

The validator checks that protobuf messages and enum members exist, but its
required field sets are intentionally structural:

- `EvidenceRef`: `evidence_id`, `aggregate_id`, `target_uri`;
- `Observation`: `observation_id`, `aggregate_id`, `target_uri`, `status`,
  `evidence`.

It does not structurally require `metric`, `value`, time fields, `media_type`
or `digest_sha256`, and it does not validate message instances. Tests cover
profile invariants, the required protobuf surface, `UNEVALUABLE`, generation
and transport declarations. They do not define cross-language `Any`
canonicalization or scalar/set equality for a data comparator.

At the pinned revision, this command was run on Windows:

```text
PYTHONPATH=src python -m pytest -q -p no:cacheprovider
```

Result: `73 passed, 7 subtests passed, 1 failed`. The only failure is
`test_generation_emits_only_declared_contract_files`: expected POSIX
`proto/twin/v1/twin.proto` but discovered the Windows representation
`proto\\twin\\v1\\twin.proto`. It is unrelated to the semantics under this
decision, but prevents claiming a completely green external checkout.

## Field-level fit

### `Observation`

| Field | Fit for `data2dsl` | Consequence |
| --- | --- | --- |
| `observation_id` | Reusable identity slot; uniqueness/canonical form is unspecified here. | Preserve it; an extension must state identity rules if used for reproducibility. |
| `aggregate_id` | Useful join key but coupled to a Twin aggregate. | Accept when supplied; do not require a live Twin aggregate or runtime. |
| `target_uri` | Strong subject join key under the profile. | Reuse it, while defining URI canonicalization and the supported subject vocabulary. |
| `metric` | Useful label, but no versioned vocabulary, unit or dimensions. | Extend with metric identity, unit and dimensions. |
| `status` | Correctly models source availability. | Preserve it; never overload it with comparison outcomes such as equal/different. |
| `value` | `Any` is extensible but underspecified for neutral comparison. | Define an allowlisted typed scalar/set model, type URLs and canonical equality. |
| `observed_at` | Useful provenance time. | Preserve it as source observation time. |
| `expires_at` | Useful freshness boundary. | Preserve it, but add an explicit query/window model where needed. |
| `evidence` | Correct provenance attachment point. | Reuse the relationship and strengthen evidence reproducibility below. |

### `EvidenceRef`

| Field | Fit for `data2dsl` | Consequence |
| --- | --- | --- |
| `evidence_id` | Useful stable reference, but resolution semantics are absent. | Preserve it and define how an authorized consumer resolves it. |
| `aggregate_id` | Supports the normative join, but inherits Twin coupling. | Keep as a join key without requiring runtime access. |
| `target_uri` | Strong subject join key, not an evidence locator. | Preserve it; do not pretend it locates the source bytes. |
| `media_type` | Correct content descriptor, weakly enforced by the validator. | Require and validate it in the extension/profile. |
| `digest_sha256` | Correct immutable content check, but length/presence are weakly enforced. | Require a 32-byte digest and verify it before evidence is accepted. |

For reproducible data acquisition, the current message lacks a normative
source locator/revision, normalized query parameters, extractor identity and
version, and optional record/span/pagination coordinates. Those additions
must not expose secrets; credentials remain outside the serialized contract.

## Required extension boundary

A future contract proposal must provide all of the following before the
`data2dsl` comparator can depend on it:

1. An effect-free observation/evidence profile or additive messages usable
   without Twin commands, events, authority checks or storage.
2. Deterministic typed values for the initial scalar and set cases, including
   allowed `Any` type URLs, ProtoJSON form, nullability, numeric precision,
   ordering and equality rules.
3. Versioned subject and metric identities, units, dimensions and an explicit
   observation/query window where a single timestamp is insufficient.
4. A resolvable evidence descriptor with immutable source revision, normalized
   query/extraction metadata, content type and verified digest.
5. Instance validation and cross-language fixtures proving that equivalent
   values serialize and compare identically.
6. A stable released contract revision before it becomes a required external
   dependency.

Comparison outcomes must remain separate from `ObservationStatus`. For
example, `MATCH`, `MISMATCH` or comparison `UNEVALUABLE` belong to a result
contract whose inputs point back to the source observations and evidence.

## Why not `REUSE AS-IS`

The schema proves structural presence, not the value semantics required by a
deterministic comparator. Reusing it without an extension would force
`data2dsl` to invent private meanings for `Any`, metrics, units, sets and
evidence resolution. That would violate the reuse-first rule while appearing
to comply with it.

## Why not `REJECT`

The identity, target, time, availability and evidence concepts already match
the intended architecture. The standard also makes the critical distinction
between unavailable data, health and enforcement. Rejection would duplicate
good contract lineage and create unnecessary translation work.

## Consequences for `data2dsl`

- Treat the capability-map candidate as `EXTEND`, not as implemented or
  reusable as-is. Updating that map requires its own authorized ticket.
- Do not add a runtime dependency on `subactor/twin` and do not copy or fork
  these protobuf messages.
- Block comparator implementation on deterministic typed-value and
  subject/metric/window semantics.
- Preserve `aggregate_id` and `target_uri` joins when present, without
  assuming that a Twin service is running.
- Preserve content digests and the separation between source status,
  comparison outcome and enforcing action.
- Any proposal to change `subactor/twin`, `wellmanifest/dsl` or another
  repository requires a separate ticket and explicit authority.

## Revisit triggers

Re-evaluate this decision when `subactor/twin` publishes a stable revision
that adds the required neutral value/evidence semantics, or when a different
existing Wellmanifest contract demonstrably supplies them without creating a
second competing model.
