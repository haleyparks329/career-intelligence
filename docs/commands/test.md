# `make test`

Run the public test suite.

```bash
make test
```

The target uses `.venv/bin/python` when a local virtual environment exists, otherwise it falls back to `python3`.

The tests cover:

- keyword extraction
- bullet ranking and selection
- match reasoning
- person-model resume safety
- positioning and interview-prep outputs
- default configuration loading
- public schema and template validation
- Andy Barks dataset validation
- synthetic demo output generation
