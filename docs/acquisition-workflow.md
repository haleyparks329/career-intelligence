# Acquisition Workflow

The acquisition workflow describes how evidence can enter a Career Intelligence system. It is a framework pattern, not an implemented public CLI command in this repository.

```text
Acquire
  ↓
Normalize
  ↓
Review
  ↓
Reason
  ↓
Generate
  ↓
Visualize
```

## Acquire

Gather candidate evidence from conversations, notes, work artifacts, public examples, or structured forms.

Conversational interviewing can be a provider-neutral evidence-acquisition strategy. The interviewer asks about work history, projects, constraints, outcomes, preferences, and examples, then turns answers into reviewable records.

## Normalize

Convert raw material into structured records with IDs, evidence status, confidence, relationships, and usage cautions.

## Review

Check whether records are accurate, synthetic when required, and safe for the intended use. Weak, conflicting, and reflection-only records should remain labeled.

## Reason

Use the structured records to analyze role fit, transferable skills, caveats, positioning angles, and interview preparation.

## Generate

Generate outputs from approved evidence. Resume generation should be narrower than reasoning and should avoid unsafe person-model claims.

## Visualize

Show relationships between person, evidence, role, and reasoning outputs so decisions remain inspectable.
