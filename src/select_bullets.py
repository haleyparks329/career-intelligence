from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.config import load_default_config


WEIGHTS = {
    "exact_keyword_match": 5,
    "multi_word_phrase_match": 8,
    "technology_match": 6,
    "skill_match": 5,
    "domain_match": 4,
    "profile_match": 6,
    "semantic_evidence_match": 7,
    "priority_evidence_match": 12,
    "evidence_level_strong": 5,
    "evidence_level_moderate": 3,
    "evidence_level_emerging": 1,
    "source_recency": 2,
}

PENALTIES = {
    "broad_parent_node": -10,
    "low_relevance_domain": -4,
    "too_many_siblings": -5,
    "older_role_overuse": -4,
}

STRONG_EVIDENCE_LEVELS = {
    "high",
    "strong",
    "source_backed",
    "source backed",
    "multi_source_normalized",
    "multi source normalized",
    "verified",
}

MODERATE_EVIDENCE_LEVELS = {
    "moderate",
    "medium",
    "needs_review",
}

EMERGING_EVIDENCE_LEVELS = {
    "emerging",
    "low",
    "placeholder",
}

OLDER_SOURCE_PREFIXES: tuple[str, ...] = ()
RECENT_SOURCE_PREFIXES: tuple[str, ...] = ()
TOKEN_STOPWORDS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with"}

SEMANTIC_EVIDENCE_GROUPS = {
    "developer_experience": {
        "job_terms": {
            "developer experience",
            "developer tools",
            "developer tooling",
            "tools",
            "move faster",
            "productivity",
            "internal tools",
            "internal ai tools",
        },
        "bullet_terms": {
            "developer experience",
            "developer tooling",
            "ci/cd",
            "cicd",
            "qa",
            "testing",
            "playwright",
            "slack",
            "internal support",
            "workflow integrations",
        },
        "label": "Developer Experience",
    },
    "internal_ai_tools": {
        "job_terms": {
            "internal ai tools",
            "internal ai tooling",
            "ai productivity",
            "internal chatbot",
            "internal chatbots",
            "efficiency agents",
            "meeting summaries",
            "requirements generation",
            "code review support",
            "rfp",
            "rfq",
            "reusable tools",
            "adoption",
        },
        "bullet_terms": {
            "slack",
            "support assistant",
            "ai workflows",
            "workflow",
            "workflow automation",
            "requirements",
            "developer experience",
            "developer tooling",
            "ci/cd",
            "playwright",
            "qa",
            "cross functional",
            "stakeholder",
        },
        "label": "Internal AI Tools",
    },
    "production_ai": {
        "job_terms": {
            "production ai",
            "production",
            "ship",
            "shipping",
            "production APIs",
            "deployed features",
            "ai features",
            "ai workflows",
            "generative ai",
            "member-facing features",
        },
        "bullet_terms": {"production", "production behavior", "ai workflows", "llm systems", "agent based systems", "applied ai"},
        "label": "Production AI",
    },
    "backend_services": {
        "job_terms": {
            "backend",
            "backend development",
            "backend services",
            "services",
            "restful api design",
            "apis",
            "api",
            "infrastructure",
            "software solutions",
        },
        "bullet_terms": {
            "backend",
            "services",
            "fastapi",
            "rest apis",
            "api",
            "apis",
            "pipeline",
            "pipelines",
            "sqlite",
            "notion api",
            "telegram bot api",
            "product engineering",
        },
        "label": "Backend Services",
    },
    "reliability_system_health": {
        "job_terms": {
            "reliability",
            "reliable",
            "observability",
            "monitoring",
            "monitoring systems",
            "system health",
            "system stability",
            "stability",
            "high-quality code",
            "deployed features",
        },
        "bullet_terms": {
            "reliability",
            "deployment stability",
            "ci/cd",
            "cicd",
            "qa",
            "quality assurance",
            "testing",
            "playwright",
            "production behavior",
            "guardrails",
            "report generation",
            "dashboard",
            "tests",
        },
        "label": "Reliability / System Health",
    },
    "async_processing": {
        "job_terms": {"asynchronous processing", "kafka", "sqs", "event driven", "event-driven", "processing systems"},
        "bullet_terms": {"event driven", "event-driven", "workflow systems", "pipelines", "ingestion pipelines", "automation"},
        "label": "Asynchronous Processing",
    },
    "infrastructure_platform": {
        "job_terms": {"infrastructure", "platform", "ai platform", "scalable system design", "scalable", "large-scale"},
        "bullet_terms": {
            "infrastructure",
            "platform",
            "enterprise ai platform",
            "kubernetes",
            "deployment stability",
            "modular",
            "architecture",
            "canonical local store",
            "sqlite",
        },
        "label": "Platform Infrastructure",
    },
    "retrieval_systems": {
        "job_terms": {"retrieval", "retrieval systems", "hybrid retrieval", "semantic search", "grounded retrieval"},
        "bullet_terms": {"retrieval", "hybrid retrieval", "semantic search", "rag", "llm answer generation"},
        "label": "Retrieval Systems",
    },
    "ambiguous_builder": {
        "job_terms": {"ambiguous problems", "vague problems", "bias for action", "prototype fast", "rapid prototyping", "startup"},
        "bullet_terms": {"ambiguous", "prototype", "rapid", "startup", "special projects", "cross functional", "requirements"},
        "label": "Ambiguous Builder",
    },
    "decision_support": {
        "job_terms": {
            "decision-making",
            "recommend",
            "recommendations",
            "personalized insights",
            "health outcomes",
            "performance optimization",
            "diagnoses",
            "monitoring",
            "reports",
        },
        "bullet_terms": {"decision support", "readiness", "auditable", "recommendations", "dashboard", "feedback loops"},
        "label": "Decision Support",
    },
    "health_performance_data": {
        "job_terms": {
            "human performance",
            "healthspan",
            "physiological metrics",
            "heart rate variability",
            "resting heart rate",
            "sleep quality",
            "fitness",
            "health",
            "recovery",
            "wearable",
            "personalized insights",
        },
        "bullet_terms": {
            "health technology",
            "human performance",
            "wearable data",
            "apple health",
            "apple watch",
            "sleep",
            "hrv",
            "resting heart rate",
            "readiness",
            "recovery",
            "training",
            "health data modeling",
        },
        "label": "Health Performance Data",
    },
    "user_pain": {
        "job_terms": {
            "customer",
            "customers",
            "user",
            "users",
            "feedback",
            "support",
            "seamless user experience",
            "pain points",
            "unmet needs",
            "adoption",
        },
        "bullet_terms": {"support", "slack", "customer", "users", "usable", "workflow", "enterprise support", "requirements"},
        "label": "Solving User Pain",
    },
}


_SCORING_DEFAULTS = load_default_config("scoring")
WEIGHTS = dict(_SCORING_DEFAULTS.get("weights", WEIGHTS))
PENALTIES = dict(_SCORING_DEFAULTS.get("penalties", PENALTIES))
_EVIDENCE_LEVELS = _SCORING_DEFAULTS.get("evidence_levels", {})
STRONG_EVIDENCE_LEVELS = set(_EVIDENCE_LEVELS.get("strong", STRONG_EVIDENCE_LEVELS))
MODERATE_EVIDENCE_LEVELS = set(_EVIDENCE_LEVELS.get("moderate", MODERATE_EVIDENCE_LEVELS))
EMERGING_EVIDENCE_LEVELS = set(_EVIDENCE_LEVELS.get("emerging", EMERGING_EVIDENCE_LEVELS))
_SOURCE_RECENCY = _SCORING_DEFAULTS.get("source_recency", {})
OLDER_SOURCE_PREFIXES = tuple(_SOURCE_RECENCY.get("older_prefixes", OLDER_SOURCE_PREFIXES))
RECENT_SOURCE_PREFIXES = tuple(_SOURCE_RECENCY.get("recent_prefixes", RECENT_SOURCE_PREFIXES))
TOKEN_STOPWORDS = set(_SCORING_DEFAULTS.get("token_stopwords", TOKEN_STOPWORDS))
SEMANTIC_EVIDENCE_GROUPS = {
    key: {
        "label": value["label"],
        "job_terms": set(value.get("job_terms", [])),
        "bullet_terms": set(value.get("bullet_terms", [])),
    }
    for key, value in _SCORING_DEFAULTS.get("semantic_evidence_groups", SEMANTIC_EVIDENCE_GROUPS).items()
}


@dataclass(frozen=True)
class RankedBullet:
    bullet: dict
    score: int
    matched_keywords: list[str]
    matched_phrases: list[str] = field(default_factory=list)
    matched_domains: list[str] = field(default_factory=list)
    matched_technologies: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    evidence_classification: str = "weak_evidence"
    reasons: list[str] = field(default_factory=list)
    penalties: list[str] = field(default_factory=list)


def normalize(value: str) -> str:
    return value.lower().replace("_", " ").strip()


def normalize_compact(value: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", "", normalize(value))


def tokens_from_values(values: list[str]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        normalized = normalize(str(value))
        if not normalized:
            continue
        tokens.add(normalized)
        tokens.add(normalize_compact(normalized))
        extracted = re.findall(r"[a-zA-Z][a-zA-Z0-9+.#-]{1,}", normalized)
        extracted = [token for token in extracted if token not in TOKEN_STOPWORDS]
        tokens.update(extracted)
        for token in extracted:
            if len(token) > 3 and token.endswith("s"):
                tokens.add(token[:-1])
            if token == "evaluation":
                tokens.update({"eval", "evals"})
            if token == "evals":
                tokens.update({"eval", "evaluation"})
            if token == "auditable":
                tokens.add("auditability")
            if token == "auditability":
                tokens.add("auditable")
            if token == "apis":
                tokens.add("api")
            if token == "api":
                tokens.add("apis")
            if token == "llms":
                tokens.add("llm")
            if token == "llm":
                tokens.add("llms")
    return {token for token in tokens if token}


def bullet_search_terms(bullet: dict) -> set[str]:
    values = [
        bullet.get("text", ""),
        bullet.get("category", ""),
        bullet.get("seniority_signal", ""),
        *bullet.get("tags", []),
        *bullet.get("technologies", []),
        *bullet.get("domains", []),
        *bullet.get("skills", []),
        *bullet.get("demonstrates_skills", []),
        *bullet.get("supports_target_roles", []),
        *bullet.get("related_accomplishments", []),
        *bullet.get("related_projects", []),
        *bullet.get("related_interview_stories", []),
    ]
    return tokens_from_values([str(value) for value in values if value])


def bullet_specific_terms(bullet: dict) -> set[str]:
    values = [
        bullet.get("text", ""),
        bullet.get("category", ""),
        bullet.get("seniority_signal", ""),
        *bullet.get("tags", []),
    ]
    return tokens_from_values([str(value) for value in values if value])


def job_term_set(job_keywords: list[str] | set[str]) -> set[str]:
    terms: set[str] = set()
    for keyword in job_keywords:
        normalized = normalize(str(keyword))
        if not normalized:
            continue
        if " " in normalized:
            terms.add(normalized)
            terms.add(normalize_compact(normalized))
        else:
            terms.update(tokens_from_values([normalized]))
    return terms


def semantic_evidence_matches(bullet_terms: set[str], job_terms: set[str]) -> list[str]:
    matches: list[str] = []
    compact_job_terms = {normalize_compact(term) for term in job_terms}
    compact_bullet_terms = {normalize_compact(term) for term in bullet_terms}
    for group in SEMANTIC_EVIDENCE_GROUPS.values():
        group_job_terms = group["job_terms"]
        group_bullet_terms = group["bullet_terms"]
        job_hit = bool(group_job_terms & job_terms or {normalize_compact(term) for term in group_job_terms} & compact_job_terms)
        bullet_hit = bool(
            group_bullet_terms & bullet_terms
            or {normalize_compact(term) for term in group_bullet_terms} & compact_bullet_terms
        )
        if job_hit and bullet_hit:
            matches.append(group["label"])
    return matches


def display_term(value: str) -> str:
    if any(char.isupper() for char in str(value)):
        return str(value)
    return normalize(value).replace("llmops", "LLMOps")


def source_id_for(bullet: dict) -> str:
    return str(bullet.get("source_experience") or bullet.get("source_id") or "")


def priority_bonus(source_id: str, profile: dict, job_terms: set[str]) -> tuple[int, str | None]:
    priority_ids = profile.get("priority_bullet_ids", {})
    if isinstance(priority_ids, dict) and source_id in priority_ids:
        return int(priority_ids[source_id]), "profile priority evidence"

    internal_terms = SEMANTIC_EVIDENCE_GROUPS["internal_ai_tools"]["job_terms"]
    internal_role = bool(internal_terms & job_terms or {normalize_compact(term) for term in internal_terms} & {normalize_compact(term) for term in job_terms})
    if internal_role and source_id.startswith(OLDER_SOURCE_PREFIXES):
        return -10, "older DevEx-adjacent evidence deprioritized for internal tooling"
    health_platform_terms = (
        SEMANTIC_EVIDENCE_GROUPS["health_performance_data"]["job_terms"]
        | SEMANTIC_EVIDENCE_GROUPS["backend_services"]["job_terms"]
        | SEMANTIC_EVIDENCE_GROUPS["reliability_system_health"]["job_terms"]
    )
    health_platform_role = bool(
        health_platform_terms & job_terms
        or {normalize_compact(term) for term in health_platform_terms} & {normalize_compact(term) for term in job_terms}
    )
    return 0, None


def evidence_bonus(evidence_level: str) -> tuple[int, str]:
    normalized = normalize(str(evidence_level))
    if normalized in STRONG_EVIDENCE_LEVELS:
        return WEIGHTS["evidence_level_strong"], "strong"
    if normalized in MODERATE_EVIDENCE_LEVELS:
        return WEIGHTS["evidence_level_moderate"], "moderate"
    if normalized in EMERGING_EVIDENCE_LEVELS:
        return WEIGHTS["evidence_level_emerging"], "emerging"
    if normalized and "source backed" in normalized:
        return WEIGHTS["evidence_level_strong"], "strong"
    return 0, "weak"


def classify_evidence(
    *,
    evidence_bucket: str,
    profile_match: bool,
    phrase_count: int,
    keyword_count: int,
    technology_count: int,
    skill_count: int,
    domain_count: int,
) -> str:
    direct_match_count = phrase_count + technology_count + skill_count
    if evidence_bucket == "strong" and profile_match and direct_match_count >= 1:
        return "strong_evidence"
    if evidence_bucket == "strong" and (direct_match_count >= 2 or domain_count >= 2):
        return "strong_evidence"
    if evidence_bucket in {"strong", "moderate"} and (profile_match or keyword_count or domain_count):
        return "adjacent_evidence"
    return "weak_evidence"


def score_bullet(bullet: dict, job_keywords: set[str], profile: dict) -> RankedBullet:
    profile_key = normalize(str(profile.get("_profile_key", profile.get("id", ""))))
    preferred_categories = {normalize(item) for item in profile.get("preferred_bullet_categories", [])}
    preferred_domains = {normalize(item) for item in profile.get("preferred_domains", [])}
    deprioritized_categories = {normalize(item) for item in profile.get("deprioritized_categories", [])}

    category = normalize(str(bullet.get("category", "")))
    domains = {normalize(item) for item in bullet.get("domains", [])}
    technologies = {normalize(item) for item in bullet.get("technologies", [])}
    skills = {normalize(item) for item in bullet.get("skills", bullet.get("demonstrates_skills", []))}
    reusable_profiles = {normalize(item) for item in bullet.get("reusable_for_profiles", [])}
    supports_target_roles = {normalize(item) for item in bullet.get("supports_target_roles", [])}
    terms = bullet_search_terms(bullet)
    specific_terms = bullet_specific_terms(bullet)
    job_terms = job_term_set(job_keywords)
    compact_job_terms = {normalize_compact(keyword) for keyword in job_keywords}

    matched_phrases = sorted(term for term in job_terms if " " in term and term in specific_terms)
    matched_keywords = sorted(term for term in specific_terms & job_terms if " " not in term)
    matched_technologies = sorted(
        item for item in technologies if item in job_terms or normalize_compact(item) in compact_job_terms
    )
    matched_skills = sorted(item for item in skills if item in job_terms or normalize_compact(item) in compact_job_terms)
    matched_domains = sorted(item for item in domains if item in job_terms or item in preferred_domains)
    matched_semantic_evidence = semantic_evidence_matches(terms, job_terms)

    score = 0
    reasons: list[str] = []
    penalties: list[str] = []

    if matched_keywords:
        points = len(matched_keywords) * WEIGHTS["exact_keyword_match"]
        score += points
        reasons.append(f"{points} exact keyword match points")
    if matched_phrases:
        points = len(matched_phrases) * WEIGHTS["multi_word_phrase_match"]
        score += points
        reasons.append(f"{points} multi-word phrase match points")
    if matched_technologies:
        points = len(matched_technologies) * WEIGHTS["technology_match"]
        score += points
        reasons.append(f"{points} technology match points")
    if matched_skills:
        points = len(matched_skills) * WEIGHTS["skill_match"]
        score += points
        reasons.append(f"{points} skill match points")
    if matched_domains:
        points = len(matched_domains) * WEIGHTS["domain_match"]
        score += points
        reasons.append(f"{points} domain match points")
    if matched_semantic_evidence:
        points = len(matched_semantic_evidence) * WEIGHTS["semantic_evidence_match"]
        score += points
        reasons.append(f"{points} semantic evidence points")

    profile_match = profile_key in reusable_profiles or profile_key in supports_target_roles
    if profile_match:
        score += WEIGHTS["profile_match"]
        reasons.append("profile match")

    if category in preferred_categories:
        score += WEIGHTS["profile_match"]
        reasons.append("preferred bullet category")

    evidence_points, evidence_bucket = evidence_bonus(str(bullet.get("evidence_level", "")))
    if evidence_points:
        score += evidence_points
        reasons.append(f"{evidence_bucket} source evidence")

    source_id = source_id_for(bullet)
    priority_points, priority_reason = priority_bonus(str(bullet.get("source_id") or source_id), profile, job_terms)
    if priority_points:
        score += priority_points
        if priority_reason:
            reasons.append(priority_reason if priority_points > 0 else priority_reason)
    if source_id.startswith(RECENT_SOURCE_PREFIXES):
        score += WEIGHTS["source_recency"]
        reasons.append("recent/current source")

    if bullet.get("selectable") is False:
        score += PENALTIES["broad_parent_node"]
        penalties.append("broad parent node")
    if category in deprioritized_categories:
        score += PENALTIES["low_relevance_domain"]
        penalties.append("deprioritized category")
    if source_id.startswith(OLDER_SOURCE_PREFIXES):
        score += PENALTIES["older_role_overuse"]
        penalties.append("older role")

    evidence_classification = classify_evidence(
        evidence_bucket=evidence_bucket,
        profile_match=profile_match,
        phrase_count=len(matched_phrases),
        keyword_count=len(matched_keywords),
        technology_count=len(matched_technologies),
        skill_count=len(matched_skills),
        domain_count=len(matched_domains),
    )
    if evidence_classification == "weak_evidence" and evidence_bucket in {"strong", "moderate"} and matched_semantic_evidence:
        evidence_classification = "adjacent_evidence"

    return RankedBullet(
        bullet=bullet,
        score=score,
        matched_keywords=[display_term(item) for item in matched_keywords],
        matched_phrases=[display_term(item) for item in matched_phrases],
        matched_domains=[display_term(item) for item in matched_domains],
        matched_technologies=[display_term(item) for item in matched_technologies],
        matched_skills=[display_term(item) for item in [*matched_skills, *matched_semantic_evidence]],
        evidence_classification=evidence_classification,
        reasons=reasons,
        penalties=penalties,
    )


def rank_bullets(bullets: list[dict], job_keywords: list[str], profile: dict) -> list[RankedBullet]:
    keyword_set = job_term_set(job_keywords)
    ranked = [score_bullet(bullet, keyword_set, profile) for bullet in bullets]
    return sorted(ranked, key=lambda item: (item.score, item.bullet.get("id", "")), reverse=True)


def select_ranked_bullets(
    ranked_bullets: list[RankedBullet],
    *,
    limit: int,
    max_siblings_per_parent: int = 2,
) -> tuple[list[RankedBullet], list[dict]]:
    selected: list[RankedBullet] = []
    decisions: list[dict] = []
    sibling_counts: dict[str, int] = {}
    strong_or_adjacent_available = sum(
        1 for item in ranked_bullets if item.evidence_classification in {"strong_evidence", "adjacent_evidence"}
    )

    for item in ranked_bullets:
        bullet = item.bullet
        bullet_id = bullet.get("id", "")
        if len(selected) >= limit:
            decisions.append({"id": bullet_id, "reason": "quota filled", "score": item.score})
            continue
        if bullet.get("selectable") is False:
            decisions.append({"id": bullet_id, "reason": "broad grouping node is not selectable", "score": item.score})
            continue
        if item.evidence_classification == "weak_evidence" and strong_or_adjacent_available >= limit:
            decisions.append({"id": bullet_id, "reason": "weak evidence skipped because stronger bullets were available", "score": item.score})
            continue

        parent_id = bullet.get("parent_id")
        parent_heavy_match = len(item.matched_phrases) >= 2 or item.score >= 55
        if parent_id and sibling_counts.get(parent_id, 0) >= max_siblings_per_parent and not parent_heavy_match:
            decisions.append(
                {
                    "id": bullet_id,
                    "reason": f"sibling suppression for parent_id={parent_id}",
                    "score": item.score,
                }
            )
            continue

        selected.append(item)
        if parent_id:
            sibling_counts[parent_id] = sibling_counts.get(parent_id, 0) + 1
        decisions.append({"id": bullet_id, "reason": "selected", "score": item.score})

    return selected, decisions


def select_top_bullets(
    bullets: list[dict],
    job_keywords: list[str],
    profile: dict,
    *,
    limit: int,
) -> list[RankedBullet]:
    ranked = rank_bullets(bullets, job_keywords, profile)
    selected, _ = select_ranked_bullets(ranked, limit=limit)
    return selected


def select_bullets_for_source(
    bullet_bank: list[dict],
    source_id: str,
    job_keywords: list[str],
    profile: dict,
    *,
    limit: int,
    source_accomplishment_ids: list[str] | None = None,
    max_siblings_per_parent: int = 2,
) -> tuple[list[RankedBullet], list[RankedBullet], list[dict]]:
    if source_accomplishment_ids is not None:
        allowed = set(source_accomplishment_ids)
        source_bullets = [bullet for bullet in bullet_bank if bullet.get("source_id") in allowed or bullet.get("id") in allowed]
    else:
        source_bullets = [bullet for bullet in bullet_bank if bullet.get("source_experience") == source_id]
    ranked = rank_bullets(source_bullets, job_keywords, profile)
    selected, decisions = select_ranked_bullets(
        ranked,
        limit=limit,
        max_siblings_per_parent=max_siblings_per_parent,
    )
    return selected, ranked, decisions
