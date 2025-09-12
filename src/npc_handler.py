from typing import List
from Pages.neopets_page import NeopetsPage
from src.Pages.overworld_page import OverworldPage
from src.Pages.battle_start_page import BattleStartPage
import logging

logger = logging.getLogger(__name__)

class NpcHandler:
    
    MAIN_GAME_URL = r"https://www.neopets.com/games/nq2/nq2.phtml"

    # MERIDELL KEY NPCs
    # You only need to be in range to use these options
    # Will use this one A LOT in the early game
    MOTHER_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10201&say=rest"]

    # OPENS A SHOP PAGE!!!
    PONGORAS_TRADE_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=10202&greet=1"]

    MIPSY_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10408&say=join"]
    
    POTRADDO_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=city",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=no",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=about",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=east",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=enter"]

    # Talk to the ghost for entry
    WITHERED_GHOST_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10801",
                            r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10801&say=key"]

    # Buy a few resurrection potions in case you get unlucky in the overworld
    UTHARE_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11201&greet=1",
                                r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11201&mact=buy&targ_item=30400&quant=10"]

    PATANNIS_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&greet=1",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&mact=buy&targ_item=10017&quant=1",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&mact=buy&targ_item=20017&quant=1",
                                  r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&mact=buy&targ_item=20116&quant=1"]

    # Rest at the temp inn
    GUARD_THYET_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=11001&say=rest"]
    
    # Recruit Talinia
    TALINIA_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=20510",
                                 r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=20510&say=join"]
    
    ALLDEN_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=20701&say=rest"]
    
    VELM_INTERACTION_LINKS = [r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30504&say=join"]

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
        self.npc_page.go_to_url_and_wait_navigation(self.MAIN_GAME_URL)
        # After all NPC interaction links visited, return to OverworldPage
        return OverworldPage(self.npc_page.page_instance)

    def talk_with_mother(self) -> None:
        return self.talk_with_npc(NpcHandler.MOTHER_INTERACTION_LINKS)

    def recruit_mipsy(self) -> None:
        logger.info("Trying to recruit Mipsy!")
        self.talk_with_npc(NpcHandler.MIPSY_INTERACTION_LINKS)

    def talk_with_potraddo(self) -> None:
        logger.info("Trying to talk with Potraddo to unlock lost city!")
        self.talk_with_npc(NpcHandler.POTRADDO_INTERACTION_LINKS)

    def talk_with_withered_ghost(self) -> None:
        self.talk_with_npc(NpcHandler.WITHERED_GHOST_INTERACTION_LINKS)

    def talk_with_uthare(self) -> None:
        self.talk_with_npc(NpcHandler.UTHARE_INTERACTION_LINKS)

    def talk_with_patannis(self) -> None:
        self.talk_with_npc(NpcHandler.PATANNIS_INTERACTION_LINKS)

    def talk_with_guard_thyet(self) -> None:
        self.talk_with_npc(NpcHandler.GUARD_THYET_INTERACTION_LINKS)

    def recruit_talinia(self) -> None:
        self.talk_with_npc(NpcHandler.TALINIA_INTERACTION_LINKS)

    def talk_with_allden(self) -> None:
        self.talk_with_npc(NpcHandler.ALLDEN_INTERACTION_LINKS)

    def recruit_velm(self) -> None:
        self.talk_with_npc(NpcHandler.VELM_INTERACTION_LINKS)