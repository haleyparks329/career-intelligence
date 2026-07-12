# `make validate`

Run the full public validation target.

```bash
make validate
```

The target runs:

- privacy scan
- schema validation
- Markdown link check
- dependency check
- test suite
- synthetic demo

This target does not initialize Git, create a repository, add a remote, or publish anything.
