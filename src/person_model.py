from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any


REFLECTION_EVIDENCE_TYPES = {"interview_recollection", "third_party_recollection"}


def load_person_model(kb: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return kb.get("person_model", {}) or {}


def iter_person_claims(person_model: dict[str, Any]) -> Iterator[dict[str, Any]]:
    for claims in person_model.values():
        if not isinstance(claims, list):
            continue
        for claim in claims:
            yield claim


def select_person_claims(
    person_model: dict[str, Any],
    usage: str,
    include_caution: bool = True,
    exclude_caution_for: Iterable[str] | None = None,
    categories: Iterable[str] | None = None,
    target_roles: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    excluded_cautions = set(exclude_caution_for or [])
    category_filter = set(categories or [])
    role_filter = set(target_roles or [])
    selected: list[tuple[int, int, dict[str, Any]]] = []

    for index, claim in enumerate(iter_person_claims(person_model)):
        if usage not in claim.get("safe_for", []):
            continue
        caution_for = set(claim.get("caution_for", []))
        if not include_caution and caution_for:
            continue
        if excluded_cautions and caution_for & excluded_cautions:
            continue
        if category_filter and claim.get("category") not in category_filter:
            continue

        role_rank = 0
        supported_roles = set(claim.get("supports_target_roles", []))
        if role_filter:
            if supported_roles & role_filter:
                role_rank = 0
            elif not supported_roles:
                role_rank = 1
            else:
                continue

        selected.append((role_rank, index, with_usage_context(claim, usage)))

    return [claim for _, _, claim in sorted(selected, key=lambda item: (item[0], item[1]))]


def with_usage_context(claim: dict[str, Any], usage: str) -> dict[str, Any]:
    caution_for = list(claim.get("caution_for", []))
    usage_cautions = [item for item in caution_for if item == usage]
    annotated = dict(claim)
    annotated["selected_for_usage"] = usage
    annotated["usage_cautions"] = usage_cautions
    annotated["has_usage_caution"] = bool(usage_cautions)
    annotated["is_resume_bullet_safe"] = is_claim_safe_for_resume_bullets(claim)
    annotated["is_resume_summary_safe"] = is_claim_safe_for_resume_summary(claim)
    return annotated


def is_claim_safe_for_resume_bullets(claim: dict[str, Any]) -> bool:
    return _is_claim_resume_safe(claim, usage="resume_bullets")


def is_claim_safe_for_resume_summary(claim: dict[str, Any]) -> bool:
    return _is_claim_resume_safe(claim, usage="resume_summary")


def _is_claim_resume_safe(claim: dict[str, Any], usage: str) -> bool:
    safe_for = set(claim.get("safe_for", []))
    caution_for = set(claim.get("caution_for", []))
    has_relationship_evidence = bool(claim.get("related_accomplishments") or claim.get("related_projects"))
    return (
        usage in safe_for
        and usage not in caution_for
        and "ats_generation" not in caution_for
        and has_relationship_evidence
        and _has_non_reflection_evidence(claim)
    )


def _has_non_reflection_evidence(claim: dict[str, Any]) -> bool:
    evidence_items = claim.get("evidence", [])
    return any(item.get("type") not in REFLECTION_EVIDENCE_TYPES for item in evidence_items)
