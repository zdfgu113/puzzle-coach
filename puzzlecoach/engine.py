"""ARC-style grid transformation engine.

Grids are lists of lists of ints. 0 is background; 1-9 are colours.
Objects are same-colour 4-connected components.

The operator and predicate vocabulary was built for inductive grid puzzles:
the engine applies a short program (a sequence of named rules) to a grid.
Puzzle Coach searches for such a program from input/output examples, then
explains it in plain language instead of only emitting a solved grid.
"""
from __future__ import annotations

import re

def parse(txt):
    """Parse a text puzzle with 'Example N input/output' and 'Test input' blocks."""
    blocks = re.findall(
        r"(Example \d+ (?:input|output)|Test input) \((\d+) rows x (\d+) cols\):\n([\d\n]+)",
        txt,
    )
    G = {k: [list(map(int, l)) for l in b.split()] for k, _, _, b in blocks}
    n = len([k for k in G if k.endswith("input") and k.startswith("Example")])
    examples = [(G[f"Example {i} input"], G[f"Example {i} output"]) for i in range(1, n + 1)]
    test = G.get("Test input")
    return examples, test


def s(g):
    return "/".join("".join(map(str, r)) for r in g)


def grid_copy(g):
    return [r[:] for r in g]


def dims(g):
    return len(g), len(g[0]) if g else 0


def comps(g, skip=None):
    H, W = len(g), len(g[0])
    seen = set()
    out = []
    for r in range(H):
        for c in range(W):
            if g[r][c] and (r, c) not in seen and (skip is None or (r, c) not in skip):
                col = g[r][c]
                st = [(r, c)]
                seen.add((r, c))
                cells = []
                while st:
                    y, x = st.pop()
                    cells.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        p = (y + dy, x + dx)
                        if (
                            0 <= p[0] < H
                            and 0 <= p[1] < W
                            and p not in seen
                            and g[p[0]][p[1]] == col
                            and (skip is None or p not in skip)
                        ):
                            seen.add(p)
                            st.append(p)
                out.append({"color": col, "cells": cells})
    return out


def bbox(o):
    ys = [y for y, _ in o["cells"]]
    xs = [x for _, x in o["cells"]]
    return min(ys), min(xs), max(ys), max(xs)


# Marker cell used as a wall when counting holes (some puzzles place a
# border marker that should close a frame). Set by run().
MK = [None]
MKC = [None]
SYM_MODE = "lr"
NEAREST_METRIC = ["man"]  # Manhattan; ties -> smallest colour


def holes(o):
    r0, c0, r1, c1 = bbox(o)
    cs = set(o["cells"])
    mk = MK[0]
    if mk is not None and r0 - 1 <= mk[0] <= r1 + 1 and c0 - 1 <= mk[1] <= c1 + 1:
        cs = cs | {mk}
        # H, W unused; kept for parity with the original semantics
        _H, _W = r1 - r0 + 3, c1 - c0 + 3
    free = {
        (y, x)
        for y in range(r0 - 1, r1 + 2)
        for x in range(c0 - 1, c1 + 2)
        if (y, x) not in cs
    }
    st = [(r0 - 1, c0 - 1)]
    out = {st[0]}
    while st:
        y, x = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (y + dy, x + dx)
            if p in free and p not in out:
                out.add(p)
                st.append(p)
    inner = free - out
    n = 0
    while inner:
        n += 1
        st = [inner.pop()]
        while st:
            y, x = st.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (y + dy, x + dx)
                if p in inner:
                    inner.remove(p)
                    st.append(p)
    return n


def sym(o):
    cs = set(o["cells"])
    r0, c0, r1, c1 = bbox(o)
    lr = {(y, c0 + c1 - x) for y, x in cs} == cs
    ud = {(r0 + r1 - y, x) for y, x in cs} == cs
    return lr if SYM_MODE == "lr" else ud if SYM_MODE == "ud" else (lr or ud)


def marker(g):
    H, W = len(g), len(g[0])
    b = [
        (r, c)
        for r in range(H)
        for c in range(W)
        if (r in (0, H - 1) or c in (0, W - 1)) and g[r][c]
    ]
    return b[0] if len(b) == 1 else None


def objs(g, mk=None):
    return [o for o in comps(g, skip={mk} if mk else None)]


PRED = {
    "solid-rect": lambda o, g: (
        lambda b: len(o["cells"]) == (b[2] - b[0] + 1) * (b[3] - b[1] + 1)
        and len(o["cells"]) >= 2
    )(bbox(o)),
    "wide": lambda o, g: (lambda b: b[3] - b[1] > b[2] - b[0])(bbox(o)),
    "tall": lambda o, g: (lambda b: b[2] - b[0] > b[3] - b[1])(bbox(o)),
    "touches-edge": lambda o, g: any(
        y in (0, len(g) - 1) or x in (0, len(g[0]) - 1) for y, x in o["cells"]
    ),
    "two-holes": lambda o, g: holes(o) >= 2,
    "asym": lambda o, g: not sym(o),
    "mirror-sym": lambda o, g: len(o["cells"]) > 1 and sym(o),
    "all": lambda o, g: True,
    "multi": lambda o, g: len(o["cells"]) > 1,
    "size-2": lambda o, g: len(o["cells"]) == 2,
    "size-4": lambda o, g: len(o["cells"]) == 4,
    "size-3": lambda o, g: len(o["cells"]) == 3,
    "size-1": lambda o, g: len(o["cells"]) == 1,
    "even-size": lambda o, g: len(o["cells"]) % 2 == 0,
    "has-hole": lambda o, g: holes(o) >= 1,
    "no-hole": lambda o, g: holes(o) == 0,
    "one-hole": lambda o, g: holes(o) == 1,
    "largest": lambda o, g: len(o["cells"]) == max(len(p["cells"]) for p in objs(g, MK[0])),
    "unique-color": lambda o, g: sum(p["color"] == o["color"] for p in objs(g, MK[0])) == 1,
    "shared-color": lambda o, g: sum(p["color"] == o["color"] for p in objs(g, MK[0])) > 1,
    "marker-color": lambda o, g: MK[0] is not None and o["color"] == MKC[0],
    "not-marker-color": lambda o, g: MK[0] is not None and o["color"] != MKC[0],
}
for k in range(1, 10):
    PRED[f"color-{k}"] = (lambda k: lambda o, g: o["color"] == k)(k)


def op_recolor_holes(g, a, b, mk=None):
    g = grid_copy(g)
    for o in objs(g, mk):
        h = holes(o)
        c = a if h == 1 else b if h >= 2 else None
        if c:
            for y, x in o["cells"]:
                g[y][x] = c
    return g


def op_recolor(g, pred, c, mk=None):
    g2 = grid_copy(g)
    for o in objs(g, mk):
        if PRED[pred](o, g):
            for y, x in o["cells"]:
                g2[y][x] = c
    return g2


def op_delete(g, pred, mk=None):
    g2 = grid_copy(g)
    for o in objs(g, mk):
        if PRED[pred](o, g):
            for y, x in o["cells"]:
                g2[y][x] = 0
    return g2


def op_frame(g, pred, c, mk=None):
    g2 = grid_copy(g)
    H, W = len(g), len(g[0])
    for o in objs(g, mk):
        if PRED[pred](o, g):
            r0, c0, r1, c1 = bbox(o)
            for y in range(r0 - 1, r1 + 2):
                for x in range(c0 - 1, c1 + 2):
                    if 0 <= y < H and 0 <= x < W and not (r0 <= y <= r1 and c0 <= x <= c1) and g2[y][x] == 0:
                        g2[y][x] = c
    return g2


D = {"left": (0, -1), "right": (0, 1), "up": (-1, 0), "down": (1, 0)}


def away(g, mk):
    H, W = len(g), len(g[0])
    y, x = mk
    return "down" if y == 0 else "up" if y == H - 1 else "right" if x == 0 else "left"


def op_gravity(g, d, pred, mk=None):
    if d == "away-from-marker":
        d = away(g, mk)
    dy, dx = D[d]
    g = grid_copy(g)
    H, W = len(g), len(g[0])
    os_ = [o for o in objs(g, mk) if PRED[pred](o, g)]
    key = lambda o: -max(y * dy + x * dx for y, x in o["cells"])
    for o in sorted(os_, key=key):
        cs = set(o["cells"])
        for y, x in cs:
            g[y][x] = 0
        k = 0
        while all(
            0 <= y + (k + 1) * dy < H
            and 0 <= x + (k + 1) * dx < W
            and g[y + (k + 1) * dy][x + (k + 1) * dx] == 0
            for y, x in cs
        ):
            k += 1
        for y, x in cs:
            g[y + k * dy][x + k * dx] = o["color"]
    return g


def op_rays(g, sel, mode, mk=None):
    g2 = grid_copy(g)
    H, W = len(g), len(g[0])
    for o in objs(g, mk):
        if len(o["cells"]) != 1 or not PRED[sel](o, g):
            continue
        y, x = o["cells"][0]
        dirs = (
            ["left", "right"]
            if mode == "left+right"
            else ["up", "down"]
            if mode == "up+down"
            else [away(g, mk)]
            if mode == "away-from-marker"
            else [mode]
        )
        for d in dirs:
            dy, dx = D[d]
            yy, xx = y + dy, x + dx
            while 0 <= yy < H and 0 <= xx < W and g[yy][xx] == 0:
                g2[yy][xx] = o["color"]
                yy += dy
                xx += dx
    return g2


def op_fill(g, c, mk=None):
    """Fill enclosed background holes of every object with colour c."""
    g2 = grid_copy(g)
    for o in objs(g, mk):
        r0, c0, r1, c1 = bbox(o)
        cs = set(o["cells"])
        free = {
            (y, x)
            for y in range(r0 - 1, r1 + 2)
            for x in range(c0 - 1, c1 + 2)
            if (y, x) not in cs
        }
        st = [(r0 - 1, c0 - 1)]
        out = {st[0]}
        while st:
            y, x = st.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (y + dy, x + dx)
                if q in free and q not in out:
                    out.add(q)
                    st.append(q)
        for y, x in free - out:
            if 0 <= y < len(g2) and 0 <= x < len(g2[0]) and g2[y][x] == 0:
                g2[y][x] = c
    return g2


def op_nearest(g, mode, mk=None):
    """Each multi-cell shape takes the colour of its nearest single-cell dot.

    Distance is Manhattan (cell-to-cell). A tie between dots of different
    colours resolves to the smallest colour. Dots themselves stay put.
    """
    g2 = grid_copy(g)
    os_ = objs(g, mk)
    dots = [o for o in os_ if len(o["cells"]) == 1]
    shapes = [o for o in os_ if len(o["cells"]) > 1]
    if not dots:
        return g2
    for o in shapes:
        def dist(d, o=o):
            dyx = d["cells"][0]
            if NEAREST_METRIC[0] == "man":
                return min(abs(dyx[0] - y) + abs(dyx[1] - x) for y, x in o["cells"])
            return min((dyx[0] - y) ** 2 + (dyx[1] - x) ** 2 for y, x in o["cells"])

        m = min(map(dist, dots))
        cols = {d["color"] for d in dots if dist(d) == m}
        c = min(cols)
        for y, x in o["cells"]:
            g2[y][x] = c
    return g2


def parse_rule(r):
    name, args = re.match(r"([\w-]+)\((.*)\)", r).groups()
    a = args.split(",")
    if name == "recolor-holes":
        x, y = a
        return lambda g, mk=None, x=x, y=y: op_recolor_holes(
            g, int(x.split("->")[1]), int(y.split("->")[1]), mk
        )
    if name in ("recolor", "frame"):
        p, c = a[0].split("->")
        f = op_recolor if name == "recolor" else op_frame
        return lambda g, mk=None, f=f, p=p, c=c: f(g, p, int(c), mk)
    if name == "delete":
        return lambda g, mk=None, p=a[0]: op_delete(g, p, mk)
    if name == "gravity":
        return lambda g, mk=None, d=a[0], p=a[1]: op_gravity(g, d, p, mk)
    if name == "rays":
        return lambda g, mk=None, p=a[0], m=a[1]: op_rays(g, p, m, mk)
    if name == "fill":
        return lambda g, mk=None, c=int(a[0]): op_fill(g, c, mk)
    if name == "nearest":
        return lambda g, mk=None: op_nearest(g, a[0], mk)
    raise ValueError(r)


def run(rules, g, use_marker=False):
    mk = marker(g) if use_marker else None
    MK[0] = mk
    MKC[0] = g[mk[0]][mk[1]] if mk else None
    for r in rules:
        g = parse_rule(r)(g, mk)
    return g


def run_steps(rules, g, use_marker=False):
    """Apply rules one at a time and return the grid after each step (including the start)."""
    mk = marker(g) if use_marker else None
    MK[0] = mk
    MKC[0] = g[mk[0]][mk[1]] if mk else None
    steps = [grid_copy(g)]
    for r in rules:
        g = parse_rule(r)(g, mk)
        steps.append(grid_copy(g))
    return steps
