from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from typing import Dict, FrozenSet, Iterable, List, Tuple

from .admissible import admissible_from_color
from .kneser94 import Color, all_colors, intersection_size

StateKey = Tuple[int, int, int]  # (a, b, r)


def admissible_center_two_relatives(x: Color, y: Color, a: int, b: int) -> FrozenSet[Color]:
    return frozenset(admissible_from_color(x, a) & admissible_from_color(y, b))


def state_size(x: Color, y: Color, a: int, b: int) -> int:
    return len(admissible_center_two_relatives(x, y, a, b))


@lru_cache(maxsize=None)
def table_N_for_pair(a: int, b: int) -> Dict[int, int]:
    """
    Returns r -> N(a,b;r), assuming the value depends only on |x ∩ y|.
    Checks consistency across all pairs (x,y) with the same intersection size.
    """
    values: Dict[int, int] = {}
    seen: Dict[int, int] = {}
    colors = all_colors()

    for x in colors:
        for y in colors:
            r = intersection_size(x, y)
            val = state_size(x, y, a, b)
            if r in seen and seen[r] != val:
                raise AssertionError(
                    f"Inconsistency for (a,b)=({a},{b}), r={r}: got both {seen[r]} and {val}"
                )
            seen[r] = val

    for r in range(5):
        values[r] = seen[r]
    return values


def table_N_for_pairs(pairs: Iterable[Tuple[int, int]]) -> Dict[Tuple[int, int], Dict[int, int]]:
    return {(a, b): table_N_for_pair(a, b) for (a, b) in pairs}


DEFAULT_DEG3_PAIRS: Tuple[Tuple[int, int], ...] = (
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (3, 3),
)


def format_table_for_latex(table: Dict[Tuple[int, int], Dict[int, int]]) -> str:
    lines = []
    lines.append(r"\begin{array}{c|ccccc}")
    lines.append(r"(a,b) & r=0 & r=1 & r=2 & r=3 & r=4\\")
    lines.append(r"\hline")
    for (a, b) in sorted(table):
        row = table[(a, b)]
        lines.append(
            f"({a},{b}) & {row[0]} & {row[1]} & {row[2]} & {row[3]} & {row[4]}\\\\"
        )
    lines.append(r"\end{array}")
    return "\n".join(lines)
