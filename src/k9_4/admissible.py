from __future__ import annotations

from functools import lru_cache
from typing import Dict, FrozenSet, Iterable, Set

from .kneser94 import Color, all_colors, neighbors


@lru_cache(maxsize=None)
def admissible_from_color(x: Color, length: int) -> FrozenSet[Color]:
    """
    A_length(x): colors reachable from x by a walk of exactly given length.
    """
    if length < 0:
        raise ValueError("length must be nonnegative")
    if length == 0:
        return frozenset({x})

    current: Set[Color] = {x}
    for _ in range(length):
        nxt: Set[Color] = set()
        for c in current:
            nxt.update(neighbors(c))
        current = nxt
    return frozenset(current)


@lru_cache(maxsize=None)
def forbidden_from_color(x: Color, length: int) -> FrozenSet[Color]:
    colors = set(all_colors())
    return frozenset(colors - set(admissible_from_color(x, length)))


def admissible_sizes(length: int) -> Dict[Color, int]:
    return {x: len(admissible_from_color(x, length)) for x in all_colors()}


def forbidden_sizes(length: int) -> Dict[Color, int]:
    return {x: len(forbidden_from_color(x, length)) for x in all_colors()}


def admissible_cardinality(length: int) -> int:
    """
    Since K(9,4) is vertex-transitive, the size does not depend on x.
    """
    x = all_colors()[0]
    return len(admissible_from_color(x, length))


def forbidden_cardinality(length: int) -> int:
    x = all_colors()[0]
    return len(forbidden_from_color(x, length))
