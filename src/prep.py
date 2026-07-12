from __future__ import annotations

from typing import Any

from src.match import normalize_target_roles, roles_from_profile
from src.person_reasoning import build_person_interview_prep
from src.position import find_title_caveats


def build_interview_prep_analysis(
    *,
    kb: dict[str, Any],
    profile: dict[str, Any] | None = None,
    target_roles: list[str] | None = None,
) -> dict[str, Any]:
    normalized_target_roles = normalize_target_roles(target_roles or roles_from_profile(profile))
    person_prep = build_person_interview_prep(kb, target_roles=normalized_target_roles or None)
    story_index = {str(story.get("id")): story for story in kb.get("stories", [])}
    title_caveats = find_title_caveats(kb)
    talking_points = [
        talking_point_from_claim(claim, person_prep["caveats"])
        for claim in person_prep["talking_points"]
    ]
    risk_flags = build_risk_flags(person_prep, title_caveats)

    return {
        "talking_points": talking_points,
        "story_links": build_story_links(person_prep["story_links"], person_prep["talking_points"], story_index, person_prep["caveats"]),
        "working_style_notes": [
            talking_point_from_claim(claim, person_prep["caveats"])
            for claim in working_style_claims(person_prep)
        ],
        "leadership_notes": [talking_point_from_claim(claim, person_prep["caveats"]) for claim in person_prep["leadership_notes"]],
        "communication_notes": [talking_point_from_claim(claim, person_prep["caveats"]) for claim in person_prep["communication_notes"]],
        "motivation_notes": [talking_point_from_claim(claim, person_prep["caveats"]) for claim in person_prep["motivation_notes"]],
        "risk_flags": risk_flags,
        "caveats": person_prep["caveats"],
        "questions_to_prepare": questions_to_prepare(risk_flags, person_prep),
    }


def talking_point_from_claim(claim: dict[str, Any], caveats: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "topic": claim.get("label"),
        "supporting_claims": [claim.get("id")],
        "supporting_evidence": claim.get("evidence", []),
        "related_stories": claim.get("related_stories", []),
        "related_projects": claim.get("related_projects", []),
        "related_accomplishments": claim.get("related_accomplishments", []),
        "caveats": [item for item in caveats if item.get("claim_id") == claim.get("id")],
    }


def working_style_claims(person_prep: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    work_style_categories = {
        "collaboration_fit",
        "collaboration_timing",
        "environment_fit",
        "ownership",
        "psychological_safety",
    }
    claims = list(person_prep["working_style_notes"])
    seen = {claim.get("id") for claim in claims}
    for claim in person_prep["talking_points"]:
        if claim.get("category") not in work_style_categories or claim.get("id") in seen:
            continue
        seen.add(claim.get("id"))
        claims.append(claim)
    return claims


def build_story_links(
    links: list[dict[str, str]],
    claims: list[dict[str, Any]],
    story_index: dict[str, dict[str, Any]],
    caveats: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    claims_by_id = {str(claim.get("id")): claim for claim in claims}
    story_links: list[dict[str, Any]] = []
    for link in links:
        claim = claims_by_id.get(str(link["claim_id"]), {})
        story = story_index.get(str(link["story_id"]), {})
        themes = list(story.get("useful_for_questions", [])) or [str(claim.get("category", ""))]
        story_links.append(
            {
                "story_id": link["story_id"],
                "why_relevant": f"Linked from person-model claim `{link['claim_id']}`.",
                "themes": [theme for theme in themes if theme],
                "related_claims": [link["claim_id"]],
                "caveats": [item for item in caveats if item.get("claim_id") == link["claim_id"]],
            }
        )
    return story_links


def build_risk_flags(person_prep: dict[str, list[dict[str, Any]]], title_caveats: list[dict[str, str]]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for caveat in title_caveats:
        risks.append(
            {
                "risk": "nonlinear_title_history",
                "why_it_matters": "Functional engineering positioning can be misread as a formal title claim.",
                "related_claims": caveat["related_ids"],
                "caveats": [caveat["note"]],
            }
        )

    for claim in person_prep["talking_points"]:
        text = claim_text(claim)
        claim_id = claim.get("id")
        if "ai-assisted" in text or "ai assisted" in text:
            risks.append(risk("ai_assisted_coding_misread", claim_id, "AI-assisted coding should be framed as experimentation and implementation support, not a substitute for engineering judgment."))
        if "qa" in text or "playwright" in text:
            risks.append(risk("qa_work_misread_as_only_qa", claim_id, "QA automation should be connected to engineering reliability, product delivery, or developer workflow evidence."))
        if "systems" in text or claim.get("category") == "systems_thinking":
            risks.append(risk("broad_systems_interest_misread_as_lack_of_focus", claim_id, "Broad systems interest should be anchored to concrete projects, stories, or accomplishments."))
        if "people management" in text or "formal management" in text:
            risks.append(risk("limited_formal_management_scope", claim_id, "Leadership examples should distinguish system direction and technical ownership from formal people management."))
        if "problem ownership" in text or claim.get("category") == "ownership":
            risks.append(risk("problem_ownership_fit", claim_id, "Ask how much room the role has for meaningful problem ownership and shaping the work."))
        if "repetitive" in text or "contextless" in text:
            risks.append(risk("repetitive_or_contextless_work", claim_id, "Check whether the role has enough context, ownership, and learning to remain energizing."))

    return dedupe_risks(risks)


def risk(risk_name: str, claim_id: Any, why: str) -> dict[str, Any]:
    return {
        "risk": risk_name,
        "why_it_matters": why,
        "related_claims": [claim_id],
        "caveats": [],
    }


def questions_to_prepare(risk_flags: list[dict[str, Any]], person_prep: dict[str, list[dict[str, Any]]]) -> list[str]:
    questions: list[str] = []
    if person_prep["story_links"]:
        questions.append("Which linked stories best demonstrate the role's core competencies?")
    for flag in risk_flags:
        if flag["risk"] == "nonlinear_title_history":
            questions.append("How will you explain the business-analysis to applied-AI/software-engineering transition without overstating title continuity?")
        if flag["risk"] == "problem_ownership_fit":
            questions.append("What questions will you ask to understand ownership, ambiguity, and decision-making scope?")
        if flag["risk"] == "limited_formal_management_scope":
            questions.append("How will you distinguish leadership through direction/system design from formal people management?")
    return dedupe_strings(questions)


def claim_text(claim: dict[str, Any]) -> str:
    parts = [
        claim.get("id", ""),
        claim.get("label", ""),
        claim.get("statement", ""),
        claim.get("category", ""),
        claim.get("notes", ""),
        *(item.get("description", "") for item in claim.get("evidence", [])),
    ]
    return " ".join(str(part) for part in parts).lower()


def dedupe_risks(risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, tuple[Any, ...]]] = set()
    deduped: list[dict[str, Any]] = []
    for item in risks:
        key = (item["risk"], tuple(item["related_claims"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = " ".join(value.split())
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped
