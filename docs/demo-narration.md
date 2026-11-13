# Puzzle Coach — demo narration

English voice-over for the SLAY HACKS 2026 demo video. Spoken by a local neural TTS voice (Microsoft Ava, via edge-tts). The wording follows `docs/demo-script.md` and stays within what the app actually does: layered hints, a check that points to a region, a verified symbolic rule walkthrough, a two-step lesson, custom-puzzle loading, an optional LLM that can only rephrase, and an English / 中文 interface that runs offline.

- Voice: `en-US-AvaNeural` at `-8%`.
- Finished video: `docs/demo.mp4` (target 2–4 minutes; narration runs to 154.7s, file length 161.2s).
- Subtitles: English, burned into the video.

## Script with timestamps (mm:ss)

### Title card

**0:00–0:05**

> Puzzle Coach. A tutor that teaches you to solve — not just answers.

### The problem

**0:06–0:14**

> People use AI to solve puzzles, but most tools just print the answer. That does not teach you how to see the hidden rule.

### The first lesson

**0:15–0:29**

> Puzzle Coach is a tutor for ARC-style grid puzzles: it gives hints, explains the rule, and lets you try the test yourself. This first lesson is called Hole Painters. Study the examples, then paint the test grid.

### Hints, not answers

**0:30–0:32**

> Hints come one at a time.

**0:32–0:40**

> The first hint says: ignore the colours for a moment, and look at the empty cells trapped inside each shape.

**0:40–0:48**

> The second hint goes further: count the enclosed holes. Shapes with holes change; solid shapes stay the same.

**0:49–0:53**

> I'll paint a couple of cells, then check my answer.

**0:53–0:58**

> The coach points me to a region still to fix — it does not fill in the grid for me.

### The verified rule

**0:59–1:02**

> Now I'll ask the coach to explain the rule.

**1:02–1:19**

> Under the hood, this is symbolic AI, not a chatbot guessing. A rule-search engine proposes short visual programs — recolour, delete, frame, gravity, rays — and only keeps a program that matches every example exactly.

**1:20–1:25**

> Here is the formal program, and the example grids after each step.

**1:25–1:30**

> I can also walk the rule on the test input, with the final answer still hidden.

**1:31–1:40**

> And when I'm ready, I can reveal the verified solution. The test grid is not used to pick the rule, so the explanation you hear is faithful.

### A two-step lesson

**1:41–1:47**

> Some lessons are short programs, not a single action. This one is Fall of Towers.

**1:48–1:57**

> Tall shapes turn yellow, then the yellow shapes fall. If you recolour and drop in the wrong order, the examples would not match.

### Offline, optional LLM, custom puzzles

**1:58–2:01**

> You can load your own puzzle as JSON or plain text.

**2:02–2:16**

> It runs entirely on your machine. No API key is required. If you do add a key, a language model can only rephrase an already-checked explanation — it is not allowed to invent the rule.

**2:16–2:22**

> The interface is available in English and Chinese, and it works fully offline.

### Close

**2:23–2:33**

> Puzzle Coach helps students practise the skill of finding a rule from examples. That is the part of AI literacy that answer-boxes skip. Thanks for watching.

### End card

**2:33–2:41**

On-screen only (no extra voice-over):

> Thanks for watching
>
> Puzzle Coach helps students practise the skill of finding a rule from examples — the part of AI literacy that answer-boxes skip.
>
> Runs fully offline · English / 中文 · SLAY HACKS 2026

## Visual beats

- Open on the title card, then fade into the first lesson, *Hole Painters*, with examples and the test canvas in the English UI.
- Click **Give me a hint** twice; the second hint is about counting enclosed holes.
- Paint a few cells green on the test canvas, click **Check my answer**, and show the coach pointing at a region (focus ring + “look again around row…”) instead of filling the grid.
- Click **Explain the rule**, hold on the formal program (`recolor-holes(1->3,2+->4)`), then scroll the walkthrough so the example grids after each step are visible.
- Click **Walk the test** with the final answer still hidden, then **Reveal the solution**.
- Switch to *Fall of Towers*, give one hint, then explain the two-step program: tall shapes turn yellow, then yellow shapes fall.
- Open **Load / paste** briefly and close it. Highlight the coach-panel note: verified engine, optional LLM may only rephrase.
- Toggle **中文**, then back to English, and close on the end card.

No claims beyond what this prototype does. There is no hosted URL, and the optional language model is off in this recording.
