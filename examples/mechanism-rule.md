# Choose how each step runs

Apply this rule when writing or changing a workflow. Record the choice for each
step next to the example you will use to test its behavior.

| What the step knows | Use | Workshop example |
| --- | --- | --- |
| The inputs and the rule determine the result | Deterministic code | Match the requested reviewer and commit, then select a new completed review. |
| The input contains the evidence and the possible answers are fixed, but picking one requires reading meaning | A bounded decision model | Ask Jev whether a comment requires a change, offers an optional suggestion, or gives too little evidence. |
| The task needs more evidence, synthesis, or an open-ended answer | A reasoning model | Read the full discussion and determine what to change or what to ask the reviewer. |

Give the decision model an explicit answer for insufficient evidence. Route
that answer, a low score, an invalid answer, or an unavailable model to
reasoning. Use code for the fallback and for any checks required before an
action. In this lab the classifier only supplies a label for review.
Merge approval and the obligation to read every review stay with the
existing review process.

Before using the label to take an action in a real workflow, record the
question and model versions, score field, threshold, and answer-to-action
mapping. Get the policy owner's approval for those bounds. Test paraphrases,
ambiguous inputs, and a provider failure. Keep the expected results with
the workflow change.

- [Coding-policy script delegation](https://github.com/jbaruch/coding-policy/blob/main/skills/coding-contracts/references/script-delegation.md)
- [TypeSafe Choice](https://docs.typesafe.ai/primitives/choice)
