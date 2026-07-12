from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}

APPROVED_SYNTHETIC_OUTPUT_DIR = Path("examples/andy-barks/generated")

PROHIBITED_PRIVATE_DIRS = {
    Path("applications"),
    Path("outputs/private"),
    Path("resumes/private"),
    Path("data/intake"),
    Path("data/normalized/private"),
    Path("data/jobs/private"),
    Path("config/private"),
}

GENERATED_CAREER_OUTPUT_NAMES = {
    "ats_report.md",
    "final_resume.md",
    "generated_resume.md",
    "match_report.md",
    "resume.md",
}

PRIVATE_TERMS = {
    "ha" + "ley",
    "complex" + "io",
    "human" + " model",
    "human" + "_model",
    "western" + " digital",
    "western" + "_digital",
    "clear" + " skye",
    "clear" + "_skye",
    "who" + "op",
    "ax" + "on",
    "roto" + "mate",
    "career-intelligence" + "-private",
    "/users/" + "ha" + "ley" + "parks",
}

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}(?!\w)")
ABSOLUTE_USER_PATH_RE = re.compile(r"/Users/[A-Za-z0-9._-]+/")


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str
    detail: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.detail}"


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.is_file():
            files.append(rel)
    return files


def is_text_file(path: Path) -> bool:
    try:
        path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return True


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel in iter_files(root):
        findings.extend(scan_path(rel))
        full_path = root / rel
        if not is_text_file(full_path):
            continue
        findings.extend(scan_text(rel, full_path.read_text(encoding="utf-8")))
    return findings


def scan_path(rel: Path) -> list[Finding]:
    findings: list[Finding] = []
    if is_under_approved_synthetic_output(rel):
        return findings

    for private_dir in PROHIBITED_PRIVATE_DIRS:
        if rel == private_dir or private_dir in rel.parents:
            findings.append(Finding(rel, 0, "prohibited-private-directory", str(private_dir)))

    if rel.name in GENERATED_CAREER_OUTPUT_NAMES:
        findings.append(Finding(rel, 0, "unexpected-generated-career-output", rel.name))

    return findings


def scan_text(rel: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()

        for term in PRIVATE_TERMS:
            if term in lowered:
                findings.append(Finding(rel, line_number, "private-identifier", term))

        for match in EMAIL_RE.finditer(line):
            email = match.group(0)
            if not email.endswith("@example.invalid"):
                findings.append(Finding(rel, line_number, "email-address", email))

        for match in PHONE_RE.finditer(line):
            candidate = match.group(0).strip()
            if looks_like_phone(candidate):
                findings.append(Finding(rel, line_number, "phone-number", candidate))

        if ABSOLUTE_USER_PATH_RE.search(line):
            findings.append(Finding(rel, line_number, "absolute-user-path", "/Users/..."))

    return findings


def looks_like_phone(candidate: str) -> bool:
    digits = re.sub(r"\D", "", candidate)
    if len(digits) < 8 or len(digits) > 15:
        return False
    return any(separator in candidate for separator in ("+", " ", "-", ".", "(", ")"))


def is_under_approved_synthetic_output(rel: Path) -> bool:
    return rel == APPROVED_SYNTHETIC_OUTPUT_DIR or APPROVED_SYNTHETIC_OUTPUT_DIR in rel.parents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan the public worktree for private content patterns.")
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    findings = scan(root)
    if findings:
        print("Privacy scan failed:", file=sys.stderr)
        for finding in findings:
            print(finding.render(), file=sys.stderr)
        return 1
    print("Privacy scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
