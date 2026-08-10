---
name: skill-evolution
description: Run a guarded, evidence-driven three-round evolution of an existing Agent Skill or SKILL.md collection. Use when the user asks to improve, self-iterate, evolve, refactor, test, score, or autonomously upgrade a skill, including “三轮升级”, “自主迭代”, “优化 skill”, or “提升 skill 质量”. Create a baseline, freeze representative test prompts, validate each candidate independently, and keep only verified improvements. Do not use to create a brand-new skill; use skill-creator instead.
---

# Skill Evolution

Improve a skill by running a bounded experiment loop, not by repeatedly making it longer. Preserve the skill's core purpose, user-control boundaries, and safety rules.

Default to three rounds. A round is one hypothesis, one minimal candidate change, one repeatable evaluation, and a keep-or-restore decision.

## Input and scope

Ask for a target path only when it cannot be inferred. A target may be one `SKILL.md`, one skill directory, or a user-owned skill collection. For a collection, inventory every `SKILL.md` but evolve one skill at a time.

Never evolve files under a system skill directory, plugin cache, or another person's workspace. Stop if the target includes any of these paths and ask for a copied, user-owned target instead.

Run the state helper before making changes:

```powershell
python <skill-evolution-dir>/scripts/evolution_state.py inspect --target <target-path>
```

Use the report to establish the target files, test-prompt coverage, and existing repository state. Do not treat its structural signals as quality scores; use them only to choose what to investigate.

## Phase 0 — establish a stable baseline

1. State the target, its core job, the requested outcome, and the fixed maximum of three rounds.
2. Inspect the Git worktree. If it is dirty, preserve the user's unrelated changes. Do not reset, stash, commit, or amend them automatically.
3. Find `test-prompts.json` next to the target skill. If it is missing, draft exactly three realistic prompts:
   - a typical success case;
   - a complex or ambiguous case;
   - a boundary or failure-recovery case.
4. Include an observable expected outcome for each prompt. Freeze this test set for all three rounds. Do not rewrite it to make a candidate look better.
5. Present the test set and request a single confirmation before editing, unless the user explicitly authorized unattended testing. In the latter case, label the test set `generated-unconfirmed` in the run log.
6. Create a non-destructive run snapshot and log with the helper:

```powershell
python <skill-evolution-dir>/scripts/evolution_state.py prepare --target <target-path> --run-id <YYYYMMDD-HHMM>
```

The helper writes to `.skill-evolution/<run-id>/` inside the target collection. It copies only relevant `SKILL.md` and test-prompt files; it never changes them.

## Baseline evaluation

Run each frozen test prompt in two fresh, independent contexts:

- `with_skill`: provide only the target skill and the user-like prompt;
- `baseline`: provide the same prompt without the skill.

Assess activation and output against the expected result. If independent agents are available, use separate agents and provide raw prompts and artifacts only; do not give them a proposed fix or expected winner. If agents are unavailable, mark the evaluation `dry-run` and do not claim a verified improvement.

Use these dimensions only for triage:

| Dimension | Look for |
| --- | --- |
| Trigger precision | activates for its job, not adjacent jobs |
| Workflow | ordered inputs, actions, outputs, and ownership |
| Specificity | executable parameters, formats, and examples where needed |
| Failure handling | explicit condition, first recovery step, and safe fallback |
| Validation and boundaries | evidence checks, stop points, and prohibited actions |
| Resource use | correct, conditional use of scripts, references, and tools |
| User outcome | complete, useful, and no worse than the baseline |

Record the baseline with `record`. Keep static ratings separate from experimental comparisons.

## The three-round loop

For rounds 1 through 3, follow this exact sequence.

1. Identify the largest observed gap from the frozen tests. Write one sentence: `Hypothesis: <one focused change> will improve <one observed gap> without weakening <protected behavior>.`
2. Make the smallest coherent edit that tests that hypothesis. Preserve the target's purpose; do not add packages, tools, external services, or unrelated capabilities unless the user explicitly asked.
3. Re-run all frozen prompts. Keep all inputs, tool availability, and evaluation criteria the same as the baseline.
4. Ask three independent judges to compare the previous accepted version with the candidate in the same judgment. Randomize presentation order. Each judge returns exactly `better`, `worse`, or `tie`, plus one evidence-based sentence.
5. Keep the candidate only if at least two judges select `better` and none selects `worse`. Otherwise restore the snapshot for that round. Never use a noisy absolute score delta as the keep-or-restore rule.
6. Record the round, hypothesis, result, vote, evidence location, and evaluation mode:

```powershell
python <skill-evolution-dir>/scripts/evolution_state.py record --target <target-path> --run-id <run-id> --round <1|2|3> --status <kept|restored|skipped> --hypothesis "<text>" --vote "<e.g. 3-0 better>" --mode <paired|dry-run>
```

7. Stop early after two consecutive non-improvements, a newly discovered safety issue, or a missing prerequisite. Report why rather than inventing another edit to fill all three rounds.

### Restoring a rejected candidate

Restore only a file that still exactly matches the rejected candidate hash. Compute the current hash, then use the stored pre-round copy:

```powershell
python <skill-evolution-dir>/scripts/evolution_state.py hash --path <changed-SKILL.md>
python <skill-evolution-dir>/scripts/evolution_state.py restore --target <target-path> --run-id <run-id> --round <round> --file <relative-path> --expected-current-hash <hash>
```

If the hash differs, stop: the user or another process may have edited the file. Do not overwrite it.

## Hard constraints

- Do not make more than three candidate rounds in one run.
- Do not judge a change in the same context that proposed it.
- Do not change a frozen prompt or expected result during the run.
- Do not use `git reset --hard`, overwrite unrelated files, or erase user work.
- Do not retain an edit because it is longer, more structured, or receives a higher single-pass score.
- Do not silently skip failed tests, missing resources, or denied tool access.
- Do not weaken explicit user approvals, safety boundaries, or stop conditions to make a workflow appear smoother.

## Final report

Return a compact report with:

1. the target and run ID;
2. the three frozen tests and their evaluation mode;
3. each round's hypothesis, outcome, and paired vote;
4. the retained files and locations of snapshots and `results.tsv`;
5. remaining risks and the next single improvement to test later.

Read [references/evaluation-protocol.md](references/evaluation-protocol.md) when designing judges, handling test contamination, or deciding whether evidence is strong enough to call an improvement verified.
