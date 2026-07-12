# Career Intelligence

> Model the person, not just the job description.

Career Intelligence is a public-safe framework for source-backed career reasoning. It separates evidence, role matching, person-model reasoning, and generated career materials so that resumes and interview prep stay grounded in what the data can actually support.

This repository currently contains a reusable engine slice, public schemas, default configuration, and a fully synthetic example persona named Andy Barks.

## What Career Intelligence Is

Career Intelligence helps reason about fit between a person and a role. It can compare target-role requirements to evidence-backed accomplishments, surface transferable skills, preserve caveats, and generate demo outputs such as match reports, resumes, positioning notes, interview prep, and a small visualization.

The framework is intentionally conservative. It treats career material as evidence-sensitive, not as generic marketing copy.

## Core Philosophy

- Evidence first: generated claims should trace back to source records.
- Person model second: work style, values, and positioning can guide reasoning, but should not become resume claims without enough evidence.
- Gaps stay visible: missing or weak evidence should remain explicit.
- Synthetic examples stay synthetic: public demos should not expose or paraphrase a real private career model.

See [docs/philosophy.md](docs/philosophy.md).

## Architecture

The current public slice includes:

- `examples/andy-barks/data.yaml`: synthetic career dataset.
- `schemas/public_data_schema.yaml`: public data model schema.
- `templates/public_data_template.yaml`: starter data template.
- `src/select_bullets.py`: source-backed evidence ranking.
- `src/match.py`: role match analysis.
- `src/position.py`: positioning analysis.
- `src/prep.py`: interview prep analysis.
- `src/render_resume.py`: conservative resume rendering helpers.
- `src/demo.py`: deterministic synthetic demo workflow.

See [docs/architecture.md](docs/architecture.md).

## Installation

Use Python 3.10 or newer.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## Quick Start

Run the test suite:

```bash
make test
```

Run the synthetic demo:

```bash
make demo
```

Demo outputs are written to:

```text
examples/andy-barks/generated/
```

## Synthetic Example

Andy Barks is a completely fictional curriculum designer and library educator. The dataset includes fictional employers, dates, projects, accomplishments, claims, caveats, and generated outputs.

The synthetic example is designed to exercise:

- high-confidence evidence-backed claims
- reflection-only claims
- conflicting evidence
- resume-prohibited person-model claims
- weak skill gaps
- strong and partial role matches
- transferable skills that matter more than job titles

## Commands

Implemented commands:

```bash
make test
make demo
make privacy-scan
make validate
make ci
```

There is no implemented acquisition CLI in this public slice. The acquisition lifecycle is documented as a framework pattern in [docs/acquisition-workflow.md](docs/acquisition-workflow.md).

See [docs/command-workflow.md](docs/command-workflow.md).

## Data Model

The public data model includes identity, experience, accomplishments, resume bullets, projects, skills, stories, values, interests, person claims, evidence records, resume profiles, job description metadata, and project visibility.

See [docs/data-model.md](docs/data-model.md).

## Evidence And Provenance

Each generated output should be explainable from source records. Evidence status, confidence, and usage cautions are part of the data model rather than afterthoughts.

See [docs/evidence-and-provenance.md](docs/evidence-and-provenance.md).

## Person-Model Safety

Person-model claims can support role matching, positioning, and interview prep, but resume generation is stricter. Reflection-only claims and explicitly prohibited claims should not become resume bullets.

See [docs/person-model-safety.md](docs/person-model-safety.md).

## Privacy

This public repository is designed around synthetic data. Real private career records, application materials, contact details, generated private resumes, and private configuration should stay outside the public dataset.

See [docs/privacy-boundaries.md](docs/privacy-boundaries.md).

## Project Status

Current status: public migration in progress.

Implemented in this public worktree:

- generic engine slice
- default public configuration
- public schemas and templates
- Andy Barks synthetic dataset
- deterministic demo workflow
- generated synthetic demo artifacts

Not yet complete:

- public documentation review
- automated privacy and CI safeguards
- full standalone validation
- clean public repository initialization
- final human review

## Contributing

This repository is not ready for broad contribution yet. The useful contribution shape, once safeguards are complete, will be small, evidence-preserving improvements to schema clarity, reasoning behavior, docs, tests, and synthetic examples.

## License

License is not finalized in this migration worktree.
