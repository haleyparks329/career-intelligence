# Architecture

Career Intelligence is organized around a simple boundary: reason from structured evidence first, then generate outputs only from what the evidence supports.

## Current Public Components

```text
Synthetic data
  -> schema validation
  -> evidence ranking
  -> match analysis
  -> person-model reasoning
  -> conservative generation
  -> demo artifacts
```

## Data Layer

The public data layer lives in `examples/andy-barks/data.yaml`. It contains one fictional person, fictional work history, fictional evidence records, and fictional target-role metadata.

The schema and template files are:

- `schemas/public_data_schema.yaml`
- `templates/public_data_template.yaml`

## Reasoning Layer

The reasoning layer is made of small modules:

- `src/select_bullets.py` scores evidence against role keywords and profile preferences.
- `src/match.py` combines capability matching with person-model fit.
- `src/position.py` turns safe person-model claims into positioning angles.
- `src/prep.py` links claims and stories for interview preparation.
- `src/person_model.py` enforces usage boundaries for person-model claims.

## Generation Layer

The generation layer is conservative. `src/render_resume.py` can polish selected evidence, but the demo keeps resume bullets tied to source-backed bullet or accomplishment records.

`src/demo.py` orchestrates the public example and writes generated files under `examples/andy-barks/generated/`.

## Boundary Rules

- Evidence records can become match signals.
- Resume bullets must come from source-backed bullets or accomplishments.
- Reflection-only claims can inform prep or positioning but should not become resume bullets.
- Claims with resume cautions remain excluded from resume generation.
- Generated artifacts should clearly identify themselves as synthetic when they are part of the public demo.
