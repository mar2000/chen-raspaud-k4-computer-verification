from k9_4.compatibility import (
    first_incompatibility_certificate,
    realizable_states_for_pairs,
    state_pair_is_compatible,
)
from k9_4.states_deg3 import DEFAULT_DEG3_PAIRS


def test_realizable_states_nonempty():
    states = realizable_states_for_pairs(DEFAULT_DEG3_PAIRS)
    assert states, "No realizable states found"


def test_certificate_matches_compatibility():
    states = realizable_states_for_pairs(DEFAULT_DEG3_PAIRS)

    # test a small sample of pairs for each m
    sample = states[:10]
    for m in [5, 6, 7]:
        for left in sample:
            for right in sample:
                is_good = state_pair_is_compatible(*left, *right, m)
                cert = first_incompatibility_certificate(*left, *right, m)
                if is_good:
                    assert cert is None
                else:
                    assert cert is not None
