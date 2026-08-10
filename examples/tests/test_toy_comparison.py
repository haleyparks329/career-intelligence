import json
import sys
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).parents[1]
sys.path.insert(0, str(EXAMPLES))

from toy_comparison import compare


class ToyComparisonTests(unittest.TestCase):
    def test_exposes_support_and_gaps_without_a_score(self):
        evidence = json.loads((EXAMPLES / "andy-barks" / "evidence.json").read_text(encoding="utf-8"))
        result = compare(["design learning material", "adapt material from feedback", "unknown"], evidence)
        self.assertEqual([item["finding"] for item in result], ["supported", "partial", "unsupported"])
        self.assertTrue(all("score" not in item for item in result))


if __name__ == "__main__":
    unittest.main()
