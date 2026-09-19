---
tags: [pinball, jev, system-one, distillation]
status: reference
created: 2026-09-19
jira: SCRUM-30
---

# Jev and System One Models

Source: typesafe.ai and docs.typesafe.ai, read 2026-09-19 through a page-summarizing fetch. **Wording below is paraphrase; check the pages before quoting.** (The domain is typesafe.ai; typesave.ai does not resolve.)

## What Jev is

- A hosted "System One Model" from TypeSafe AI. Not a text generator.
- Input: a `state` (text or JSON) plus typed `questions`.
- Output per question: a choice with a probability distribution and confidence, a score with a distribution, or a yes-probability in [0, 1].
- The output schema is fixed in advance, so there are no type errors by construction.
- API only (`POST https://api.typesafe.ai/v1/systemone`, Python SDK `typesafe-sdk`). No weights. One model, `jev-1.13.0`.
- Architecture is undisclosed beyond "a new model architecture" with "a parallel sampler", trained with "Reinforcement Learning for Calibrated Decisions".

## Hard constraint

Their Master Customer Agreement prohibits using the service or its outputs for model distillation or to train a model that imitates it, and prohibits publishing benchmarks. **Jev is design inspiration only in this project. It is never a teacher and never a comparator.**

## What we took from it

The interface, not the model:

| Jev | `collatz.pinball` |
|---|---|
| state (text / JSON) | `encode_state(state, width)` → feature bits |
| Choice question | `Decision.choice`, `Decision.probabilities` |
| Score question | `Decision.score()` (expected label) |
| yes-probability | `Decision.probability_of(True)` |
| calibrated confidence | `Decision.confidence`, exact `Fraction`; measured by `ece` |
| no type errors | labels are whatever was counted; probabilities sum to exactly 1 |

## Distillation notes (general skill)

- **Soft-label distillation**: student matches the teacher's distribution, loss `α·T²·KL(teacher_T ‖ student_T) + (1−α)·CE`. Needs teacher probabilities.
- **Sequence-level (black-box)**: fine-tune on teacher generations. Works with API-only teachers whose terms allow it; open-weight teachers avoid the licence problem.
- **For a count model there is no loss function**: distillation is adding the teacher's probabilities to the lanes as fixed-point integer weights (`fit_soft`, `fixed_point`). This is the exact analogue of soft-label training for a histogram student.
- What distillation can and cannot do here is measured in [[Integer Decision Model]].
