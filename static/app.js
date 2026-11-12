const COLORS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const I18N = {
  en: {
    tagline: "Learn the hidden rule — not just the answer.",
    library: "Lesson puzzles",
    load: "Load / paste",
    library_help: "Each lesson hides a short visual program. Study the examples, then paint the test grid.",
    test_title: "Your turn: the test grid",
    reset: "Reset canvas",
    check: "Check my answer",
    test_input: "Test input",
    your_canvas: "Your canvas — click to paint",
    solution: "Verified solution",
    steps_title: "Rule walkthrough",
    coach: "Coach",
    hint: "Give me a hint",
    explain: "Explain the rule",
    walk: "Walk the test",
    search: "Search for a rule",
    reveal: "Reveal the solution",
    fineprint: "The coach uses a verified rule-search engine. It will not invent a rule that fails the examples. An optional language model can only rephrase an already-checked explanation.",
    paste_title: "Load a custom puzzle",
    paste_help: "Paste ARC-style JSON, or text with “Example 1 input / output” and “Test input” grids (rows of digits 0–9).",
    marker: "This puzzle uses a border marker",
    start_custom: "Start coaching",
    welcome: "I'm your puzzle coach. We'll study the examples together and find the hidden rule. Ask for a hint when you want a nudge — I won't dump the answer first.",
    loaded: (t) => `Loaded “${t}”. Compare each example, then paint the test output on the canvas.`,
    no_more: "No further hints. Try the test grid, or ask me to explain the rule.",
    need_search: "I haven't verified a rule for this custom puzzle yet. I can search for one — it stays on your machine and only uses the examples, never the test grid, to pick the program.",
    searching: "Searching the rule vocabulary… this may take a few seconds.",
    found_rule: (rules, sec) => `Found a verified program in ${sec}s:\n${rules.join("\n")}`,
    not_found: "I couldn't verify a short program in time. You can still use the observation hints and try the grid yourself.",
    explain_intro: "Here is the hidden rule, checked against every example:",
    walk_intro: "Applying the rule to the test input, step by step. The final grid stays hidden until you ask to reveal it, or finish it yourself.",
    revealed: "Here is the verified test output. Notice how each step of the program produces it.",
    correct: "That's exactly right. You found the rule.",
    copy: "Copied a starter colouring from the test input. Change only the cells the rule would change.",
    offline: "Works fully offline with the built-in rule engine.",
  },
  zh: {
    tagline: "学会隐藏的规则，而不只是看到答案。",
    library: "课程谜题",
    load: "加载 / 粘贴",
    library_help: "每课都藏着一段短的视觉程序。先研究例题，再给测试网格涂色。",
    test_title: "轮到你：测试网格",
    reset: "重置画布",
    check: "检查我的答案",
    test_input: "测试输入",
    your_canvas: "你的画布 — 点击涂色",
    solution: "已验证的答案",
    steps_title: "规则逐步演示",
    coach: "教练",
    hint: "给我一个提示",
    explain: "讲解规则",
    walk: "在测试题上逐步演示",
    search: "搜索规则",
    reveal: "揭晓答案",
    fineprint: "教练使用可验证的规则搜索引擎，不会编造通不过例题的规则。可选的语言模型只能改写已经核对过的讲解。",
    paste_title: "加载自定义谜题",
    paste_help: "请粘贴 ARC 风格的 JSON，或带有 “Example 1 input / output” 和 “Test input” 的文本（每行是 0–9 的数字）。",
    marker: "这道题使用了边界标记",
    start_custom: "开始辅导",
    welcome: "我是你的解谜教练。我们一起看例题，找出隐藏规则。想要提示时再问我——我不会一开始就把答案告诉你。",
    loaded: (t) => `已加载「${t}」。先对比例题，再在画布上涂出测试输出。`,
    no_more: "没有更多提示了。可以先试着填测试题，或让我讲解规则。",
    need_search: "这道自定义谜题还没有验证过的规则。我可以在本地搜索，而且只会用到例题，不会用测试题来挑选程序。",
    searching: "正在搜索规则词表……可能需要几秒钟。",
    found_rule: (rules, sec) => `已在 ${sec} 秒内找到可验证的程序：\n${rules.join("\n")}`,
    not_found: "没能在时限内验证出一段短程序。你仍然可以用观察提示，自己尝试填写。",
    explain_intro: "这是已经在每组例题上核对过的隐藏规则：",
    walk_intro: "把规则一步一步用到测试输入上。最终网格会先藏起来，直到你自己做完或选择揭晓。",
    revealed: "这是已验证的测试输出。注意程序的每一步是如何得到它的。",
    correct: "完全正确。你找到规则了。",
    copy: "已把测试输入的颜色复制到画布上。只需改动规则会改变的那些格子。",
    offline: "只用内置规则引擎，就可以完全离线使用。",
  },
};

const state = {
  lang: "en",
  puzzles: [],
  session: null,
  puzzle: null,
  brush: 1,
  canvas: null,
  revealed: false,
};

const $ = (id) => document.getElementById(id);

function t(key, ...args) {
  const v = I18N[state.lang][key];
  return typeof v === "function" ? v(...args) : v;
}

function applyI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (I18N[state.lang][key]) el.textContent = I18N[state.lang][key];
  });
  $("btn-lang").textContent = state.lang === "en" ? "中文" : "EN";
  document.documentElement.lang = state.lang;
}

function renderGrid(grid, opts = {}) {
  const wrap = document.createElement("div");
  const rows = grid.length;
  const cols = grid[0].length;
  wrap.className = "grid " + (opts.size || "");
  wrap.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  wrap.setAttribute("role", opts.paint ? "grid" : "img");
  grid.forEach((row, r) => {
    row.forEach((v, c) => {
      const cell = document.createElement("div");
      cell.className = `cell c${v}`;
      if (opts.paint) {
        cell.classList.add("paint");
        cell.addEventListener("click", () => {
          state.canvas[r][c] = state.brush;
          cell.className = `cell paint c${state.brush}`;
        });
        cell.addEventListener("contextmenu", (ev) => {
          ev.preventDefault();
          state.canvas[r][c] = 0;
          cell.className = "cell paint c0";
        });
      }
      if (opts.focus && opts.focus[0] === r && opts.focus[1] === c) cell.classList.add("focus");
      wrap.appendChild(cell);
    });
  });
  return wrap;
}

function mountGrid(el, grid, opts) {
  el.innerHTML = "";
  if (grid) el.appendChild(renderGrid(grid, opts));
}

function addMsg(text, who = "coach") {
  const div = document.createElement("div");
  div.className = "msg" + (who === "you" ? " user" : "");
  const label = document.createElement("span");
  label.className = "who";
  label.textContent = who === "you" ? (state.lang === "zh" ? "你" : "You") : (state.lang === "zh" ? "教练" : "Coach");
  div.appendChild(label);
  div.appendChild(document.createTextNode(text));
  $("chat").appendChild(div);
  $("chat").scrollTop = $("chat").scrollHeight;
}

function clearChat() {
  $("chat").innerHTML = "";
}

function palette() {
  const box = $("palette");
  box.innerHTML = "";
  COLORS.forEach((c) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "swatch cell c" + c + (state.brush === c ? " active" : "");
    b.title = "Colour " + c;
    b.addEventListener("click", () => {
      state.brush = c;
      palette();
    });
    box.appendChild(b);
  });
}

function renderLibrary() {
  const list = $("puzzle-list");
  list.innerHTML = "";
  state.puzzles.forEach((p) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "puzzle-card" + (state.puzzle && state.puzzle.id === p.id ? " active" : "");
    const title = state.lang === "zh" ? p.title_zh : p.title;
    const skill = state.lang === "zh" ? p.skill_zh : p.skill;
    btn.innerHTML = `<b>${title}</b><span>${skill} · ${p.difficulty}</span>`;
    btn.addEventListener("click", () => startBuiltin(p.id));
    list.appendChild(btn);
  });
}

function showPuzzle(p) {
  state.puzzle = p;
  state.revealed = false;
  state.canvas = p.test.map((row) => row.slice());
  const title = state.lang === "zh" ? p.title_zh : p.title;
  const skill = state.lang === "zh" ? p.skill_zh : p.skill;
  const blurb = state.lang === "zh" ? p.blurb_zh : p.blurb;
  $("puzzle-title").textContent = title;
  $("puzzle-skill").textContent = skill || (state.lang === "zh" ? "自定义" : "Custom");
  $("puzzle-blurb").textContent = blurb;
  $("puzzle-diff").textContent = p.difficulty;
  $("puzzle-diff").className = "badge " + (p.difficulty || "");
  const ex = $("examples");
  ex.innerHTML = "";
  p.examples.forEach((pair, i) => {
    const box = document.createElement("div");
    box.className = "example";
    const a = document.createElement("div");
    a.className = "grid-block";
    a.innerHTML = `<p class="grid-label">${state.lang === "zh" ? "例题" : "Example"} ${i + 1} ${state.lang === "zh" ? "输入" : "in"}</p>`;
    a.appendChild(renderGrid(pair.input, { size: "sm" }));
    const arrow = document.createElement("div");
    arrow.className = "arrow";
    arrow.textContent = "→";
    const b = document.createElement("div");
    b.className = "grid-block";
    b.innerHTML = `<p class="grid-label">${state.lang === "zh" ? "输出" : "out"}</p>`;
    b.appendChild(renderGrid(pair.output, { size: "sm" }));
    box.append(a, arrow, b);
    ex.appendChild(box);
  });
  mountGrid($("test-input"), p.test, { size: "lg" });
  mountGrid($("test-canvas"), state.canvas, { size: "lg", paint: true });
  $("reveal-slot").classList.add("hidden");
  $("test-solution").innerHTML = "";
  $("steps-panel").classList.add("hidden");
  $("steps").innerHTML = "";
  $("check-result").hidden = true;
  palette();
  renderLibrary();
}

function renderSteps(groups, title) {
  const root = $("steps");
  root.innerHTML = "";
  $("steps-panel").classList.remove("hidden");
  (groups || []).forEach((g) => {
    const row = document.createElement("div");
    row.className = "step-row";
    const heading = document.createElement("p");
    heading.style.flexBasis = "100%";
    heading.style.margin = "0";
    heading.style.fontWeight = "700";
    heading.textContent = g.example ? (state.lang === "zh" ? `例题 ${g.example}` : `Example ${g.example}`) : (title || (state.lang === "zh" ? "测试输入" : "Test input"));
    row.appendChild(heading);
    (g.steps || g).forEach((step) => {
      if (step.grid === undefined && !Array.isArray(step)) return;
      const st = step.grid ? step : { grid: step, label: "", rule: null };
      const el = document.createElement("div");
      el.className = "step";
      const exp = state.lang === "zh" ? (st.explanation_zh || st.label) : (st.explanation_en || st.label);
      el.innerHTML = `<p>${st.label || ""}${st.rule ? ` · <code>${st.rule}</code>` : ""}</p><p>${exp || ""}</p>`;
      el.appendChild(renderGrid(st.grid, { size: "sm" }));
      row.appendChild(el);
    });
    root.appendChild(row);
  });
}

async function api(path, body) {
  const res = await fetch(path, {
    method: body === undefined ? "GET" : "POST",
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

async function startBuiltin(id) {
  const data = await api("/api/session", { puzzle_id: id });
  state.session = data.session_id;
  showPuzzle(data.puzzle);
  clearChat();
  addMsg(t("welcome"));
  addMsg(t("loaded", state.lang === "zh" ? data.puzzle.title_zh : data.puzzle.title));
  if (data.analysis && data.analysis.observations && data.analysis.observations.length) {
    /* keep the first observation for the first hint, not dumped immediately */
  }
}

async function startCustom(text, useMarker) {
  const data = await api("/api/session", { text, use_marker: useMarker });
  state.session = data.session_id;
  showPuzzle(data.puzzle);
  clearChat();
  addMsg(t("welcome"));
  addMsg(t("loaded", data.puzzle.title));
  if (data.analysis && data.analysis.observations) {
    addMsg(data.analysis.observations.join("\n"));
  }
}

async function onHint() {
  if (!state.session) return;
  addMsg(state.lang === "zh" ? "给我一个提示。" : "Give me a hint.", "you");
  const data = await api(`/api/session/${state.session}/hint`, { lang: state.lang });
  if (data.done) addMsg(data["message_" + state.lang] || t("no_more"));
  else {
    const h = data.hint;
    const text = h[state.lang] || h.text;
    addMsg(`Hint ${data.index}/${data.total}\n${text}`);
  }
}

async function onExplain() {
  if (!state.session) return;
  addMsg(state.lang === "zh" ? "请讲解规则。" : "Please explain the rule.", "you");
  const data = await api(`/api/session/${state.session}/explain`, { lang: state.lang });
  if (!data.ready) {
    addMsg(data["message_" + state.lang] || t("need_search"));
    return;
  }
  const exp = data.explanation;
  const text = (exp.polished || exp[state.lang] || exp.en) + (exp.formal ? "\n\n" + (state.lang === "zh" ? "形式化程序：" : "Formal program:") + "\n" + exp.formal.join("\n") : "");
  addMsg(t("explain_intro") + "\n" + text);
  if (data.steps_examples) renderSteps(data.steps_examples);
}

async function onWalk() {
  if (!state.session) return;
  addMsg(state.lang === "zh" ? "请在测试题上逐步演示。" : "Walk the rule on the test input.", "you");
  const data = await api(`/api/session/${state.session}/walk`, {});
  addMsg(t("walk_intro"));
  renderSteps([{ steps: data.steps }], state.lang === "zh" ? "测试输入（逐步）" : "Test input (step by step)");
}

async function onSearch() {
  if (!state.session) return;
  addMsg(state.lang === "zh" ? "请搜索规则。" : "Search for a rule.", "you");
  addMsg(t("searching"));
  $("btn-search").disabled = true;
  try {
    const data = await api(`/api/session/${state.session}/search`, { lang: state.lang });
    if (data.solved) {
      addMsg(t("found_rule", data.rules, data.elapsed) + "\n\n" + (state.lang === "zh" ? data.explanation_zh : data.explanation_en));
      if (data.log && data.log.length) {
        addMsg((state.lang === "zh" ? "搜索过程：\n" : "Search trace:\n") + data.log.join("\n"));
      }
    } else {
      addMsg(data["message_" + state.lang] || t("not_found"));
      if (data.log) addMsg(data.log.join("\n"));
    }
  } finally {
    $("btn-search").disabled = false;
  }
}

async function onReveal() {
  if (!state.session) return;
  addMsg(state.lang === "zh" ? "请揭晓答案。" : "Reveal the solution.", "you");
  const data = await api(`/api/session/${state.session}/reveal`, {});
  state.revealed = true;
  $("reveal-slot").classList.remove("hidden");
  mountGrid($("test-solution"), data.test_output, { size: "lg" });
  addMsg(t("revealed"));
  if (data.steps) renderSteps([{ steps: data.steps }], state.lang === "zh" ? "测试题解答过程" : "How the test was solved");
}

async function onCheck() {
  if (!state.session) return;
  const data = await api(`/api/session/${state.session}/check`, { grid: state.canvas });
  const box = $("check-result");
  box.hidden = false;
  if (data.correct) {
    box.className = "check-result good";
    box.textContent = t("correct");
    addMsg(t("correct"));
  } else {
    box.className = "check-result bad";
    const msg = data["hint_" + state.lang] || data.error || "";
    box.textContent = msg;
    addMsg(msg);
    if (data.focus) {
      mountGrid($("test-canvas"), state.canvas, { size: "lg", paint: true, focus: [data.focus.row, data.focus.col] });
    }
  }
}

function onReset() {
  if (!state.puzzle) return;
  state.canvas = state.puzzle.test.map((row) => row.slice());
  mountGrid($("test-canvas"), state.canvas, { size: "lg", paint: true });
  $("check-result").hidden = true;
  addMsg(t("copy"));
}

async function boot() {
  applyI18n();
  palette();
  const data = await api("/api/puzzles");
  state.puzzles = data.puzzles;
  renderLibrary();
  if (state.puzzles.length) await startBuiltin(state.puzzles[0].id);
}

$("btn-lang").addEventListener("click", () => {
  state.lang = state.lang === "en" ? "zh" : "en";
  applyI18n();
  if (state.puzzle) showPuzzle(state.puzzle);
  renderLibrary();
});
$("btn-hint").addEventListener("click", () => onHint().catch((e) => addMsg(e.message)));
$("btn-explain").addEventListener("click", () => onExplain().catch((e) => addMsg(e.message)));
$("btn-walk").addEventListener("click", () => onWalk().catch((e) => addMsg(e.message)));
$("btn-search").addEventListener("click", () => onSearch().catch((e) => addMsg(e.message)));
$("btn-reveal").addEventListener("click", () => onReveal().catch((e) => addMsg(e.message)));
$("btn-check").addEventListener("click", () => onCheck().catch((e) => addMsg(e.message)));
$("btn-reset").addEventListener("click", onReset);
$("btn-paste").addEventListener("click", () => $("modal").classList.remove("hidden"));
$("btn-close-modal").addEventListener("click", () => $("modal").classList.add("hidden"));
$("btn-load-paste").addEventListener("click", async () => {
  $("paste-error").hidden = true;
  try {
    await startCustom($("paste-text").value, $("use-marker").checked);
    $("modal").classList.add("hidden");
  } catch (e) {
    $("paste-error").hidden = false;
    $("paste-error").textContent = e.message;
  }
});

boot().catch((e) => addMsg(e.message));
