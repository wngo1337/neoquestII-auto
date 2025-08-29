"""
This is the top level class of the autoplayer itself. May need one level higher for the program
launcher. It is composed of all individual components.

It should have a PageFactory instance so that it can generate and return pages based on what it
sees, and probably also a PageParser for handling the extraction of page info.
"""

from login_handler import LoginHandler
from overworld_handler import OverworldHandler
from battle_handler import BattleHandler
from skillpoint_handler import SkillpointSpender
from inventory_handler import InventoryHandler
from Pages.neopets_page import NeopetsPage

import logging

logger = logging.getLogger(__name__)


class Autoplayer:
    login_handler: LoginHandler
    overworld_handler: OverworldHandler
    battle_handler: BattleHandler
    skillpoint_spender: SkillpointSpender
    inventory_handler: InventoryHandler

    current_page: NeopetsPage

    def __init__(self, page: NeopetsPage, use_neopass: bool = False) -> None:
        self.login_handler = LoginHandler(page, use_neopass)
        self.current_page = self.login_handler.login_and_go_to_game()

        self.overworld_handler = OverworldHandler(self.current_page)
        # JUST KIDDING, WE NEED TO ENSURE THAT WE ARE ON THE OVERWORLD HERE, NOT IN THE MAIN METHOD

        # WE NEED TO ENSURE THAT LOGIN HANDLER IS LOADED BEFORE WE LOAD UP THE PAGE REFERENCE
        # ORRR WE COULD MAKE A GLOBAL PAGE REFERENCE HERE SO EACH OBJECT CAN ACCESS THE CURRENT PAGE

        self.battle_handler = BattleHandler()
        self.skillpoint_spender = SkillpointSpender()
        self.inventory_handler = InventoryHandler()

    logging.info("Mike Oxlong created an autoplayer instance. That's crazy")

    # def run_autoplayer(self) -> None:
    #     """
    #     This method should provide a list of menu options that the user can select from to perform a task.
    #     These tasks should include predefined tasks like beating the Miner Foreman, but also generic
    #     tasks like grinding levels or walking an arbitrary route.
    #     """
    #     logging.info("We called the autoplayer run method!")

    def follow_path(self, path: str) -> str:
        """
        This method lets the user follow an arbitrary path, fighting enemies that they encounter along the way.
        :param path: a string of numbers representing the directions to follow
        :return: a string representing summary details of the path followed (steps, enemies fought, etc.)
        """
        return "oxlong"
