# Puzzle Coach — 2 to 4 minute demo script

Record the local app at http://127.0.0.1:5000 in a 1280×720 or 1920×1080 window. Speak in English for the judges (you can add a short Chinese line at the end if you want). Target about 3 minutes.

## 0:00–0:25  The problem

Open the app on the first lesson, *Hole Painters*. Show the examples and the empty-looking test canvas.

> “People use AI to solve puzzles, but most tools just print the answer. That does not teach you how to see the hidden rule. Puzzle Coach is a tutor for ARC-style grid puzzles: it gives hints, explains the rule, and lets you try the test yourself.”

## 0:25–1:10  Hints, not answers

Click **Give me a hint** twice. Read the second hint aloud (holes vs solid shapes). Paint a couple of cells on the canvas, click **Check my answer**, and show that the coach points you to a region instead of filling the grid for you.

> “Hints come one at a time. When I check a wrong attempt, it tells me where to look, not what every cell should be.”

## 1:10–2:10  The verified rule

Click **Explain the rule**. Scroll the walkthrough so the judges see the formal program and the example grids after each step. Then click **Walk the test** and show the intermediate test grids with the final answer still hidden. Finally click **Reveal the solution**.

> “Under the hood this is symbolic AI, not a chatbot guessing. A rule-search engine proposes short visual programs — recolour, delete, frame, gravity, rays — and only keeps a program that matches every example exactly. The test grid is not used to pick the rule. So the explanation you hear is faithful.”

## 2:10–2:40  A two-step lesson

Switch to *Fall of Towers*. Click **Explain the rule** (or give one hint first). Point out that order matters: tall shapes turn yellow, then the yellow shapes fall.

> “Some lessons are short programs, not a single action. If you recolour and drop in the wrong order, the examples would not match.”

## 2:40–3:10  Offline, optional LLM, custom puzzles

Open **Load / paste** briefly, then close it. Point to the note at the bottom of the coach panel.

> “It runs entirely on your machine. No API key is required. If you do add a key, a language model can only rephrase an already-checked explanation — it is not allowed to invent the rule.”

## 3:10–3:30  Close

Return to the main view.

> “Puzzle Coach helps students practise the skill of finding a rule from examples. That is the part of AI literacy that answer-boxes skip. Thanks for watching.”

## Recording tips

- Use the English UI for the judges (`EN` if the page is in 中文).
- Avoid covering the grids with the cursor.
- If a click is slow, pause on the walkthrough — that is the money shot.
- You do not need a voice-over script word for word; the beats above are enough.
