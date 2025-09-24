class PotionHandler:
    POTIONS = {
        30011: ("Healing Vial", 15),
        30012: ("Healing Flask", 25),
        30013: ("Healing Potion", 35),
        30014: ("Healing Bottle", 50),
        30021: ("Potion of Regeneration", 60),
        30022: ("Potion of Fortitude", 70),
        30023: ("Potion of Growth", 80),
        30031: ("Potion of Potent Health", 90),
        30032: ("Potion of Greater Health", 100),
        30033: ("Potion of Abundant Health", 110),
        30041: ("Vitality Potion", 120),
        30042: ("Stamina Potion", 130),
        30043: ("Constitution Potion", 140),
        30051: ("Faerie's Gift Potion", 150),
        30052: ("Fyora's Blessing Potion", 160),
        30053: ("Jhudora's Lifeforce Potion", 170),
    }

    @staticmethod
    def get_best_potions_by_efficiency(
            character_current_hp: int, character_max_hp: int
    ) -> list[tuple[int, str]]:
        """
        Go through all potions and return the in order of healing efficiency for the given HP values.
        Whole potion list is required because there is no guarantee what potions we have in inventory.
        """
        missing_hp = character_max_hp - character_current_hp
        potion_waste_list = [
            (pid, name, abs(heal - missing_hp))
            for pid, (name, heal) in PotionHandler.POTIONS.items()
        ]
        potion_waste_list.sort(key=lambda x: x[2])
        return [(pid, name) for pid, name, _ in potion_waste_list]
