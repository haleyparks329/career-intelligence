# Evidence And Provenance

Evidence is the core safety mechanism in Career Intelligence.

## Evidence Status

Records can carry statuses such as:

- `synthetic`
- `reflection_only`
- `conflicting`
- `needs_review`

These statuses are not decoration. They affect how a record should be used.

## Confidence

Confidence indicates how strongly the record is supported within the dataset. High-confidence records are easier to use in generated materials. Low-confidence records should usually remain as gaps, cautions, or review prompts.

## Usage Cautions

Usage cautions explain where a record can be misleading. For example, a small AI-assisted tool can demonstrate learning and process improvement without implying professional software engineering experience.

## Provenance In Outputs

The public demo preserves provenance by:

- selecting evidence records before generating resume bullets
- reporting selected evidence in the match report
- keeping person-model caveats available in prep and positioning
- writing `demo_data.json` for inspectable intermediate output

## Conflicting Evidence

Conflicting evidence should not be smoothed over. If one record suggests broad leadership and another suggests a narrower support role, the generated output should reflect that uncertainty instead of choosing the more impressive version.
