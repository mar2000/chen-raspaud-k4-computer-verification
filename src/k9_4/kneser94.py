from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, List, Set, Tuple

Color = FrozenSet[int]


def normalize_color(vertices: Iterable[int]) -> Color:
    color = frozenset(vertices)
    if len(color) != 4:
        raise ValueError(f"Color must have size 4, got {sorted(color)}")
    if any(v < 0 or v > 8 for v in color):
        raise ValueError(f"Color must be a 4-subset of [0..8], got {sorted(color)}")
    return color


@lru_cache(maxsize=1)
def all_colors() -> Tuple[Color, ...]:
    return tuple(frozenset(c) for c in combinations(range(9), 4))


def intersection_size(x: Color, y: Color) -> int:
    return len(x & y)


def are_adjacent(x: Color, y: Color) -> bool:
    return len(x & y) == 0


@lru_cache(maxsize=1)
def adjacency_dict() -> Dict[Color, FrozenSet[Color]]:
    colors = all_colors()
    adj: Dict[Color, Set[Color]] = {c: set() for c in colors}
    for i, x in enumerate(colors):
        for y in colors[i + 1 :]:
            if are_adjacent(x, y):
                adj[x].add(y)
                adj[y].add(x)
    return {k: frozenset(v) for k, v in adj.items()}


def neighbors(x: Color) -> FrozenSet[Color]:
    return adjacency_dict()[x]


def color_to_bitmask(x: Color) -> int:
    mask = 0
    for v in x:
        mask |= 1 << v
    return mask


def bitmask_to_color(mask: int) -> Color:
    verts = [i for i in range(9) if (mask >> i) & 1]
    return normalize_color(verts)


@dataclass(frozen=True)
class Kneser94:
    colors: Tuple[Color, ...]
    adjacency: Dict[Color, FrozenSet[Color]]

    @classmethod
    def build(cls) -> "Kneser94":
        return cls(colors=all_colors(), adjacency=adjacency_dict())

    def degree(self, x: Color) -> int:
        return len(self.adjacency[x])

    def common_neighbors(self, x: Color, y: Color) -> FrozenSet[Color]:
        return frozenset(self.adjacency[x] & self.adjacency[y])
