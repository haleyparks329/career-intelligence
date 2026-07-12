from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


RENDER_MODES = {"raw", "polished", "concise", "technical", "product"}
STRONG_VERBS = {
    "built": "Built",
    "designed": "Designed",
    "implemented": "Implemented",
    "shipped": "Shipped",
    "created": "Created",
    "integrated": "Integrated",
    "translated": "Translated",
    "modeled": "Modeled",
    "automated": "Automated",
    "established": "Established",
    "improved": "Improved",
    "led": "Led",
    "planned": "Planned",
    "developed": "Developed",
    "hardened": "Hardened",
    "operated": "Operated",
}
WEAK_VERB_REPLACEMENTS = {
    "helped build": "Built",
    "helped create": "Created",
    "worked on": "Contributed to",
    "supported": "Supported",
}


def load_yaml_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or []


def load_rendering_data(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    rendering_root = root / "data" / "rendering"
    bullets = {
        item["source_bullet_id"]: item
        for item in load_yaml_list(rendering_root / "resume_bullets.yaml")
        if item.get("source_bullet_id")
    }
    summaries = {
        item["source_summary_id"]: item
        for item in load_yaml_list(rendering_root / "summaries.yaml")
        if item.get("source_summary_id")
    }
    projects = {
        item["source_project_id"]: item
        for item in load_yaml_list(rendering_root / "project_descriptions.yaml")
        if item.get("source_project_id")
    }
    return {"bullets": bullets, "summaries": summaries, "projects": projects}


def load_identity(root: Path) -> dict[str, Any]:
    path = root / "data" / "identity.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("professional_identity", {})


def variant_key(entry: dict[str, Any], *, profile_name: str, render_mode: str) -> str:
    preferred = entry.get("preferred_variant_by_profile", {})
    profile_aliases = {"ai_productivity_engineer": "ai_product_engineer"}
    aliased_profile = profile_aliases.get(profile_name, profile_name)
    if render_mode == "polished" and preferred.get(profile_name):
        return str(preferred[profile_name])
    if render_mode == "polished" and preferred.get(aliased_profile):
        return str(preferred[aliased_profile])
    if render_mode in entry.get("variants", {}):
        return render_mode
    if preferred.get(profile_name):
        return str(preferred[profile_name])
    if preferred.get(aliased_profile):
        return str(preferred[aliased_profile])
    return "polished"


def render_variant(entry: dict[str, Any], *, profile_name: str, render_mode: str, fallback: str) -> str:
    variants = entry.get("variants", {})
    key = variant_key(entry, profile_name=profile_name, render_mode=render_mode)
    return str(variants.get(key) or variants.get("polished") or variants.get("raw") or fallback)


def ensure_sentence(text: str) -> str:
    cleaned = " ".join(str(text).split())
    if not cleaned:
        return cleaned
    return cleaned if cleaned.endswith((".", "!", "?")) else f"{cleaned}."


def split_sentences(text: str) -> list[str]:
    sentences = []
    for part in str(text).split("."):
        cleaned = part.strip()
        if cleaned:
            sentences.append(ensure_sentence(cleaned))
    return sentences


def identity_summary(identity: dict[str, Any], rendered_summary: str) -> str:
    headline = ensure_sentence(str(identity.get("headline", "")))
    if not headline:
        return rendered_summary
    remainder = split_sentences(rendered_summary)[1:]
    if not remainder:
        return headline
    return " ".join([headline, *remainder[:2]])


def fallback_render_bullet(bullet: dict[str, Any]) -> str:
    text = ensure_sentence(str(bullet.get("text", "")))
    lowered = text.lower()
    for weak, replacement in WEAK_VERB_REPLACEMENTS.items():
        if lowered.startswith(weak):
            rest = text[len(weak) :].lstrip(" .")
            return ensure_sentence(f"{replacement} {rest}")
    first_word = text.split(" ", 1)[0].strip(".").lower() if text else ""
    if first_word in STRONG_VERBS:
        rest = text.split(" ", 1)[1] if " " in text else ""
        return ensure_sentence(f"{STRONG_VERBS[first_word]} {rest}".strip())
    if text:
        technologies = [
            str(item).replace("_", " ").title()
            for item in bullet.get("technologies", [])
            if str(item).lower() not in {"skill_python", "skill_typescript"}
        ][:4]
        domains = [str(item).replace("_", " ") for item in bullet.get("domains", [])[:2]]
        skills = [str(item).replace("_", " ") for item in bullet.get("skills", [])[:2]]
        context_parts = []
        if technologies and not any(tech.lower() in lowered for tech in technologies):
            context_parts.append("using " + ", ".join(technologies))
        if domains and not any(domain in lowered for domain in domains):
            context_parts.append("for " + ", ".join(domains))
        if skills and len(text.split()) < 9:
            context_parts.append("demonstrating " + ", ".join(skills))
        first_word = text.split(" ", 1)[0].strip(".").lower() if text else ""
        if context_parts and len(text.split()) < 10 and first_word in {"built", "created", "designed", "implemented"}:
            return ensure_sentence(f"{text.rstrip('.')} {'; '.join(context_parts)}")
        return text

    artifact = bullet.get("category", "system").replace("_", " ")
    technologies = ", ".join(str(item) for item in bullet.get("technologies", [])[:3])
    context = f" using {technologies}" if technologies else ""
    return ensure_sentence(f"Built {artifact}{context}")


class ResumeRenderer:
    def __init__(self, *, root: Path, profile_name: str, render_mode: str = "polished") -> None:
        if render_mode not in RENDER_MODES:
            allowed = ", ".join(sorted(RENDER_MODES))
            raise ValueError(f"Unknown render mode '{render_mode}'. Expected one of: {allowed}.")
        self.profile_name = profile_name
        self.render_mode = render_mode
        self.data = load_rendering_data(root)
        self.identity = load_identity(root)

    def bullet(self, bullet: dict[str, Any]) -> str:
        if self.render_mode == "raw":
            return ensure_sentence(str(bullet.get("text", "")))
        bullet_id = str(bullet.get("id", ""))
        entry = self.data["bullets"].get(bullet_id)
        if not entry:
            return fallback_render_bullet(bullet)
        return ensure_sentence(
            render_variant(
                entry,
                profile_name=self.profile_name,
                render_mode=self.render_mode,
                fallback=fallback_render_bullet(bullet),
            )
        )

    def summary(self, summary: dict[str, Any] | None, fallback: str) -> str:
        if self.render_mode == "raw" or not summary:
            return ensure_sentence(fallback)
        entry = self.data["summaries"].get(str(summary.get("id", "")))
        if not entry:
            return ensure_sentence(fallback)
        rendered = ensure_sentence(
            render_variant(
                entry,
                profile_name=self.profile_name,
                render_mode=self.render_mode,
                fallback=fallback,
            )
        )
        if self.render_mode == "polished" and self.identity:
            return identity_summary(self.identity, rendered)
        return rendered

    def project_description(self, project: dict[str, Any]) -> str:
        fallback = str(project.get("description", ""))
        if self.render_mode == "raw":
            return ensure_sentence(fallback)
        entry = self.data["projects"].get(str(project.get("id", "")))
        if not entry:
            return ensure_sentence(fallback)
        return ensure_sentence(
            render_variant(
                entry,
                profile_name=self.profile_name,
                render_mode=self.render_mode,
                fallback=fallback,
            )
        )
