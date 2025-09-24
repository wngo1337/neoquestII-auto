import logging
from enum import Enum

from src.AutoplayerBaseHandler import AutoplayerBaseHandler
from src.Pages.neopets_page import NeopetsPage
from src.Pages.overworld_page import OverworldPage

logger = logging.getLogger(__name__)


class InventoryHandler(AutoplayerBaseHandler):
    class AllyId(Enum):
        ROHANE = 1
        MIPSY = 2
        TALINIA = 3
        VELM = 4

    EQUIP_EQUIPMENT_URL_TEMPLATE = "https://www.neopets.com/games/nq2/nq2.phtml?act=inv&iact=equip&targ_item={0}&targ_char={1}"

    # ROHANE EQUIPMENT
    IRON_SHORTSWORD_ID = 10011
    RUSTY_CHAIN_TUNIC_ID = 20010

    # BACKUP CHAPTER 3 UPGRADES
    IRON_LONGSWORD_ID = 10030
    STEEL_SPLINT_MAIL_ID = 20030

    # MIPSY EQUIPMENT

    # BACKUP CHAPTER 3 UPGRADES
    ACOLYTE_ROBE_ID = 20130

    # TALINIA EQUIPMENT

    # BACKUP CHAPTER 3 UPGRADES
    ASH_SHORT_BOW_ID = 10230
    REINFORCED_LEATHER_TUNIC_ID = 20230

    def __init__(self, current_page: NeopetsPage) -> None:
        logger.info("Initializing inventory handler with current page for later use...")
        self.overworld_page = OverworldPage(current_page.page_instance)
        # We don't actually need to represent the inventory page. We will just visit the link and it takes us to a thing
        # Then we navigate back to the main game page

    def equip_equipment(self, equipment_id: int, ally_id: int) -> OverworldPage:
        logger.info(f"Equipping item with id {equipment_id} on ally with id {ally_id}")
        self.overworld_page.go_to_url_and_wait_navigation(
            self.EQUIP_EQUIPMENT_URL_TEMPLATE.format(equipment_id, ally_id)
        )
        logger.info("Navigating back to the overworld page after equipping item...")
        self.overworld_page.go_to_url_and_wait_navigation(
            InventoryHandler.MAIN_GAME_URL
        )

        return self.overworld_page
