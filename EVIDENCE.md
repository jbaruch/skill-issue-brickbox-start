# Workshop results you can use without a live run

These are excerpts from workshop runs. Use the matching exercise in the
[workbook](WORKBOOK.md) to decide what each result tells you.

## 1. Route a docs request

In a fresh Codex session, the trace showed a read of
`.agents/skills/fix-the-ticket/SKILL.md`. This was the broad starter skill.
The file-change event and `git diff --name-only` showed `README.md` only.
The run made no PR and did not change the app. In a fresh clone with the
two reference skill descriptions, the same prompt produced a read of
`update-docs/SKILL.md` and another README-only diff. These were single runs.
Would checking the diff alone catch the extra skill read?

## 2. Fix the selector

The starter tests returned `5 failed, 1 passed`. With the selector repaired,
the same tests returned `6 passed`. The released reference helper returned
this extract from its fixture result:

```json
{
  "head_sha": "workshop-head",
  "review_id": 12,
  "state": "COMMENTED",
  "received": true,
  "merge_authorized": false
}
```

The reference fixture is available in the
[v0.2.0 checkout](https://github.com/jbaruch/skill-issue-policy/tree/v0.2.0/skills/fix-the-ticket).

## 3. Score the plans

These code-plan excerpts come from trial one in each group. The words
around the excerpts describe proposed steps.

**No context**

> Request review from a code owner or payments maintainer. Wait for CI to pass.

**Broad starter skill**

> Check periodically for the review rather than blocking indefinitely. If it
> hasn't arrived after a reasonable time, ask a human reviewer.

**Repaired skills and rules**

> Request review. Then run the skill's companion helper, with `skill_dir` taken
> from the loaded fix-the-ticket SKILL.md path:
> `python3 <skill_dir>/scripts/await_review.py <pr-number> --repo <owner/repository>`

<details>
<summary>Check your scores</summary>

The saved sweep ran on November 17, 2026, with `claude-sonnet-5-5`. Each
group had three completed runs per task. All 18 runs completed and none
reported a run error.

| Check | No context | Broad skill | Repaired policy |
| --- | ---: | ---: | ---: |
| Code plan contains `await_review.py` | 0/3 | 0/3 | 3/3 |
| Code plan contains helper and `--repo` | 0/3 | 0/3 | 3/3 |
| Docs run leaves no `workflow_log.md` | 3/3 | 3/3 | 3/3 |

The runner supplied context directly, with native skill discovery disabled.
The passing code excerpt still contains a placeholder after `--repo`.
A separate check could require a known repository value. The saved counts
measure these specific checks on the plans. More trials would be needed
to estimate a success rate.

</details>

## 4. Check the hook

In the Codex rehearsal, ACR 0.6.0 installed the hook from v0.2.0.
Both requests targeted the workshop's local MCP server.

| Request | Observation |
| --- | --- |
| `mcp__workshop__publish` with `channel=production` | `PreToolUse` denied the call. No production record appeared. |
| The same tool with `channel=sandbox` | The server returned `Synthetic publication recorded locally.` |

The hook's stderr included `Workshop publishing is restricted to channel=sandbox.`
The local file contained one record:

```json
{"channel": "sandbox", "summary": "classroom"}
```

The hook checks the arguments of this MCP tool. Changing the tool name or
calling another route changes what the hook can see.

## 5. Review a proposed change

The proposal returns only `APPROVED` reviews. Give it a matching
`CHANGES_REQUESTED` review. The selector should return it so the caller
can read the requested changes.

One way to encode that finding using the starter tests:

```python
def test_changes_requested_completes_the_wait():
    selected = choose([review(state='CHANGES_REQUESTED')])
    assert selected is not None
    assert selected['state'] == 'CHANGES_REQUESTED'
```

A second review example from the workshop code itself is in
[policy PR #8](https://github.com/jbaruch/skill-issue-policy/pull/8).
Claude found that a missing starter could make the eval quit after spending
quota in the no-context group. The follow-up validates the starter before
running any model when the broad-skill group is selected.

### Review interpretation

The Jev lab asks what a comment means, using a fixed set of answers. The
table below describes the classroom replay, which uses handwritten
answers. A live Jev run can disagree with those labels.

| Case | Replay label | What the routing code does |
| --- | --- | --- |
| Required change and its paraphrase | `required_change` | Records the same label for both. |
| Optional follow-up | `optional_suggestion` | Records the suggestion label. |
| Unclear request | `not_enough_evidence` | Routes to reasoning. |
| Close call | `required_change` at 0.51 | Routes to reasoning because the demo threshold is 0.80. |

A reviewer's GitHub state controls review gating. Read the actual review
body and inline comments to understand the feedback. See
[coding-policy's review-reading rule](https://github.com/jbaruch/coding-policy/blob/main/rules/reviewer-feedback-reading.md).

## 6. Verify and roll back

Cisco skill-scanner 2.2.0 reported zero findings on the clean reference
copy and a critical finding on the inert test copy. The run used the
static, bytecode, pipeline, and correlation analyzers. A clean scan says
what those checks found in that input. Files a skill retrieves later can
carry instructions the scanner never saw.

The classroom signature verifier accepted the original archive. With the
same public key and signature, it refused a modified copy before the
install. The key used here was generated for the demo.

### Rollback recording

The initial published install resolved Latest to `v0.2.1`. Running the
bundled COMMENTED fixture gave:

```json
{"received": false, "error": "timeout waiting for a new review on the current head"}
```

The rollback pinned `v0.2.0` behind a hold and rejected `v0.2.1`.
`acr list --json` showed the hold with the following declaration:

```json
{
  "source": "github:jbaruch/skill-issue-policy",
  "requested": "latest",
  "hold": {"pin": "v0.2.0", "rejected": "v0.2.1"}
}
```

The installed fixture returned COMMENTED review 12 after the rollback
and after `acr update` followed by `acr realize`. The stable release
resolved to commit `434e2107d464922b359e28c3fbce5d9c128e98c9`.

## 7. Count reuse

The following fields came from a replay of a sample Claude Code
`PostToolUse` input. The event was supplied to the bundled logger for
the exercise.

```json
{
  "event": "skill_tool_completed",
  "policy_version": "0.2.0",
  "skill": "fix-the-ticket",
  "session_id": "workshop-replay",
  "tool_use_id": "example"
}
```

For a practice calculation, suppose 8 of 10 target projects installed the
policy. In those 8 projects, you observed 40 eligible tasks, 22 of which
selected the skill. The logger recorded 31 completed calls because some
tasks called it more than once. Installation coverage is 8/10. Observed
routing is 22/40. To calculate task success, collect a result per task.
