from k9_4.kneser94 import Kneser94, all_colors, are_adjacent


def test_number_of_vertices():
    g = Kneser94.build()
    assert len(g.colors) == 126


def test_degree():
    g = Kneser94.build()
    x = g.colors[0]
    assert g.degree(x) == 5


def test_adjacency_is_disjointness():
    colors = all_colors()
    for x in colors[:10]:
        for y in colors[:10]:
            assert are_adjacent(x, y) == (len(x & y) == 0)
