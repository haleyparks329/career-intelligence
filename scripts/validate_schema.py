from __future__ import annotations

import sys
from pathlib import Path

from src.schema_validation import load_yaml, validate_template


DATASETS = [
    Path("templates/public_data_template.yaml"),
    Path("examples/andy-barks/data.yaml"),
]


def main() -> int:
    schema = load_yaml(Path("schemas/public_data_schema.yaml"))
    failures: list[str] = []
    for path in DATASETS:
        errors = validate_template(schema, load_yaml(path))
        print(f"{path}: {errors}")
        failures.extend(f"{path}: {error}" for error in errors)

    if failures:
        print("Schema validation failed:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
