"""Turn verified rule programs and grid observations into teaching hints."""
from __future__ import annotations

from collections import Counter

from .engine import PRED, bbox, holes, marker, objs, run, run_steps

PRED_TEXT = {
    "solid-rect": {"en": "solid rectangles (completely filled boxes of at least two cells)", "zh": "实心矩形（完全填满、至少两格）"},
    "wide": {"en": "wide shapes (wider than they are tall)", "zh": "宽形状（宽度大于高度）"},
    "tall": {"en": "tall shapes (taller than they are wide)", "zh": "高形状（高度大于宽度）"},
    "touches-edge": {"en": "shapes that touch the grid border", "zh": "碰到网格边界的形状"},
    "two-holes": {"en": "shapes with two or more enclosed holes", "zh": "有两个或更多封闭洞的形状"},
    "asym": {"en": "asymmetric shapes", "zh": "不对称的形状"},
    "mirror-sym": {"en": "mirror-symmetric shapes (single cells do not count)", "zh": "左右镜像对称的形状（单格不算）"},
    "all": {"en": "every object", "zh": "每一个物体"},
    "multi": {"en": "every multi-cell shape", "zh": "每一个多格形状"},
    "size-1": {"en": "single-cell objects", "zh": "只有一格的物体"},
    "size-2": {"en": "objects made of exactly two cells", "zh": "正好两格的物体"},
    "size-3": {"en": "objects made of exactly three cells", "zh": "正好三格的物体"},
    "size-4": {"en": "objects made of exactly four cells", "zh": "正好四格的物体"},
    "even-size": {"en": "objects with an even number of cells", "zh": "格子数为偶数的物体"},
    "has-hole": {"en": "shapes that contain at least one enclosed hole", "zh": "至少有一个封闭洞的形状"},
    "no-hole": {"en": "shapes with no enclosed hole", "zh": "没有封闭洞的形状"},
    "one-hole": {"en": "shapes with exactly one enclosed hole", "zh": "正好有一个封闭洞的形状"},
    "largest": {"en": "the largest object(s) on the grid", "zh": "网格上最大的物体"},
    "unique-color": {"en": "objects whose colour appears only once", "zh": "颜色在图中只出现一次的物体"},
    "shared-color": {"en": "objects that share their colour with another object", "zh": "和别的物体共用同一颜色的物体"},
    "marker-color": {"en": "objects that match the border-marker colour", "zh": "颜色与边界标记相同的物体"},
    "not-marker-color": {"en": "objects that do not match the border-marker colour", "zh": "颜色与边界标记不同的物体"},
}
for k in range(1, 10):
    PRED_TEXT[f"color-{k}"] = {"en": f"objects of colour {k}", "zh": f"颜色为 {k} 的物体"}

COLOR_NAME = {
    0: {"en": "background (0)", "zh": "背景（0）"},
    1: {"en": "blue (1)", "zh": "蓝色（1）"},
    2: {"en": "red (2)", "zh": "红色（2）"},
    3: {"en": "green (3)", "zh": "绿色（3）"},
    4: {"en": "yellow (4)", "zh": "黄色（4）"},
    5: {"en": "grey (5)", "zh": "灰色（5）"},
    6: {"en": "magenta (6)", "zh": "品红（6）"},
    7: {"en": "orange (7)", "zh": "橙色（7）"},
    8: {"en": "cyan (8)", "zh": "青色（8）"},
    9: {"en": "maroon (9)", "zh": "栗色（9）"},
}


def color_name(c: int, lang: str = "en") -> str:
    return COLOR_NAME.get(c, {"en": f"colour {c}", "zh": f"颜色 {c}"})[lang]


def pred_text(p: str, lang: str = "en") -> str:
    return PRED_TEXT.get(p, {"en": p, "zh": p})[lang]


def parse_rule_parts(rule: str) -> tuple[str, list[str]]:
    name, args = rule.split("(", 1)
    args = args[:-1]
    return name, args.split(",") if args else []


def explain_rule(rule: str, lang: str = "en") -> str:
    name, args = parse_rule_parts(rule)
    if name == "recolor-holes":
        a = int(args[0].split("->")[1])
        b = int(args[1].split("->")[1])
        if lang == "zh":
            return f"按洞的数量重新上色：正好 1 个洞的形状涂成{color_name(a, lang)}，2 个或更多洞的形状涂成{color_name(b, lang)}。没有洞的形状不变。"
        return f"Recolour by hole count: shapes with exactly one hole become {color_name(a, lang)}; shapes with two or more holes become {color_name(b, lang)}. Solid shapes stay the same."
    if name == "recolor":
        pred, c = args[0].split("->")
        if lang == "zh":
            return f"把所有{pred_text(pred, lang)}涂成{color_name(int(c), lang)}。"
        return f"Recolour {pred_text(pred, lang)} to {color_name(int(c), lang)}."
    if name == "delete":
        pred = args[0]
        if lang == "zh":
            return f"删除所有{pred_text(pred, lang)}。"
        return f"Delete {pred_text(pred, lang)}."
    if name == "frame":
        pred, c = args[0].split("->")
        if lang == "zh":
            return f"给所有{pred_text(pred, lang)}画一圈一格厚的{color_name(int(c), lang)}边框。边框只画在空格子上。"
        return f"Draw a one-cell-thick {color_name(int(c), lang)} frame around {pred_text(pred, lang)}. The frame only fills empty cells."
    if name == "gravity":
        d, pred = args[0], args[1]
        direction = {
            "left": {"en": "left", "zh": "左"},
            "right": {"en": "right", "zh": "右"},
            "up": {"en": "up", "zh": "上"},
            "down": {"en": "down", "zh": "下"},
            "away-from-marker": {"en": "away from the border marker", "zh": "远离边界标记"},
        }.get(d, {"en": d, "zh": d})[lang]
        if lang == "zh":
            return f"让所有{pred_text(pred, lang)}向{direction}滑动，直到碰上其他物体或边界。"
        return f"Let {pred_text(pred, lang)} slide {direction} until they hit another object or the border."
    if name == "rays":
        pred, mode = args[0], args[1]
        modes = {
            "left+right": {"en": "left and right", "zh": "左右两侧"},
            "up+down": {"en": "up and down", "zh": "上下两侧"},
            "away-from-marker": {"en": "away from the border marker", "zh": "远离边界标记"},
            "left": {"en": "left", "zh": "左"},
            "right": {"en": "right", "zh": "右"},
            "up": {"en": "up", "zh": "上"},
            "down": {"en": "down", "zh": "下"},
        }
        m = modes.get(mode, {"en": mode, "zh": mode})[lang]
        if lang == "zh":
            return f"从每一个单格的{pred_text(pred, lang)}向{m}射出光线，沿着空格子一直画到被挡住为止。"
        return f"From every single-cell object among {pred_text(pred, lang)}, paint a ray {m} through empty cells until blocked."
    if name == "fill":
        c = int(args[0])
        if lang == "zh":
            return f"用{color_name(c, lang)}填满每个物体内部封闭的洞。"
        return f"Fill every enclosed hole with {color_name(c, lang)}."
    if name == "nearest":
        if lang == "zh":
            return "每一个多格形状都染成离它最近的那颗单格种子的颜色。距离用曼哈顿距离（上下左右）；如果两颗种子一样近，取编号更小的颜色。种子本身不变。"
        return "Each multi-cell shape takes the colour of the nearest single-cell seed. Distance is Manhattan (no diagonals); ties go to the smallest colour number. Seeds stay as they are."
    return rule


def explain_program(rules: list[str], lang: str = "en") -> str:
    if not rules:
        return "The engine has not found a rule yet." if lang == "en" else "引擎还没有找到规则。"
    if len(rules) == 1:
        return explain_rule(rules[0], lang)
    lines = []
    if lang == "zh":
        lines.append(f"这是一个由 {len(rules)} 步组成的短程序，必须按顺序执行：")
        for i, r in enumerate(rules, 1):
            lines.append(f"{i}. {explain_rule(r, lang)}")
    else:
        lines.append(f"This is a short {len(rules)}-step program. Apply the steps in order:")
        for i, r in enumerate(rules, 1):
            lines.append(f"{i}. {explain_rule(r, lang)}")
    return "\n".join(lines)


def _obj_summary(g, use_marker=False):
    mk = marker(g) if use_marker else None
    out = []
    for i, o in enumerate(objs(g, mk), 1):
        r0, c0, r1, c1 = bbox(o)
        h = holes(o)
        out.append(
            {
                "index": i,
                "color": o["color"],
                "size": len(o["cells"]),
                "bbox": [r0, c0, r1, c1],
                "holes": h,
                "touches_edge": any(
                    y in (0, len(g) - 1) or x in (0, len(g[0]) - 1) for y, x in o["cells"]
                ),
                "tall": (r1 - r0) > (c1 - c0),
                "wide": (c1 - c0) > (r1 - r0),
                "solid_rect": len(o["cells"]) == (r1 - r0 + 1) * (c1 - c0 + 1) and len(o["cells"]) >= 2,
            }
        )
    return out


def analyze_examples(examples, use_marker=False, lang: str = "en") -> dict:
    reports = []
    observations = []
    for i, pair in enumerate(examples, 1):
        inp, out = (pair["input"], pair["output"]) if isinstance(pair, dict) else pair
        if (len(inp), len(inp[0])) != (len(out), len(out[0])):
            reports.append({"example": i, "note": "input and output have different sizes"})
            continue
        changes = Counter(
            (inp[r][c], out[r][c])
            for r in range(len(inp))
            for c in range(len(inp[0]))
            if inp[r][c] != out[r][c]
        )
        painted = sum(1 for r in range(len(inp)) for c in range(len(inp[0])) if inp[r][c] == 0 and out[r][c] != 0)
        erased = sum(1 for r in range(len(inp)) for c in range(len(inp[0])) if inp[r][c] != 0 and out[r][c] == 0)
        recoloured = sum(1 for r in range(len(inp)) for c in range(len(inp[0])) if inp[r][c] != 0 and out[r][c] != 0 and inp[r][c] != out[r][c])
        reports.append(
            {
                "example": i,
                "size": [len(inp), len(inp[0])],
                "input_objects": _obj_summary(inp, use_marker),
                "output_objects": _obj_summary(out, use_marker),
                "colour_changes": {f"{a}->{b}": n for (a, b), n in changes.items()},
                "painted": painted,
                "erased": erased,
                "recoloured": recoloured,
            }
        )
    # Cross-example observations
    any_erased = any(r.get("erased", 0) for r in reports)
    any_painted = any(r.get("painted", 0) for r in reports)
    any_recolour = any(r.get("recoloured", 0) for r in reports)
    if lang == "zh":
        if any_erased:
            observations.append("有一些原来非空的格子在输出里变成了背景，说明有物体被删除或移走了。")
        if any_painted:
            observations.append("有一些原来空着的格子被涂上了颜色，说明规则会画出新的格子（比如边框、光线或填洞）。")
        if any_recolour:
            observations.append("有一些物体换了颜色，但位置大致还在，说明规则会按某种属性重新上色。")
        if not observations:
            observations.append("先逐个对比例题：哪些物体变了，哪些没变，变的是颜色、位置还是形状。")
    else:
        if any_erased:
            observations.append("Some non-empty cells become background, so objects are being deleted or moved.")
        if any_painted:
            observations.append("Some empty cells gain colour, so the rule paints new cells (a frame, a ray, or a filled hole).")
        if any_recolour:
            observations.append("Some objects change colour but stay roughly in place, so the rule recolours them by a property.")
        if not observations:
            observations.append("Compare each example: which objects change, and do they change colour, position, or shape?")
    return {"examples": reports, "observations": observations}


def apply_steps(rules, grid, use_marker=False) -> list[dict]:
    steps = run_steps(rules, grid, use_marker)
    out = [{"label": "start", "rule": None, "explanation_en": "Original grid.", "explanation_zh": "原始网格。", "grid": steps[0]}]
    for i, rule in enumerate(rules):
        out.append(
            {
                "label": f"step {i + 1}",
                "rule": rule,
                "explanation_en": explain_rule(rule, "en"),
                "explanation_zh": explain_rule(rule, "zh"),
                "grid": steps[i + 1],
            }
        )
    return out


def check_attempt(expected, attempt) -> dict:
    if not attempt or not expected:
        return {"correct": False, "error": "Missing grid"}
    if len(attempt) != len(expected) or any(len(r) != len(expected[0]) for r in attempt):
        return {"correct": False, "error": "The attempt does not match the test grid size."}
    wrong = [
        [r, c]
        for r in range(len(expected))
        for c in range(len(expected[0]))
        if int(attempt[r][c]) != expected[r][c]
    ]
    total = len(expected) * len(expected[0])
    if not wrong:
        return {"correct": True, "wrong_count": 0, "total": total, "accuracy": 1.0}
    # Regional hint without dumping the solution
    r, c = wrong[0]
    return {
        "correct": False,
        "wrong_count": len(wrong),
        "total": total,
        "accuracy": round((total - len(wrong)) / total, 3),
        "focus": {"row": r, "col": c},
        "hint_en": f"{len(wrong)} cell(s) still differ. Look again around row {r + 1}, column {c + 1} (1-based).",
        "hint_zh": f"还有 {len(wrong)} 格不对。请再看第 {r + 1} 行、第 {c + 1} 列附近（行列从 1 开始）。",
    }


def generic_hints(analysis: dict, lang: str = "en") -> list[str]:
    obs = analysis.get("observations") or []
    if lang == "zh":
        base = obs or ["先仔细对比每组例题的输入和输出，找出所有变化的格子。"]
        base.append("试着把物体按属性分类：大小、是否靠边、有没有洞、高还是宽。看看哪一类总是发生同样的变化。")
        base.append("当你觉得自己找到规则时，先在每一组例题上检查一遍，再应用到测试题。")
    else:
        base = obs or ["Carefully compare each example's input and output and mark every cell that changes."]
        base.append("Group objects by a property — size, touching the border, holes, tall vs wide — and see which group always changes the same way.")
        base.append("When you think you have the rule, check it on every example before you apply it to the test grid.")
    return base


def build_session_hints(puzzle: dict, lang: str = "en") -> list[dict]:
    authored = puzzle.get("hints") or []
    hints = []
    for i, h in enumerate(authored, 1):
        text = h.get(lang) or h.get("en") or ""
        hints.append({"level": i, "kind": "hint", "text": text, "en": h.get("en"), "zh": h.get("zh")})
    if not hints:
        analysis = analyze_examples(puzzle["examples"], puzzle.get("use_marker", False), lang)
        for i, text in enumerate(generic_hints(analysis, lang), 1):
            hints.append({"level": i, "kind": "hint", "text": text})
    rules = puzzle.get("rules") or []
    if rules:
        hints.append(
            {
                "level": len(hints) + 1,
                "kind": "rule",
                "text": explain_program(rules, lang),
                "en": explain_program(rules, "en"),
                "zh": explain_program(rules, "zh"),
                "rules": rules,
            }
        )
    return hints
