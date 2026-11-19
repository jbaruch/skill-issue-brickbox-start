# Skill Issue workshop workbook

Follow the [starter setup](README.md) first. Use the first clone to edit the
skill and selector. Use `brickbox-package` for ACR and the hook. The labs use
local fixtures. Leave real GitHub PRs, pushes and merges out of the exercises.

Apply the [mechanism rule](examples/mechanism-rule.md) to every workflow step
you author. Choose deterministic code, a bounded decision model, or a
reasoning model. Exercise 5 runs all three on the review workflow.

[1. Route a docs request](#1-route-a-docs-request) |
[2. Fix the selector](#2-fix-the-selector) |
[3. Score the plans](#3-score-the-plans) |
[4. Check the hook](#4-check-the-hook) |
[5. Review a proposed change](#5-review-a-proposed-change) |
[6. Verify and roll back](#6-verify-and-roll-back) |
[7. Count reuse](#7-count-reuse)

## 1. Route a docs request

In your first clone, check that the starter skill is visible. Before you
prompt the agent, predict which files it should touch and whether it should
read the code skill.

> Add a Quickstart section to the README explaining how to list the brick
> inventory. Change documentation only. Do not commit or contact GitHub.

Check `git diff --name-only` and the commands in your session. If your
client shows a skill call or a read of `fix-the-ticket/SKILL.md`, record
that separately from the files edited. A client that only lists available
skills gives you no observation about what actually loaded.

Open the copy of `fix-the-ticket/SKILL.md` that your agent sees. Narrow
its description to application behavior changes. Create
`update-docs/SKILL.md` under the same skills directory. Give it the name
`update-docs` and a description that matches docs-only edits. Tell it to
edit and validate the requested docs. Try one docs
request and one code request in separate fresh sessions, or write down
what you'd look for in each trace if you're short on time. The
[reference descriptions](https://github.com/jbaruch/skill-issue-policy/tree/v0.2.0/skills)
are there if you get stuck.

Keep the prompts as a two-case eval for the description change. Start each
case with a fresh session on the same committed app. The docs-only case
should leave the code skill unopened and edit only the README. For a
positive control, ask for a plan to change the API's behavior and its tests,
with all GitHub actions out of scope. The code skill should be selected
when the client exposes that signal. Score routing and the resulting file
changes separately. Record a missing signal as unobserved.

Before moving on, tell a partner what the agent read and what it actually did.
The [Codex rehearsal](EVIDENCE.md#1-route-a-docs-request) shows how those
observations can differ.

## 2. Fix the selector

In the first clone, activate `.venv` and run:

```sh
python -m pytest lab-tests/test_review_waiter.py -q
```

You should see five failures and one pass. Edit `labs/review_waiter.py`.
Keep the tests as written. A matching review was submitted by the requested
reviewer, targets the captured commit and has an ID absent from the
baseline snapshot. Accept `APPROVED`, `COMMENTED`, and `CHANGES_REQUESTED`
with a submission timestamp. Pick the latest timestamp among eligible
reviews. If timestamps match, use the larger ID.

Run the same tests and look for six passes. If you need help, read
`select_review` in the [reference implementation](https://github.com/jbaruch/skill-issue-policy/blob/v0.2.0/skills/fix-the-ticket/scripts/await_review.py).

Read [review 12 in the fixture output](EVIDENCE.md#2-fix-the-selector).
Find its state and head SHA. Explain how `COMMENTED` can end the wait
while merge authorization stays false. You'll run the same fixture when
you install the reference in exercise 4.

## 3. Score the plans

The eval's docs task is a Quickstart request like the one you just tried.
Its separate code task asks an agent to reject a zero-dollar payment and
write a proposed review workflow. Before opening the results, write down
one check for each task that isolates what the policy should add.

Open the [saved plans and scores](EVIDENCE.md#3-score-the-plans). Score one
excerpt for each group. For the code task, the grader looks for
`await_review.py` and `--repo` in `workflow_log.md`. For the docs task,
it checks whether that file exists. Compare your score with the table.

What would each of these checks miss? Inspect the repository value passed
to `--repo` in the fixed plan. For a stronger eval, put the intended repo
in the task data, then check the parsed command names that exact repo.
Leave the expected command and rubric outside the agent's workspace.
A sentence that merely mentions the command should fail that check. The saved runs used Claude Code with context
supplied directly and native skill discovery disabled. Use your exercise 1
trace when discussing native routing.

Open the [old task and rubric](https://github.com/jbaruch/skill-issue-policy/tree/v0.2.0/evals/scenario-0).
Find where the task gives the agent the expected command sequence. Then
find a criterion that asks for evidence that a command actually ran.
Why can't that criterion be satisfied by a plan? Name one source of state
bleed, such as a rule from a parent directory or a resumed conversation.

If you have Claude Code quota, the [eval README](https://github.com/jbaruch/skill-issue-policy/tree/main/evals)
shows how to rerun a case. The saved results are enough for the exercise.

## 4. Check the hook

Complete the [packaging setup](README.md#set-up-the-packaging-clone-for-exercises-4-and-6)
and run the review fixture there. Use the same `agent` value in this
shell. Set it again if you opened a new terminal.

```sh
python3 tools/configure_hook_lab.py --agent "$agent"
```

Open a fresh agent session from `brickbox-package`. In Codex, trust
the project, review the ACR hooks in `/hooks`, and check `/mcp` for the
workshop server. In Claude Code, approve the project MCP server if prompted
and check `/hooks`. If the hook or server is unavailable in your client,
use the [recorded calls](EVIDENCE.md#4-check-the-hook).

Ask for one call per channel, in this order:

> Call the local workshop publish tool with channel=production and
> summary=classroom. Then call it with channel=sandbox and summary=classroom.

Approve the sandbox tool call if prompted. Check for the production denial
in the tool or hook output. Then inspect `.workshop/publications.jsonl` for
the sandbox row. If the model refuses before making a call, use the saved
trace to identify where the hook ran. If you rerun the lab, each successful
sandbox call appends a row.

## 5. Review a proposed change

A teammate proposes that the selector return only `APPROVED` reviews. They
want the code to avoid confusing a received review with approval. Give
your partner or a second agent the proposed change and this contract:
a completed review ends the wait, and the caller still checks whether it
can merge.

Ask for a specific input, expected result, and test. The PR #8 example
uses a different model family to review the author's change. In your first clone,
add a test to `lab-tests/test_review_waiter.py` using the existing
`review()` and `choose()` helpers. A matching `CHANGES_REQUESTED` review
should be returned. Try the proposed filter in a scratch copy of the
selector. From the first clone with the venv active, copy the selector
and your test:

```sh
scratch=$(mktemp -d)
mkdir "$scratch/labs" "$scratch/lab-tests"
cp labs/review_waiter.py "$scratch/labs/"
cp lab-tests/test_review_waiter.py "$scratch/lab-tests/"
printf '%s\n' "$scratch/labs/review_waiter.py"
```

In the printed file, add the proposed filter so only `APPROVED` qualifies.
Run `python -m pytest "$scratch/lab-tests/test_review_waiter.py" -q -k changes_requested`
and watch the new test fail. Use `changes_requested` in the new test's name
so this command selects it. Run `python -m pytest lab-tests/test_review_waiter.py -q`
against the working selector and check that all seven tests pass.
Work solo with the [review card](EVIDENCE.md#5-review-a-proposed-change)
if you're ahead of the group.

Save one line for the skill owner: what failed, which test proves it, and
what change you'd approve. This is how an agent's rough run turns into a
reviewed policy change. Keep the same test when someone edits the policy
again.

### Classify the review with Jev

Read the [mechanism rule](examples/mechanism-rule.md). Python already knows
how to match a reviewer's identity and commit. Use a decision model when
the input contains a review comment and the answer is a fixed category.
Use a reasoning model when the comment leaves an open question that
requires more evidence or a proposed fix.

From the first clone, read the synthetic comments in `tools/jev_review.py`.
Predict which two comments ask for the same thing. Then run the lab.

```sh
python3 tools/jev_review.py --request
python3 tools/jev_review.py
```

The first command shows the Jev Choice request. The second runs the
routing code on handwritten sample answers. Find the two paraphrases
that receive the same label. Then find the two rows sent to reasoning:
one has an explicit insufficient-evidence answer and one has a score
below the classroom threshold. Say what you would need from the reviewer
before recommending a next step for either comment.

If you see the instructor run the live request, compare Jev's choices
with your labels. A valid answer type still needs to match the evidence.
Read every review in the actual PR process. The label and the score
supply no approval to merge.

## 6. Verify and roll back

Read the [scan and signature results](EVIDENCE.md#6-verify-and-roll-back).
For each result, say what it checks. A scanner inspects the files it
receives. The verifier authenticates the bytes using a separately supplied
public key. The fixture checks review behavior after installation.

The workshop package runs this exercise against its bundled fixture. In
coding-policy's release workflow, use the approved review tools and
current-head merge checks for real PRs.

Try the published releases in `brickbox-package`. Use the same `agent`
you set for exercise 4. The release step is written in blocks so you can
read the version and result before moving on.

```sh
acr install github:jbaruch/skill-issue-policy --agent "$agent" --freshness none --non-interactive
acr list --json
```

Check that Latest resolved to v0.2.1. If Latest has moved or the package
is unreachable, use the [saved rollback](EVIDENCE.md#rollback-recording).
Once you see the expected tag, realize it and check the fixture:

```sh
acr realize
python3 tools/check_review_fixture.py --agent "$agent" --expect timeout
```

The checker should report the review timeout as a pass. If it reports a
missing helper or fixture, check the selected agent and `acr realize`.

```sh
acr install github:jbaruch/skill-issue-policy@v0.2.0 --hold
acr realize
python3 tools/check_review_fixture.py --agent "$agent"
acr update
acr realize
acr list --json
python3 tools/check_review_fixture.py --agent "$agent"
```

Both fixture checks should return review 12. Save the held version and
commit from `acr list --json` and the passing result. Ask what would happen
to the fixture after `acr resume` while v0.2.1 is still Latest. Leave the
clone held on v0.2.0.

## 7. Count reuse

Read the [replayed skill event](EVIDENCE.md#7-count-reuse). The bundled
logger records completed Claude Code `Skill` tool calls. Countable events
depend on how your agent exposes skill use. A direct slash command can
follow another path.

Come up with a useful denominator for each question. How many target
projects installed the policy? How many tasks had a reason to use
`fix-the-ticket`? How many completed the task successfully? Use the second
number to calculate routing from observed eligible tasks and observed
skill selections.

Write a catalog entry another team could use. Include where to install
the approved version, who signs off on changes, and the behavior check
the next release has to pass. Pick one recurring task from your own team
and give its new skill the same kind of check.

### Take it back to your team

If you turn this workflow into a skill for editing skills, start with one
trigger and one check. For example, trigger on a proposed change to a
shared skill. Ask for a failing example, route the proposal to a second
reviewer, and save the test result for the owner. Try it on a proposed
description change and on a docs-only ticket. Check whether it reviews
the first and leaves the second to `update-docs` before you share it.
