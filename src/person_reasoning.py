from __future__ import annotations

from typing import Any

from src.config import load_default_config
from src.person_model import REFLECTION_EVIDENCE_TYPES, load_person_model, select_person_claims


_REASONING_DEFAULTS = load_default_config("reasoning_rules")
_PERSON_REASONING_CATEGORIES = _REASONING_DEFAULTS.get("person_reasoning_categories", {})

MATCH_ENVIRONMENT_CATEGORIES = {
    "collaboration_fit",
    "collaboration_timing",
    "environment_fit",
    "psychological_safety",
}
MATCH_DEMOTIVATOR_CATEGORIES = {
    "ownership",
    "product_values",
}
MATCH_MISINTERPRETATION_CATEGORIES = {
    "collaboration_timing",
    "communication_processing",
    "identity_accuracy",
    "influence",
}
PREP_COMMUNICATION_CATEGORIES = {
    "collaboration_fit",
    "collaboration_timing",
    "communication_processing",
    "influence",
    "psychological_safety",
    "user_context",
}
PREP_LEADERSHIP_CATEGORIES = {
    "ambiguity_to_artifacts",
    "influence",
    "leadership",
    "ownership",
    "systems_thinking",
}
PREP_MOTIVATION_CATEGORIES = {
    "identity_accuracy",
    "product_values",
    "purpose",
}

MATCH_ENVIRONMENT_CATEGORIES = set(
    _PERSON_REASONING_CATEGORIES.get("match_environment", MATCH_ENVIRONMENT_CATEGORIES)
)
MATCH_DEMOTIVATOR_CATEGORIES = set(
    _PERSON_REASONING_CATEGORIES.get("match_demotivator", MATCH_DEMOTIVATOR_CATEGORIES)
)
MATCH_MISINTERPRETATION_CATEGORIES = set(
    _PERSON_REASONING_CATEGORIES.get("match_misinterpretation", MATCH_MISINTERPRETATION_CATEGORIES)
)
PREP_COMMUNICATION_CATEGORIES = set(
    _PERSON_REASONING_CATEGORIES.get("prep_communication", PREP_COMMUNICATION_CATEGORIES)
)
PREP_LEADERSHIP_CATEGORIES = set(
    _PERSON_REASONING_CATEGORIES.get("prep_leadership", PREP_LEADERSHIP_CATEGORIES)
)
PREP_MOTIVATION_CATEGORIES = set(
    _PERSON_REASONING_CATEGORIES.get("prep_motivation", PREP_MOTIVATION_CATEGORIES)
)


def build_person_match_signals(kb: dict[str, Any], target_roles: list[str] | None = None) -> dict[str, list[dict[str, Any]]]:
    claims = select_person_claims(load_person_model(kb), "role_matching", target_roles=target_roles)
    result: dict[str, list[dict[str, Any]]] = {
        "fit_signals": [],
        "mismatch_signals": [],
        "environment_signals": [],
        "demotivator_signals": [],
        "misinterpretation_risks": [],
        "caveats": [],
    }

    for claim in claims:
        entry = _claim_entry(claim)
        category = _category(claim)
        claim_id = str(claim.get("id", ""))
        text = " ".join(
            str(claim.get(key, ""))
            for key in ("id", "label", "statement", "category", "notes")
        ).lower()

        if _has_usage_caution(claim):
            result["mismatch_signals"].append(entry)
        elif category in MATCH_ENVIRONMENT_CATEGORIES or "environment" in claim_id:
            result["environment_signals"].append(entry)
        elif _is_demotivator(claim):
            result["demotivator_signals"].append(entry)
        else:
            result["fit_signals"].append(entry)

        if category in MATCH_MISINTERPRETATION_CATEGORIES or "misinterpret" in text or "avoid implying" in text:
            result["misinterpretation_risks"].append(entry)

        result["caveats"].extend(_claim_caveats(claim))

    return _dedupe_caveats(result)


def build_person_positioning_angles(
    kb: dict[str, Any],
    target_roles: list[str] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    claims = select_person_claims(load_person_model(kb), "positioning", target_roles=target_roles)
    result: dict[str, list[dict[str, Any]]] = {
        "positioning_angles": [],
        "supporting_evidence": [],
        "misinterpretation_risks": [],
        "caveats": [],
    }

    for claim in sorted(claims, key=lambda item: _positioning_sort_key(item, target_roles)):
        if _is_caution_only_public_claim(claim):
            result["caveats"].extend(_claim_caveats(claim))
            continue

        entry = _claim_entry(claim)
        result["positioning_angles"].append(entry)
        result["supporting_evidence"].append(
            {
                "claim_id": entry["id"],
                "related_accomplishments": entry["related_accomplishments"],
                "related_projects": entry["related_projects"],
                "related_stories": entry["related_stories"],
                "evidence": entry["evidence"],
            }
        )
        if _category(claim) in MATCH_MISINTERPRETATION_CATEGORIES or "public_claims" in claim.get("caution_for", []):
            result["misinterpretation_risks"].append(entry)
        result["caveats"].extend(_claim_caveats(claim))

    return _dedupe_caveats(result)


def build_person_interview_prep(
    kb: dict[str, Any],
    target_roles: list[str] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    claims = select_person_claims(load_person_model(kb), "interview_prep", target_roles=target_roles)
    result: dict[str, list[dict[str, Any]]] = {
        "talking_points": [],
        "story_links": [],
        "working_style_notes": [],
        "leadership_notes": [],
        "communication_notes": [],
        "motivation_notes": [],
        "caveats": [],
    }

    for claim in claims:
        entry = _claim_entry(claim)
        category = _category(claim)
        result["talking_points"].append(entry)
        for story_id in entry["related_stories"]:
            result["story_links"].append({"claim_id": entry["id"], "story_id": story_id})
        if category in PREP_COMMUNICATION_CATEGORIES:
            result["communication_notes"].append(entry)
        if category in PREP_LEADERSHIP_CATEGORIES:
            result["leadership_notes"].append(entry)
        if category in PREP_MOTIVATION_CATEGORIES:
            result["motivation_notes"].append(entry)
        if category not in PREP_COMMUNICATION_CATEGORIES | PREP_LEADERSHIP_CATEGORIES | PREP_MOTIVATION_CATEGORIES:
            result["working_style_notes"].append(entry)
        result["caveats"].extend(_claim_caveats(claim))

    result["story_links"] = _dedupe_story_links(result["story_links"])
    return _dedupe_caveats(result)


def _claim_entry(claim: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": claim.get("id"),
        "label": claim.get("label"),
        "statement": claim.get("statement"),
        "category": claim.get("category"),
        "confidence": claim.get("confidence"),
        "related_accomplishments": list(claim.get("related_accomplishments", [])),
        "related_projects": list(claim.get("related_projects", [])),
        "related_stories": list(claim.get("related_stories", [])),
        "supports_target_roles": list(claim.get("supports_target_roles", [])),
        "evidence": [_evidence_entry(item) for item in claim.get("evidence", [])],
        "caution_for": list(claim.get("caution_for", [])),
        "has_usage_caution": bool(claim.get("has_usage_caution")),
        "notes": claim.get("notes"),
    }


def _evidence_entry(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": evidence.get("id"),
        "type": evidence.get("type"),
        "source": evidence.get("source"),
        "source_ref": evidence.get("source_ref"),
        "description": evidence.get("description"),
    }


def _claim_caveats(claim: dict[str, Any]) -> list[dict[str, Any]]:
    caveats: list[dict[str, Any]] = []
    claim_id = claim.get("id")
    if _has_usage_caution(claim):
        caveats.append(
            {
                "claim_id": claim_id,
                "type": "usage_caution",
                "detail": f"Use cautiously for {claim.get('selected_for_usage')}.",
                "caution_for": list(claim.get("caution_for", [])),
            }
        )
    for evidence in claim.get("evidence", []):
        evidence_type = evidence.get("type")
        if evidence_type in REFLECTION_EVIDENCE_TYPES:
            caveats.append(
                {
                    "claim_id": claim_id,
                    "type": evidence_type,
                    "detail": "Treat as recollection or reflection, not independently verified employment evidence.",
                    "evidence_id": evidence.get("id"),
                    "source_ref": evidence.get("source_ref"),
                }
            )
    return caveats


def _dedupe_caveats(result: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    seen: set[tuple[Any, ...]] = set()
    deduped: list[dict[str, Any]] = []
    for caveat in result["caveats"]:
        key = (
            caveat.get("claim_id"),
            caveat.get("type"),
            caveat.get("evidence_id"),
            tuple(caveat.get("caution_for", [])),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(caveat)
    result["caveats"] = deduped
    return result


def _dedupe_story_links(links: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, str]] = []
    for link in links:
        key = (link["claim_id"], link["story_id"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(link)
    return deduped


def _category(claim: dict[str, Any]) -> str:
    return str(claim.get("category", ""))


def _has_usage_caution(claim: dict[str, Any]) -> bool:
    return bool(claim.get("has_usage_caution"))


def _is_demotivator(claim: dict[str, Any]) -> bool:
    category = _category(claim)
    text = " ".join(str(claim.get(key, "")) for key in ("id", "label", "statement", "notes")).lower()
    return (
        category in MATCH_DEMOTIVATOR_CATEGORIES
        or "demotivat" in text
        or "struggles" in text
        or "loses energy" in text
        or "dislikes" in text
    )


def _is_caution_only_public_claim(claim: dict[str, Any]) -> bool:
    return (
        "public_claims" in claim.get("caution_for", [])
        and not claim.get("related_accomplishments")
        and not claim.get("related_projects")
        and not claim.get("related_stories")
    )


def _positioning_sort_key(claim: dict[str, Any], target_roles: list[str] | None) -> tuple[int, int, int, str]:
    role_filter = set(target_roles or [])
    supported_roles = set(claim.get("supports_target_roles", []))
    if not role_filter:
        role_rank = 0
    elif supported_roles & role_filter:
        role_rank = 0
    elif not supported_roles:
        role_rank = 1
    else:
        role_rank = 2
    confidence_rank = {"high": 0, "medium": 1, "low": 2}.get(str(claim.get("confidence")), 3)
    evidence_rank = 0 if _has_non_reflection_evidence(claim) else 1
    return (role_rank, confidence_rank, evidence_rank, str(claim.get("id", "")))


def _has_non_reflection_evidence(claim: dict[str, Any]) -> bool:
    return any(item.get("type") not in REFLECTION_EVIDENCE_TYPES for item in claim.get("evidence", []))
