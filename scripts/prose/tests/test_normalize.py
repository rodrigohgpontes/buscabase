from scripts.prose.normalize import bag_coverage, join_hyphenated, normalize


def test_join_hyphenated_linebreak():
    assert join_hyphenated(["Identificar e repre-", "sentar frações"]) == "Identificar e representar frações"


def test_normalize_quotes_and_spaces():
    assert normalize("“Arte”   na\u00a0BNCC") == '"Arte" na BNCC'


def test_bag_coverage_full():
    assert bag_coverage("Frações no 5º ano", "Frações no 5º ano") == 1.0


def test_bag_coverage_partial():
    score = bag_coverage("abcdef", "abc")
    assert 0.4 < score < 0.6
