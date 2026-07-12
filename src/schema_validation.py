from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


TYPE_CHECKS = {
    "list": list,
    "map": dict,
    "string": str,
}


def load_yaml(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return data


def validate_template(schema: Mapping[str, Any], template: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    record_types = schema.get("record_types", {})
    enums = schema.get("enums", {})
    reference_fields = schema.get("reference_fields", {})
    ids_by_collection = _ids_by_collection(schema, template, errors)

    for record_type, spec in record_types.items():
        collection = spec["collection"]
        if collection not in template:
            errors.append(f"Missing collection `{collection}` for `{record_type}`.")
            continue
        records = _records(template[collection])
        for index, record in enumerate(records):
            prefix = f"{collection}[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{prefix} must be a mapping.")
                continue
            for field in spec.get("required", []):
                if field not in record:
                    errors.append(f"{prefix} missing required field `{field}`.")
            for field, expected in spec.get("fields", {}).items():
                if field not in record:
                    continue
                _validate_value(errors, prefix, field, record[field], expected, enums)
                _validate_reference(
                    errors,
                    prefix,
                    field,
                    record[field],
                    reference_fields.get(field),
                    ids_by_collection,
                )

    return errors


def _records(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return [value]


def _ids_by_collection(
    schema: Mapping[str, Any],
    template: Mapping[str, Any],
    errors: list[str],
) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {}
    for spec in schema.get("record_types", {}).values():
        collection = spec["collection"]
        seen = ids.setdefault(collection, set())
        if collection not in template:
            continue
        for index, record in enumerate(_records(template[collection])):
            if not isinstance(record, dict):
                continue
            record_id = record.get("id") or record.get("project_id")
            if not isinstance(record_id, str) or not record_id:
                errors.append(f"{collection}[{index}] must include a stable string id.")
                continue
            if record_id in seen:
                errors.append(f"{collection}[{index}] duplicates id `{record_id}`.")
            seen.add(record_id)
    return ids


def _validate_value(
    errors: list[str],
    prefix: str,
    field: str,
    value: Any,
    expected: str,
    enums: Mapping[str, list[str]],
) -> None:
    if expected.startswith("enum:"):
        enum_name = expected.split(":", 1)[1]
        allowed = set(enums.get(enum_name, []))
        if value not in allowed:
            errors.append(f"{prefix}.{field} must be one of {sorted(allowed)}.")
        return
    if expected.startswith("ref:"):
        if not isinstance(value, str):
            errors.append(f"{prefix}.{field} must be a string reference.")
        return
    python_type = TYPE_CHECKS.get(expected)
    if python_type and not isinstance(value, python_type):
        errors.append(f"{prefix}.{field} must be {expected}.")


def _validate_reference(
    errors: list[str],
    prefix: str,
    field: str,
    value: Any,
    target_collection: str | None,
    ids_by_collection: Mapping[str, set[str]],
) -> None:
    if not target_collection:
        return
    targets = ids_by_collection.get(target_collection, set())
    values = value if isinstance(value, list) else [value]
    for item in values:
        if item and item not in targets:
            errors.append(f"{prefix}.{field} references missing `{item}` in `{target_collection}`.")
