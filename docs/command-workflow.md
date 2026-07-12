# Command Workflow

This public slice exposes two Make targets.

## Test

```bash
make test
```

Runs the test suite with the local virtual environment when present.

## Demo

```bash
make demo
```

Runs the Andy Barks synthetic demo and writes outputs to:

```text
examples/andy-barks/generated/
```

Generated outputs:

- match report
- resume
- interview prep
- positioning
- visualization
- inspectable JSON data

## Privacy Scan

```bash
make privacy-scan
```

Scans the public worktree for private identifiers, private paths, email and phone patterns, prohibited private directories, and generated career outputs outside approved synthetic paths.

## CI

```bash
make ci
```

Runs the full public validation target.

## Validate

```bash
make validate
```

Runs privacy scanning, schema validation, Markdown link checks, dependency checks, tests, and the synthetic demo.

## Not Implemented In This Public Slice

The documentation describes an acquisition lifecycle, but there is no implemented public acquisition command yet. Do not assume `/acquire` or similar commands exist unless they are added and tested in a later phase.

Private application workflows, private resume generation, and real job-specific pipelines are outside this public demo.
