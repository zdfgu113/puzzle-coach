"""Load puzzles from JSON or the example/test text format used in the UI."""
from __future__ import annotations

import json
import re
from typing import Any


def _row_from_token_line(line: str) -> list[int]:
    line = line.strip()
    if not line:
        return []
    if re.fullmatch(r"[0-9]+(?:\s+[0-9]+)+", line):
        return [int(x) for x in line.split()]
    if re.fullmatch(r"[0-9]+", line):
        return [int(ch) for ch in line]
    raise ValueError(f"Cannot parse grid row: {line!r}")


def parse_text(txt: str) -> dict:
    blocks = re.findall(
        r"(Example \d+ (?:input|output)|Test (?:input|output))[^\n]*\n((?:[0-9]+(?:[ \t]+[0-9]+)*\n?)+)",
        txt,
    )
    if not blocks:
        raise ValueError(
            "No examples found. Use headings like 'Example 1 input' followed by rows of digits."
        )
    ex: dict[int, dict] = {}
    test = None
    test_output = None
    for name, body in blocks:
        rows = [_row_from_token_line(l) for l in body.splitlines() if l.strip()]
        if not rows:
            continue
        width = len(rows[0])
        if any(len(r) != width for r in rows):
            raise ValueError(f"Jagged grid under {name}")
        if name.lower().startswith("test output"):
            test_output = rows
        elif name.lower().startswith("test"):
            test = rows
        else:
            n = int(name.split()[1])
            ex.setdefault(n, {})["output" if "output" in name.lower() else "input"] = rows
    examples = []
    for k in sorted(ex):
        if "input" not in ex[k] or "output" not in ex[k]:
            raise ValueError(f"Example {k} needs both input and output")
        examples.append({"input" : ex[k]["input"], "output": ex[k]["output"]})
    if not examples:
        raise ValueError("Need at least one complete input/output example")
    if test is None:
        raise ValueError("Need a Test input grid")
    return {"examples": examples, "test": test, "test_output": test_output}


def _as_grid(obj: Any, label: str) -> list[list[int]]:
    if not isinstance(obj, list) or not obj or not isinstance(obj[0], list):
        raise ValueError(f"{label} must be a 2D array of integers")
    w = len(obj[0])
    grid = []
    for row in obj:
        if len(row) != w:
            raise ValueError(f"{label} is jagged")
        grid.append([int(x) for x in row])
    return grid


def parse_json_obj(data: Any) -> dict:
    if not isinstance(data, dict):
        raise ValueError("JSON puzzle must be an object")
    if "train" in data:
        examples = [
            {"input": _as_grid(p["input"], "train input"), "output": _as_grid(p["output"], "train output")}
            for p in data["train"]
        ]
        test_list = data.get("test") or []
        if not test_list:
            raise ValueError("ARC JSON needs a test grid")
        test = _as_grid(test_list[0]["input"], "test input")
        test_output = _as_grid(test_list[0]["output"], "test output") if "output" in test_list[0] else None
    elif "examples" in data:
        examples = [
            {"input": _as_grid(p["input"], "example input"), "output": _as_grid(p["output"], "example output")}
            for p in data["examples"]
        ]
        test = _as_grid(data["test"], "test")
        test_output = _as_grid(data["test_output"], "test_output") if data.get("test_output") else None
    else:
        raise ValueError("JSON must use {'examples', 'test'} or ARC {'train', 'test'} keys")
    if not examples:
        raise ValueError("Need at least one example")
    return {"examples": examples, "test": test, "test_output": test_output}


def parse_json_text(txt: str) -> dict:
    return parse_json_obj(json.loads(txt))


def parse_any(txt: str) -> dict:
    txt = txt.strip()
    if not txt:
        raise ValueError("Empty puzzle")
    if txt[0] in "{[":
        return parse_json_text(txt)
    return parse_text(txt)
