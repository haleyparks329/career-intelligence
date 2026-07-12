# Person-Model Safety

The person model captures claims about work style, motivation, collaboration, positioning, and fit. These claims can be useful, but they are not all safe for every output.

## Usage Boundaries

Person-model claims can be marked safe for uses such as:

- role matching
- positioning
- interview prep
- resume summary
- resume bullets

The engine treats resume use more strictly than reasoning use.

## Resume Safety

A person-model claim should not become a resume bullet unless it is explicitly safe for resume bullets, has relationship evidence, and is supported by non-reflection evidence.

The Andy Barks demo includes claims that are useful for reasoning but prohibited from resume generation. The generated resume excludes those claims.

## Reflection-Only Claims

Reflection-only claims can be useful. They can help a person prepare questions, notice fit, or explain preferred working conditions.

They should not be rewritten as verified employment evidence.

## Public Positioning

Positioning can use a broader set of signals than resume bullets, but it still needs caveats. Public-facing positioning should avoid turning traits, preferences, or reflections into credentials.
