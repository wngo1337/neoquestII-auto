from enum import Enum, auto
import re
from bs4 import BeautifulSoup

from playwright.sync_api import Page

from .neopets_page import NeopetsPage
from src.potion_handler import PotionHandler

from typing import Dict, List


class BattlePage(NeopetsPage):
    # NOTE: we will conduct battles by passing query string parameters
    # It is really difficult to create selectors for the elements that set a javascript call
    # LOCATORS FOR ELEMENTS ON ENEMY TURN

    # If this is present, it is the enemy's turn
    # Likely the only selector even needed on enemy turn
    ENEMY_TURN_LOCATOR = r"img[src='//images.neopets.com/nq2/x/com_next.gif']"

    # LOCATORS FOR ALLY TURN

    PLAYER_TURN_LOCATOR = r"img[src='//images.neopets.com/nq2/x/com_atk.gif']"
    FLEE_LOCATOR = r"img[src='//images.neopets.com/nq2/x/com_flee.gif']"

    DO_NOTHING_ONE_SEC_LOCATOR = r"img[src='//images.neopets.com/nq2/x/1s.gif']"
    DO_NOTHING_THREE_SEC_LOCATOR = r"img[src='//images.neopets.com/nq2/x/3s.gif']"
    DO_NOTHING_FIVE_SEC_LOCATOR = r"img[src='//images.neopets.com/nq2/x/5s.gif']"

    # LOCATOR FOR BATTLE END
    END_FIGHT_LOCATOR = r"[src='//images.neopets.com/nq2/x/com_end.gif']"

    ALLY_NAMES = ["Rohane", "Mipsy", "Talinia", "Velm"]

    class TurnType(Enum):
        ENEMY = auto()
        PLAYER = auto()
        BATTLE_OVER = auto()

    class AllyTurnType(Enum):
        ROHANE = auto()
        MIPSY = auto()
        TALINIA = auto()
        VELM = auto()

    def __init__(self, neopets_page_instance: Page) -> None:
        # umm need all the selectors and stuff...
        super().__init__(neopets_page_instance)
        # Note: these are NOT clickable elements - their presence is used to identify ally or enemy turn only
        self.ENEMY_TURN_IDENTIFIER = self.page_instance.locator(
            BattlePage.ENEMY_TURN_LOCATOR
        )
        self.PLAYER_TURN_IDENTIFIER = self.page_instance.locator(
            BattlePage.PLAYER_TURN_LOCATOR
        )
        self.END_FIGHT_IDENTIFIER = self.page_instance.locator(
            BattlePage.END_FIGHT_LOCATOR
        )

    def get_turn_type(self) -> TurnType:
        """
        Determines if it is the enemy's turn or an ally's turn.
        Mainly used as a helper method to determine which method to call to advance the battle.
        :return: a TurnType enum value of either ENEMY or PLAYER
        """
        if self.ENEMY_TURN_IDENTIFIER.count() > 0:
            return BattlePage.TurnType.ENEMY
        elif self.PLAYER_TURN_IDENTIFIER.count() > 0:
            return BattlePage.TurnType.PLAYER
        elif self.END_FIGHT_IDENTIFIER.count() > 0:
            return BattlePage.TurnType.BATTLE_OVER
        else:
            # TODO: return a more specific exception
            raise Exception(
                "It is neither the player or enemy's turn. You are likely not on a battle page!"
            )

    def get_next_actor_id(self) -> int:
        """
        Parses the page HTML to extract the hidden nxactor input element value required to perform an action
        :return: actor id of the next (current turn) actor
        """
        battle_html = self.page_instance.content()  # Playwright: gets current page HTML
        soup = BeautifulSoup(battle_html, "html.parser")
        hidden_input_tag = soup.find(
            "input", attrs={"type": "hidden", "name": "nxactor"}
        )
        if hidden_input_tag:
            return int(hidden_input_tag["value"])
        else:
            raise Exception("Could not find nxactor hidden input on the battle page.")

    def get_character_hp_vals(self) -> Dict[str, Dict[str, int]]:
        battle_html = self.page_instance.content()
        soup = BeautifulSoup(battle_html, "html.parser")
        game_container = soup.find("div", class_="contentModule phpGamesNonPortalView")

        # Ensure that we do not assign the same character name to multiple HP values
        added_chars = {}
        ally_hp_info = {}

        # Basically two numerical values separate by a slash
        hp_pattern = re.compile(r"^\d+/\d+$")

        # Find all font tags that have HP text
        hp_font_tags = game_container.find_all("font")
        for hp_tag in hp_font_tags:
            raw_hp_text = hp_tag.get_text(strip=True)

            # Check if this font tag contains HP text based on pattern
            if hp_pattern.match(raw_hp_text):
                # Walk up the tree to parent td of this HP
                td_hp = hp_tag.find_parent("td")
                if not td_hp:
                    continue

                # Then find the parent table
                table = td_hp.find_parent("table")
                if not table:
                    continue

                # Then find parent td of this table (HP table container)
                parent_td = table.find_parent("td")
                if not parent_td:
                    continue

                # THIS IS TRICKY BECAUSE SOMETIMES WE HAVE A CONTAINING FONT TAG IF OUR TURN, ELSE NOT
                turn_type = self.get_turn_type()
                if turn_type == BattlePage.TurnType.PLAYER:
                    # Text will be further inside a bold tag, but the container doesn't contain any other text
                    character_name_tag = parent_td.find(
                        "b", string=BattlePage.ALLY_NAMES, recursive=True
                    )
                    # Character names are in the same td element as the HP text
                    # Monster names are not
                    if character_name_tag:
                        character_name = character_name_tag.get_text().strip()
                    else:
                        character_name = "NOT_A_NAME"
                else:
                    # If not our turn, then text will simply be inside the td tag
                    character_name_tag = parent_td
                    character_name = character_name_tag.find(
                        string=BattlePage.ALLY_NAMES, recursive=False
                    )

                if (
                        character_name in BattlePage.ALLY_NAMES
                        and character_name not in added_chars.keys()
                ):
                    print(
                        f"Adding entry to character list: {character_name} - {raw_hp_text}"
                    )
                    hp_vals = raw_hp_text.split("/")
                    current_hp = int(hp_vals[0])
                    max_hp = int(hp_vals[1])
                    added_chars[character_name] = {
                        "current_hp": current_hp,
                        "max_hp": max_hp,
                    }
                    # break
        print("These are the allies we see on the page:")
        print(added_chars)

        return added_chars

    def get_available_healing_potions(self) -> List[str]:
        """
        Read through the page HTML and check if each potion name is in the page.
        :return: list of potion names available to use
        """

        page_html = self.get_page_content()
        # NOW CHECK IF EACH POTION IS IN THE STRING!!!
        available_potions = []
        for potion_id, (potion_name, heal_val) in PotionHandler.POTIONS.items():
            if potion_name in page_html:
                available_potions.append(potion_name)
        return available_potions
