# Getting Started

## Requirements

- Python 3.10 or newer
- `pip`

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## Run Tests

```bash
make test
```

## Run The Demo

```bash
make demo
```

The demo uses only the Andy Barks synthetic dataset and writes outputs to:

```text
examples/andy-barks/generated/
```

Expected files:

- `match_report.md`
- `resume.md`
- `interview_prep.md`
- `positioning.md`
- `visualization.svg`
- `demo_data.json`

## Read The Data

Start with:

- `examples/andy-barks/data.yaml`
- `schemas/public_data_schema.yaml`
- `templates/public_data_template.yaml`

The quickest way to understand the current public slice is to compare the dataset with the generated files.
