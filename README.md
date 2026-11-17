# Skill Issue — workshop starting point

**How To Write Skills That Actually Work**, QCon San Francisco, Thursday
November 19, 2026, 13:00–16:00 PST. A 301 workshop: bring an agent you already use.

You start with a small Lego inventory API and a skill that handles every ticket
through the same expensive code-review workflow. By the end, you can separate
judgment from deterministic work, measure what context adds, enforce a scoped
constraint, and distribute and roll back the resulting policy.

## Before Thursday

Bring Git, Python **3.11+**, and a working Claude Code login. Claude Code is the
reference harness; authoring principles transfer to other agents, but native
hooks and activation telemetry differ. Codex review is demonstrated by the
instructor, not a second account every participant must configure.

Install **ACR 0.4.3** using its [installation guide](https://github.com/jbaruch/agentic-context-registry/blob/main/docs/install.md).
Use macOS or Linux. **Windows users need WSL**; ACR has no native Windows support
([issue #14](https://github.com/jbaruch/agentic-context-registry/issues/14)). Run
Git, Python, Claude Code and ACR inside the same WSL environment.

```sh
git clone https://github.com/jbaruch/skill-issue-brickbox-start.git
cd skill-issue-brickbox-start
python3 -m venv .venv
# macOS, Linux and WSL:
. .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
python tools/preflight.py --require-acr --require-claude
```

The dependency lock is generated from `requirements.in`. The first exercise
intentionally has failing tests; environment readiness does not require making
them green. Real GitHub PRs and Copilot review access are unnecessary for the
core labs: review I/O uses fixtures. Model experiments consume your agent quota.

## Start here

Read [WORKBOOK.md](WORKBOOK.md). Keep this clone for the broken-skill and
script-delegation exercises. Its local `.claude/skills/fix-the-ticket` is
**intentionally bad**; do not install the reference package on top of it.

```sh
python -m uvicorn app.main:app --reload
# GET /bricks
# GET /sets/cottage/buildable
```

## Packaging exercise — use a second clone

```sh
git clone https://github.com/jbaruch/skill-issue-brickbox-start.git ../brickbox-package
cd ../brickbox-package
python3 tools/use_packaged_context.py
acr install github:jbaruch/skill-issue-policy@v0.1.6 --agent claude-code --freshness none --non-interactive
acr realize
acr check
python3 tools/preflight.py --require-acr
```

The helper preserves the local skill under `.workshop/local-skill`, outside skill
discovery. Start a fresh agent session after realization. The installed skill
has the same logical name but an ACR-prefixed directory; leaving both local and
packaged definitions discoverable confounds the activation experiment.

The [reference policy](https://github.com/jbaruch/skill-issue-policy) contains the
finished skill, tests, fixtures, hooks, eval runner and rollback instructions.
Pin the known-good `v0.1.6` here. Use unversioned/latest installation only when the
instructor starts the deliberately broken `v0.1.7` rollback exercise.

## GitHub authentication errors

`GH_TOKEN` takes precedence over `GITHUB_TOKEN`, then ACR can reuse `gh` login.
An unrelated, expired or restricted token can change access to public release
metadata. The message “not found or is inaccessible” alone does not establish
whether the repository, release or token is the problem. Compare the exact
endpoint authenticated versus anonymous without displaying token values.
Never paste tokens into the exercise. Clearing variables does not force anonymous
access if `gh` or Git's credential helper still supplies credentials.

## Recovery

Every exercise names its reference artifact and an observable success condition.
If blocked, inspect that reference and resume the next lab. For a GitHub outage,
use a locally provided reference checkout with `acr install ../skill-issue-policy`
and `acr realize`; this rehearses realization but not published-release rollback.
The instructor supplies observed release evidence and a saved model experiment;
example output is never presented as a run that did not happen.
