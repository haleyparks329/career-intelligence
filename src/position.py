from __future__ import annotations

from typing import Any

from src.match import normalize_target_roles, roles_from_profile
from src.person_model import REFLECTION_EVIDENCE_TYPES
from src.person_reasoning import build_person_positioning_angles


def build_positioning_analysis(
    *,
    kb: dict[str, Any],
    profile: dict[str, Any] | None = None,
    target_roles: list[str] | None = None,
) -> dict[str, Any]:
    normalized_target_roles = normalize_target_roles(target_roles or roles_from_profile(profile))
    person_positioning = build_person_positioning_angles(kb, target_roles=normalized_target_roles or None)
    title_caveats = find_title_caveats(kb)
    identity = kb.get("identity") or {}

    positioning_angles = [
        positioning_angle_from_claim(claim, person_positioning["caveats"])
        for claim in person_positioning["positioning_angles"]
    ]

    misinterpretation_risks = [
        misinterpretation_risk_from_claim(claim)
        for claim in person_positioning["misinterpretation_risks"]
    ]
    misinterpretation_risks.extend(title_caveat_risk(caveat) for caveat in title_caveats)

    return {
        "positioning_angles": positioning_angles,
        "misinterpretation_risks": misinterpretation_risks,
        "evidence_gaps": evidence_gaps(positioning_angles),
        "narrative_constraints": {
            "do_not_overstate": do_not_overstate(identity, title_caveats),
            "safe_to_emphasize": safe_to_emphasize(identity, positioning_angles),
            "needs_review": needs_review(title_caveats, person_positioning["caveats"]),
        },
        "caveats": person_positioning["caveats"],
    }


def positioning_angle_from_claim(claim: dict[str, Any], caveats: list[dict[str, Any]]) -> dict[str, Any]:
    related_caveats = [item for item in caveats if item.get("claim_id") == claim.get("id")]
    return {
        "angle": claim.get("label"),
        "supporting_claims": [claim.get("id")],
        "supporting_evidence": claim.get("evidence", []),
        "related_stories": claim.get("related_stories", []),
        "related_projects": claim.get("related_projects", []),
        "related_accomplishments": claim.get("related_accomplishments", []),
        "confidence": claim.get("confidence"),
        "caveats": related_caveats,
    }


def misinterpretation_risk_from_claim(claim: dict[str, Any]) -> dict[str, Any]:
    return {
        "risk": claim.get("label"),
        "mitigation": "Pair this positioning angle with concrete accomplishments, projects, or stories instead of presenting it as a standalone trait.",
        "related_claims": [claim.get("id")],
    }


def title_caveat_risk(caveat: dict[str, str]) -> dict[str, Any]:
    return {
        "risk": "Functional engineering title may be read as an official HR title.",
        "mitigation": caveat["note"],
        "related_claims": caveat["related_ids"],
    }


def evidence_gaps(positioning_angles: list[dict[str, Any]]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for angle in positioning_angles:
        has_relationship_evidence = bool(
            angle["related_stories"]
            or angle["related_projects"]
            or angle["related_accomplishments"]
        )
        has_non_reflection_evidence = any(
            item.get("type") not in REFLECTION_EVIDENCE_TYPES
            for item in angle["supporting_evidence"]
        )
        if has_relationship_evidence and has_non_reflection_evidence:
            continue
        gaps.append(
            {
                "gap": f"{angle['angle']} needs stronger non-recollection support before becoming public-facing positioning.",
                "why_it_matters": "Positioning can guide reasoning, but weakly linked claims should not become credentials or polished public claims.",
                "suggested_source_to_add": "Add or link a concrete accomplishment, project, story, work artifact, or repo artifact.",
            }
        )
    return gaps


def do_not_overstate(identity: dict[str, Any], title_caveats: list[dict[str, str]]) -> list[str]:
    constraints = list(identity.get("anti_positioning", []))
    constraints.append("Do not turn person-model claims into credentials, titles, certifications, or accomplishments.")
    if title_caveats:
        constraints.append("Do not present Software Engineer / Applied AI Engineer as a formal HR title without review.")
    return _dedupe_strings(constraints)


def safe_to_emphasize(identity: dict[str, Any], positioning_angles: list[dict[str, Any]]) -> list[str]:
    values = list(identity.get("differentiators", []))
    for angle in positioning_angles:
        if angle["related_accomplishments"] or angle["related_projects"] or angle["related_stories"]:
            values.append(str(angle["angle"]))
    return _dedupe_strings(values)


def needs_review(title_caveats: list[dict[str, str]], caveats: list[dict[str, Any]]) -> list[str]:
    review_items = [item["note"] for item in title_caveats]
    for caveat in caveats:
        if caveat.get("type") in {"usage_caution", *REFLECTION_EVIDENCE_TYPES}:
            review_items.append(str(caveat.get("detail")))
    return _dedupe_strings(review_items)


def find_title_caveats(kb: dict[str, Any]) -> list[dict[str, str]]:
    caveats: list[dict[str, str]] = []
    for story in kb.get("stories", []):
        note = str(story.get("title_note") or story.get("review_notes") or "")
        if not note:
            continue
        if "official HR title" in note or "formal HR title" in note:
            caveats.append(
                {
                    "note": note,
                    "related_ids": [str(story.get("id"))],
                }
            )
    return caveats


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = " ".join(str(value).split())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped
