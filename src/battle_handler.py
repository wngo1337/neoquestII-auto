import logging

from bs4 import BeautifulSoup
from Pages.neopets_page import NeopetsPage
from Pages.battle_page import BattlePage
from Pages.battle_start_page import BattleStartPage

from typing import Optional

logger = logging.getLogger(__name__)


# TODO: It is important that we have a way to handle battles that are already in progress on program start!
# The current way requires a battle start page to be fed to the program first!!


def does_need_healing(current_hp: int, max_hp: int) -> bool:
    """
    Evaluates a character's HP status and determines if they require potion healing
    :param current_hp: current character HP
    :param max_hp: max character HP
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
        pass

    # def get_player_turn_type(self) -> BattlePage.AllyTurnType:
    #     """
    #     Parse the page HTML for unique identifiers to determine which specific ally's turn it is.
    #     Assumes that it is the player's turn already.
    #     :return: Enum value representing the ally whose turn it is.
    #     """
    #
    #     # I think we can basically just look for bolded name text
    #     soup = BeautifulSoup(self.battle_page.get_page_content(), "html.parser")
    #
    #     turn_type = self.battle_page.get_turn_type()
    #     if turn_type != BattlePage.TurnType.PLAYER:
    #         logger.error(
    #             "The method was called on the enemy's turn instead of an ally's turn!"
    #         )
    #         raise Exception(
    #             "Yeah something went wrong when trying to determine the ally's turn."
    #         )
    #
    #     rohane_turn_tag = soup.find(BattleHandler.ROHANE_TURN_IDENTIFIER)
    #     mipsy_turn_tag = soup.find(BattleHandler.MIPSY_TURN_IDENTIFIER)
    #     talinia_turn_tag = soup.find(BattleHandler.TALINIA_TURN_IDENTIFIER)
    #     velm_turn_tag = soup.find(BattleHandler.VELM_TURN_IDENTIFIER)
    #
    #     if rohane_turn_tag:
    #         return BattlePage.AllyTurnType.ROHANE
    #     elif mipsy_turn_tag:
    #         return BattlePage.AllyTurnType.MIPSY
    #     elif talinia_turn_tag:
    #         return BattlePage.AllyTurnType.TALINIA
    #     elif velm_turn_tag:
    #         return BattlePage.AllyTurnType.VELM
    #     else:
    #         raise Exception(
    #             "It is an ally's turn, but the program could not determine whose turn it is!"
    #         )
