# Granular Spec Directive

Every component must be fully specified — schema, validation rules, versioning behavior, storage layer, access patterns — before wiring anything together.

## Why

The architecture doc shows how everything connects. But connections only work if each component's interface is precisely defined. Two components that both call something a "Claim" will silently corrupt data if their Claim schemas differ. This has already happened with ROs (some are single-source, some are multi-source, the distinction was implicit).

## Process

For every entity in the data model, produce:
1. **JSON Schema** — what a valid instance looks like
2. **Validation rules** — what makes an instance acceptable or rejectable
3. **Versioning behavior** — what triggers a version bump, how history is stored
4. **Storage** — where it lives (git file, D1, R2) and how it's indexed
5. **Access patterns** — how it's read and written by each factory
6. **Migration policy** — what happens when the schema changes

## Priority Order

1. Research Object (RO) — the core knowledge unit
2. Essay Object (EO) — the bridge between research and production
3. Truth Map Question — the Bayesian node
4. Claim — the atomic evidence unit
5. Translation Object (TO) — Sanskrit pipeline output
6. Source Object (SO) — cleaned source text
7. Edge Weight — the TPN graph
8. User Profile — the Satsang user
9. Session Log — what the Dreaming Loop consumes
10. Render Version — HITL iteration history
