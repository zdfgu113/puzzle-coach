#!/usr/bin/env python3
"""Puzzle Coach web app. Run: python app.py  then open http://127.0.0.1:5000"""
from __future__ import annotations

import copy
import secrets
import traceback
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from puzzlecoach import __version__
from puzzlecoach.coach import (
    analyze_examples,
    apply_steps,
    build_session_hints,
    check_attempt,
    explain_program,
)
from puzzlecoach.engine import run
from puzzlecoach.format import parse_any
from puzzlecoach.llm import llm_configured, polish
from puzzlecoach.puzzles import PUZZLE_BY_ID, public_puzzle, list_public
from puzzlecoach.search import search_rules

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JSON_SORT_KEYS"] = False

# In-memory tutoring sessions. Fine for a local demo; not a production store.
SESSIONS: dict[str, dict] = {}


def _pairs(examples):
    return [(e["input"], e["output"]) for e in examples]


def _new_session(puzzle: dict, source: str) -> dict:
    sid = secrets.token_hex(8)
    session = {
        "id": sid,
        "source": source,
        "puzzle": puzzle,
        "hint_index": 0,
        "revealed": False,
        "search": None,
    }
    SESSIONS[sid] = session
    return session


def _get(sid: str) -> dict:
    s = SESSIONS.get(sid)
    if not s:
        raise KeyError(sid)
    return s


def _client_puzzle(p: dict, include_hidden: bool = False) -> dict:
    data = public_puzzle(p) if p.get("id") in PUZZLE_BY_ID and p is PUZZLE_BY_ID.get(p.get("id")) else {
        "id": p.get("id") or "custom",
        "title": p.get("title") or "Custom puzzle",
        "title_zh": p.get("title_zh") or "自定义谜题",
        "difficulty": p.get("difficulty") or "custom",
        "skill": p.get("skill") or "",
        "skill_zh": p.get("skill_zh") or "",
        "blurb": p.get("blurb") or "A puzzle you loaded yourself.",
        "blurb_zh": p.get("blurb_zh") or "你自己加载的谜题。",
        "use_marker": bool(p.get("use_marker")),
        "examples": p["examples"],
        "test": p["test"],
        "hint_count": len(p.get("hints") or []),
    }
    if include_hidden and p.get("test_output") is not None:
        data = dict(data)
        data["test_output"] = p["test_output"]
        data["rules"] = p.get("rules") or []
    return data


@app.get("/")
def index():
    return render_template("index.html", version=__version__)


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "version": __version__, "llm": llm_configured()})


@app.get("/api/puzzles")
def api_list_puzzles():
    return jsonify({"puzzles": list_public()})


@app.get("/api/puzzles/<pid>")
def api_get_puzzle(pid: str):
    p = PUZZLE_BY_ID.get(pid)
    if not p:
        return jsonify({"error": "Unknown puzzle"}), 404
    return jsonify({"puzzle": public_puzzle(p)})


@app.post("/api/parse")
def api_parse():
    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Paste a puzzle in JSON or example/test text form."}), 400
    try:
        parsed = parse_any(text)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"puzzle": parsed, "has_test_output": parsed.get("test_output") is not None})


@app.post("/api/session")
def api_start_session():
    body = request.get_json(silent=True) or {}
    if body.get("puzzle_id"):
        p = PUZZLE_BY_ID.get(body["puzzle_id"])
        if not p:
            return jsonify({"error": "Unknown puzzle"}), 404
        puzzle = copy.deepcopy(p)
        source = "builtin"
    elif body.get("puzzle") or body.get("text"):
        try:
            parsed = body.get("puzzle") or parse_any(body.get("text") or "")
            if "examples" not in parsed:
                from puzzlecoach.format import parse_json_obj
                parsed = parse_json_obj(parsed)
            puzzle = {
                "id": parsed.get("id") or "custom",
                "title": parsed.get("title") or "Custom puzzle",
                "title_zh": parsed.get("title_zh") or "自定义谜题",
                "difficulty": "custom",
                "skill": "",
                "skill_zh": "",
                "blurb": parsed.get("blurb") or "A puzzle you loaded yourself.",
                "blurb_zh": parsed.get("blurb_zh") or "你自己加载的谜题。",
                "use_marker": bool(body.get("use_marker") or parsed.get("use_marker")),
                "examples": parsed["examples"],
                "test": parsed["test"],
                "test_output": parsed.get("test_output"),
                "rules": list(parsed.get("rules") or []),
                "hints": parsed.get("hints") or [],
            }
        except (ValueError, TypeError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400
        source = "custom"
    else:
        return jsonify({"error": "Provide puzzle_id or a pasted puzzle."}), 400

    session = _new_session(puzzle, source)
    analysis = analyze_examples(puzzle["examples"], puzzle.get("use_marker", False))
    return jsonify(
        {
            "session_id": session["id"],
            "puzzle": _client_puzzle(puzzle),
            "analysis": analysis,
            "llm": llm_configured(),
        }
    )


@app.post("/api/session/<sid>/hint")
def api_hint(sid: str):
    try:
        session = _get(sid)
    except KeyError:
        return jsonify({"error": "Session expired. Load the puzzle again."}), 404
    lang = (request.get_json(silent=True) or {}).get("lang") or "en"
    hints = build_session_hints(session["puzzle"], lang)
    # Only serve authored/generic hints from this endpoint, not the full rule,
    # unless the user has already asked to explain or no authored hints remain.
    teach = [h for h in hints if h.get("kind") != "rule"]
    if not teach:
        teach = hints
    idx = session["hint_index"]
    if idx >= len(teach):
        return jsonify(
            {
                "done": True,
                "hint": None,
                "index": idx,
                "total": len(teach),
                "message_en": "No further hints. Try the test grid, or ask the coach to explain the rule.",
                "message_zh": "没有更多提示了。可以先试着填测试题，或让教练讲解规则。",
            }
        )
    hint = teach[idx]
    session["hint_index"] = idx + 1
    return jsonify({"done": False, "hint": hint, "index": idx + 1, "total": len(teach)})


@app.post("/api/session/<sid>/explain")
def api_explain(sid: str):
    try:
        session = _get(sid)
    except KeyError:
        return jsonify({"error": "Session expired. Load the puzzle again."}), 404
    body = request.get_json(silent=True) or {}
    lang = body.get("lang") or "en"
    puzzle = session["puzzle"]
    rules = puzzle.get("rules") or []
    search_info = session.get("search")
    if not rules:
        return jsonify(
            {
                "ready": False,
                "need_search": True,
                "message_en": "The coach has not verified a rule for this custom puzzle yet. Run a rule search first.",
                "message_zh": "这道自定义谜题还没有验证过的规则。请先运行规则搜索。",
            }
        )
    steps_examples = [
        {"example": i, "steps": apply_steps(rules, ex["input"], puzzle.get("use_marker", False))}
        for i, ex in enumerate(puzzle["examples"], 1)
    ]
    steps_test = apply_steps(rules, puzzle["test"], puzzle.get("use_marker", False))
    explanation = {
        "en": explain_program(rules, "en"),
        "zh": explain_program(rules, "zh"),
        "rules": rules,
        "formal": rules,
    }
    polished = None
    if body.get("polish") and llm_configured():
        polished = polish(explanation[lang])
        if polished.get("ok"):
            explanation["polished"] = polished["text"]
            explanation["polished_model"] = polished.get("model")
    return jsonify(
        {
            "ready": True,
            "explanation": explanation,
            "steps_examples": steps_examples,
            "steps_test_input": [steps_test[0]],  # start grid only; full walk after reveal or walk=true
            "steps_test": steps_test if body.get("walk_test") or session["revealed"] else None,
            "search": search_info,
        }
    )


@app.post("/api/session/<sid>/walk")
def api_walk(sid: str):
    """Walk the verified rule over the test input, one step at a time, without dumping the final answer first."""
    try:
        session = _get(sid)
    except KeyError:
        return jsonify({"error": "Session expired. Load the puzzle again."}), 404
    puzzle = session["puzzle"]
    rules = puzzle.get("rules") or []
    if not rules:
        return jsonify({"error": "No verified rule yet."}), 400
    steps = apply_steps(rules, puzzle["test"], puzzle.get("use_marker", False))
    # Omit the final grid unless the client asks to include it (or already revealed).
    body = request.get_json(silent=True) or {}
    if not (body.get("include_final") or session["revealed"]):
        visible = steps[:-1] if len(steps) > 1 else steps
        return jsonify({"steps": visible, "final_hidden": True, "rule_count": len(rules)})
    return jsonify({"steps": steps, "final_hidden": False, "rule_count": len(rules)})


@app.post("/api/session/<sid>/reveal")
def api_reveal(sid: str):
    try:
        session = _get(sid)
    except KeyError:
        return jsonify({"error": "Session expired. Load the puzzle again."}), 404
    puzzle = session["puzzle"]
    rules = puzzle.get("rules") or []
    if puzzle.get("test_output") is None and rules:
        puzzle["test_output"] = run(rules, puzzle["test"], puzzle.get("use_marker", False))
    if puzzle.get("test_output") is None:
        return jsonify({"error": "No verified solution to reveal yet. Run a rule search first."}), 400
    session["revealed"] = True
    steps = apply_steps(rules, puzzle["test"], puzzle.get("use_marker", False)) if rules else None
    return jsonify(
        {
            "test_output": puzzle["test_output"],
            "rules": rules,
            "explanation_en": explain_program(rules, "en") if rules else None,
            "explanation_zh": explain_program(rules, "zh") if rules else None,
            "steps": steps,
        }
    )


@app.post("/api/session/<sid>/check")
def api_check(sid: str):
    try:
        session = _get(sid)
    except KeyError:
        return jsonify({"error": "Session expired. Load the puzzle again."}), 404
    body = request.get_json(silent=True) or {}
    puzzle = session["puzzle"]
    expected = puzzle.get("test_output")
    if expected is None and puzzle.get("rules"):
        expected = run(puzzle["rules"], puzzle["test"], puzzle.get("use_marker", False))
        puzzle["test_output"] = expected
    if expected is None:
        return jsonify({"error": "No verified answer to check against yet. Run a rule search first."}), 400
    result = check_attempt(expected, body.get("grid"))
    return jsonify(result)


@app.post("/api/session/<sid>/search")
def api_search(sid: str):
    try:
        session = _get(sid)
    except KeyError:
        return jsonify({"error": "Session expired. Load the puzzle again."}), 404
    body = request.get_json(silent=True) or {}
    puzzle = session["puzzle"]
    marker_mode = bool(body.get("use_marker", puzzle.get("use_marker", False)))
    try:
        result = search_rules(
            _pairs(puzzle["examples"]),
            test=puzzle["test"],
            marker_mode=marker_mode,
            beam=int(body.get("beam") or 40),
            depth=int(body.get("depth") or 4),
            timeout=float(body.get("timeout") or 25),
        )
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Search failed unexpectedly. Try a simpler puzzle or a longer timeout."}), 500
    session["search"] = {"elapsed": result["elapsed"], "log": result["log"], "candidates": result["candidates"]}
    if result["solutions"]:
        # Prefer a unique test answer; take the first verified program.
        best = result["solutions"][0]
        puzzle["rules"] = best["rules"]
        puzzle["use_marker"] = marker_mode
        if best.get("test_output") is not None:
            puzzle["test_output"] = best["test_output"]
        keys = {s.get("test_key") for s in result["solutions"] if s.get("test_key")}
        return jsonify(
            {
                "solved": True,
                "rules": best["rules"],
                "alternative_count": len(result["solutions"]),
                "unique_test_answers": len(keys),
                "elapsed": result["elapsed"],
                "log": result["log"],
                "candidates": result["candidates"],
                "explanation_en": explain_program(best["rules"], "en"),
                "explanation_zh": explain_program(best["rules"], "zh"),
            }
        )
    return jsonify(
        {
            "solved": False,
            "elapsed": result["elapsed"],
            "log": result["log"],
            "candidates": result["candidates"],
            "message_en": "The engine could not verify a short rule program in time. You can still use the observation hints and try the test grid yourself.",
            "message_zh": "引擎没能在时限内验证出一段短规则。你仍然可以用观察提示，自己尝试填写测试题。",
        }
    )


@app.get("/docs/<path:filename>")
def docs_file(filename: str):
    return send_from_directory(ROOT / "docs", filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
