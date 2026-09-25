# CLAUDE.md — Project Charter for Future Claude Code Sessions

This file tells any future Claude Code session (or human contributor) how to
work in this repository. Read it before writing a lesson, a service, or a
diagram.

## Mission

`feature-engineering-for-ai-from-scratch` teaches AI/ML/Data/GenAI engineers
how production feature engineering actually works, by building the same
system they'll be asked to operate: feature pipelines, point-in-time-correct
joins, offline and online feature stores, streaming aggregations,
embeddings, and drift monitoring. It shares its philosophy with the sibling
project `microservices-for-ai-from-scratch` (first principles, build real
systems, break things on purpose, observe, fix with production patterns) —
never copy that repo's text or diagrams, only its pedagogical spine.

The project tells **one continuous engineering story** (see `ROADMAP.md`):
a single inline pandas script evolves into a full production feature
platform, codenamed **Loom**. Every lesson is a chapter in that story.
Don't bolt on unrelated tutorials.

## Non-negotiable rules

1. **Never create placeholder lessons.** A lesson that isn't runnable,
   tested, and diagrammed is not done — don't merge it half-finished. Fewer,
   excellent lessons beat many shallow ones.
2. **Always run what you write.** Code samples, `docker compose` configs,
   and Makefile targets must be executed and verified before being described
   as working. If you can't run something, say so explicitly in the lesson
   instead of claiming success.
3. **Every lesson updates `PROJECT_STATUS.md`** (Completed / In Progress /
   Planned / Known Issues) in the same change.
4. **Every architecture claim gets a diagram.** Use Mermaid (renders on
   GitHub, stays diffable) for flow/sequence diagrams, plus polished ASCII
   for before/after comparisons. Never leave a multi-component interaction
   described only in prose. Store reusable diagram sources under
   `docs/architecture/{beginner,intermediate,expert}/`.
5. **Every diagram is explained.** State what each box is, and what each
   arrow means in plain language ("Prediction Service → Feature Store:
   before scoring, fetch this entity's latest online features"). No
   unexplained diagrams.
6. **"From scratch" progression is mandatory.** Before introducing a
   production technology, build the naive version first (inline pandas
   before a shared feature library, in-memory dict before Redis, one-off
   script before Airflow-style orchestration, batch join before streaming
   aggregation). The reader must feel *why* the tool exists, not just how to
   configure it.
7. **Follow the lesson format exactly** (see "Lesson format" below). It is
   the pedagogical spine of the whole repo.
8. **Label the level everywhere.** 🟢 Beginner / 🟡 Intermediate /
   🔴 Expert must appear at the top of every lesson file and in nav.
9. **No fabricated data or numbers.** Datasets are either generated
   deterministically (fixed seed, checked into the lesson as code, not as a
   binary) or are small, real, public datasets. Benchmarks under
   `benchmarks/` must be executed scripts, never invented figures.

## Directory structure

```
docs/            cross-cutting docs: architecture diagrams, learning paths,
                 system design, interview questions, ADRs, glossary
lessons/         the curriculum, one directory per numbered lesson,
                 grouped under beginner/ intermediate/ expert/
services/        real, runnable services used across lessons (feature
                 serving API, online store, etc. — introduced from Lesson 07)
infra/           init scripts / config for Postgres, Redis, Kafka, etc.
tests/           pytest suites, one directory per service + integration/
labs/            failure labs (break-it exercises with a fix)
benchmarks/      executable scripts producing real numbers, never fabricated
website/         MkDocs Material site that publishes docs/ + lessons/
```

## Lesson format (required sections, in order)

`Level & metadata header` → Problem → Intuition → Architecture → How It
Works → Naive Implementation → Break It → Observe It → Production Pattern →
Architecture After Fix → Implement It → Test It → Scale It → Common
Mistakes → Interview Mode → Challenge → Summary → Next Lesson.

Header block at the top of every lesson:

```
Level: 🟢 Beginner
Prerequisites: <bullets>
Estimated difficulty: N/5
You will learn: <bullets>
You will build: <one line>
```

## Code standards

- Python 3.12+.
- Type hints everywhere; Pydantic models for request/response schemas once
  services exist (Lesson 07+).
- Config via environment variables (`pydantic-settings`) once services
  exist, never hardcoded hosts/ports.
- Structured logging (JSON) in service code, never bare `print()` — plain
  `print()` is fine in lesson scripts that are meant to be read top-to-
  bottom in a terminal.
- Feature functions are pure: same input always produces the same output,
  no hidden state, no reliance on wall-clock time unless the time is passed
  in explicitly. This is the load-bearing invariant of the whole repo.
- No unnecessary abstraction: a lesson's naive implementation should be as
  simple as the concept allows. Don't add layers "for later."

## Testing requirements

- Every lesson that introduces feature-computation code ships `pytest`
  tests proving the invariant it teaches (e.g. Lesson 00: training-time and
  serving-time feature values are identical for the same raw input).
- Every service ships `pytest` unit tests under `tests/<service>/`.
- Cross-service behavior gets an integration test under
  `tests/integration/`, run against `docker compose`.
- `make test` must run the full suite and pass before a lesson is called
  done.

## Command conventions

`make setup`, `make test`, `make lint` must always work. Additional targets
(`make up`, `make down`, `make logs`, `make load-test`, `make benchmark`)
are added only once the thing they target actually exists — don't ship a
stub target that fails.

## Diagrams requirements

- Mermaid `flowchart` for architecture overviews.
- Mermaid `sequenceDiagram` for request/data flow.
- ASCII for failure propagation and before/after comparisons (these read
  better as plain text in a terminal and in PR diffs).
- Advanced lessons (15+) add a Scaling Architecture diagram.

## Documentation requirements

- `README.md` is the front door: what this is, who it's for, the level
  ladder, how to run the current slice, link to `ROADMAP.md`.
- `ROADMAP.md` holds the full curriculum and the architecture evolution
  (v1-raw-script … v10-production-feature-platform).
- `PROJECT_STATUS.md` is the source of truth for what's actually built vs.
  planned — keep it honest, update it in the same commit as the work.

## When extending this repo

Before adding a new lesson: confirm the previous lesson's code still runs,
confirm the new lesson's "problem" is caused by something the reader already
built (not an abstract description), and confirm there's a diagram before
any implementation section.
