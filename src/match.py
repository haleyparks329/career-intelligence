from __future__ import annotations

from typing import Any

from src.generate_ats_report import (
    classify_keywords,
    overall_match_score,
    recommended_changes,
    strength_lines,
)
from src.person_reasoning import build_person_match_signals
from src.select_bullets import RankedBullet, normalize


def build_match_analysis(
    *,
    kb: dict[str, Any],
    job_keywords: list[str],
    resume_keywords: set[str],
    selected_bullets: list[RankedBullet] | None = None,
    profile: dict[str, Any] | None = None,
    target_roles: list[str] | None = None,
) -> dict[str, Any]:
    selected_bullets = selected_bullets or []
    capability = classify_keywords(
        job_keywords=job_keywords,
        resume_keywords=resume_keywords,
        selected_bullets=selected_bullets,
    )
    score = overall_match_score(
        strong_count=len(capability["strong_matches"]),
        adjacent_count=len(capability["adjacent_matches"]),
        gap_count=len(capability["true_gaps"]),
    )
    normalized_target_roles = normalize_target_roles(target_roles or roles_from_profile(profile))
    person_fit = build_person_match_signals(kb, target_roles=normalized_target_roles or None)
    recommendations = recommended_changes(
        selected_bullets=selected_bullets,
        adjacent_matches=capability["adjacent_matches"],
        true_gaps=capability["true_gaps"],
    )

    return {
        "capability_fit": {
            "existing_skills": capability["strong_matches"],
            "transferable_skills": capability["adjacent_matches"],
            "evidence_strength": evidence_strength_summary(selected_bullets),
            "genuine_gaps": capability["true_gaps"],
            "score": score,
        },
        "person_fit": person_fit,
        "overall_assessment": {
            "strengths": strength_lines(selected_bullets, job_keywords) or capability["strong_matches"],
            "concerns": capability["true_gaps"] + [item["label"] for item in person_fit["mismatch_signals"]],
            "questions_to_investigate": questions_to_investigate(capability, person_fit),
            "recommended_actions": recommendations,
        },
    }


def roles_from_profile(profile: dict[str, Any] | None) -> list[str]:
    if not profile:
        return []
    roles = [str(item) for item in profile.get("target_roles", [])]
    profile_id = profile.get("_profile_key") or profile.get("id")
    if profile_id:
        roles.append(str(profile_id))
    return roles


def normalize_target_roles(target_roles: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for role in target_roles:
        value = normalize(str(role)).replace(" ", "_")
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def evidence_strength_summary(selected_bullets: list[RankedBullet]) -> dict[str, int]:
    summary = {
        "strong_evidence": 0,
        "adjacent_evidence": 0,
        "weak_evidence": 0,
    }
    for item in selected_bullets:
        key = item.evidence_classification if item.evidence_classification in summary else "weak_evidence"
        summary[key] += 1
    return summary


def questions_to_investigate(capability: dict[str, list[str]], person_fit: dict[str, list[dict[str, Any]]]) -> list[str]:
    questions: list[str] = []
    if capability["true_gaps"]:
        questions.append("Which listed requirements are hard requirements versus learnable or adjacent gaps?")
    if person_fit["environment_signals"]:
        questions.append("Does the environment provide the problem ownership and collaboration style where this fit is strongest?")
    if person_fit["demotivator_signals"]:
        questions.append("Could the role contain repeated work patterns that are likely to drain energy despite capability fit?")
    if person_fit["misinterpretation_risks"]:
        questions.append("Where might nonlinear title history or working style need careful explanation?")
    return questions
