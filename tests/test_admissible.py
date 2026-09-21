from k9_4.admissible import admissible_cardinality, forbidden_cardinality


def test_admissible_known_values():
    expected = {
        1: (5, 121),
        2: (21, 105),
        3: (45, 81),
        4: (81, 45),
        5: (105, 21),
        6: (121, 5),
        7: (125, 1),
        8: (126, 0),
    }

    for i, (a_exp, f_exp) in expected.items():
        assert admissible_cardinality(i) == a_exp
        assert forbidden_cardinality(i) == f_exp


def test_admissible_partition():
    for i in range(1, 9):
        assert admissible_cardinality(i) + forbidden_cardinality(i) == 126
        
def test_all_colors_admissible_from_length_8_onwards():
    for i in range(8, 11):
        assert admissible_cardinality(i) == 126
        assert forbidden_cardinality(i) == 0
