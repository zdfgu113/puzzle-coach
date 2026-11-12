# Devpost submission draft (paste, then edit in your own voice)

Submit at https://slayy-hacks.devpost.com/ before **2026-12-07 17:00 EST (2026-12-08 06:00 Asia/Shanghai)**. Only you can register, push the repo, record the video, and click submit. Built locally in `/workspace/slayhacks-puzzle-coach/`.

## Project name

Puzzle Coach

## Tagline / elevator (one line)

An AI tutor that teaches you the hidden rule in a logic-grid puzzle, instead of just filling in the answer.

## Problem and solution

Abstract reasoning puzzles ask you to infer a transformation from a few input/output examples and apply it to a new grid. Students get stuck, and chatbots that dump the finished grid do not teach the skill. Puzzle Coach is a local web tutor: you load an ARC-style puzzle, ask for hints one step at a time, try the test grid yourself, and hear a plain-language explanation of a *verified* rule program, with the grid shown after each step.

It is aimed at students who want to practise visual rule-finding — the same habit that helps with programming and with abstraction-and-reasoning tasks.

## AI implementation

The main AI is a symbolic program-synthesis engine. It beam-searches a vocabulary of grid operators (recolour by object properties, delete, frame, fill holes, gravity, rays, nearest-seed colouring) and accepts a short program only when every training example matches exactly. The test grid is never used to choose the program. Built-in lessons also have hand-written hints.

A language model is optional and off by default. If an API key is provided, it may only rephrase an already-verified explanation. It does not invent the rule. The prototype runs fully offline without any paid API or credits.

Stack: Python, Flask, a custom rule engine and search module, a vanilla HTML/CSS/JS front end.

## What to attach

- GitHub repo (public), with this README and screenshots in `docs/`.
- Demo video, 2–4 minutes, following `docs/demo-script.md`.
- Screenshots: `docs/01-lesson-and-hint.png`, `docs/02-check-attempt.png`, `docs/03-rule-walkthrough.png`, `docs/04-two-step-lesson.png`.
- Built-in demo is local: `python app.py` then http://127.0.0.1:5000. There is no hosted URL unless you later deploy one yourself.

## Team

Individual submission. Use your real name and student status. Do not list anyone who did not work on the project. It is fair to say that AI coding tools helped write the prototype, and that you can explain the engine and the tutoring design.

## Suggested judging self-check

- Innovation: tutoring + verified symbolic rules, not “GPT solves ARC”.
- Technical execution: engine, search, hints, canvas checking, custom puzzle loader; tests in `tests/`.
- Impact: a concrete education tool students can run locally for free.
- Responsible AI: no hallucinated rules; optional LLM is sandboxed to wording; no secrets in the repo.
- Presentation: README, screenshots, and the short video.

## Hard limits (already respected in this prototype)

Do not put API keys or `.env` files in the GitHub repo. Do not claim features the demo cannot show.
