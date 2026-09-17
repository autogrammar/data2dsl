# Ticket Changelog (ticket-094)

## [0.1.0] - 2026-09-17

- Initial governance scaffold created.
- No human participant identity or content was generated.

## [0.2.0] - 2026-09-17

- Completed intent delivery contract for the 0.16.2 -> 0.20.32 standard
  adoption, including the `standardAdoption` revision declaration
  (63a03d0c -> b6ba9c21).
- Adopted wellmanifest/new-project 0.20.32 standard-managed projection
  (94 verified managed payload updates, lock regenerated).
- Migrated extendable carriers: manifest ticket policy normalized,
  governance workstream now owns `.gitignore`, required-checks moved to the
  managed governance workflow.
- Declared `[tool.wellmanifest]` and the governance pytest plugin in
  `pyproject.toml`; activated the managed clone hook.
