# `make privacy-scan`

Run the public privacy scan.

```bash
make privacy-scan
```

The scan fails on:

- private identifier patterns
- private local path patterns
- email addresses other than reserved example addresses
- phone-number-like strings
- prohibited private directories
- generated career outputs outside the approved Andy Barks synthetic output path

The scan intentionally does not include a sensitive private denylist. Detailed private denylist values should remain outside the public repository.
