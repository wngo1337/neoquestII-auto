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
    MOTHER_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10201&say=rest"
    ]

    # OPENS A SHOP PAGE!!!
    PONGORAS_TRADE_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=10202&greet=1"
    ]

    TEBOR_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=10401&greet=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=10401&mact=buy&targ_item=10011&quant=1",
    ]

    MIPSY_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10408&say=join"
    ]

    POTRADDO_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=city",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=no",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=about",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=east",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10718&say=enter",
    ]

    # Talk to the ghost for entry
    WITHERED_GHOST_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10801",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=10801&say=key",
    ]

    # Buy a few resurrection potions in case you get unlucky in the overworld
    UTHARE_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11201&greet=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11201&mact=buy&targ_item=30400&quant=10",
    ]

    PATANNIS_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&greet=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&mact=buy&targ_item=10017&quant=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&mact=buy&targ_item=20017&quant=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=11203&mact=buy&targ_item=20116&quant=1",
    ]

    # Rest at the temp inn
    GUARD_THYET_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=11001&say=rest"
    ]

    # Recruit Talinia
    TALINIA_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=20510",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=20510&say=join",
    ]

    ALLDEN_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=20701&say=rest"
    ]

    SABALIZ_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=30203&greet=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=30203&mact=buy&targ_item=10030&quant=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=30203&mact=buy&targ_item=10230&quant=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=30203&mact=buy&targ_item=20030&quant=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=30203&mact=buy&targ_item=20130&quant=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=30203&mact=buy&targ_item=20230&quant=1",
    ]

    VELM_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30504&say=join"
    ]

    LIFIRA_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510&say=calm",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510&say=home",
    ]

    LIFIRA_PART2_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510&say=curious",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510&say=purpose",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510&say=find",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30510&say=fates",
    ]

    BUKARU_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30101",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30101&say=code",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30101&say=medallion",
    ]

    MEDALLION_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?continue=1"
    ]

    MEDALLION_CENTREPIECE_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?continue=1"
    ]

    COLTZAN_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=30701"
    ]

    MEDALLION_GEMSTONE_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?continue=1"
    ]

    BRAIN_TREE_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=40501",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=40501&say=adventurers",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=40501&say=yes",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=40501&say=how",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=40501&say=anything",
    ]

    # This guy gives a bunch of powerful potions that can be used for Terask II fight
    AUGUR_FAUNT_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=40510&say=rest",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&greet=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&mact=buy&targ_item=30208&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&mact=buy&targ_item=30208&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&mact=buy&targ_item=30403&quant=5",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&mact=buy&targ_item=30308&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&mact=buy&targ_item=30308&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&mact=buy&targ_item=30109&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=40510&mact=buy&targ_item=30109&quant=10",
    ]

    CAERELI_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50703&greet=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50703&mact=buy&targ_item=10053&quant=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50703&mact=buy&targ_item=10253&quant=1",
    ]

    DELERI_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50701&say=rest"
    ]

    MEKAVA_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50704&greet=1",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50704&mact=buy&targ_item=30111&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50704&mact=buy&targ_item=30111&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50704&mact=buy&targ_item=30210&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50704&mact=buy&targ_item=30210&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50704&mact=buy&targ_item=30310&quant=10",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=merch&targ=50704&mact=buy&targ_item=30310&quant=10",
    ]

    LUSINA_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50501",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50501&say=who",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50501&say=what",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50501&say=faerie",
    ]

    STENVELA_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50602",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50602&say=who",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50602&say=you",
    ]

    VITRINI_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50605",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50605&say=not",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50605&say=rest",
    ]

    VITRINI_KEY_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50605&say=devil3"
    ]

    LYRA_INTERACTION_LINKS = [
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50606",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50606&say=who",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50606&say=help",
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=talk&targ=50606&say=rest",
    ]

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

    def talk_with_lifira(self) -> None:
        self.talk_with_npc(NpcHandler.LIFIRA_INTERACTION_LINKS)

    def talk_with_lifira_part2(self) -> None:
        self.talk_with_npc(NpcHandler.LIFIRA_PART2_INTERACTION_LINKS)

    def talk_with_bukaru(self) -> None:
        self.talk_with_npc(NpcHandler.BUKARU_INTERACTION_LINKS)

    def get_medallion(self) -> None:
        self.talk_with_npc(NpcHandler.MEDALLION_INTERACTION_LINKS)

    def talk_with_coltzan(self) -> None:
        self.talk_with_npc(NpcHandler.COLTZAN_INTERACTION_LINKS)

    def get_medallion_centrepiece(self) -> None:
        self.talk_with_npc(NpcHandler.MEDALLION_CENTREPIECE_INTERACTION_LINKS)

    def get_medallion_gemstone(self) -> None:
        self.talk_with_npc(NpcHandler.MEDALLION_GEMSTONE_INTERACTION_LINKS)

    def talk_with_brain_tree(self) -> None:
        self.talk_with_npc(NpcHandler.BRAIN_TREE_INTERACTION_LINKS)

    def talk_with_augur_faunt(self) -> None:
        self.talk_with_npc(NpcHandler.AUGUR_FAUNT_INTERACTION_LINKS)

    def talk_with_caereli(self) -> None:
        self.talk_with_npc(NpcHandler.CAERELI_INTERACTION_LINKS)

    def talk_with_deleri(self) -> None:
        self.talk_with_npc(NpcHandler.DELERI_INTERACTION_LINKS)

    def talk_with_mekava(self) -> None:
        self.talk_with_npc(NpcHandler.MEKAVA_INTERACTION_LINKS)

    def talk_with_lusina(self) -> None:
        self.talk_with_npc(NpcHandler.LUSINA_INTERACTION_LINKS)

    def talk_with_stenvela(self) -> None:
        self.talk_with_npc(NpcHandler.STENVELA_INTERACTION_LINKS)

    def talk_with_vitrini(self) -> None:
        self.talk_with_npc(NpcHandler.VITRINI_INTERACTION_LINKS)

    def talk_with_vitrini_key(self) -> None:
        self.talk_with_npc(NpcHandler.VITRINI_KEY_INTERACTION_LINKS)

    def talk_with_lyra(self) -> None:
        self.talk_with_npc(NpcHandler.LYRA_INTERACTION_LINKS)

    def talk_with_tebor(self) -> None:
        self.talk_with_npc(NpcHandler.TEBOR_INTERACTION_LINKS)

    def talk_with_sabaliz(self) -> None:
        self.talk_with_npc(NpcHandler.SABALIZ_INTERACTION_LINKS)
