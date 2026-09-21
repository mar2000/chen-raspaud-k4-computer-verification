from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, FrozenSet, Iterable, List, Sequence, Tuple

from .admissible import admissible_from_color
from .kneser94 import Color, all_colors, intersection_size
from .states_deg3 import admissible_center_two_relatives

State = Tuple[int, int, int]  # (a, b, r)


@dataclass(frozen=True)
class StateRealization:
    x: Color
    y: Color
    admissible_centers: FrozenSet[Color]


@lru_cache(maxsize=None)
def realizations_of_state(a: int, b: int, r: int) -> Tuple[StateRealization, ...]:
    """
    Enumerate all ordered pairs (x,y) with |x ∩ y| = r and record
    U_{a,b}(x,y) = A_a(x) ∩ A_b(y), keeping only realizable ones.
    """
    out: List[StateRealization] = []
    colors = all_colors()

    for x in colors:
        ax = admissible_from_color(x, a)
        for y in colors:
            if intersection_size(x, y) != r:
                continue
            centers = ax & admissible_from_color(y, b)
            if centers:
                out.append(
                    StateRealization(
                        x=x,
                        y=y,
                        admissible_centers=frozenset(centers),
                    )
                )
    return tuple(out)


@lru_cache(maxsize=None)
def canonical_realization_of_state(a: int, b: int, r: int) -> StateRealization:
    """
    Return one fixed realization of the state.
    By symmetry, this is enough on one side when testing universal compatibility.
    """
    reals = realizations_of_state(a, b, r)
    if not reals:
        raise ValueError(f"State ({a},{b};{r}) is not realizable")
    return reals[0]


@lru_cache(maxsize=None)
def reachable_from_realization_centers(
    a: int, b: int, r: int, m: int
) -> FrozenSet[Color]:
    """
    For the canonical realization of state (a,b;r), compute
    union_{s in U_{a,b}} A_m(s).
    Then a right-hand realization is compatible iff its admissible center set
    intersects this union.
    """
    real = canonical_realization_of_state(a, b, r)
    out = set()
    for s in real.admissible_centers:
        out.update(admissible_from_color(s, m))
    return frozenset(out)


@lru_cache(maxsize=None)
def state_pair_is_compatible(
    a: int, b: int, r: int,
    c: int, d: int, s: int,
    m: int,
) -> bool:
    """
    Check whether state (a,b;r) is universally compatible with state (c,d;s)
    through a thread of length m.

    By symmetry, it is enough to fix one canonical realization of the left state
    and test all realizations of the right state.
    """
    left_reachable = reachable_from_realization_centers(a, b, r, m)
    right_reals = realizations_of_state(c, d, s)

    if not right_reals:
        raise ValueError(
            f"Trying to test compatibility with a non-realizable state ({c},{d};{s})"
        )

    for right in right_reals:
        if not (right.admissible_centers & left_reachable):
            return False
    return True


@lru_cache(maxsize=None)
def first_incompatibility_certificate(
    a: int, b: int, r: int,
    c: int, d: int, s: int,
    m: int,
) -> tuple[StateRealization, StateRealization] | None:
    """
    Return one witness pair:
    - the canonical realization of the left state,
    - a realization of the right state incompatible with it,
    if such exists.
    """
    left = canonical_realization_of_state(a, b, r)
    left_reachable = reachable_from_realization_centers(a, b, r, m)
    right_reals = realizations_of_state(c, d, s)

    for right in right_reals:
        if not (right.admissible_centers & left_reachable):
            return (left, right)
    return None


def realizable_states_for_pairs(pairs: Iterable[Tuple[int, int]]) -> List[State]:
    out: List[State] = []
    for a, b in pairs:
        for r in range(5):
            if realizations_of_state(a, b, r):
                out.append((a, b, r))
    return out


def incompatible_pairs(
    states: Sequence[State],
    m: int,
    symmetric: bool = True,
) -> List[Tuple[State, State]]:
    out: List[Tuple[State, State]] = []
    for i, ls in enumerate(states):
        start = i if symmetric else 0
        for j in range(start, len(states)):
            rs = states[j]
            if not state_pair_is_compatible(*ls, *rs, m):
                out.append((ls, rs))
    return out


def format_state(state: State) -> str:
    a, b, r = state
    return f"({a},{b};{r})"


def format_incompatible_pairs_latex(
    pairs: Sequence[Tuple[State, State]], m: int
) -> str:
    lines = [f"% Incompatible state pairs through a thread of length {m}"]
    lines.append(r"\begin{itemize}")
    for left, right in pairs:
        lines.append(
            rf"\item ${format_state(left)}$ and ${format_state(right)}$ are not {m}-compatible."
        )
    lines.append(r"\end{itemize}")
    return "\n".join(lines)
