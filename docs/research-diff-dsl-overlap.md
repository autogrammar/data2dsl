# Research: Boundary and Overlap Analysis between `data2dsl` and `diff-dsl`

- **Date:** 2026-08-24
- **Related:** ADR-002, ticket-041
- **Status:** Research Note

## 1. Context and Problem Statement

`autogrammar/diff-dsl` and `autogrammar/data2dsl` both operate on structured differences and representations. This note delineates their distinct architectural boundaries to avoid duplicate code or conceptual confusion.

## 2. Core Separation of Concerns

| Dimension | `autogrammar/data2dsl` | `autogrammar/diff-dsl` |
| --- | --- | --- |
| **Primary Purpose** | **Epistemic verification & evidence comparison** | **Declarative mutation & state transformation** |
| **Core Abstraction** | Observation vs Observation $\to$ Comparison Result | Base State + Diff Patch $\to$ New State |
| **Output Type** | Diagnostic outcome (`MATCH`/`CONFLICT`) with SHA-256 provenance | AST transformation instructions (insert/delete/update) |
| **Execution Effect** | **Read-only / pure calculation** (no side-effects) | **Stateful modification / mutation application** |
| **Target Consumers** | Quality gates (`pyqual`), audit logs, reasoning engines | Code patchers, schema migration runners, AST modifiers |

## 3. Shared Vocabulary & Synergies

While their purposes differ, they share a common factual vocabulary:
- **Set differences**: `data2dsl` computes added/removed keys for set metrics; `diff-dsl` can consume these sets to synthesize mutation patches.
- **Hierarchical paths**: Both tools identify target elements via URI-like location paths (`markdown-lines`, `ast-node`, `json-pointer`).

## 4. Architectural Invariant

- `data2dsl` **never** applies changes or generates AST patches.
- `diff-dsl` **never** computes provenance hashes or decides governance pass/fail gates.
- Pipeline composition: `data2dsl` detects and proves discrepancies $\to$ `diff-dsl` compiles and executes the restorative patch.
