# Project Status

Last updated: 2026-09-25

This file is the source of truth for what's actually built vs. planned.
Update it in the same change as any lesson, service, or doc work.

## Completed

**Lessons — 🟢 Beginner**

- `00-foundations` — synthetic customer/orders dataset generator
  (`generate_data.py`, fixed seed, no network dependency); a naive
  implementation (`naive_train.py` + `naive_serve.py`) that demonstrates a
  real, executed train/serve skew bug caused by two independent
  re-implementations of "the same" features; the fix (`feature_lib.py` +
  `train.py` + `serve.py`) — one shared, pure feature library used by both
  paths, with a pytest regression test proving the skew is gone. Complete,
  runnable.

## In Progress

- None currently — see "Planned" for next milestone.

## Planned (not started)

- Lessons 01–06 (Feature Functions & Testing through Docker &
  Reproducibility).
- Lessons 07–14 (Online Store through Observability) — this repo's scope
  currently ends at Lesson 14 (Beginner + Intermediate only; Expert tier is
  explicitly out of scope, see `ROADMAP.md`).
- `docs/architecture/{beginner,intermediate}/` diagrams beyond Lesson 00's
  inline Mermaid diagram.
- `docs/learning-paths/`, `docs/interview/`, `docs/system-design/`,
  `docs/glossary/`, `docs/adr/` — no content yet.
- `services/` — first service (feature serving API) arrives in Lesson 12.
- `infra/` — Postgres/Redis/Kafka init config arrives with Lessons 05, 07,
  08 respectively.
- `labs/failure-labs/` — none yet.
- `benchmarks/` — directory doesn't exist yet, no scripts.
- `website/` — MkDocs Material site not scaffolded yet.
- CI: no `.github/workflows/` yet.

## Known Issues

- None yet — Lesson 00 has no known gaps relative to what it claims to
  teach. Its "Scale It" section is explicit about what it deliberately does
  not solve (no registry, no versioning, no point-in-time correctness, all
  in-memory) — that's the motivation for Lessons 01–05, not a defect.
