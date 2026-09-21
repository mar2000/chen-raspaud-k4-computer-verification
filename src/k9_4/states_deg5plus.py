from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

LengthTuple = Tuple[int, ...]


@dataclass(frozen=True)
class CandidateType:
    degree: int
    lengths: LengthTuple
    excess: int


def local_excess(lengths: Sequence[int]) -> int:
    """
    For a vertex of degree d with incident thread lengths lengths,
    the local excess is

        sum(lengths) - 9*d + 18.

    This matches the formulas used in the paper:
      d=4: sum - 18
      d=5: sum - 27
      d=6: sum - 36
      d=7: sum - 45
      ...
    """
    d = len(lengths)
    return sum(lengths) - 9 * d + 18


def generate_ordered_types(
    degree: int,
    min_len: int = 1,
    max_len: int = 7,
    shortest_at_most: int | None = 4,
) -> List[LengthTuple]:
    """
    Generate all nondecreasing tuples (a1,...,ad) with
        min_len <= a1 <= ... <= ad <= max_len
    and optionally a1 <= shortest_at_most.
    """
    out: List[LengthTuple] = []

    def rec(prefix: List[int], last: int) -> None:
        if len(prefix) == degree:
            tpl = tuple(prefix)
            if shortest_at_most is None or tpl[0] <= shortest_at_most:
                out.append(tpl)
            return

        for x in range(last, max_len + 1):
            prefix.append(x)
            rec(prefix, x)
            prefix.pop()

    for first in range(min_len, max_len + 1):
        rec([first], first)

    if shortest_at_most is not None:
        out = [tpl for tpl in out if tpl[0] <= shortest_at_most]

    return out


def all_types_with_excess(
    degree: int,
    min_len: int = 1,
    max_len: int = 7,
    shortest_at_most: int | None = 4,
) -> List[CandidateType]:
    return [
        CandidateType(degree=degree, lengths=tpl, excess=local_excess(tpl))
        for tpl in generate_ordered_types(
            degree=degree,
            min_len=min_len,
            max_len=max_len,
            shortest_at_most=shortest_at_most,
        )
    ]


def positive_candidates(
    degree: int,
    min_len: int = 1,
    max_len: int = 7,
    shortest_at_most: int | None = 4,
) -> List[CandidateType]:
    return [
        c for c in all_types_with_excess(
            degree=degree,
            min_len=min_len,
            max_len=max_len,
            shortest_at_most=shortest_at_most,
        )
        if c.excess > 0
    ]


def nonnegative_candidates(
    degree: int,
    min_len: int = 1,
    max_len: int = 7,
    shortest_at_most: int | None = 4,
) -> List[CandidateType]:
    return [
        c for c in all_types_with_excess(
            degree=degree,
            min_len=min_len,
            max_len=max_len,
            shortest_at_most=shortest_at_most,
        )
        if c.excess >= 0
    ]


def grouped_positive_candidates(
    degrees: Iterable[int],
    min_len: int = 1,
    max_len: int = 7,
    shortest_at_most: int | None = 4,
) -> Dict[int, List[CandidateType]]:
    return {
        d: positive_candidates(
            d,
            min_len=min_len,
            max_len=max_len,
            shortest_at_most=shortest_at_most,
        )
        for d in degrees
    }


def format_candidate(candidate: CandidateType) -> str:
    return f"{candidate.lengths} (excess={candidate.excess})"


def format_candidates_for_latex(cands: Sequence[CandidateType]) -> str:
    if not cands:
        return r"\emptyset"
    return ",\qquad ".join(
        [f"{cand.lengths}" for cand in cands]
    )


def format_candidates_with_excess_for_latex(cands: Sequence[CandidateType]) -> str:
    if not cands:
        return r"\emptyset"
    return "\n".join(
        [rf"{cand.lengths}\ \text{{with excess}}\ {cand.excess}," for cand in cands]
    )


def summary_by_degree(
    degrees: Iterable[int],
    min_len: int = 1,
    max_len: int = 7,
    shortest_at_most: int | None = 4,
) -> Dict[int, Dict[str, int]]:
    out: Dict[int, Dict[str, int]] = {}
    for d in degrees:
        all_c = all_types_with_excess(
            d,
            min_len=min_len,
            max_len=max_len,
            shortest_at_most=shortest_at_most,
        )
        pos_c = [c for c in all_c if c.excess > 0]
        nonneg_c = [c for c in all_c if c.excess >= 0]
        out[d] = {
            "all": len(all_c),
            "nonnegative": len(nonneg_c),
            "positive": len(pos_c),
        }
    return out
