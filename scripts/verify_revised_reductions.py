"""Verification for the revised Chen--Raspaud k=4 reduction scheme.

Chronology note: this script uses only the K(9,4) local framework already
present in the recovered April-2026 project.  It does not import or encode
any later proof.

It verifies three finite statements used by the revised manuscript:

(P) Positive types.  For degrees 3,...,8, every positive-excess type is
    reducible either by the elementary forbidden-set union bound or by the
    rooted star replacement, except (3,3,4).

(C) Capacity exceptions.  For degrees 4,...,7, every nonpositive type for
    which the number of incident 4-threads exceeds its negative excess is
    reducible by the rooted star replacement.  For degree >=8 the required
    capacity inequality is proved algebraically in the paper.

(D3) Degree-3 support for (3,3,4).  Through a 4-thread, a realizable
    (3,3;r)-state can be incompatible only with states whose two other
    thread lengths are (1,1), (1,2), or (1,3).

The rooted-star test is an exact finite set-cover feasibility problem.
For a fixed root color X, let C=A_a(X).  Each other branch i has endpoint
color Y_i constrained by Y_i in A_{a+a_i}(X).  It forbids
F_{a_i}(Y_i) cap C.  The star fails to extend iff one can choose one allowed
endpoint color on every branch so that these forbidden subsets cover C.
We encode this as a 0--1 feasibility problem and solve it with scipy/HiGHS.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import combinations_with_replacement
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from k9_4.admissible import admissible_from_color, forbidden_from_color
from k9_4.compatibility import realizations_of_state, state_pair_is_compatible
from k9_4.kneser94 import all_colors

COLORS = all_colors()
ROOT_COLOR = COLORS[0]
F_SIZE = {i: len(forbidden_from_color(ROOT_COLOR, i)) for i in range(1, 8)}


def local_excess(lengths: Sequence[int]) -> int:
    d = len(lengths)
    return sum(lengths) - 9 * d + 18


def union_bound_reducible(lengths: Sequence[int]) -> bool:
    """Sufficient condition: union of all forbidden sets has size < 126."""
    return sum(F_SIZE[a] for a in lengths) < len(COLORS)


@lru_cache(maxsize=None)
def rooted_star_has_cover(lengths: tuple[int, ...], root: int = 0) -> bool:
    """Return True iff an obstructing cover exists for this rooted star.

    Thus False means the rooted star replacement universally extends and
    the local type is reducible.
    """
    a = lengths[root]
    center_candidates = tuple(admissible_from_color(ROOT_COLOR, a))

    # One block of variables per non-root branch.  Duplicate forbidden
    # incidence vectors are collapsed; this does not change feasibility.
    branch_options: list[list[tuple[int, ...]]] = []
    for i, ai in enumerate(lengths):
        if i == root:
            continue
        seen: set[tuple[int, ...]] = set()
        for endpoint in admissible_from_color(ROOT_COLOR, a + ai):
            A_endpoint = admissible_from_color(endpoint, ai)
            incidence = tuple(int(c not in A_endpoint) for c in center_candidates)
            seen.add(incidence)
        branch_options.append(sorted(seen))

    offsets: list[tuple[int, int]] = []
    options: list[tuple[int, ...]] = []
    pos = 0
    for block in branch_options:
        options.extend(block)
        offsets.append((pos, pos + len(block)))
        pos += len(block)

    nvar = len(options)
    rows: list[np.ndarray] = []
    lb: list[float] = []
    ub: list[float] = []

    # Exactly one endpoint-pattern is selected on each branch.
    for lo, hi in offsets:
        row = np.zeros(nvar)
        row[lo:hi] = 1.0
        rows.append(row)
        lb.append(1.0)
        ub.append(1.0)

    # Every candidate center color must be forbidden by at least one branch.
    for j in range(len(center_candidates)):
        row = np.array([opt[j] for opt in options], dtype=float)
        rows.append(row)
        lb.append(1.0)
        ub.append(np.inf)

    constraints = LinearConstraint(np.vstack(rows), np.array(lb), np.array(ub))
    result = milp(
        c=np.zeros(nvar),
        integrality=np.ones(nvar),
        bounds=Bounds(0, 1),
        constraints=constraints,
        options={"presolve": True},
    )
    # Feasible = an obstruction exists.  Infeasible = universal extension.
    return bool(result.success)


def rooted_star_reducible(lengths: Sequence[int]) -> bool:
    """Use the shortest incident thread as the root."""
    t = tuple(lengths)
    return not rooted_star_has_cover(t, 0)


def positive_type_audit() -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    for d in range(3, 9):
        threshold = 9 * d - 18
        positive = [
            t for t in combinations_with_replacement(range(1, 8), d)
            if sum(t) > threshold
        ]
        by_union = [t for t in positive if union_bound_reducible(t)]
        need_star = [t for t in positive if t not in by_union]
        star_survivors = [t for t in need_star if not rooted_star_reducible(t)]
        out[d] = {
            "positive": positive,
            "union": by_union,
            "star_tested": need_star,
            "survivors": star_survivors,
        }
    return out


def capacity_exception_audit() -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    for d in range(4, 8):
        exceptions: list[tuple[int, ...]] = []
        survivors: list[tuple[int, ...]] = []
        for t in combinations_with_replacement(range(1, 8), d):
            eps = local_excess(t)
            q4 = t.count(4)
            if eps <= 0 and q4 > -eps:
                exceptions.append(t)
                if not rooted_star_reducible(t):
                    survivors.append(t)
        out[d] = {"exceptions": exceptions, "survivors": survivors}
    return out


def degree3_support_audit() -> list[tuple[int, int]]:
    """Return pairs (a,b) that can be incompatible with a (3,3)-state via m=4."""
    bad_pairs: list[tuple[int, int]] = []
    for a in range(1, 8):
        for b in range(a, 8):
            bad = False
            for r in range(5):
                if not realizations_of_state(3, 3, r):
                    continue
                for s in range(5):
                    if not realizations_of_state(a, b, s):
                        continue
                    if not state_pair_is_compatible(3, 3, r, a, b, s, 4):
                        bad = True
            if bad:
                bad_pairs.append((a, b))
    return bad_pairs


def main() -> None:
    print("=== Positive-type audit ===")
    pa = positive_type_audit()
    for d, data in pa.items():
        print(
            f"degree {d}: positive={len(data['positive'])}, "
            f"union-bound={len(data['union'])}, "
            f"star-tested={len(data['star_tested'])}, "
            f"survivors={data['survivors']}"
        )

    print("\n=== Capacity-exception audit ===")
    ca = capacity_exception_audit()
    for d, data in ca.items():
        print(
            f"degree {d}: exceptions={len(data['exceptions'])}, "
            f"survivors={data['survivors']}"
        )
        for t in data["exceptions"]:
            print(
                f"  {t}: excess={local_excess(t)}, q4={t.count(4)}, "
                f"star-reducible={rooted_star_reducible(t)}"
            )

    print("\n=== Degree-3 support through a 4-thread ===")
    bad = degree3_support_audit()
    print("potentially incompatible shorter-length pairs:", bad)

    assert [x for x in pa[3]["survivors"]] == [(3, 3, 4)]
    assert all(not pa[d]["survivors"] for d in range(4, 9))
    assert all(not ca[d]["survivors"] for d in range(4, 8))
    assert bad == [(1, 1), (1, 2), (1, 3)]
    print("\nALL REVISED REDUCTION CHECKS PASSED")


if __name__ == "__main__":
    main()
