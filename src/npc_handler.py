from typing import List
from Pages.neopets_page import NeopetsPage
from src.Pages.overworld_page import OverworldPage
from src.Pages.battle_start_page import BattleStartPage
import logging

logger = logging.getLogger(__name__)

class NpcHandler:

    # MERIDELL KEY NPCs
    # You only need to be in range to use these options
    # Will use this one A LOT in the early game
    MOTHER_INTERACTION_LINKS = ["https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10201&say=rest"]

    # OPENS A SHOP PAGE!!!
    PONGORAS_TRADE_LINKS = ["https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=10202&greet=1"]

    def __init__(self, current_page: NeopetsPage) -> OverworldPage:
        logger.info("NPC Handler initialized")
        self.npc_page = OverworldPage(current_page.page_instance)

    def set_npc_page(self, npc_page: NeopetsPage) -> None:
        self.npc_page = OverworldPage(npc_page.page_instance)

    def talk_with_npc(self, dialogue_urls: List[str]) -> OverworldPage:
        """
        Visit each link in the npc_links list to interact with NPCs in sequence.
        After finishing all NPC interactions, return OverworldPage control.

        :param dialogue_urls: A list of URL strings to visit
        """
        for link in dialogue_urls:
            logger.info(f"Visiting NPC link: {link}")
            self.npc_page.go_to_url_and_wait_navigation(link)

        logger.info("NPC interactions completed, returning to Overworld.")
        # After all NPC interaction links visited, return to OverworldPage
        return OverworldPage(self.npc_page.page_instance)

    def talk_with_mother(self) -> OverworldPage:
        return self.talk_with_npc(NpcHandler.MOTHER_INTERACTION_LINKS)
