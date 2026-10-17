from octo import exit_plan, kelly_units, passes_filter


def test_bundle_filter():
    assert passes_filter(0.40, 0.01) == (False, "bundle 40%")


def test_dev_filter():
    ok, why = passes_filter(0.10, 0.109)
    assert not ok and why == "dev holding 10.9%"


def test_clean_launch_passes():
    assert passes_filter(0.10, 0.02)[0]


def test_kelly_capped():
    assert kelly_units(0.99, 100) == 12  # MAX_BAG
    assert kelly_units(0.10, 2) == 0     # no edge, no bet


def test_exit_ladder_and_trail():
    entry = 7.0
    path = [21, 56, 140, 60]  # 3x, 8x, 20x, then a dump below the 35% trail
    sells = exit_plan(path, entry)
    assert sells[:3] == [("ladder", 3), ("ladder", 8), ("ladder", 20)]
    assert sells[-1][0] == "stop"
