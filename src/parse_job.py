from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "to",
    "we",
    "with",
    "you",
    "your",
    "about",
    "areas",
    "assets",
    "around",
    "based",
    "build",
    "building",
    "but",
    "capabilities",
    "can",
    "challenge",
    "chance",
    "company",
    "core",
    "customers",
    "demos",
    "depend",
    "developer",
    "design",
    "engine",
    "enough",
    "every",
    "focus",
    "front",
    "good",
    "halves",
    "has",
    "have",
    "help",
    "helping",
    "key",
    "leading",
    "learn",
    "moved",
    "more",
    "not",
    "offer",
    "our",
    "one",
    "people",
    "product",
    "products",
    "put",
    "reliable",
    "responsibilities",
    "role",
    "shape",
    "ship",
    "software",
    "strong",
    "systems",
    "team",
    "this",
    "turn",
    "two",
    "way",
    "what",
    "will",
    "work",
    "writer",
}

IMPORTANT_PHRASES = [
    "AI colleague",
    "AI application",
    "AI assistants",
    "AI features",
    "AI Platform",
    "AI productivity",
    "AI workflows",
    "agentic AI",
    "agent systems",
    "ambiguous problems",
    "API integrations",
    "asynchronous processing",
    "bias for action",
    "backend development",
    "backend services",
    "business process",
    "code review support",
    "condition monitoring",
    "customer feedback",
    "customer-facing",
    "data-intensive products",
    "decision-making",
    "developer experience",
    "efficiency agents",
    "grounded retrieval",
    "hybrid retrieval",
    "internal AI tools",
    "internal AI tooling",
    "internal chatbot",
    "internal chatbots",
    "internal knowledge retrieval",
    "internal tools",
    "industrial AI",
    "industrial asset monitoring",
    "knowledge retrieval",
    "machine monitoring",
    "machine signals",
    "meeting summaries",
    "context engineering",
    "deployed features",
    "production AI",
    "product engineering",
    "production APIs",
    "productivity",
    "relational database design",
    "requirements generation",
    "RESTful API design",
    "reusable tools",
    "RFP",
    "RFQ",
    "tool use",
    "guardrails",
    "evals",
    "observability",
    "production APIs",
    "rapid prototyping",
    "reasoning loops",
    "scalable features",
    "scalable system design",
    "semantic search",
    "signal analytics",
    "startup",
    "system health",
    "system stability",
    "service design",
    "infrastructure as code",
    "vector databases",
    "vector search",
    "workflow automation",
    "document comparison",
    "content classification",
    "traceability",
    "auditability",
    "regulated cloud",
    "secure cloud",
    "multi-tenancy",
    "LLMOps",
    "GxP",
    "21 CFR Part 11",
    "GDPR",
    "HIPAA",
    "Veeva",
    "clinical workflows",
    "regulatory workflows",
    "pharmaceutical workflows",
    "human performance",
    "health outcomes",
    "personalized insights",
    "performance optimization",
    "monitoring systems",
]

IMPORTANT_TERMS = [
    "Python",
    "React",
    "FastAPI",
    "Kubernetes",
    "CI/CD",
    "APIs",
    "integrations",
    "deployment",
    "retrieval",
    "summarization",
    "orchestration",
    "backend",
    "architecture",
    "cloud",
    "AWS",
    "Azure",
    "GCP",
    "Docker",
    "security",
    "databases",
    "services",
    "LLMs",
    "AI",
    "adoption",
    "chatbots",
    "connectors",
    "Java",
    "Kafka",
    "SQS",
    "PostgreSQL",
]

ROLE_NOUNS = {
    "agent",
    "agents",
    "analytics",
    "application",
    "architecture",
    "assistant",
    "asset",
    "automation",
    "backend",
    "cloud",
    "colleague",
    "data",
    "deployment",
    "developer",
    "diagnoses",
    "engineering",
    "evaluation",
    "features",
    "feedback",
    "industrial",
    "infrastructure",
    "integrations",
    "machine",
    "monitoring",
    "platform",
    "prototyping",
    "reliability",
    "retrieval",
    "scalable",
    "search",
    "semantic",
    "signal",
    "startup",
    "tools",
    "workflows",
}

LOW_SIGNAL_STANDALONE_TERMS = {
    "application",
    "assets",
    "capabilities",
    "company",
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

JOB_TITLE_TERMS = {
    "Backend Software Engineer II",
    "Software Engineer II",
}

DOMAIN_STOPWORDS = STOPWORDS | {
    "about",
    "across",
    "all",
    "also",
    "already",
    "available",
    "based",
    "brief",
    "directly",
    "early",
    "end",
    "entire",
    "exact",
    "experience",
    "fit",
    "full",
    "growth",
    "high",
    "impact",
    "include",
    "interested",
    "like",
    "member",
    "office",
    "practicalities",
    "previous",
    "real",
    "ready",
    "right",
    "salary",
    "senior",
    "simple",
    "solid",
    "such",
    "through",
    "type",
    "use",
    "using",
    "value",
    "youll",
}

CAPITALIZED_HEADING_WORDS = {
    "about",
    "accelerated",
    "backend",
    "boston",
    "bonus",
    "build",
    "career",
    "competitive",
    "employment",
    "engineer",
    "experiences",
    "future",
    "great",
    "how",
    "impactful",
    "key",
    "location",
    "nice",
    "offer",
    "points",
    "practicalities",
    "ready",
    "reports",
    "toolkit",
    "what",
    "when",
    "with",
    "you",
    "your",
}


def read_job_description(path: str | Path) -> str:
    text = Path(path).read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].strip()
    return text


def extract_capitalized_terms(text: str) -> list[str]:
    terms: list[str] = []
    for match in re.finditer(r"\b(?:[A-Z][A-Za-z0-9+.#-]*|AI|LLM|GCP|AWS|CI/CD)(?:[ .-]+(?:[A-Z][A-Za-z0-9+.#-]*|AI|LLM|GCP|AWS|CI/CD))*\b", text):
        value = " ".join(match.group(0).replace("\n", " ").split()).strip(".,;:!?()[]{}")
        if len(value) < 2:
            continue
        words = [word.lower() for word in re.findall(r"[A-Za-z][A-Za-z0-9+.#-]*", value)]
        if value.lower() in DOMAIN_STOPWORDS or any(word in CAPITALIZED_HEADING_WORDS for word in words):
            continue
        has_acronym = value in IMPORTANT_TERMS
        has_role_noun = any(word in ROLE_NOUNS for word in words) and len(words) > 1
        has_known_tech = value in IMPORTANT_TERMS or value in IMPORTANT_PHRASES
        if not (has_acronym or has_known_tech or has_role_noun):
            continue
        terms.append(value)
    return terms[:8]


def extract_role_phrases(words: list[str], *, limit: int = 18) -> list[str]:
    counts: Counter[str] = Counter()
    important_phrase_keys = {phrase.lower() for phrase in IMPORTANT_PHRASES}
    for size in (3, 2):
        for index in range(0, max(0, len(words) - size + 1)):
            phrase_words = words[index : index + size]
            if any(word in DOMAIN_STOPWORDS for word in phrase_words):
                continue
            phrase = " ".join(phrase_words)
            if phrase not in important_phrase_keys and any(word in LOW_SIGNAL_STANDALONE_TERMS for word in phrase_words):
                continue
            role_noun_count = sum(1 for word in phrase_words if word in ROLE_NOUNS)
            if phrase not in important_phrase_keys and role_noun_count < size:
                continue
            if len(phrase) < 8:
                continue
            counts[phrase] += 1
    return [phrase for phrase, _ in counts.most_common(limit)]


def extract_keywords(text: str, *, limit: int = 40) -> list[str]:
    lowered = text.lower()
    phrases = [phrase for phrase in IMPORTANT_PHRASES if phrase.lower() in lowered]
    priority_terms = [
        term
        for term in IMPORTANT_TERMS
        if re.search(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", lowered)
    ]
    raw_words = re.findall(r"[a-zA-Z][a-zA-Z0-9+.#-]{2,}", lowered)
    words = [word.strip(".,;:!?()[]{}") for word in raw_words]
    role_phrases = extract_role_phrases(words)
    capitalized_terms = extract_capitalized_terms(text)
    counts = Counter(
        word
        for word in words
        if word not in DOMAIN_STOPWORDS
        and word not in LOW_SIGNAL_STANDALONE_TERMS
        and word in ROLE_NOUNS
    )
    remaining = max(0, limit - len(phrases) - len(priority_terms) - len(role_phrases) - len(capitalized_terms))
    keywords = phrases + priority_terms + role_phrases + capitalized_terms + [word for word, _ in counts.most_common(remaining)]
    deduped: list[str] = []
    seen: set[str] = set()
    for keyword in keywords:
        key = keyword.lower()
        if keyword in JOB_TITLE_TERMS:
            continue
        if key in LOW_SIGNAL_STANDALONE_TERMS:
            continue
        if key not in seen:
            deduped.append(keyword)
            seen.add(key)
    return deduped
