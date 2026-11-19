# Skill Issue workshop starter

**How To Write Skills That Actually Work**, QCon San Francisco, Thursday
November 19, 2026, 13:00 to 16:00 PST. Bring a working login for Codex, Claude Code, or Cursor.

The starter contains a LEGO inventory API and a skill that treats every request
like a code ticket. Start by asking your agent to add a Quickstart paragraph.
Then open the workbook to see what the agent picked and fix the review selector.

## Before Thursday

Bring Git and Python **3.11+**. The signature demo uses OpenSSL. Baruch runs
the live examples in Codex. Use your own agent for the routing exercise and
the package install. The workbook includes saved or local examples for the
eval, hook and skill log exercises.

Install **ACR 0.6.0** using its [installation guide](https://github.com/jbaruch/agentic-context-registry/blob/main/docs/install.md).
Use macOS or Linux. **Windows users need WSL**; ACR has no native Windows support
([issue #14](https://github.com/jbaruch/agentic-context-registry/issues/14)). Run
Git, Python and ACR in the same WSL environment. Open the clone in your agent.

```sh
git clone https://github.com/jbaruch/skill-issue-brickbox-start.git
cd skill-issue-brickbox-start
python3 -m venv .venv
# macOS, Linux and WSL:
. .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
python tools/preflight.py --require-acr
```

The preflight checks your setup. The starter selector tests are supposed to
fail before exercise 2. You can work through the review exercises with the
bundled fixtures. Live agent requests use your own account.

## Start here

Open [WORKBOOK.md](WORKBOOK.md) in this clone. The original starter skill is
under `.claude/skills/fix-the-ticket`. For Codex, copy it to the
project's `.agents/skills` directory before starting the routing exercise:

```sh
mkdir -p .agents/skills
cp -R .claude/skills/fix-the-ticket .agents/skills/
```

In Cursor, check whether the original skill appears. Copy it only if
you need to. Check that your agent sees a single starter skill. Keep your edits in this clone and start
the package exercise in a fresh clone.

```sh
python -m uvicorn app.main:app --reload
# GET /bricks
# GET /sets/cottage/buildable
```

## Install the reference in a second clone

```sh
git clone https://github.com/jbaruch/skill-issue-brickbox-start.git ../brickbox-package
cd ../brickbox-package
python3 tools/use_packaged_context.py
agent=codex                  # or claude-code or cursor
acr install github:jbaruch/skill-issue-policy@v0.2.0 --agent "$agent" --freshness none --non-interactive
acr realize
acr check
python3 tools/preflight.py --require-acr
```

`tools/use_packaged_context.py` moves the local skill to `.workshop/local-skill`.
Start a fresh session in the agent you selected. ACR installs the skill in
`.codex/skills`, `.claude/skills`, or `.cursor/skills` for the corresponding
agent.

Use the [v0.2.0 reference policy](https://github.com/jbaruch/skill-issue-policy/tree/v0.2.0)
for setup. Switch to an unversioned install only in the rollback lab, where
Latest points to the deliberately broken v0.2.1 release.

## GitHub authentication errors

`GH_TOKEN` takes precedence over `GITHUB_TOKEN`, then ACR can reuse `gh` login.
An unrelated, expired or restricted token can change access to public release
metadata. If ACR reports "not found or is inaccessible", check the repository name,
release tag and credential in use. Compare the exact
endpoint authenticated versus anonymous without displaying token values.
Never paste tokens into the exercise. Clearing variables does not force anonymous
access if `gh` or Git's credential helper still supplies credentials.

## Recovery

If you get stuck, keep the starter clone and use the v0.2.0 files to rejoin
at the next workbook exercise. If GitHub is down, ask for a local reference
checkout and install it in the packaging clone with
`acr install ../skill-issue-policy --agent "$agent"` followed by `acr realize`. For the
published-release rollback and full model comparison, use the instructor's
saved runs.
