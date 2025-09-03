import logging

from bs4 import BeautifulSoup
from Pages.neopets_page import NeopetsPage
from Pages.battle_page import BattlePage
from Pages.battle_start_page import BattleStartPage

from potion_handler import PotionHandler
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


# TODO: It is important that we have a way to handle battles that are already in progress on program start!
# The current way requires a battle start page to be fed to the program first!!


def does_need_healing(current_hp: int, max_hp: int) -> bool:
    """
    Evaluates a character's HP status and determines if they require potion healing
    :param current_hp: character current HP
    :param max_hp: character max HP
    :return: True if HP ratio is below threshold, else False
    """
    return current_hp / max_hp < 0.55


class BattleHandler:
    ROHANE_TURN_IDENTIFIER = r"<b>Rohane</b>"
    MIPSY_TURN_IDENTIFIER = r"<b>Mipsy</b>"
    TALINIA_TURN_IDENTIFIER = r"<b>Talinia</b>"
    VELM_TURN_IDENTIFIER = r"<b>Velm</b>"

    ENEMY_TURN_URL_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?target=-1&fact=1&parm=&use_id=&nxactor={0}"
    PLAYER_TURN_URL_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?target={0}&fact={1}&parm={2}&use_id={3}&nxactor={4}"

    def __init__(self, neopets_page: NeopetsPage) -> None:
        # This will always get initialized when we go into a battle
        # We expect a BattlePage object to be passed
        # NOTE: may not be a BattleStartPage when we receive it if we are in middle of battle
        self.battle_start_page = BattleStartPage(neopets_page.page_instance)
        # Check if we are actually on a BattleStartPage or if we should proceed with existing battle
        if self.battle_start_page.is_battle_start():
            logger.info(
                "Found battle start. Starting battle and initializing battle page..."
            )
            self.battle_start_page.click_start_battle_button()
            self.battle_page = BattlePage(self.battle_start_page.page_instance)
        else:
            logger.info("Detected existing battle. Initializing battle page...")
            self.battle_page = BattlePage(self.battle_start_page.page_instance)

    def handle_enemy_turn(self, enemy_id: int) -> None:
        """
        Advance the enemy turn by passing the required query parameters to the enemy turn URL template.
        Uses the URL to submit the form with the specified actions.
        :param enemy_id: actor id of enemy to take action
        """

        # Need to wait for navigation to complete before doing anything
        with self.battle_page.page_instance.expect_navigation():
            self.battle_page.go_to_url(
                BattleHandler.ENEMY_TURN_URL_TEMPLATE.format(enemy_id)
            )

    def handle_ally_turn(self, ally_id: int) -> None:
        """
        Take action based on the ally actor id that is passed in.
        Action priority differs by character, but in general: potion heal? -> castable skill? -> basic attack?

        We have not figured out how haste or damage potions fit in yet
        """
        match ally_id:
            case 1:
                # Rohane turn
                pass
            case 2:
                # Mipsy turn
                pass
            case 3:
                # Talinia turn
                pass
            case 4:
                # Velm turn
                pass
            case _:
                # Error because we expected an ally's ID
                raise ValueError(f"Expected an ally ID between 1-4. Got: {ally_id}")

    def handle_rohane_turn(self) -> None:
        # Check if we need potion heal
        # Otherwise, just basic attack
        # Melee haste + crit is the standard build

        # WE CAN'T MOVE FORWARD UNTIL WE FIND A WAY TO EXTRACT THE HP VALUES!!!
        hp_vals = self.battle_page.get_character_hp_vals()["Rohane"]
        # if does_need_healing(hp_vals["current_hp"], hp_vals["max_hp"]):
        #     """
        #     Target = -1
        #     fact = 5
        #     parm =
        #     use_id = WHATEVER POTION IS
        #     nxactor = ACTOR ID!!!
        #     """
        ranked_potions = PotionHandler.get_best_potions_by_efficiency(
            hp_vals["current_hp"], hp_vals["max_hp"]
        )

        available_potions = self.battle_page.get_available_healing_potions()
        available_potions_lowercase = [
            potion_name.lower() for potion_name in available_potions
        ]

        best_potion_id = -1
        for potion_id, potion_name in ranked_potions:
            if potion_name.lower() in available_potions_lowercase:
                best_potion_id = potion_id
                break

        formatted_healing_url = BattleHandler.PLAYER_TURN_URL_TEMPLATE.format(
            -1, 5, "", best_potion_id, 1
        )
        print(f"We would go to url: {formatted_healing_url}")
