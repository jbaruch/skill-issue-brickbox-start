# Workshop lab book

Work locally. Do not publish, push or merge real changes during these exercises.
The reference solution is `jbaruch/skill-issue-policy@v0.1.6`. Keep task prompts,
eval rubrics and generated outputs separate.

## 1. Observe the wrong workflow

Ask your agent: “Add a Quickstart section to the README explaining how to list the
brick inventory. Change documentation only. Do not commit or contact GitHub.”

Read the selected skill and trace. Did it choose the heavy code-ticket lane?
Record the observation, including a run that behaves correctly. One run is not a
rate. The starter description makes almost every request a trigger.

Rewrite the activation description and split documentation from code work.
Do not force the skill name into the task: that would hide routing failure.

**Checkpoint:** explain which task should use each skill, and one negative example.

## 2. Delegate the deterministic work

```sh
python -m pytest lab-tests/test_review_waiter.py -q
```

The selector in `labs/review_waiter.py` is intentionally incorrect. The tests
include an existing review, a different reviewer, the wrong commit, a pending
review and a completed COMMENTED review. Repair the selector without changing
the tests. Run red → green. The finished implementation is the reference
skill's `select_review` function, not an invitation to copy an entire framework.

Then inspect the reference `await_review.py`: identify the baseline snapshot,
request failure, timeout budget, head-change check, output contract and the
parts that need semantic judgment. Use the bundled fixture to run the whole CLI.

**Checkpoint:** old or unrelated reviews never satisfy a new request; receiving
CHANGES_REQUESTED is a completed review but does not authorize a merge.

## 3. Measure the contribution

Run `evals/run.py --dry-run` from the reference checkout with an explicit model.
The runner compares explicitly injected none/bad/fixed context in fresh projects.
Native skill discovery is disabled to exclude personal skills from the baseline.
It measures planning, not activation. Run one case live, then inspect the full
saved sweep when available. Lab 1 separately observes native skill routing.

Before seeing its hidden checks, predict what belongs in the rubric. Grade only
the contribution: unnecessary workflow creation and use of the packaged helper
in the written plan.
Generic bug-fixing quality is a different measurement. For the separate native activation experiment, inspect raw Skill calls rather
than trusting a statement that the model “used the skill”.

Read the intentionally leaking historical `evals/scenario-0/task.md`. Find the
places where it gives away the expected answer. State bleed includes inherited
rules, prior edits and cached sessions, not just chat history.

**Checkpoint:** distinguish a plan, an observed action, and an enforced constraint.
Report errors separately. A small sample and zero lift are both valid outcomes.

## 4. Give a hard constraint its own mechanism

Use the second packaging clone and install the known-good policy as in README.
Configure the synthetic server:

```sh
python3 tools/configure_hook_lab.py
```

Start a new Claude session. Approve the project-local workshop MCP server if
asked. In `/hooks`, confirm the ACR PreToolUse gate is registered. Ask the agent
to call the workshop publish tool with `channel=production`, then `channel=sandbox`.
The tool writes synthetic local records only; no actual deployment exists.

The production call should be blocked by the hook, while sandbox writes a record
to `.workshop/publications.jsonl`. Record whether the model refused first; a
self-refusal is not evidence that the hook executed. The instructor can show
the same structured payload sent directly to the hook to separate the mechanisms.

**Checkpoint:** explain what this gate sees and what it cannot constrain. A
second LLM is not a deterministic boundary. In the automode experiment, explicit
in-prompt authorization passed 6/6 in both auto cells; show that counterexample.

## 5. Review and improve the context

Give a second model the changed artifact, intended behavior, and a failing or
ambiguous example. Ask for specific regressions and evidence. Do not substitute
an unexplained percentage for a finding. Instructor demo: Codex reviews a
Claude-authored change. The core exercise does not require a second subscription.

Turn one accepted finding into a regression check and rerun it. Friction can
propose a change; review, tests and evals decide whether that change ships.

Optional semantic-classification extension: compare paraphrases with a typed
Jev classifier. Evaluate meaning and abstention separately. Typed output is not
proof that the semantic decision is deterministic; this extension must not hold
up the core labs.

**Checkpoint:** one changed artifact, one concrete finding, one regression check.

## 6. Scan, verify and roll back

The instructor scans the exact workshop artifact with a pinned scanner version.
Contrast static signatures with semantic inspection. Add an inert poisoned
reference that requests sending a synthetic marker to `example.invalid`; do not
run exfiltration code or use real secrets. Discuss what a package scanner can
inspect and what later retrieved content adds to the attack surface.

Sign/verify demonstration must bind a trusted signer to the exact artifact.
A hash from the same untrusted download is not signer verification. Show a
verified artifact accepted and a modified artifact rejected **before install**.
If this demonstration is not rehearsed, mark it pending rather than claiming
that ACR's content hash implements it.

Follow the reference README rollback exercise: install the intentionally regressed
latest, observe the COMMENTED-review fixture timeout, hold `v0.1.6`, realize,
repeat the same fixture, update and verify that the hold remains in effect.
Predict what resume will do while latest is still broken.

**Checkpoint:** capture declaration, locked tag/commit/hash, the held resolution
and the repeated behavioral result. Scan findings, signature validity and
regression quality are separate checks.

## 7. Observe reuse

Invoke a skill through the agent and inspect `.workshop/skill-events.jsonl`.
The PostToolUse hook records completed Skill tool calls without prompts or
argument text. A direct `/skillname` follows another path; the log is incomplete
unless that path is instrumented too. A completed invocation is not task success.

Track installation coverage, eligible tasks, routed invocations and task outcomes
separately. At organization scale, connect ownership, discovery, version rollout
and usage. The final Port example uses provider analytics and needs the relevant
Enterprise access; installing a registry does not create universal telemetry.

**Checkpoint:** explain which denominator your proposed adoption metric uses,
and how a team discovers the approved version and learns an update exists.
