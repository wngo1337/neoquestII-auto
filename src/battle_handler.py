import logging
from enum import Enum

from bs4 import BeautifulSoup
from Pages.neopets_page import NeopetsPage
from Pages.battle_page import BattlePage
from Pages.battle_start_page import BattleStartPage
from Pages.battle_result_page import BattleResultPage

from potion_handler import PotionHandler
from typing import Optional, Dict, List

from src.Pages.overworld_page import OverworldPage

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

    class AllyId(Enum):
        ROHANE = 1
        MIPSY = 2
        TALINIA = 3
        VELM = 4

    ENEMY_TURN_URL_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?target=-1&fact=1&parm=&use_id=&nxactor={0}"
    PLAYER_TURN_URL_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?target={0}&fact={1}&parm={2}&use_id={3}&nxactor={4}"
    PLAYER_ATTACK_URL_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?target={0}&fact=3&parm=&use_id=&nxactor={1}"
    # Only need to specify use_id and nxactor for convenience
    PLAYER_USE_POTION_URL_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?target=-1&fact=5&parm=&use_id={0}&nxactor={1}"
    END_BATTLE_URL_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?target=-1&fact=2&parm=&use_id=-1&nxactor={0}"

    # Enemies always have ID ranging from 5 to 8
    INITIAL_ENEMY_ID = 5

    def __init__(self, neopets_page: NeopetsPage, in_battle: bool = True) -> None:
        # We expect a BattlePage object to be passed
        # NOTE: may not be a BattleStartPage when we receive it if we are in middle of battle
        if in_battle:
            self.battle_start_page = BattleStartPage(neopets_page.page_instance)
            if self.is_battle_start():
                logger.info(
                    "Found battle start. Starting battle and initializing battle page..."
                )
                self.battle_start_page.click_start_battle_button()
                self.battle_page = BattlePage(self.battle_start_page.page_instance)
            else:
                logger.info("Detected existing battle. Initializing battle page...")
                # Just need to initialize to make sur eit isn't None when we are checking
                self.battle_start_page = BattleStartPage(neopets_page.page_instance)
                self.battle_page = BattlePage(neopets_page.page_instance)
            self.battle_result_page: BattleResultPage | None = None

        else:
            logger.info("We are not any a battle page. Just initializing the battle handler...")
            self.battle_start_page = None
            self.battle_page = None
            self.battle_result_page = None
        # WE NEED TO KEEP TRACK OF THIS SO WE DON'T HAVE TO LOOP THROUGH NUMS 5-8 EVERY TIME WE ATTACK LOL
        # BUT!!! THIS NEEDS TO BE RESET!!! SO MAYBE WE... I DON'T KNOW
        self.current_target = BattleHandler.INITIAL_ENEMY_ID


    def is_battle_start(self) -> bool:
        """
        Method to determine how to initialize the battle handler depending on if battle is in progress or starting.
        :return: True if we are actually on a battle start page, else False
        """
        if self.battle_start_page.start_battle_button.count() > 0:
            logger.info("We are starting a battle!")
            return True
        else:
            return False

    def is_battle_over(self) -> bool:
        """
        Determine if the battle is over because either the allies or the enemy won.
        :return: True if battle is over, otherwise return False
        """
        # turn_type = self.battle_page.get_turn_type()
        # if turn_type == BattlePage.TurnType.BATTLE_OVER:
        # BELOW IS UNRELIABLE BECAUSE PAGE CAN CONTAIN AN OUTDATED REFERENCE!!!
        # if self.battle_page.END_FIGHT_IDENTIFIER.count() > 0:
        if self.battle_page.page_instance.locator(BattlePage.END_FIGHT_LOCATOR).count() > 0:
            logger.info("The battle is over! Passing off control to the next method...")
            return True
        else:
            logger.info("Performed check and battle is not yet over...")
            return False

    def start_battle(self, neopets_page: NeopetsPage) -> BattlePage:
        self.battle_start_page = BattleStartPage(neopets_page.page_instance)
        self.battle_start_page.click_start_battle_button()
        self.battle_page = BattlePage(self.battle_start_page.page_instance)

        return self.battle_page

    def win_battle(self) -> None:
        """
        (Hopefully) win any existing battle that the player is currently in.
        """
        while not self.is_battle_over():
            logger.info("Battle is not over yet!")
            self.advance_battle()
        # When battle is finished, reset current target to initial value for next fight
        # KIND OF MESSY BECAUSE THIS IS STATEFUL WHILE BATTLE LOSE STATE AFTER ENDING
        # TODO: figure out better way to handle resetting the target
        self.current_target = BattleHandler.INITIAL_ENEMY_ID

    def advance_battle(self) -> BattlePage:
        max_retries = 5
        actor_id = None
        for attempt in range(max_retries):
            try:
                actor_id = self.battle_page.get_next_actor_id()
                break
            except Exception as e:
                logger.info(f"Attempt {attempt}: Failed to get actor id for supposed battle page: {e}")
                self.battle_page.page_instance.reload()
        else:
            logger.warning("All attempts to get actor id failed.")
            # Optionally raise or handle according to your needs

        if actor_id >= 1 and actor_id <= 8:
            match actor_id:
                case BattlePage.AllyTurnType.ROHANE.value:
                    self.handle_rohane_turn()
                case BattlePage.AllyTurnType.MIPSY.value:
                    pass
                case BattlePage.AllyTurnType.TALINIA.value:
                    pass
                case _:
                    self.handle_enemy_turn(actor_id)
            return self.battle_page
        # elif turn_type == BattlePage.TurnType.ENEMY:
        #     # Enemy's actor id should be available, assuming method exists:
        #     enemy_id = self.battle_page.get_next_actor_id()
        #     self.handle_enemy_turn(enemy_id)
        #
        # elif turn_type == BattlePage.TurnType.BATTLE_OVER:
        #     logger.info("Battle is complete!")
        #     # Perform any cleanup or next steps here
        #
        else:
            raise Exception("The program ran into an unexpected page during battle")

    def handle_enemy_turn(self, enemy_id: int) -> BattlePage:
        """
        Advance the enemy turn by passing the required query parameters to the enemy turn URL template.
        Uses the URL to submit the form with the specified actions.
        :param enemy_id: actor id of enemy to take action
        """

        # Need to wait for navigation to complete before doing anything
        self.battle_page.go_to_url_and_wait_navigation(
            BattleHandler.ENEMY_TURN_URL_TEMPLATE.format(enemy_id))

        return self.battle_page

    def handle_ally_turn(self, ally_id: int) -> BattlePage:
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
        return self.battle_page

    def handle_rohane_turn(self) -> BattlePage:
        # Check if we need potion heal
        # Otherwise, just basic attack
        # Melee haste + crit is the standard build

        # WE CAN'T MOVE FORWARD UNTIL WE FIND A WAY TO EXTRACT THE HP VALUES!!!
        hp_vals = self.battle_page.get_character_hp_vals()["Rohane"]
        if does_need_healing(hp_vals["current_hp"], hp_vals["max_hp"]):
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
            # WE SHOULD PROBABLY STOP ATTACKING AND GO HEAL HERE, BUT TELL IT TO CONTINUE FIGHTING
            if best_potion_id == -1:
                logger.warning("The player is out of potions! This is extremely dangerous.")

                attack_url = BattleHandler.PLAYER_ATTACK_URL_TEMPLATE.format(
                    self.current_target, BattleHandler.AllyId.ROHANE.value
                )
                logger.info(f"We would go to the attack url: {attack_url}")
                self.battle_page.go_to_url_and_wait_navigation(attack_url)
                while self.battle_page.has_attacked_invalid_target():
                    self.current_target += 1
                    attack_url = BattleHandler.PLAYER_ATTACK_URL_TEMPLATE.format(
                        self.current_target, BattleHandler.AllyId.ROHANE.value
                    )
                    self.battle_page.go_to_url_and_wait_navigation(attack_url)
                # # raise ValueError(
                # #     f"We got a potion ID of: {best_potion_id}. Double check if you have any potions!"
                # )

            healing_url = BattleHandler.PLAYER_TURN_URL_TEMPLATE.format(
                -1, 5, "", best_potion_id, BattleHandler.AllyId.ROHANE.value
            )
            logger.info(f"We would go to healing url: {healing_url}")
            self.battle_page.go_to_url_and_wait_navigation(healing_url)

        else:
            # Try attacking the first monster -> if defeated, increment the id and try again, etc.
            attack_url = BattleHandler.PLAYER_ATTACK_URL_TEMPLATE.format(
                self.current_target, BattleHandler.AllyId.ROHANE.value
            )
            logger.info(f"We would go to the attack url: {attack_url}")
            self.battle_page.go_to_url_and_wait_navigation(attack_url)
            while self.battle_page.has_attacked_invalid_target():
                if self.is_battle_over():
                    logger.warning("The battle ended but we were still trying to attack a target! Returning control from Rohane's turn call.")
                    # self.end_battle()
                    break
                else:
                    self.current_target += 1
                    attack_url = BattleHandler.PLAYER_ATTACK_URL_TEMPLATE.format(
                        self.current_target, BattleHandler.AllyId.ROHANE.value
                    )
                    self.battle_page.go_to_url_and_wait_navigation(attack_url)
            # You must select a valid target to cast on!
        return self.battle_page

    # NOTE: The resulting page after using this method is NOT a BattlePage instance
    # We just put the end battle methods into here to avoid adding another really empty page class
    def end_battle(self) -> OverworldPage:
        """
        Exit the battle instance and go to the post battle page
        :return:
        """
        # RESET THE CURRENT TARGET COUNT FOR BATTLE HANDLER TO ZERO AFTER FINISHING BATTLE
        self.current_target = 5
        if self.is_battle_over():
            logger.info("Trying to exit the completed battle...")
            actor_id = self.battle_page.get_next_actor_id()
            self.battle_page.go_to_url_and_wait_navigation(
                BattleHandler.END_BATTLE_URL_TEMPLATE.format(actor_id)
            )
            self.battle_result_page = BattleResultPage(self.battle_page.page_instance)
            self.battle_result_page.click_return_to_map_button()
        else:
            logger.error("Program tried to end the battle when the battle is not over!")
            raise Exception("Program tried to end the battle when the battle is not over, so we are confused!")
        # Clicking return to map button results in an overworld page in MOST cases
        return OverworldPage(self.battle_result_page.page_instance)