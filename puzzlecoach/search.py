"""Beam search over short rule programs, scored on the training examples.

This is the symbolic AI at the heart of Puzzle Coach: it enumerates a
vocabulary of grid operators, keeps the programs that shrink the cell-wise
error on the examples, and only accepts a program when every training
pair matches exactly. The test grid is never used to pick the program.
"""
from __future__ import annotations

import itertools
import time
from typing import Callable, Iterable

from .engine import marker, parse_rule, run, s as serialize

TraceFn = Callable[[str], None]


def cell_diff(a, b) -> int:
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def candidates(examples, marker_mode: bool) -> list[str]:
    inc = {v for i, _ in examples for r in i for v in r}
    outc = {v for _, o in examples for r in o for v in r}
    cols = sorted((outc | inc) - {0})
    preds = [
        "solid-rect",
        "wide",
        "tall",
        "touches-edge",
        "two-holes",
        "asym",
        "mirror-sym",
        "all",
        "multi",
        "size-1",
        "size-2",
        "size-3",
        "size-4",
        "even-size",
        "has-hole",
        "no-hole",
        "one-hole",
        "largest",
        "unique-color",
        "shared-color",
    ]
    if marker_mode:
        preds += ["marker-color", "not-marker-color"]
    preds += [f"color-{k}" for k in sorted(inc - {0})]
    dirs = ["left", "right", "up", "down"]
    if marker_mode:
        dirs += ["away-from-marker"]
    C = []
    for a in cols:
        for b in cols:
            if a != b:
                C.append(f"recolor-holes(1->{a},2+->{b})")
    for p in preds:
        for c in cols:
            C.append(f"recolor({p}->{c})")
            C.append(f"frame({p}->{c})")
        C.append(f"delete({p})")
        for d in dirs:
            C.append(f"gravity({d},{p})")
    for p in ["all"] + [f"color-{k}" for k in sorted(inc - {0})]:
        for m in ["left+right", "up+down"] + dirs:
            C.append(f"rays({p},{m})")
    for c in cols:
        C.append(f"fill({c})")
    C.append("nearest(shapes-take)")
    return C


def _exact(seq, examples, marker_mode) -> bool:
    for inp, out in examples:
        try:
            g = run(seq, inp, marker_mode)
        except Exception:
            return False
        if cell_diff(g, out):
            return False
    return True


def search_rules(
    examples,
    test=None,
    marker_mode: bool = False,
    beam: int = 50,
    depth: int = 4,
    timeout: float = 25.0,
    trace: TraceFn | None = None,
) -> dict:
    """Return verified rule sequences that fit every example.

    `examples` is a list of (input, output) grid pairs. `test` is optional and
    only used to report the implied test output of each solution — it does not
    guide the search.
    """
    log: list[str] = []

    def say(msg: str):
        log.append(msg)
        if trace:
            trace(msg)

    t0 = time.time()
    C = candidates(examples, marker_mode)
    F = {}
    for c in C:
        try:
            F[c] = parse_rule(c)
        except Exception:
            continue
    mks = [marker(i) if marker_mode else None for i, _ in examples]
    beam_state: list[tuple[tuple[str, ...], list]] = [((), [i for i, _ in examples])]
    sols: list[tuple[str, ...]] = []
    say(f"Searching {len(C)} candidate rules, beam={beam}, max depth={depth}.")

    def expand(seq, gs):
        used = {r.split("(")[0] for r in seq}
        out = []
        found = []
        for c, fn in F.items():
            if c.split("(")[0] in used:
                continue
            try:
                ng = [fn(g, mk) for g, mk in zip(gs, mks)]
            except Exception:
                continue
            if all(n == g for n, g in zip(ng, gs)):
                continue
            sc = sum(cell_diff(n, o) for n, (_, o) in zip(ng, examples))
            item = (sc, seq + (c,), ng)
            out.append(item)
            if sc == 0:
                found.append(seq + (c,))
        out.sort(key=lambda x: x[0])
        return out[: beam * 2], found

    for d in range(depth):
        if time.time() - t0 > timeout:
            say("Search stopped: time limit reached.")
            break
        nxt = []
        for seq, gs in beam_state:
            if time.time() - t0 > timeout:
                break
            top, found = expand(seq, gs)
            nxt.extend(top)
            sols.extend(found)
        if sols:
            say(f"Depth {d + 1}: found {len(sols)} exact program(s) in {time.time() - t0:.1f}s.")
            break
        nxt.sort(key=lambda x: x[0])
        seen = set()
        beam_state = []
        for sc, seq, ng in nxt:
            k = str(ng)
            if k in seen:
                continue
            seen.add(k)
            beam_state.append((seq, ng))
            if len(beam_state) >= beam:
                break
        best = nxt[0][0] if nxt else None
        best_seq = nxt[0][1] if nxt else ()
        say(f"Depth {d + 1}: best leftover error {best} via {list(best_seq)} ({time.time() - t0:.1f}s).")
        # Greedy order can be wrong; try permutations of the top sequences.
        for seq, _ in beam_state[:12]:
            if len(seq) < 2:
                continue
            for p in itertools.permutations(seq):
                if _exact(p, examples, marker_mode):
                    sols.append(p)
        if sols:
            say(f"Order repair found {len(sols)} exact program(s).")
            break

    # Deduplicate while preserving order
    uniq: list[tuple[str, ...]] = []
    seen_s = set()
    for sq in sols:
        if sq not in seen_s:
            seen_s.add(sq)
            uniq.append(sq)

    answers = []
    for sq in uniq:
        item = {"rules": list(sq)}
        if test is not None:
            try:
                item["test_output"] = run(sq, test, marker_mode)
                item["test_key"] = serialize(item["test_output"])
            except Exception as exc:
                item["error"] = str(exc)
        answers.append(item)

    return {
        "solutions": answers,
        "elapsed": round(time.time() - t0, 3),
        "candidates": len(C),
        "log": log,
        "solved": bool(answers),
    }
