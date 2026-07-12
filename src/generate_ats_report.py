from __future__ import annotations

from pathlib import Path

from src.config import load_default_config
from src.select_bullets import RankedBullet, normalize, normalize_compact


_REASONING_DEFAULTS = load_default_config("reasoning_rules")

ADJACENT_KEYWORDS = {
    "azure": "No cloud provider is explicit, but Kubernetes, CI/CD, and deployment stability provide adjacent infrastructure evidence.",
    "aws": "No cloud provider is explicit, but Kubernetes, CI/CD, and deployment stability provide adjacent infrastructure evidence.",
    "gcp": "No cloud provider is explicit, but Kubernetes, CI/CD, and deployment stability provide adjacent infrastructure evidence.",
    "auditability": "Auditable project evidence may be adjacent, but regulated audit trails are not evidenced.",
    "traceability": "Testing, source-backed reporting, and auditable scoring are adjacent, but regulated traceability is not explicit.",
    "backend architecture": "FastAPI, services, pipelines, and SQLite are present, but formal backend architecture ownership is not deeply detailed.",
    "ai product development": "Strong product/AI overlap exists, but the life-sciences product context is not direct.",
    "vector search": "Retrieval, semantic search, hybrid retrieval, and Neo4j are present, but vector databases are not explicit.",
    "vector databases": "Neo4j and retrieval are present, but vector database ownership is not explicit.",
    "security": "Privacy-aware local health data handling exists, but application security engineering is not explicit.",
    "secure cloud": "Deployment and privacy-adjacent work exists, but secure cloud deployment is not explicit.",
    "grounded retrieval": "Hybrid retrieval and RAG are evidenced, but grounded retrieval is not named directly.",
    "agentic ai": "Agent-based systems are evidenced, but agentic AI is not named directly in the source material.",
    "production apis": "FastAPI, REST APIs, and production behavior are evidenced, but production API ownership is not stated as a single claim.",
    "databases": "SQLite and Neo4j are evidenced, but broad database engineering is not deeply detailed.",
    "services": "FastAPI and integrations are evidenced, but service design/ownership is not deeply detailed.",
    "clinical workflows": "Health and enterprise workflow experience exist, but clinical workflows are not direct.",
    "regulatory workflows": "Enterprise workflow experience exists, but regulatory workflows are not direct.",
    "pharmaceutical workflows": "No pharmaceutical workflow experience is evidenced.",
    "document comparison": "Document/data workflow work is adjacent, but document comparison is not explicit.",
    "content classification": "AI workflow work is adjacent, but content classification is not explicit.",
    "summarization": "LLM answer generation is adjacent, but summarization is not explicit.",
    "guardrails": "Evaluation and production behavior are adjacent, but guardrails are not explicit.",
    "observability": "Production behavior and CI/CD are adjacent, but observability is not explicit.",
    "monitoring systems": "Readiness reports, dashboards, guardrails, and CI/CD reliability are adjacent, but production observability ownership is not explicit.",
    "monitoring": "Readiness reports, dashboards, and system-health adjacent work exist, but production monitoring ownership is not explicit.",
    "ai platform": "Platform-oriented AI work may be evidenced, but the target platform context may not be direct.",
    "backend development": "Python/FastAPI backend work is evidenced, but the role's Java/PostgreSQL backend stack is not direct.",
    "deployed features": "Production behavior, CI/CD reliability, and product delivery may be evidenced, but the target deployment scale may not be direct.",
    "health outcomes": "Human-performance and recovery decision-support work is evidenced, but member-facing health outcomes are not direct.",
    "member-facing features": "User-facing product surfaces may be evidenced, but this exact audience may not be direct.",
    "performance optimization": "Human-performance modeling is evidenced, but backend performance optimization is not explicit.",
    "personalized insights": "Decision-support or recommendation work may be adjacent, but this exact personalization context may not be direct.",
    "relational database design": "SQLite structured storage is evidenced, but relational database design at PostgreSQL scale is not explicit.",
    "scalable": "Modular architecture, FastAPI services, and CI/CD reliability are adjacent, but large-scale scalability is not explicit.",
    "scalable system design": "Modular architecture, FastAPI services, and CI/CD reliability are adjacent, but large-scale system design is not explicit.",
    "tool use": "Agent-based systems are adjacent, but tool use is not explicit.",
    "llmops": "Production behavior, evaluation, CI/CD, and deployment stability are adjacent, but LLMOps is not explicit.",
    "java": "Backend engineering is evidenced in Python/FastAPI, but Java is not evidenced.",
    "postgreSQL": "SQLite is evidenced for local structured storage, but PostgreSQL is not evidenced.",
    "postgresql": "SQLite is evidenced for local structured storage, but PostgreSQL is not evidenced.",
    "kafka": "Event-driven workflow systems are evidenced, but Kafka itself is not evidenced.",
    "sqs": "Asynchronous/event-driven workflow evidence exists, but SQS itself is not evidenced.",
}

CRITICAL_GAPS = {
    "gxp",
    "hipaa",
    "21 cfr part 11",
    "veeva",
    "gdpr",
    "multi-tenancy",
    "infrastructure as code",
    "docker",
    "java",
    "postgresql",
}

LOW_SIGNAL_GAP_TERMS = {
    "application",
    "assets",
    "capabilities",
    "customers",
    "developer",
    "features",
    "member",
    "members",
    "people",
    "product",
    "products",
    "role",
    "software",
    "system",
    "systems",
    "team",
    "tools",
    "users",
    "work",
}

INTERNAL_TOOLING_TERMS = {
    "internal ai tools",
    "internal ai tooling",
    "ai productivity",
    "workflow automation",
    "internal chatbot",
    "internal chatbots",
    "knowledge retrieval",
    "internal knowledge retrieval",
    "efficiency agents",
    "meeting summaries",
    "requirements generation",
    "code review support",
    "rfp",
    "rfq",
    "developer experience",
    "adoption",
    "productivity",
    "business process",
}

STRENGTH_LABELS_BY_ID: dict[str, str] = {}
INTERNAL_TOOLING_STRENGTH_ORDER: list[str] = []
DISPLAY_KEYWORD_OVERRIDES = {
    "llmops": "LLMOps",
    "gxp": "GxP",
    "hipaa": "HIPAA",
    "gdpr": "GDPR",
    "veeva": "Veeva",
    "21 cfr part 11": "21 CFR Part 11",
    "ci/cd": "CI/CD",
    "apis": "APIs",
    "llms": "LLMs",
}

ADJACENT_KEYWORDS = dict(_REASONING_DEFAULTS.get("adjacent_keywords", ADJACENT_KEYWORDS))
CRITICAL_GAPS = set(_REASONING_DEFAULTS.get("critical_gaps", CRITICAL_GAPS))
LOW_SIGNAL_GAP_TERMS = set(_REASONING_DEFAULTS.get("low_signal_gap_terms", LOW_SIGNAL_GAP_TERMS))
INTERNAL_TOOLING_TERMS = set(_REASONING_DEFAULTS.get("internal_tooling_terms", INTERNAL_TOOLING_TERMS))
STRENGTH_LABELS_BY_ID = dict(_REASONING_DEFAULTS.get("strength_labels_by_id", STRENGTH_LABELS_BY_ID))
INTERNAL_TOOLING_STRENGTH_ORDER = list(
    _REASONING_DEFAULTS.get("internal_tooling_strength_order", INTERNAL_TOOLING_STRENGTH_ORDER)
)
DISPLAY_KEYWORD_OVERRIDES = dict(_REASONING_DEFAULTS.get("display_keyword_overrides", DISPLAY_KEYWORD_OVERRIDES))


def render_list(items: list[str], *, empty: str) -> str:
    if not items:
        return f"- {empty}"
    return "\n".join(f"- {item}" for item in items)


def display_keyword(keyword: str) -> str:
    normalized = normalize(keyword)
    return DISPLAY_KEYWORD_OVERRIDES.get(normalized, keyword if any(char.isupper() for char in keyword) else normalized.title())


def bullet_label(item: RankedBullet) -> str:
    source = str(item.bullet.get("source_experience") or item.bullet.get("source_id") or item.bullet.get("parent_id") or "")
    label_source = source or str(item.bullet.get("id", "Selected evidence"))
    return label_source.replace("_", " ").replace("-", " ").title()


def match_terms_for(item: RankedBullet) -> list[str]:
    return [
        *item.matched_phrases,
        *item.matched_technologies,
        *item.matched_skills,
        *item.matched_domains,
        *item.matched_keywords,
    ]


def is_internal_tooling_role(job_keywords: list[str]) -> bool:
    return bool({normalize(item) for item in job_keywords} & INTERNAL_TOOLING_TERMS)


def strength_term(item: RankedBullet) -> str:
    bullet_id = str(item.bullet.get("id", ""))
    if bullet_id in STRENGTH_LABELS_BY_ID:
        return STRENGTH_LABELS_BY_ID[bullet_id]
    terms = match_terms_for(item)
    semantic_terms = [
        term
        for term in terms
        if normalize(term)
        in {
            "developer experience",
            "internal ai tools",
            "retrieval systems",
            "ambiguous builder",
            "solving user pain",
            "decision support",
        "production ai",
        "production ai systems",
        "backend services",
        "backend services and apis",
        "platform infrastructure",
        "reliability / system health",
        "asynchronous processing",
        "health performance data",
        }
    ]
    return display_keyword(semantic_terms[0] if semantic_terms else terms[0])


def selected_match_terms(selected_bullets: list[RankedBullet]) -> set[str]:
    terms: set[str] = set()
    for item in selected_bullets:
        if item.evidence_classification != "strong_evidence":
            continue
        for value in [
            *item.matched_keywords,
            *item.matched_phrases,
            *item.matched_technologies,
            *item.matched_skills,
            *item.matched_domains,
        ]:
            terms.add(normalize(value))
            terms.add(normalize_compact(value))
    return terms


def classify_keywords(
    *,
    job_keywords: list[str],
    resume_keywords: set[str],
    selected_bullets: list[RankedBullet],
) -> dict[str, list[str]]:
    resume_terms = {normalize(item) for item in resume_keywords} | {normalize_compact(item) for item in resume_keywords}
    strong_terms = selected_match_terms(selected_bullets)
    strong_matches: list[str] = []
    adjacent_matches: list[str] = []
    true_gaps: list[str] = []

    for keyword in job_keywords:
        normalized = normalize(keyword)
        compact = normalize_compact(keyword)
        if normalized in LOW_SIGNAL_GAP_TERMS:
            continue
        label = display_keyword(keyword)
        if normalized in strong_terms or compact in strong_terms or normalized in resume_terms or compact in resume_terms:
            strong_matches.append(label)
        elif normalized == "apis" and ({"api", "apis", "fastapi", "restapis"} & resume_terms):
            strong_matches.append(label)
        elif normalized in {"backend services", "restful api design", "production apis"} and (
            {"api", "apis", "fastapi", "restapis", "backend"} & resume_terms
        ):
            strong_matches.append(label)
        elif normalized in ADJACENT_KEYWORDS:
            adjacent_matches.append(f"{label}: {ADJACENT_KEYWORDS[normalized]}")
        elif normalized in CRITICAL_GAPS:
            true_gaps.append(label)
        elif "workflow" in normalized and {"workflows", "workflow automation"} & resume_terms:
            adjacent_matches.append(f"{label}: Workflow experience exists, but this exact domain is not evidenced.")
        else:
            true_gaps.append(label)

    return {
        "strong_matches": sorted(dict.fromkeys(strong_matches)),
        "adjacent_matches": sorted(dict.fromkeys(adjacent_matches)),
        "true_gaps": sorted(dict.fromkeys(true_gaps)),
    }


def strength_lines(selected_bullets: list[RankedBullet], job_keywords: list[str], *, limit: int = 8) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    if is_internal_tooling_role(job_keywords):
        by_id = {str(item.bullet.get("id", "")): item for item in selected_bullets}
        ordered = [by_id[item] for item in INTERNAL_TOOLING_STRENGTH_ORDER if item in by_id]
        ordered.extend(sorted([item for item in selected_bullets if item not in ordered], key=lambda ranked: ranked.score, reverse=True))
    else:
        ordered = sorted(selected_bullets, key=lambda ranked: ranked.score, reverse=True)

    for item in ordered:
        if item.evidence_classification not in {"strong_evidence", "adjacent_evidence"}:
            continue
        terms = match_terms_for(item)
        if not terms:
            continue
        term = strength_term(item)
        key = normalize_compact(f"{term}-{bullet_label(item)}")
        if key in seen:
            continue
        seen.add(key)
        why = "; ".join(item.reasons[:3]) if item.reasons else "selected as source-backed role evidence"
        lines.append(f"{term} -> {bullet_label(item)} ({why})")
        if len(lines) >= limit:
            break
    return lines


def recommended_changes(
    *,
    selected_bullets: list[RankedBullet],
    adjacent_matches: list[str],
    true_gaps: list[str],
) -> list[str]:
    recommendations: list[str] = []
    selected_ids = {str(item.bullet.get("id", "")) for item in selected_bullets}
    selected_terms = {normalize(term) for item in selected_bullets for term in match_terms_for(item)}

    if "rapid prototyping" in selected_terms or "ambiguous builder" in selected_terms:
        recommendations.append("Mention rapid prototyping, ambiguity, and bias for action where source evidence supports it.")
    if {"decision support", "recommendations"} & selected_terms:
        recommendations.append("Surface decision-support evidence for roles involving monitoring or recommendations.")
    if adjacent_matches:
        recommendations.append("Use adjacent matches carefully: explain the evidence without renaming it as direct experience.")
    if true_gaps:
        recommendations.append("Do not add true-gap terms unless there is source-backed experience; keep them as honest missing context.")
    return recommendations or ["Review selected evidence manually before sending."]


def overall_match_score(*, strong_count: int, adjacent_count: int, gap_count: int) -> int:
    total = strong_count + adjacent_count + gap_count
    if total == 0:
        return 0
    score = ((strong_count * 1.0) + (adjacent_count * 0.45)) / total
    return round(score * 100)


def generate_ats_report(
    *,
    template_path: str | Path,
    output_path: str | Path,
    resume_output: str | Path,
    job_path: str | Path,
    profile_name: str,
    job_keywords: list[str],
    resume_keywords: set[str],
    selected_bullets: list[RankedBullet] | None = None,
    ranked_bullets: list[RankedBullet] | None = None,
) -> dict[str, list[str]]:
    selected_bullets = selected_bullets or []
    ats_data = classify_keywords(
        job_keywords=job_keywords,
        resume_keywords=resume_keywords,
        selected_bullets=selected_bullets,
    )
    notes = [
        "Rule-based career-strategy report; review manually before sending.",
        "Adjacent matches are not claims of direct experience.",
        "Do not add missing regulated keywords unless they reflect real source-backed experience.",
    ]
    strengths = strength_lines(selected_bullets, job_keywords)
    recommendations = recommended_changes(
        selected_bullets=selected_bullets,
        adjacent_matches=ats_data["adjacent_matches"],
        true_gaps=ats_data["true_gaps"],
    )
    overall_score = overall_match_score(
        strong_count=len(ats_data["strong_matches"]),
        adjacent_count=len(ats_data["adjacent_matches"]),
        gap_count=len(ats_data["true_gaps"]),
    )

    rendered = "\n".join(
        [
            f"# ATS Report: {Path(job_path).stem}",
            "",
            f"Resume: `{resume_output}`",
            f"Job description: `{job_path}`",
            f"Profile: `{profile_name}`",
            "",
            f"## Overall Match: {overall_score}%",
            "",
            "## Top Strengths",
            "",
            render_list(strengths or ats_data["strong_matches"], empty="No strong source-backed strengths found."),
            "",
            "## Strong Matches",
            "",
            render_list(ats_data["strong_matches"], empty="No strong keyword matches found."),
            "",
            "## Partial Matches",
            "",
            render_list(ats_data["adjacent_matches"], empty="No adjacent keyword matches found."),
            "",
            "## True Gaps",
            "",
            render_list(ats_data["true_gaps"], empty="No true gaps found."),
            "",
            "## Recommended Resume Changes",
            "",
            render_list(recommendations, empty="No recommendations."),
            "",
            "## Honesty Note",
            "",
            render_list(notes, empty="No notes."),
        ]
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered + "\n", encoding="utf-8")
    return ats_data
