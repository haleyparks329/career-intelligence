# Career Intelligence

> **Model the person, not just the job description.**

Career Intelligence is a local-first framework for representing a career as structured, source-backed evidence and reasoning over it without inventing experience.

Instead of treating a resume as the source of truth, the framework separates:

- what a person has actually done
- what evidence supports each claim
- which skills transfer across roles
- how capability fit differs from person and environment fit
- what is safe to emphasize
- what should not be overstated

Resumes, match reports, positioning notes, interview preparation, and visualizations become explainable views over the same underlying career model.

This repository contains a reusable engine slice, public schemas and templates, default configuration, validation tooling, and a fully synthetic example persona named **Andy Barks**.

## Why This Exists

Most job-search tools begin with a job description and ask how closely a candidate can be rewritten to match it.

Career Intelligence starts somewhere else:

> What is true about this person, what supports it, and how should that truth be represented for this opportunity?

That distinction matters for career changers, nonlinear careers, people whose strongest work never made it onto a resume, and anyone who wants useful automation without turning inference into fiction.

## Core Principles

- **Evidence before language.** Generated claims should trace back to source records.
- **Facts and wording stay separate.** Accomplishments are career evidence; resume bullets are reusable representations of that evidence.
- **Capability fit and person fit are different questions.** A person may be able to do a role without thriving in its environment.
- **Transferable skills matter.** Job titles are evidence, not the whole model.
- **Uncertainty stays visible.** Reflection, conflicting evidence, gaps, confidence, and usage cautions are first-class data.
- **Person-model claims have boundaries.** Work style and preferences can support reasoning, but they must not silently become credentials or accomplishments.
- **Human review remains necessary.** The system helps organize and reason over evidence; it does not replace judgment.

Read more in [docs/philosophy.md](docs/philosophy.md).

## How It Works

```text
Acquire
  ↓
Normalize
  ↓
Review
  ↓
Reason
  ↓
Generate
  ↓
Visualize
```

Career information may come from resumes, interviews, project notes, portfolios, LinkedIn exports, performance reviews, Git history, or other user-provided sources. The public repository currently focuses on the normalized model, reasoning layer, generated outputs, and safety boundaries.

```text
Source records
    ↓
Evidence-backed career model
    ├── identity
    ├── experience
    ├── accomplishments
    ├── projects
    ├── skills
    ├── stories
    ├── values and interests
    └── person-model claims
          ↓
Reasoning
    ├── capability fit
    ├── transferable skills
    ├── person and environment fit
    ├── evidence gaps
    ├── positioning
    └── interview preparation
          ↓
Generated views
    ├── match report
    ├── resume
    ├── positioning notes
    ├── interview prep
    └── visualization
```

See [docs/architecture.md](docs/architecture.md) and [docs/acquisition-workflow.md](docs/acquisition-workflow.md).

## Quick Start

Career Intelligence requires Python 3.10 or newer.

```bash
git clone https://github.com/haleyparks329/career-intelligence.git
cd career-intelligence
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
make validate
```

`make validate` runs the complete public validation suite:

- privacy scan
- schema validation
- Markdown link validation
- dependency check
- test suite
- synthetic demo generation

Run only the demo with:

```bash
make demo
```

Generated demo outputs are written to:

```text
examples/andy-barks/generated/
```

## Meet Andy Barks

Andy Barks is a completely fictional example used to demonstrate the framework without exposing or paraphrasing a real person's private career model.

His synthetic career moves through library services, education, and curriculum design:

```text
Library Assistant
    ↓
Public Librarian
    ↓
School Librarian
    ↓
Middle School Teacher
    ↓
Curriculum Designer
```

Andy is intentionally not a software engineer. His example demonstrates that Career Intelligence can reason about:

- nonlinear careers
- transferable skills across different job titles
- library and education work
- evidence-backed accomplishments
- reflection-only person claims
- conflicting evidence
- strong and partial role matches
- claims prohibited from resume generation
- small AI-assisted tools built by a non-software professional

Start with [`examples/andy-barks/data.yaml`](examples/andy-barks/data.yaml).

## What the Demo Produces

The deterministic demo generates:

- a role-match analysis
- capability-fit and person-fit views
- selected evidence-backed resume bullets
- positioning guidance
- interview-preparation notes
- usage caveats and risk flags
- a small career visualization

A generated output can distinguish between concepts such as:

```text
verified evidence
reflection or recollection
strong and weak evidence
genuine gaps
safe to emphasize
do not overstate
resume-safe claims
resume-prohibited claims
```

The goal is not merely to produce polished copy. The goal is to preserve the reasoning behind it.

## Repository Map

```text
career-intelligence/
├── config/                       # public default reasoning configuration
├── docs/                         # architecture, safety, workflow, and data-model guides
├── examples/andy-barks/          # fully synthetic example career model
├── schemas/                      # public schema definitions
├── scripts/                      # validation and privacy helpers
├── src/                          # generic reasoning and generation engine
├── templates/                    # starter public data templates
├── tests/                        # deterministic test suite
├── visuals/                      # public visualization helpers
├── Makefile
└── pyproject.toml
```

Key implementation files include:

- [`src/select_bullets.py`](src/select_bullets.py) — source-backed evidence ranking
- [`src/match.py`](src/match.py) — capability and role-match analysis
- [`src/position.py`](src/position.py) — evidence-aware positioning
- [`src/prep.py`](src/prep.py) — interview-preparation analysis
- [`src/render_resume.py`](src/render_resume.py) — conservative resume rendering
- [`src/demo.py`](src/demo.py) — deterministic synthetic workflow
- [`schemas/public_data_schema.yaml`](schemas/public_data_schema.yaml) — public data schema
- [`templates/public_data_template.yaml`](templates/public_data_template.yaml) — starter template

## Commands

```bash
make test              # run the test suite
make demo              # generate Andy Barks demo outputs
make privacy-scan      # scan for prohibited private content
make schema-check      # validate the public dataset
make link-check        # validate local Markdown links
make dependency-check  # verify installed dependencies
make validate          # run all validation and demo targets
make ci                # CI alias for full validation
```

There is not yet an implemented `/acquire` CLI in this public release. Conversational interviewing and other evidence-acquisition methods are documented as framework patterns in [docs/acquisition-workflow.md](docs/acquisition-workflow.md).

## Data Model

The public schema includes:

- identity
- experience
- accomplishments
- reusable resume bullets
- projects
- skills
- stories
- values and interests
- evidence records
- person-model claims
- resume profiles
- job-description metadata
- project visibility

Entities use stable IDs and ID-based relationships so accomplishments, evidence, skills, stories, projects, claims, and generated views remain traceable.

See [docs/data-model.md](docs/data-model.md).

## Evidence and Provenance

Evidence provenance is part of the model, not an annotation added after generation.

The framework can preserve:

- source references
- evidence type
- evidence strength
- confidence
- review status
- conflicting records
- usage cautions
- links between claims and accomplishments

This allows an output to explain not only *what* it recommends, but *why* the recommendation is supportable.

See [docs/evidence-and-provenance.md](docs/evidence-and-provenance.md).

## Person-Model Safety

Person-model claims can support:

- role and environment matching
- positioning
- interview preparation
- questions to investigate
- potential misinterpretation risks

Resume generation is deliberately stricter.

Reflection-only claims, preferences, personality descriptions, and explicitly prohibited claims must not become titles, credentials, accomplishments, or resume bullets without appropriate evidence.

See [docs/person-model-safety.md](docs/person-model-safety.md).

## Privacy

This public repository contains synthetic data only.

Keep real career records outside a public clone, including:

- raw resumes and source documents
- contact information
- real job descriptions
- application history
- generated application materials
- private interview notes
- person-model reflections
- private configuration and calibration
- graphs derived from a real person's model

The repository includes a privacy scan to help detect accidental leakage, but users remain responsible for reviewing what they commit.

See [docs/privacy-boundaries.md](docs/privacy-boundaries.md).

## Editor and Obsidian Use

Career Intelligence is editor-agnostic. Its source data is stored in plain-text YAML and Markdown, so it can be used with VS Code, Neovim, Obsidian, or another local knowledge workflow.

Obsidian is an optional interface, not a requirement and not the core architecture. A future integration guide may cover vault layout, graph views, generated-note separation, and public/private publishing boundaries.

## Project Status

**Version:** `0.1.0`

The current release includes:

- generic source-backed reasoning engine
- public schemas and starter templates
- configurable public defaults
- synthetic Andy Barks dataset
- deterministic match, positioning, prep, resume, and visualization outputs
- automated privacy scanning
- schema and Markdown-link validation
- standalone installation validation
- 18 passing tests

This is an early public foundation, not a finished career platform. The current emphasis is on a trustworthy data model, explainable reasoning, and safe extension points.

Likely next areas include:

- guided evidence acquisition
- additional synthetic career examples
- richer visualization
- broader career-domain testing
- optional editor and Obsidian recipes
- more configurable reasoning rules

## Contributing

Small, evidence-preserving contributions are welcome, especially improvements to:

- schema clarity
- provenance and safety behavior
- tests
- documentation
- synthetic examples
- domain-neutral reasoning
- privacy safeguards

Please keep real personal career data out of issues, pull requests, fixtures, and examples.

## License

A software license has not yet been added. Until one is selected, the repository is publicly viewable but should not be treated as licensed for reuse, modification, or redistribution.
