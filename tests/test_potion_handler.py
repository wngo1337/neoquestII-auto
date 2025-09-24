from src.potion_handler import PotionHandler


def test_sorting_standard_case():
    # missing_hp = 65  
    result = PotionHandler.get_best_potions_by_efficiency(35, 100)
    assert result[0] in [
        (30021, "Potion of Regeneration"),
        (30022, "Potion of Fortitude"),
    ]


def test_zero_missing_hp():
    # Full health, missing = 0
    result = PotionHandler.get_best_potions_by_efficiency(100, 100)
    assert result[0] == (30011, "Healing Vial")  # 15 is closest to 0


def test_one_hp_missing():
    result = PotionHandler.get_best_potions_by_efficiency(99, 100)
    assert result[0] == (30011, "Healing Vial")


def test_full_missing_hp():
    # missing = 100
    result = PotionHandler.get_best_potions_by_efficiency(0, 100)
    # closest: 100 (Potion of Greater Health)
    assert result[0] == (30032, "Potion of Greater Health")


def test_negative_hp():
    # Negative HP is not possible, but still want to test
    result = PotionHandler.get_best_potions_by_efficiency(-10, 100)
    assert isinstance(result, list)
    assert (30014, "Healing Bottle") in result


def test_tied_healing_values():
    # Ahp = 15, which potion heals 15 exactly?
    result = PotionHandler.get_best_potions_by_efficiency(85, 100)  # missing = 15
    # Should return Healing Vial (heals 15) first
    assert result[0] == (30011, "Healing Vial")


def test_ordering_with_all_potions():
    # Check all potions are included, sorted properly by difference to missing_hp
    result = PotionHandler.get_best_potions_by_efficiency(70, 200)  # missing = 130
    all_ids = [pid for pid, _ in result]
    expected_ids = sorted(
        PotionHandler.POTIONS,
        key=lambda pid: abs(PotionHandler.POTIONS[pid][1] - 130)
    )
    assert all_ids == expected_ids
