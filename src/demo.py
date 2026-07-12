from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.match import build_match_analysis
from src.position import build_positioning_analysis
from src.prep import build_interview_prep_analysis
from src.render_resume import ResumeRenderer
from src.schema_validation import load_yaml
from src.select_bullets import RankedBullet, rank_bullets, select_ranked_bullets


DEFAULT_DATASET = Path("examples/andy-barks/data.yaml")
DEFAULT_OUTPUT_DIR = Path("examples/andy-barks/generated")
DEFAULT_PROFILE_ID = "profile_curriculum_designer"
DEFAULT_JOB_ID = "job_curriculum_designer_strong"


def run_demo(
    *,
    dataset_path: Path = DEFAULT_DATASET,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    profile_id: str = DEFAULT_PROFILE_ID,
    job_id: str = DEFAULT_JOB_ID,
) -> dict[str, Path]:
    dataset = load_yaml(dataset_path)
    profile = require_by_id(dataset["resume_profiles"], profile_id)
    job = require_by_id(dataset["job_description_metadata"], job_id)
    skill_names = {item["id"]: item["name"] for item in dataset["skills"]}
    job_keywords = build_job_keywords(job, skill_names)
    bullets = adapt_resume_bullets(dataset, skill_names, profile_id)
    ranked = rank_bullets(bullets, job_keywords, profile)
    selected, selection_decisions = select_ranked_bullets(ranked, limit=4)
    kb = build_kb(dataset)
    resume_keywords = build_resume_keywords(selected)

    match_analysis = build_match_analysis(
        kb=kb,
        job_keywords=job_keywords,
        resume_keywords=resume_keywords,
        selected_bullets=selected,
        profile=profile,
    )
    positioning = build_positioning_analysis(kb=kb, profile=profile)
    prep = build_interview_prep_analysis(kb=kb, profile=profile)

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "match_report": output_dir / "match_report.md",
        "resume": output_dir / "resume.md",
        "interview_prep": output_dir / "interview_prep.md",
        "positioning": output_dir / "positioning.md",
        "visualization": output_dir / "visualization.svg",
        "data": output_dir / "demo_data.json",
    }

    paths["match_report"].write_text(
        render_match_report(
            dataset=dataset,
            profile=profile,
            job=job,
            job_keywords=job_keywords,
            selected=selected,
            decisions=selection_decisions,
            analysis=match_analysis,
        ),
        encoding="utf-8",
    )
    paths["resume"].write_text(render_resume(dataset, profile, selected), encoding="utf-8")
    paths["interview_prep"].write_text(render_interview_prep(prep), encoding="utf-8")
    paths["positioning"].write_text(render_positioning(positioning), encoding="utf-8")
    paths["visualization"].write_text(render_svg(dataset, selected, match_analysis), encoding="utf-8")
    paths["data"].write_text(
        json.dumps(
            {
                "dataset": str(dataset_path),
                "profile_id": profile_id,
                "job_id": job_id,
                "job_keywords": job_keywords,
                "selected_bullets": [ranked_to_dict(item) for item in selected],
                "selection_decisions": selection_decisions,
                "match_analysis": match_analysis,
                "positioning": positioning,
                "interview_prep": prep,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return paths


def require_by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any]:
    for item in items:
        if item.get("id") == item_id:
            return dict(item)
    raise ValueError(f"Missing required item `{item_id}`.")


def build_job_keywords(job: dict[str, Any], skill_names: dict[str, str]) -> list[str]:
    keywords: list[str] = []
    keywords.extend(skill_names[skill_id] for skill_id in job.get("keyword_ids", []) if skill_id in skill_names)
    return dedupe(keywords)


def adapt_resume_bullets(dataset: dict[str, Any], skill_names: dict[str, str], profile_id: str) -> list[dict[str, Any]]:
    adapted = []
    explicit_sources = {
        str(bullet.get("source_id"))
        for bullet in dataset["resume_bullets"]
        if bullet.get("source_id")
    }
    for bullet in dataset["resume_bullets"]:
        skill_values = [skill_names.get(skill_id, skill_id) for skill_id in bullet.get("skill_ids", [])]
        adapted.append(
            {
                **bullet,
                "category": first_or_default(bullet.get("tags", []), "synthetic evidence"),
                "skills": skill_values,
                "domains": list(bullet.get("tags", [])),
                "technologies": [],
                "evidence_level": bullet.get("confidence", bullet.get("evidence_status", "medium")),
                "reusable_for_profiles": [profile_id],
                "supports_target_roles": [profile_id],
            }
        )
    for accomplishment in dataset["accomplishments"]:
        if str(accomplishment["id"]) in explicit_sources:
            continue
        skill_values = [skill_names.get(skill_id, skill_id) for skill_id in accomplishment.get("skill_ids", [])]
        adapted.append(
            {
                "id": f"demo_{accomplishment['id']}",
                "text": accomplishment["statement"],
                "source_id": accomplishment["id"],
                "source_type": "accomplishment",
                "skill_ids": list(accomplishment.get("skill_ids", [])),
                "evidence_ids": list(accomplishment.get("evidence_ids", [])),
                "tags": [value.lower() for value in skill_values],
                "category": first_or_default([value.lower() for value in skill_values], "synthetic evidence"),
                "skills": skill_values,
                "domains": [value.lower() for value in skill_values],
                "technologies": [],
                "evidence_level": accomplishment.get("confidence", accomplishment.get("evidence_status", "medium")),
                "reusable_for_profiles": [profile_id],
                "supports_target_roles": [profile_id],
            }
        )
    return adapted


def build_kb(dataset: dict[str, Any]) -> dict[str, Any]:
    person_model: dict[str, list[dict[str, Any]]] = {}
    for claim in dataset["person_claims"]:
        normalized = dict(claim)
        normalized["evidence"] = normalize_claim_evidence(normalized.get("evidence", []))
        person_model.setdefault(str(normalized.get("category", "general")), []).append(normalized)
    return {
        "identity": dataset["identity"],
        "person_model": person_model,
        "stories": dataset["stories"],
        "projects": dataset["projects"],
        "accomplishments": dataset["accomplishments"],
    }


def normalize_claim_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for item in evidence:
        entry = dict(item)
        if entry.get("type") == "reflection":
            entry["type"] = "interview_recollection"
        normalized.append(entry)
    return normalized


def build_resume_keywords(selected: list[RankedBullet]) -> set[str]:
    keywords: set[str] = set()
    for item in selected:
        bullet = item.bullet
        for value in [
            bullet.get("text", ""),
            bullet.get("category", ""),
            *bullet.get("tags", []),
            *bullet.get("skills", []),
            *bullet.get("domains", []),
        ]:
            if value:
                keywords.add(str(value))
    return keywords


def render_match_report(
    *,
    dataset: dict[str, Any],
    profile: dict[str, Any],
    job: dict[str, Any],
    job_keywords: list[str],
    selected: list[RankedBullet],
    decisions: list[dict[str, Any]],
    analysis: dict[str, Any],
) -> str:
    identity = dataset["identity"]
    capability = analysis["capability_fit"]
    assessment = analysis["overall_assessment"]
    return "\n".join(
        [
            f"# Match Report: {identity['display_name']} -> {job['role_title']}",
            "",
            "Synthetic public demo. All employers, projects, dates, evidence, and outputs are fictional.",
            "",
            f"- Profile: {profile['label']}",
            f"- Organization: {job['organization_label']}",
            f"- Overall match score: {capability['score']}%",
            f"- Keywords: {', '.join(job_keywords)}",
            "",
            "## Strong Matches",
            render_list(capability["existing_skills"]),
            "",
            "## Transferable Or Partial Matches",
            render_list(capability["transferable_skills"]),
            "",
            "## Genuine Gaps",
            render_list(capability["genuine_gaps"]),
            "",
            "## Selected Evidence",
            render_ranked_bullets(selected),
            "",
            "## Selection Decisions",
            render_selection_decisions(decisions),
            "",
            "## Questions To Investigate",
            render_list(assessment["questions_to_investigate"]),
            "",
            "## Recommended Actions",
            render_list(assessment["recommended_actions"]),
            "",
        ]
    )


def render_resume(dataset: dict[str, Any], profile: dict[str, Any], selected: list[RankedBullet]) -> str:
    identity = dataset["identity"]
    renderer = ResumeRenderer(root=Path("."), profile_name=str(profile["id"]), render_mode="polished")
    lines = [
        f"# {identity['display_name']}",
        "",
        identity["headline"],
        "",
        "Synthetic example resume generated from fictional evidence only.",
        "",
        "## Summary",
        "",
        renderer.summary(None, "Curriculum designer and library educator focused on accessible learning resources."),
        "",
        "## Selected Experience Evidence",
        "",
    ]
    lines.extend(f"- {renderer.bullet(item.bullet)}" for item in selected)
    lines.extend(["", "## Safety Notes", "", "- Do not present Andy as a software engineer or data scientist."])
    lines.append("- Reflection-only and prohibited person-model claims are excluded from generated resume bullets.")
    lines.append("")
    return "\n".join(lines)


def render_interview_prep(prep: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Interview Prep",
            "",
            "Synthetic public demo based on Andy Barks only.",
            "",
            "## Talking Points",
            render_topic_items(prep["talking_points"]),
            "",
            "## Story Links",
            render_story_links(prep["story_links"]),
            "",
            "## Working Style Notes",
            render_topic_items(prep["working_style_notes"]),
            "",
            "## Risk Flags",
            render_risk_flags(prep["risk_flags"]),
            "",
            "## Questions To Prepare",
            render_list(prep["questions_to_prepare"]),
            "",
        ]
    )


def render_positioning(positioning: dict[str, Any]) -> str:
    constraints = positioning["narrative_constraints"]
    return "\n".join(
        [
            "# Positioning",
            "",
            "Synthetic public demo based on Andy Barks only.",
            "",
            "## Safe To Emphasize",
            render_list(constraints["safe_to_emphasize"]),
            "",
            "## Do Not Overstate",
            render_list(constraints["do_not_overstate"]),
            "",
            "## Positioning Angles",
            render_positioning_angles(positioning["positioning_angles"]),
            "",
            "## Evidence Gaps",
            render_evidence_gaps(positioning["evidence_gaps"]),
            "",
            "## Needs Review",
            render_list(constraints["needs_review"]),
            "",
        ]
    )


def render_svg(dataset: dict[str, Any], selected: list[RankedBullet], match_analysis: dict[str, Any]) -> str:
    identity = dataset["identity"]["display_name"]
    score = match_analysis["capability_fit"]["score"]
    bullet_labels = [str(item.bullet["id"]).replace("_", " ") for item in selected[:4]]
    nodes = [
        (80, 80, identity, "#244c5a"),
        (360, 80, f"Curriculum Designer {score}%", "#4a6b42"),
        (80, 220, "Evidence", "#725738"),
        (360, 220, "Person Model", "#62517a"),
    ]
    evidence_text = "".join(
        f'<text x="105" y="{255 + index * 22}" font-size="13" fill="#2d2d2d">{escape_xml(label.title())}</text>'
        for index, label in enumerate(bullet_labels)
    )
    node_markup = "\n".join(
        f'<rect x="{x}" y="{y}" width="210" height="64" rx="8" fill="{color}"/>\n'
        f'<text x="{x + 18}" y="{y + 38}" font-size="16" fill="#ffffff">{escape_xml(label)}</text>'
        for x, y, label, color in nodes
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360" role="img" aria-labelledby="title desc">
<title id="title">Andy Barks synthetic Career Intelligence demo graph</title>
<desc id="desc">A small visualization connecting Andy Barks, a curriculum designer target role, selected evidence, and person-model reasoning.</desc>
<rect width="640" height="360" fill="#f7f4ee"/>
<line x1="290" y1="112" x2="360" y2="112" stroke="#6f6a60" stroke-width="2"/>
<line x1="185" y1="144" x2="185" y2="220" stroke="#6f6a60" stroke-width="2"/>
<line x1="465" y1="144" x2="465" y2="220" stroke="#6f6a60" stroke-width="2"/>
<line x1="290" y1="252" x2="360" y2="252" stroke="#6f6a60" stroke-width="2"/>
{node_markup}
{evidence_text}
<text x="385" y="255" font-size="13" fill="#2d2d2d">evidence-backed claims</text>
<text x="385" y="277" font-size="13" fill="#2d2d2d">reflection-only caveats</text>
<text x="385" y="299" font-size="13" fill="#2d2d2d">resume safety boundaries</text>
</svg>
"""


def render_ranked_bullets(items: list[RankedBullet]) -> str:
    if not items:
        return "- None."
    return "\n".join(
        f"- `{item.bullet['id']}` ({item.evidence_classification}, score {item.score}): {item.bullet['text']}"
        for item in items
    )


def render_selection_decisions(decisions: list[dict[str, Any]]) -> str:
    if not decisions:
        return "- None."
    return "\n".join(f"- `{item['id']}`: {item['reason']} (score {item['score']})" for item in decisions)


def render_topic_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- None."
    return "\n".join(
        f"- {item.get('topic') or item.get('label')}: {', '.join(item.get('supporting_claims', []))}"
        for item in items
    )


def render_story_links(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- None."
    return "\n".join(f"- `{item['story_id']}`: {', '.join(item['themes'])}" for item in items)


def render_risk_flags(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- None."
    return "\n".join(f"- {item['risk']}: {item['why_it_matters']}" for item in items)


def render_positioning_angles(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- None."
    return "\n".join(
        f"- {item['angle']} ({item['confidence']}): {', '.join(item['supporting_claims'])}"
        for item in items
    )


def render_evidence_gaps(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- None."
    return "\n".join(f"- {item['gap']} {item['why_it_matters']}" for item in items)


def render_list(items: list[str]) -> str:
    if not items:
        return "- None."
    return "\n".join(f"- {item}" for item in items)


def ranked_to_dict(item: RankedBullet) -> dict[str, Any]:
    return asdict(item)


def first_or_default(values: list[str], default: str) -> str:
    return str(values[0]) if values else default


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the public synthetic Career Intelligence demo.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--job-id", default=DEFAULT_JOB_ID)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_demo(
        dataset_path=args.dataset,
        output_dir=args.output_dir,
        profile_id=args.profile_id,
        job_id=args.job_id,
    )
    print("Generated synthetic demo outputs:")
    for label, path in paths.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
