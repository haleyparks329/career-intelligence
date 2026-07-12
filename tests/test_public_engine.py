from pathlib import Path
import subprocess
import sys

from src.config import load_default_config
from src.demo import run_demo
from src import generate_ats_report, person_reasoning, select_bullets
from src.generate_ats_report import classify_keywords, overall_match_score
from src.match import build_match_analysis
from src.parse_job import extract_keywords
from src.person_model import is_claim_safe_for_resume_bullets, select_person_claims
from src.position import build_positioning_analysis
from src.prep import build_interview_prep_analysis
from src.render_resume import ResumeRenderer
from src.schema_validation import load_yaml, validate_template
from src.select_bullets import RankedBullet, rank_bullets, select_ranked_bullets


def claim(
    claim_id: str,
    *,
    category: str = "systems_thinking",
    safe_for: list[str] | None = None,
    caution_for: list[str] | None = None,
    supports_target_roles: list[str] | None = None,
    related_accomplishments: list[str] | None = None,
    related_projects: list[str] | None = None,
    related_stories: list[str] | None = None,
    evidence_type: str = "work_artifact",
) -> dict:
    return {
        "id": claim_id,
        "label": claim_id.replace("_", " ").title(),
        "statement": "A neutral public fixture claim.",
        "category": category,
        "confidence": "high",
        "evidence": [
            {
                "id": f"{claim_id}_evidence",
                "type": evidence_type,
                "source": "synthetic_fixture",
                "source_ref": "tests",
                "description": "Synthetic evidence.",
            }
        ],
        "related_accomplishments": related_accomplishments or [],
        "related_projects": related_projects or [],
        "related_stories": related_stories or [],
        "supports_target_roles": supports_target_roles or [],
        "safe_for": safe_for or ["role_matching", "positioning", "interview_prep"],
        "caution_for": caution_for or [],
        "notes": "Synthetic fixture.",
    }


def sample_kb() -> dict:
    return {
        "identity": {
            "differentiators": ["Turns ambiguous workflow problems into usable systems."],
            "anti_positioning": ["Do not imply direct regulated-domain experience without evidence."],
        },
        "person_model": {
            "work_style": [
                claim(
                    "systems_fit",
                    supports_target_roles=["workflow_engineer"],
                    related_accomplishments=["accomp_workflow"],
                    related_projects=["project_ops"],
                    related_stories=["story_ops"],
                ),
                claim(
                    "reflection_only",
                    evidence_type="interview_recollection",
                    caution_for=["role_matching"],
                    supports_target_roles=["workflow_engineer"],
                ),
            ]
        },
        "stories": [
            {
                "id": "story_ops",
                "useful_for_questions": ["workflow automation"],
            }
        ],
    }


def ranked_python_evidence() -> list[RankedBullet]:
    return [
        RankedBullet(
            bullet={"id": "python_pipeline", "source_id": "synthetic_project"},
            score=25,
            matched_keywords=[],
            matched_phrases=[],
            matched_domains=[],
            matched_technologies=["Python"],
            matched_skills=[],
            evidence_classification="strong_evidence",
            reasons=["synthetic evidence"],
        )
    ]


def test_extract_keywords_finds_terms_without_private_fixtures() -> None:
    text = "Build Python workflow automation with APIs, reliability, and user-facing reporting."
    keywords = extract_keywords(text)

    assert "Python" in keywords
    assert "workflow automation" in keywords
    assert "APIs" in keywords


def test_bullet_ranking_and_selection_use_neutral_profile_data() -> None:
    bullets = [
        {
            "id": "workflow_python",
            "text": "Built Python workflow automation for support teams.",
            "source_experience": "synthetic_role",
            "category": "automation",
            "technologies": ["Python"],
            "skills": ["workflow automation"],
            "evidence_level": "verified",
            "reusable_for_profiles": ["workflow_engineer"],
        },
        {
            "id": "broad_group",
            "text": "General operations work.",
            "source_experience": "synthetic_role",
            "selectable": False,
        },
    ]
    ranked = rank_bullets(bullets, ["Python", "workflow automation"], {"id": "workflow_engineer"})
    selected, decisions = select_ranked_bullets(ranked, limit=1)

    assert selected[0].bullet["id"] == "workflow_python"
    assert selected[0].evidence_classification == "strong_evidence"
    assert any(item["id"] == "broad_group" for item in decisions)


def test_match_keeps_capability_and_person_reasoning_separate() -> None:
    result = build_match_analysis(
        kb=sample_kb(),
        job_keywords=["Python", "GxP"],
        resume_keywords={"python"},
        selected_bullets=ranked_python_evidence(),
        profile={"id": "workflow_engineer", "target_roles": ["Workflow Engineer"]},
    )

    assert result["capability_fit"]["existing_skills"] == ["Python"]
    assert result["capability_fit"]["genuine_gaps"] == ["GxP"]
    assert "systems_fit" in {item["id"] for item in result["person_fit"]["fit_signals"]}
    assert "reflection_only" in {item["id"] for item in result["person_fit"]["mismatch_signals"]}


def test_person_model_resume_safety_is_conservative() -> None:
    unsafe = claim(
        "reflection_resume_claim",
        safe_for=["resume_bullets"],
        related_accomplishments=["accomp"],
        evidence_type="interview_recollection",
    )
    safe = claim(
        "safe_resume_claim",
        safe_for=["resume_bullets"],
        related_accomplishments=["accomp"],
    )

    assert is_claim_safe_for_resume_bullets(unsafe) is False
    assert is_claim_safe_for_resume_bullets(safe) is True


def test_position_and_prep_outputs_are_source_linked() -> None:
    positioning = build_positioning_analysis(
        kb=sample_kb(),
        profile={"id": "workflow_engineer", "target_roles": ["Workflow Engineer"]},
    )
    prep = build_interview_prep_analysis(
        kb=sample_kb(),
        profile={"id": "workflow_engineer", "target_roles": ["Workflow Engineer"]},
    )

    assert positioning["positioning_angles"][0]["supporting_claims"] == ["systems_fit"]
    assert prep["story_links"][0]["story_id"] == "story_ops"
    assert "broad_systems_interest_misread_as_lack_of_focus" in {item["risk"] for item in prep["risk_flags"]}


def test_keyword_classifier_reports_score_and_gaps() -> None:
    classified = classify_keywords(
        job_keywords=["Python", "HIPAA"],
        resume_keywords={"python"},
        selected_bullets=ranked_python_evidence(),
    )

    assert classified["strong_matches"] == ["Python"]
    assert classified["true_gaps"] == ["HIPAA"]
    assert overall_match_score(strong_count=1, adjacent_count=0, gap_count=1) == 50


def test_renderer_works_without_private_rendering_data(tmp_path: Path) -> None:
    renderer = ResumeRenderer(root=tmp_path, profile_name="workflow_engineer", render_mode="polished")

    assert renderer.bullet({"text": "built a workflow automation prototype"}).startswith("Built")
    assert renderer.summary(None, "builder of source-backed systems") == "builder of source-backed systems."
    assert renderer.project_description({"description": "Synthetic project"}) == "Synthetic project."


def test_claim_selection_filters_target_roles() -> None:
    selected = select_person_claims(
        sample_kb()["person_model"],
        "role_matching",
        target_roles=["workflow_engineer"],
    )

    assert [item["id"] for item in selected] == ["systems_fit", "reflection_only"]


def test_default_configs_load_and_drive_runtime_constants() -> None:
    scoring = load_default_config("scoring")
    reasoning = load_default_config("reasoning_rules")
    visualization = load_default_config("visualization")

    assert scoring["weights"]["exact_keyword_match"] == select_bullets.WEIGHTS["exact_keyword_match"]
    assert "verified" in select_bullets.STRONG_EVIDENCE_LEVELS
    assert "gxp" in generate_ats_report.CRITICAL_GAPS
    assert "environment_fit" in person_reasoning.MATCH_ENVIRONMENT_CATEGORIES
    assert visualization["graph"]["default_node_size"] == 1.0


def test_default_configs_do_not_include_known_private_identifiers() -> None:
    private_terms = {
        "ha" + "ley",
        "complex" + "io",
        "human" + "_model",
        "western" + "_digital",
        "clear" + "_skye",
        "who" + "op",
        "ax" + "on",
        "roto" + "mate",
        "career-intelligence" + "-private",
        "/users/" + "ha" + "ley" + "parks",
    }
    combined = "\n".join(
        str(load_default_config(name)).lower()
        for name in ("scoring", "reasoning_rules", "visualization")
    )

    assert not any(term in combined for term in private_terms)


def test_public_schema_and_template_cover_required_record_types() -> None:
    schema = load_yaml(Path("schemas/public_data_schema.yaml"))
    template = load_yaml(Path("templates/public_data_template.yaml"))
    required_collections = {
        "identity",
        "experience",
        "accomplishments",
        "resume_bullets",
        "projects",
        "skills",
        "stories",
        "values",
        "interests",
        "person_claims",
        "evidence_records",
        "resume_profiles",
        "job_description_metadata",
        "project_visibility",
    }

    assert required_collections <= set(template)
    assert required_collections == {
        spec["collection"]
        for spec in schema["record_types"].values()
    }


def test_public_data_template_validates_against_schema() -> None:
    schema = load_yaml(Path("schemas/public_data_schema.yaml"))
    template = load_yaml(Path("templates/public_data_template.yaml"))

    assert validate_template(schema, template) == []


def test_public_schema_template_text_has_no_known_private_identifiers() -> None:
    private_terms = {
        "ha" + "ley",
        "complex" + "io",
        "human" + "_model",
        "western" + "_digital",
        "clear" + "_skye",
        "who" + "op",
        "ax" + "on",
        "roto" + "mate",
        "career-intelligence" + "-private",
        "/users/" + "ha" + "ley" + "parks",
    }
    combined = "\n".join(
        Path(path).read_text(encoding="utf-8").lower()
        for path in (
            "schemas/public_data_schema.yaml",
            "templates/public_data_template.yaml",
        )
    )

    assert not any(term in combined for term in private_terms)


def test_andy_barks_dataset_validates_against_public_schema() -> None:
    schema = load_yaml(Path("schemas/public_data_schema.yaml"))
    dataset = load_yaml(Path("examples/andy-barks/data.yaml"))

    assert validate_template(schema, dataset) == []
    assert dataset["identity"]["display_name"] == "Andy Barks"


def test_andy_barks_dataset_exercises_required_edge_cases() -> None:
    dataset = load_yaml(Path("examples/andy-barks/data.yaml"))
    claims = {claim["id"]: claim for claim in dataset["person_claims"]}
    evidence_statuses = {
        item["evidence_status"]
        for collection in ("person_claims", "accomplishments", "skills", "projects")
        for item in dataset[collection]
    }
    profile_ids = {item["id"] for item in dataset["resume_profiles"]}
    job_ids = {item["id"] for item in dataset["job_description_metadata"]}

    assert claims["claim_verified_information_organization"]["confidence"] == "high"
    assert claims["claim_reflection_prefers_predictable_work"]["evidence_status"] == "reflection_only"
    assert "conflicting" in evidence_statuses
    assert "resume_bullets" in claims["claim_not_change_initiator"]["caution_for"]
    assert "resume_summary" in claims["claim_not_change_initiator"]["caution_for"]
    assert "skill_data_analysis_gap" in {item["id"] for item in dataset["skills"]}
    assert "profile_curriculum_designer" in profile_ids
    assert "profile_program_coordinator" in profile_ids
    assert "job_information_architect_transferable" in job_ids


def test_andy_barks_dataset_has_no_known_private_identifiers() -> None:
    private_terms = {
        "ha" + "ley",
        "complex" + "io",
        "human" + "_model",
        "western" + "_digital",
        "clear" + "_skye",
        "who" + "op",
        "ax" + "on",
        "roto" + "mate",
        "career-intelligence" + "-private",
        "/users/" + "ha" + "ley" + "parks",
    }
    combined = Path("examples/andy-barks/data.yaml").read_text(encoding="utf-8").lower()

    assert not any(term in combined for term in private_terms)


def test_demo_workflow_writes_required_synthetic_outputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "generated"

    paths = run_demo(output_dir=output_dir)

    assert set(paths) == {
        "match_report",
        "resume",
        "interview_prep",
        "positioning",
        "visualization",
        "data",
    }
    for path in paths.values():
        assert path.exists()

    match_report = paths["match_report"].read_text(encoding="utf-8")
    resume = paths["resume"].read_text(encoding="utf-8")
    visualization = paths["visualization"].read_text(encoding="utf-8")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths.values()).lower()
    private_terms = {
        "ha" + "ley",
        "complex" + "io",
        "human" + "_model",
        "western" + "_digital",
        "clear" + "_skye",
        "who" + "op",
        "ax" + "on",
        "roto" + "mate",
        "career-intelligence" + "-private",
        "/users/" + "ha" + "ley" + "parks",
    }

    assert "Andy Barks" in match_report
    assert "Curriculum Designer" in match_report
    assert "Synthetic example resume" in resume
    assert "software engineer" in resume
    assert visualization.startswith("<svg")
    assert not any(term in combined for term in private_terms)


def test_privacy_scan_passes_public_worktree() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/privacy_scan.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
