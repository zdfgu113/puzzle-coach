# Devpost submission fields

Paste these into the SLAY HACKS submission form at
https://slayy-hacks.devpost.com/ after you click **Enter a submission**.
Deadline: 2026-12-07 17:00 EST (2026-12-08 06:00 Asia/Shanghai). Aim to
submit by 2026-12-06.

All text below is limited to what the prototype actually does. Do not
claim a hosted demo, a paid model, or coverage of every ARC task.

---

## Project name

Puzzle Coach

---

## Elevator pitch (one sentence, 200-character limit)

An AI tutor that teaches you the hidden rule in a logic-grid puzzle, instead of just filling in the answer.

(107 characters, including spaces and the final period.)

---

## About the project

Paste the block below into the "About the project" box. Devpost will
recognize the standard section headings.

### Inspiration

Abstract reasoning puzzles — the kind used in the Abstraction and Reasoning Corpus, and in many logic games — ask you to infer a transformation from a few input/output examples and apply it to a new grid. That habit of finding a rule from examples is useful for programming and for school, but students often get stuck. Chatbots that dump the finished grid do not teach the skill. I wanted a tutor that would study the examples with me, give hints one step at a time, and only then explain a rule that had actually been checked against every example.

### What it does

Puzzle Coach is a local web tutor for ARC-style grid puzzles. You pick one of six built-in lessons or paste your own puzzle as JSON or plain text. The coach gives progressive hints, lets you paint the test grid yourself, and checks your attempt by highlighting a region that still needs work — it does not fill in the answer. When you ask for the rule, it explains a short program in plain language (English or 中文) and walks the grid through each operator so you can see the transformation happen.

The six lessons are Hole Painters, Border Cleanup, Picture Frames, Nearest Seed, Laser Dots, and Fall of Towers (a two-step "recolour, then fall" program).

### How we built it

The primary AI is a symbolic rule-induction engine, not a chatbot wrapper. It beam-searches a vocabulary of grid operators (recolour by object properties, delete, draw a frame, fill a hole, gravity, rays, nearest-seed colouring, and similar moves) and keeps only those short programs that reproduce every training example exactly. The test grid is never used to choose the program. Built-in lessons also have hand-written hints; custom puzzles get automatic observations and a live search.

The app is a small Python/Flask server with a vanilla HTML, CSS, and JavaScript front end. A language model is optional and off by default: if an API key is provided, it may only rephrase an already-verified explanation. It does not invent the rule. The prototype runs fully offline, with no account and no paid credits required. Unit tests in `tests/test_puzzles.py` check that every authored lesson is consistent, that explanations are produced in English and Chinese, that the attempt checker flags a wrong region, that the loaders parse JSON and text, and that search recovers the intended programs, including the two-step lesson.

AI coding tools helped write the prototype; the rule engine and the tutoring design are original work for this project.

### Challenges we ran into

Keeping explanations honest was the main design constraint. A language model can invent a plausible rule that fails the examples, which is the opposite of what a tutor should do, so the engine has to verify a program before any wording is shown, and the optional LLM is sandboxed to rephrasing only.

Search also has to stay fast enough for a live lesson. The vocabulary is finite, so the prototype cannot express every ARC task, and a large many-step custom puzzle may hit the time limit. Built-in lessons are instant because their programs are already verified. For the attempt checker, the useful behaviour was to point at a region still to fix without spoiling every cell — a full "here is the answer grid" would short-circuit the learning.

### Accomplishments that we're proud of

- A working tutor, not a slide deck: hints, a paintable canvas, a verified rule walkthrough, custom-puzzle loading, and an English / 中文 interface, all runnable on a laptop with `python app.py`.
- The engine recovers the intended programs in tests, including the two-step Fall of Towers lesson.
- A 2 minute 41 second demo video recorded from the real running app, with English narration and subtitles, is in the repository at `docs/demo.mp4`.

### What we learned

A checked symbolic program is a better teaching artefact than a free-form model completion: you can show the grid after each step, and you can refuse to explain a rule that does not fit. I also learned how quickly a "just add a chatbot" design fails a tutoring goal, and how much of the work is in the hint sequence and the checker, not only in finding a program.

### What's next for Puzzle Coach

- Grow the operator vocabulary so more ARC-style puzzles can be expressed, without giving up the "verified or don't explain" rule.
- Improve search so larger custom puzzles finish more reliably inside the time limit.
- Optionally host a demo deployment so judges can try it without installing Python. This submission has no hosted URL; please run it locally from the README.
- Interactive "world" puzzles (sliding, pushing) are out of scope for this prototype and would need a different engine.

---

## Built with

Add these tags (one at a time, or however the form accepts them):

- Python
- Flask
- JavaScript
- HTML
- CSS
- JSON

Do not add React, a database, or a hosted model. Those are not in this project.

---

## Try it out

**GitHub repository (required):** https://github.com/zdfgu113/puzzle-coach

There is no hosted live demo in this submission. After cloning the repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

---

## Video link

Devpost only accepts a YouTube, Vimeo, or Youku URL — not a raw MP4.

1. Upload `docs/demo.mp4` from the repo (or the copy already sent in chat) to YouTube.
2. Set visibility to **Unlisted** (or Public).
3. Paste the watch URL here, then into the Devpost video field:

```
https://youtu.be/3iM9Z5VeFbI
```

The video is 2 minutes 41 seconds, 1080p, with English narration and subtitles, recorded from the real app.

---

## Images to attach

Upload these from the repo's `docs/` folder (the form usually allows several screenshots):

- `docs/01-lesson-and-hint.png` — hint on Hole Painters
- `docs/02-check-attempt.png` — checker highlights a region to fix
- `docs/03-rule-walkthrough.png` — step-by-step rule walkthrough
- `docs/04-two-step-lesson.png` — Fall of Towers, the two-step lesson

---

## Team / other form notes

- Individual student submission. Use your real name and student status.
- Do not list anyone who did not work on the project.
- It is fair to say that AI coding tools helped write the prototype, and that you can explain the engine and the tutoring design.
