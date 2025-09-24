import logging
from enum import Enum, auto

from src.AutoplayerBaseHandler import AutoplayerBaseHandler
from src.Pages.neopets_page import NeopetsPage

logger = logging.getLogger(__name__)


class SkillpointHandler(AutoplayerBaseHandler):
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

    # These look identical to Rohane's but I'm really not sure until I see them
    class MipsySkill(Enum):
        DIRECT_DAMAGE = 9201
        GROUP_DIRECT_DAMAGE = 9202
        GROUP_HASTE = 9203
        SLOW = 9204
        DAMAGE_SHIELDS = 9205
        MELEE_DEFENSE = 9601
        CASTING_HASTE = 9602

    # Talinia is going to be built like a stun bot
    class TaliniaSkill(Enum):
        INCREASE_BOW_DAMAGE = 9301
        MULTI_TARGETS = 9302
        RANGED_ATTACKS = 9303
        SHOCKWAVE = 9304
        SLOWING_STRIKE = 9305
        MAGIC_RESIST = 9501
        MELEE_HASTE = 9502

    class VelmSkill(Enum):
        HEAL = 9401
        GROUP_HEAL = 9402
        GROUP_SHIELD = 9403
        MESMERIZE = 9404
        CELESTIAL_HAMMER = 9405
        MELEE_DEFENSE = 9601
        CASTING_HASTE = 9602

    # Everything is filled besides the skillpoint ID here
    # e.g. crit is 9101
    ROHANE_SKILLPOINT_SPEND_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?act=skills&buy_char=1&buy_char=1&confirm=1&skopt_{0}=1"
    MIPSY_SKILLPOINT_SPEND_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?act=skills&buy_char=2&buy_char=2&confirm=1&skopt_{0}=1"
    TALINIA_SKILLPOINT_SPEND_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?act=skills&buy_char=3&buy_char=3&confirm=1&skopt_{0}=1"
    VELM_SKILLPOINT_SPEND_TEMPLATE = r"https://www.neopets.com/games/nq2/nq2.phtml?act=skills&buy_char=4&buy_char=4&confirm=1&skopt_{0}=1"

    def __init__(self, overworld_page: NeopetsPage) -> None:
        logger.info("Initializing skillpoint handler with current page for later use...")
        self.overworld_page = overworld_page

    def try_spend_skillpoint(self, ally: AllyType, skill_id: int) -> bool:
        """
        Try to spend a skillpoint for a character on the overworld page.
        We do not always keep track of when player has leveled, so handle cases where it can fail.
        """
        logger.info(f"Trying to invest a skillpoint for ally: {ally}")
        if ally is SkillpointHandler.AllyType.ROHANE:
            skillpoint_spend_url = self.ROHANE_SKILLPOINT_SPEND_TEMPLATE.format(skill_id)
        elif ally is SkillpointHandler.AllyType.MIPSY:
            skillpoint_spend_url = self.MIPSY_SKILLPOINT_SPEND_TEMPLATE.format(skill_id)
        elif ally is SkillpointHandler.AllyType.TALINIA:
            skillpoint_spend_url = self.TALINIA_SKILLPOINT_SPEND_TEMPLATE.format(skill_id)
        elif ally is SkillpointHandler.AllyType.VELM:
            skillpoint_spend_url = self.VELM_SKILLPOINT_SPEND_TEMPLATE.format(skill_id)
        else:
            logger.error("We did not receive a valid ally to spend a skillpoint for!")
            raise ValueError(f"Expected a valid ally name but got: {ally}")

        logger.info(f"Trying to invest a skillpoint for skill_id: {skill_id}")
        self.overworld_page.go_to_url_and_wait_navigation(skillpoint_spend_url)

        logger.info("Returning to main game page after spending skillpoint...")
        self.overworld_page.go_to_url_and_wait_navigation(SkillpointHandler.MAIN_GAME_URL)
        return True

    def try_spend_multiple_skillpoints(self, ally: AllyType, skill_id: int, num_points: int) -> None:
        logger.info(f"Attempting to spend {num_points} points for ally: {ally}")
        for i in range(num_points):
            self.try_spend_skillpoint(ally, skill_id)
