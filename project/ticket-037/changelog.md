# Ticket Changelog (ticket-037)

## [0.1.0] - 2026-08-24

- Implemented `PlanfileAdapter` (`semcod.planfile`) for ticket counts and ID sets.
- Implemented `DetaAdapter` (`semcod.deta`) for infrastructure topology services and ports.
- Implemented `IntentContractAdapter` (`subactor.intent-contract-dsl`) for deliverables, obligations, and parties.
- Added raw payload dispatch in `Data2DslSkill` for `planfile`, `deta`, and `intent_contract`.
- Added 6 new unit and skill test cases in `tests/test_golden_case_e2e.py` and `tests/test_skill.py` (31 total passing).
- Verified deterministic governance gate passes.
