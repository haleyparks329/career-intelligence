# Data Model

The public data model is YAML-based and intentionally explicit. Records carry IDs so generated outputs can trace claims back to source evidence.

## Main Collections

- `identity`: headline, differentiators, anti-positioning rules, and usage cautions.
- `experience`: fictional roles and their linked skills, projects, accomplishments, and evidence.
- `accomplishments`: source-backed work outcomes.
- `resume_bullets`: conservative generated-output candidates.
- `projects`: project-level evidence containers.
- `skills`: capability records with confidence and cautions.
- `stories`: interview-prep examples linked to evidence.
- `values`: value statements with evidence status.
- `interests`: interest statements with evidence status.
- `person_claims`: person-model claims for reasoning.
- `evidence_records`: reusable evidence references.
- `resume_profiles`: target positioning profiles.
- `job_description_metadata`: synthetic role requirements.
- `project_visibility`: public-use guidance for projects.

## Required Fields

The schema expects records to preserve:

- stable IDs
- evidence status
- confidence
- usage cautions
- relationship IDs where relevant

## Validation

The schema validator lives in `src/schema_validation.py`. The test suite validates both the public template and the Andy Barks dataset.

```bash
make test
```

## Design Notes

The model is intentionally not just a resume format. It includes claims that may be useful for role fit or interview prep but unsafe for resume generation.
