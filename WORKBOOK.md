# Skill Issue workshop workbook

Do the exercises in your local clones. Use the bundled review fixtures and the
workshop MCP server. Leave GitHub PRs, pushes and merges out of the labs.

Start in `skill-issue-brickbox-start`. If you get stuck, keep your edits and open
the [v0.2.0 reference policy](https://github.com/jbaruch/skill-issue-policy/tree/v0.2.0)
to find the finished files for that exercise. The [starter README](README.md)
has setup commands and explains when to make a second clone.

## 1. Which skill handles a README edit?

Open a fresh session with your agent in the starter clone. Give it this prompt.

> Add a Quickstart section to the README explaining how to list the brick
> inventory. Change documentation only. Do not commit or contact GitHub.

Check your agent's trace or skill display for what it loaded. A `Skill` call
is one way Claude Code reports that. Record a missing or ambiguous signal as
well. Leave skill names out of the prompt so the agent has to choose.

Open the starter `fix-the-ticket/SKILL.md` from the directory your agent
uses. Rewrite its description
to cover application code changes. Give documentation work its own skill
description. Write down one prompt that should call `fix-the-ticket` and one
that should leave it alone.

## 2. Fix the review selector

From the starter clone, run the tests.

```sh
python -m pytest lab-tests/test_review_waiter.py -q
```

Expect five failures and one pass in the starter. Edit `labs/review_waiter.py`
with the tests as written. Skip reviews that were already present when you
requested review, that came from another reviewer, that target an older commit,
or that are still pending. When several reviews qualify, pick the newest even
if the API returns them out of order. A completed `COMMENTED` review can qualify.

Run the same command again and look for six passes. If you're stuck, read
`select_review` in the reference policy's
`skills/fix-the-ticket/scripts/await_review.py`.

Then run the bundled fixture using the command in the reference README.
Find the review ID, state and head SHA in the JSON. Explain why a
`CHANGES_REQUESTED` review can end the wait while leaving changes to make.

## 3. Compare the agent's plans

Before looking at the rubric, write down what you would check in plans for
the Quickstart and code tasks. Then compare your checks with the saved
sweep. The code checks look for `await_review.py` and `--repo` in the plan.
The Quickstart check looks for an unwanted `workflow_log.md`.

Open the instructor's saved plans and results for `none`, `bad`, and `fixed`.
Find the helper in a code plan and compare it with what the grader counted.
Count run errors separately from completed plans that fail a check.

The saved runner supplied context directly to Claude Code and disabled
native skill discovery. Compare its results with the routing observation
you made with your own agent in exercise 1. If you use Claude Code and have
quota, the [optional eval commands](https://github.com/jbaruch/skill-issue-policy/tree/main/evals)
let you rerun a case.

Open `evals/scenario-0/task.md` for an example of a task that gives away the
grader's answer. Find that wording, then name another way a baseline could
accidentally receive context, such as an inherited rule or a resumed session.

## 4. Watch the hook block a publish call

Install v0.2.0 in the second clone using the packaging instructions in the
[starter README](README.md).

With Codex, add the following table to the packaging clone's
`.codex/config.toml`. Use the absolute path to the script in that clone.

```toml
[mcp_servers.workshop]
command = "python3"
args = ["/path/to/brickbox-package/tools/workshop_mcp.py", "--output", "/path/to/brickbox-package/.workshop/publications.jsonl"]
```

Open an interactive Codex session in that clone, trust the project, and
review the ACR hooks in `/hooks`. Use `/mcp` to check for the workshop server.
For Claude Code, run `python3 tools/configure_hook_lab.py` and approve the
project MCP server when prompted.

Ask the agent to call the workshop `publish` tool with `channel=production`,
then `channel=sandbox`. Approve the sandbox tool call if prompted. Find the
production hook denial and the sandbox entry in `.workshop/publications.jsonl`.
If your client or account can't make those calls, use the instructor's
recorded run. Point to the tool name and the argument the hook checked.

## 5. Turn one review finding into a test

Give a partner or a second agent the file you changed and an example of how
it should behave. Ask for an input you can try and an explanation of what
would go wrong. In the instructor's example, Claude reviewed a change Codex
wrote and found that the eval could spend quota before checking for the starter
files. You can do this exercise with a partner using one account.

Pick a finding you can reproduce. Run a test that exposes it, fix the issue
and rerun the test. Save the finding with the test so the person who owns the
skill can decide whether to release the change.

If time allows, try the Jev extension. Give a typed classifier two paraphrases
of the same review and one ambiguous example. Check its interpretation of
the paraphrases and whether it abstains on the ambiguous example.

## 6. Verify the package and roll back a release

The instructor will show Cisco skill-scanner's output for the release files
and for an inert copy with flagged text. Ask which files the scanner read
and whether the skill can read additional content after installation.

Watch `verified_install.py` verify the original archive using a separately
supplied public key. Compare that run with the wrapper's refusal to install a
modified copy using the original signature.

Use the commands below in the packaging clone. Set `agent` and `skill_root`
for the agent you used to install v0.2.0.

```sh
agent=codex
skill_root=.codex/skills      # claude-code uses .claude/skills; cursor uses .cursor/skills
skill="$skill_root/acr__jbaruch__skill-issue-policy__fix-the-ticket"
check_review() {
  python3 "$skill/scripts/await_review.py" 7 --repo workshop/brickbox \
    --fixture "$skill/fixtures/review.json" --interval 0.01 --timeout 0.2
}
acr install github:jbaruch/skill-issue-policy --agent "$agent" --freshness none --non-interactive
acr realize
check_review
acr install github:jbaruch/skill-issue-policy@v0.2.0 --hold
acr realize
check_review
acr update
acr realize
check_review
```

1. Install Latest, realize it and run the COMMENTED fixture. Expect v0.2.1
   to time out.
2. Install v0.2.0 with `--hold` and run `acr realize`. Repeat the fixture
   and check for `review_id=12`.
3. Run `acr update` and `acr realize`, then rerun the same fixture. Check
   that the hold is still in the lockfile and the review ID still matches.

Save the declaration, locked tag, commit, content hash and passing fixture
output. Predict which release `acr resume` would select while v0.2.1 is Latest.
Leave your clone held on v0.2.0.

## 7. Read a Skill call in the log

The bundled logger recognizes Claude Code's completed `Skill` tool events.
With Codex or Cursor, read the instructor's replay of that event and find
the skill name in the resulting `.workshop/skill-events.jsonl`. Claude Code
users can also invoke a skill through the `Skill` tool and inspect their
own event. Direct slash commands may use a different path.

A prompted invocation checks the logger. To measure routing in ordinary
work, count the tasks that should use the skill, then check how many the
agent actually routed to it. Check task outcomes separately.

Tell your partner where another team would find the approved release and who
would tell that team about the next update. The closing Port slide shows an
example of a skill catalog that imports usage data from provider APIs.
