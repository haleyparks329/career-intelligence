"""Deliberately incomplete synthetic evidence comparison."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent


def compare(needs: list[str], evidence: list[dict]) -> list[dict[str, str]]:
    counts = {need: 0 for need in needs}
    for item in evidence:
        for need in item.get("supports", []):
            if need in counts:
                counts[need] += 1
    return [
        {
            "need": need,
            "finding": "supported" if count > 1 else "partial" if count == 1 else "unsupported",
            "note": "Toy fixture label; human review required.",
        }
        for need, count in counts.items()
    ]


if __name__ == "__main__":
    items = json.loads((ROOT / "andy-barks" / "evidence.json").read_text(encoding="utf-8"))
    needs = ["design learning material", "adapt material from feedback", "administer enterprise platform"]
    print(json.dumps(compare(needs, items), indent=2))
