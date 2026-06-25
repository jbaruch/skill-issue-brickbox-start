# Skill Issue — Workshop Starting Point

The clone-and-follow-along repo for **"Skill Issue: How to Write Skills That Actually
Work"** (Baruch Sadogursky). You start with a tiny API and a skill that *kind of*
works — then you make it actually work, the way you make code work.

**Slides & shownotes:** https://speaking.jbaru.ch/talks/agentcon-st-louis-2026-skill-issue/

## The project

`brickbox` — a tiny Lego brick-inventory API. Know what you can build from the bricks
you own.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# then hit:  GET /bricks   and   GET /sets/cottage/buildable
```

## What's already here — and what's wrong with it

`.claude/skills/fix-the-ticket/SKILL.md` handles "tickets." It works… kind of. The
description is vague and the conditional is mushy, so it mis-activates and takes the
heavy code path (branch → PR → review poll) even on a docs-only ticket — burning tokens
on a review nobody needed. **That's the skill issue.** Your job is to make it actually
work.

## Follow along — ask your agent to do each task, in order

Each step is a real engineering practice, not prompt-tweaking.

1. **Kill the non-determinism → a script.** The review summon + poll loop is
   deterministic; it shouldn't cost model tokens every run. Ask your agent to extract it
   into `scripts/await_review.py` (a GitHub GraphQL review summon + a bounded poll), with
   a **pytest that goes red, then green**.

2. **Remove the activation gamble → rules.** Skills *activate* (and can mis-activate).
   Rules *apply* — always. Ask your agent "what here must always be true?" and add the
   mandatory guardrails as rules (e.g. never commit straight to `main`; every PR needs a
   review; never merge with unaddressed comments). Then prove it: ask it to do the
   forbidden thing and watch it refuse.

3. **Grow a library → package a plugin.** Loose files are a pile. Ask your agent to bundle
   the skill + script + rules into a distributable plugin (a manifest that declares them)
   and publish it, so other repos can install it instead of copy-pasting.

4. **Test the fuzzy parts → evals.** "Improve against *what*?" Ask your agent to write an
   eval scenario and run it **with vs without** the plugin as context — the gap (the
   *lift*) is the signal that the context actually helps. Watch the scenario for
   bleeding/leaking.

5. **Keep going — the rest of the practices.** Review across models (don't let a model
   grade its own family), scan the skill as **code AND a prompt**, and ship to a registry
   with install/activation telemetry — reuse you can measure, not vibes.

## Stuck? Reference implementation

The finished plugin lives on the Tessl registry as `jbaruch/skill-issue-policy`
(`tessl install jbaruch/skill-issue-policy`). Peek if you're stuck — but try it yourself
first; the point is the doing.
