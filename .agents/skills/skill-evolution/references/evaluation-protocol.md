# Evaluation protocol

## Separate discovery, generation, and judgment

Use different contexts for three roles:

1. **Evaluator:** executes a frozen test prompt with and without the skill.
2. **Editor:** proposes the minimal candidate change from the evaluator's raw artifact.
3. **Judge:** compares the previous accepted version and the candidate without learning the editor's preference.

Do not leak diagnosis, desired outcomes, prior scores, or which version is new to a judge. Randomize the order in which the two versions appear.

## Test-set quality

Each expected result must describe observable behavior, not a preferred phrasing. Good examples include:

- asks for a named missing identifier before changing an existing record;
- produces an outline with the required fields;
- stops and provides a recovery path after validation fails.

Poor examples include "sounds professional" or "is more complete." Replace a poor expectation before the baseline is frozen.

## Accepting an improvement

Require all of the following:

1. all frozen prompts completed or a failure is explicitly explained;
2. at least two of three paired judges select `better`;
3. no judge selects `worse`;
4. the candidate does not violate a protected boundary or add unrelated scope.

A tie is not evidence of improvement. Restore the candidate and carry the unresolved observation into a later, separately designed run.

## Evidence quality labels

- `paired`: independent, same-judge comparison of previous and candidate output; eligible for a keep decision.
- `full-test`: user-like execution with a target skill; strong baseline evidence, but not sufficient alone for a keep decision.
- `dry-run`: an inspection or reasoning simulation; triage only, never proof of improvement.
