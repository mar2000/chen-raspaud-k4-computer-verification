from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement
from typing import Dict, FrozenSet, Iterable, List, Sequence, Tuple

from .admissible import admissible_from_color
from .kneser94 import Color, all_colors

LengthTriple = Tuple[int, int, int]


@dataclass(frozen=True)
class TripleRealization:
    x: Color
    y: Color
    z: Color
    admissible_centers: FrozenSet[Color]


def admissible_center_three_relatives(
    x: Color,
    y: Color,
    z: Color,
    a: int,
    b: int,
    c: int,
) -> FrozenSet[Color]:
    """
    Return A_a(x) ∩ A_b(y) ∩ A_c(z).
    """
    return frozenset(
        admissible_from_color(x, a)
        & admissible_from_color(y, b)
        & admissible_from_color(z, c)
    )


@lru_cache(maxsize=None)
def realizations_of_length_triple(a: int, b: int, c: int) -> Tuple[TripleRealization, ...]:
    """
    Enumerate all ordered triples (x,y,z) of colors for which
    A_a(x) ∩ A_b(y) ∩ A_c(z) is nonempty.
    """
    out: List[TripleRealization] = []
    colors = all_colors()

    for x in colors:
        ax = admissible_from_color(x, a)
        for y in colors:
            axy = ax & admissible_from_color(y, b)
            if not axy:
                continue
            for z in colors:
                centers = axy & admissible_from_color(z, c)
                if centers:
                    out.append(
                        TripleRealization(
                            x=x,
                            y=y,
                            z=z,
                            admissible_centers=frozenset(centers),
                        )
                    )
    return tuple(out)


@lru_cache(maxsize=None)
def min_admissible_size_for_triple(a: int, b: int, c: int) -> int:
    """
    Return the minimum of |A_a(x) ∩ A_b(y) ∩ A_c(z)| over all realizable triples (x,y,z),
    i.e. over all triples for which the intersection is nonempty.
    """
    reals = realizations_of_length_triple(a, b, c)
    if not reals:
        raise ValueError(f"No realizable triples for lengths ({a},{b},{c})")
    return min(len(r.admissible_centers) for r in reals)


@lru_cache(maxsize=None)
def first_minimum_witness_for_triple(a: int, b: int, c: int) -> TripleRealization:
    """
    Return one realization attaining the minimum admissible set size.
    """
    reals = realizations_of_length_triple(a, b, c)
    if not reals:
        raise ValueError(f"No realizable triples for lengths ({a},{b},{c})")

    best = min(reals, key=lambda r: len(r.admissible_centers))
    return best


def minima_for_triples(triples: Iterable[LengthTriple]) -> Dict[LengthTriple, int]:
    return {triple: min_admissible_size_for_triple(*triple) for triple in triples}


def witnesses_for_triples(triples: Iterable[LengthTriple]) -> Dict[LengthTriple, TripleRealization]:
    return {triple: first_minimum_witness_for_triple(*triple) for triple in triples}


def format_triple_table_for_latex(table: Dict[LengthTriple, int]) -> str:
    lines: List[str] = []
    lines.append(r"\begin{array}{c|c}")
    lines.append(r"(\ell_1,\ell_2,\ell_3) & \min |A_{\ell_1}(X)\cap A_{\ell_2}(Y)\cap A_{\ell_3}(Z)|\\")
    lines.append(r"\hline")
    for triple in sorted(table):
        val = table[triple]
        lines.append(f"{triple} & {val}\\\\")
    lines.append(r"\end{array}")
    return "\n".join(lines)


def pretty_color(x: Color) -> str:
    return "{" + ",".join(map(str, sorted(x))) + "}"


def witness_to_text(w: TripleRealization) -> str:
    centers_str = ", ".join(pretty_color(c) for c in sorted(w.admissible_centers, key=lambda s: tuple(sorted(s))))
    return (
        f"x={pretty_color(w.x)}, "
        f"y={pretty_color(w.y)}, "
        f"z={pretty_color(w.z)}, "
        f"centers=[{centers_str}]"
    )


# Natural triples for the degree-4 analysis:
# if a vertex has type (a,b,c,d), then for the longest thread d we look at (a,b,c).
DEFAULT_DEG4_TRIPLES: Tuple[LengthTriple, ...] = (
    (1, 1, 1),
    (1, 1, 2),
    (1, 1, 3),
    (1, 1, 4),
    (1, 1, 5),
    (1, 1, 6),
    (1, 1, 7),
    (1, 2, 2),
    (1, 2, 3),
    (1, 2, 4),
    (1, 2, 5),
    (1, 2, 6),
    (1, 2, 7),
    (1, 3, 3),
    (1, 3, 4),
    (1, 3, 5),
    (1, 3, 6),
    (1, 3, 7),
    (1, 4, 4),
    (1, 4, 5),
    (1, 4, 6),
    (1, 4, 7),
    (2, 2, 2),
    (2, 2, 3),
    (2, 2, 4),
    (2, 2, 5),
    (2, 2, 6),
    (2, 2, 7),
    (2, 3, 3),
    (2, 3, 4),
    (2, 3, 5),
    (2, 3, 6),
    (2, 3, 7),
    (2, 4, 4),
    (2, 4, 5),
    (2, 4, 6),
    (2, 4, 7),
    (3, 3, 3),
    (3, 3, 4),
    (3, 3, 5),
    (3, 3, 6),
    (3, 3, 7),
    (3, 4, 4),
    (3, 4, 5),
    (3, 4, 6),
    (3, 4, 7),
    (4, 4, 4),
    (4, 4, 5),
    (4, 4, 6),
    (4, 4, 7),
)


def generate_all_length_triples(max_len: int = 7, min_len: int = 1) -> Tuple[LengthTriple, ...]:
    """
    Utility generator for all nondecreasing triples (a,b,c) with min_len <= a <= b <= c <= max_len.
    """
    out: List[LengthTriple] = []
    for a in range(min_len, max_len + 1):
        for b in range(a, max_len + 1):
            for c in range(b, max_len + 1):
                out.append((a, b, c))
    return tuple(out)
