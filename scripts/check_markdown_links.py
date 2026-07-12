from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SKIP_DIRS = {".git", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__"}


@dataclass(frozen=True)
class BrokenLink:
    path: Path
    line: int
    target: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: broken markdown link: {self.target}"


def iter_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        files.append(rel)
    return files


def check_links(root: Path) -> list[BrokenLink]:
    broken: list[BrokenLink] = []
    for rel in iter_markdown_files(root):
        full_path = root / rel
        for line_number, line in enumerate(full_path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in LINK_RE.finditer(line):
                target = match.group(1).strip()
                if should_skip(target):
                    continue
                target_path = (full_path.parent / target.split("#", 1)[0]).resolve()
                try:
                    target_path.relative_to(root.resolve())
                except ValueError:
                    broken.append(BrokenLink(rel, line_number, target))
                    continue
                if not target_path.exists():
                    broken.append(BrokenLink(rel, line_number, target))
    return broken


def should_skip(target: str) -> bool:
    return (
        not target
        or target.startswith("#")
        or target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local Markdown links.")
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    broken = check_links(args.root.resolve())
    if broken:
        print("Markdown link check failed:", file=sys.stderr)
        for item in broken:
            print(item.render(), file=sys.stderr)
        return 1
    print("Markdown link check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
