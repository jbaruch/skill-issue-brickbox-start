# Skill Issue workshop starter

**How To Write Skills That Actually Work**, QCon San Francisco, Thursday
November 19, 2026, 13:00 to 16:00 PST, Seacliff C.

Open the [workbook](WORKBOOK.md) in this repo. The [exercise evidence](EVIDENCE.md)
is in the same clone. It includes the [required mechanism rule](examples/mechanism-rule.md)
and a local replay for the Jev lab.

## Before coming to the room

Bring Git, Python 3.11 or later, and a working login for Codex, Claude Code,
or Cursor. Baruch will demo in Codex. The signature exercise uses OpenSSL.

Install [ACR 0.6.0](https://github.com/jbaruch/agentic-context-registry/blob/v0.6.0/docs/install.md).
Use macOS, Linux, or WSL, and run Git, Python, and ACR in the same environment.

```sh
git clone https://github.com/jbaruch/skill-issue-brickbox-start.git
cd skill-issue-brickbox-start
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
python tools/preflight.py
acr version
```

If ACR is still installing, start exercises 1 to 3. Exercise 2 uses the
virtual environment above. Expect five failures the first time you run its
tests.

## Open the starter in your agent

The original skill is `.claude/skills/fix-the-ticket/SKILL.md`. For Codex,
copy that skill into the project's `.agents/skills` directory before opening
the clone:

```sh
mkdir -p .agents/skills
cp -R .claude/skills/fix-the-ticket .agents/skills/
```

Cursor can see the original Claude-format skill when third-party skill
discovery is enabled. If it can't see that skill, copy it as above. Pick one
copy to edit.

Brickbox has an in-memory inventory. For exercise 1 you can read
`app/main.py` in the starter. If you want to try the API, start it from the
starter with the virtual environment activated:

```sh
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, run `curl -fsS http://127.0.0.1:8000/bricks`. Stop the
server with Ctrl+C when you're done.

## Set up the packaging clone for exercises 4 and 6

From the original starter clone, run the block below. If you already made a
clean `brickbox-package` clone, use it. Set `agent` to your agent's ACR name.

```sh
git clone https://github.com/jbaruch/skill-issue-brickbox-start.git ../brickbox-package
cd ../brickbox-package
agent=codex                   # claude-code or cursor also work
python3 tools/use_packaged_context.py
acr install github:jbaruch/skill-issue-policy@v0.2.0 --agent "$agent" --freshness none --non-interactive
acr realize
acr check
python3 tools/check_review_fixture.py --agent "$agent"
```

Expect `PASS: received COMMENTED review 12. Merge authorization is false.`
Keep this clone for both labs. The setup tool moves the original broad skill
out of discovery. Your first clone keeps the edits you make in exercises 1
and 2. Return to it and reactivate `.venv` when you work on the selector.

## If setup fails

- Check the [preflight output](tools/preflight.py) for the missing dependency.
  From the starter, rerun `python tools/preflight.py --require-acr` before
  exercise 4.
- If ACR can't fetch the public release, check the repo and tag. `GH_TOKEN`
  takes precedence over `GITHUB_TOKEN`; ACR may then reuse your `gh` login.
  A stale token can interfere with public downloads. Check which credential
  is active without displaying its value.
- If you can't install or authenticate during the session, open
  [exercise evidence](EVIDENCE.md) and rejoin the current lab. Keep your
  working files so you can finish the commands later.
