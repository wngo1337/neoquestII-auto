from enum import Enum, auto
import logging

from Pages.neopets_page import NeopetsPage

logger = logging.getLogger(__name__)

from Pages.overworld_page import OverworldPage

class SkillpointHandler:
    class AllyType(Enum):
        ROHANE = auto()
        MIPSY = auto()
        TALINIA = auto()
        VELM = auto()

    class RohaneSkill(Enum):
        CRIT = 9101
        DAMAGE_INCREASE = 9102
        FOCUS = 9103
        STUN = 9104
        TAUNT = 9105
        MAGIC_RESIST = 9501
        MELEE_HASTE = 9502

    MAIN_GAME_URL = "https://www.neopets.com/games/nq2/nq2.phtml"

    # Everything is filled besides the skillpoint ID here
    # e.g. crit is 9101
    ROHANE_SKILLPOINT_SPEND_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?act=skills&buy_char=1&buy_char=1&confirm=1&skopt_{0}=1"

    def __init__(self, overworld_page: NeopetsPage) -> None:
        logger.info("Skillpoint handler oh yeahhh")
        self.overworld_page = overworld_page

    def try_spend_skillpoint(self, ally: AllyType, skill_id: int) -> bool:
        """
        Try to spend a skillpoint for a character on the overworld page.
        We do not always keep track of when player has leveled, so handle cases where it can fail.
        """
        if ally is SkillpointHandler.AllyType.ROHANE:
            skillpoint_spend_url = self.ROHANE_SKILLPOINT_SPEND_TEMPLATE.format(skill_id)
            self.overworld_page.go_to_url_and_wait_navigation(
                skillpoint_spend_url
            )
            # TODO: Probably find a way to identify if we actually spent a skillpoint here...
            logger.info("Returning to main game page")
            self.overworld_page.go_to_url_and_wait_navigation(SkillpointHandler.MAIN_GAME_URL)
            return True
        elif ally is SkillpointHandler.AllyType.MIPSY:
            pass
        else:
            logger.error("We did not receive a valid ally or skill to spend a skillpoint for!")
            raise Exception("Unable to spend skillpoint for that character!")