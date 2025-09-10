"""
This is the top level class of the autoplayer itself. May need one level higher for the program
launcher. It is composed of all individual components.

It should have a PageFactory instance so that it can generate and return pages based on what it
sees, and probably also a PageParser for handling the extraction of page info.
"""

from login_handler import LoginHandler
from overworld_handler import OverworldHandler
from battle_handler import BattleHandler
from skillpoint_handler import SkillpointHandler
from inventory_handler import InventoryHandler
from npc_handler import NpcHandler
from Pages.neopets_page import NeopetsPage
from Pages.overworld_page import OverworldPage

import logging

from page_parser import PageParser

logger = logging.getLogger(__name__)


class Autoplayer:
    login_handler: LoginHandler
    overworld_handler: OverworldHandler
    battle_handler: BattleHandler
    skillpoint_spender: SkillpointHandler
    inventory_handler: InventoryHandler

    current_page: NeopetsPage

    def __init__(self, page: NeopetsPage, use_neopass: bool = False) -> None:
        self.login_handler = LoginHandler(page, use_neopass)
        self.current_page = self.login_handler.login_and_go_to_game()
        self.overworld_handler = OverworldHandler(self.current_page)
        if self.overworld_handler.is_overworld():
        # JUST KIDDING, WE NEED TO ENSURE THAT WE ARE ON THE OVERWORLD HERE, NOT IN THE MAIN METHOD

        # WE NEED TO ENSURE THAT LOGIN HANDLER IS LOADED BEFORE WE LOAD UP THE PAGE REFERENCE
        # ORRR WE COULD MAKE A GLOBAL PAGE REFERENCE HERE SO EACH OBJECT CAN ACCESS THE CURRENT PAGE

            self.battle_handler = BattleHandler(self.current_page, in_battle=False)
        else:
            self.battle_handler = BattleHandler(self.overworld_handler.overworld_page)
            if self.battle_handler.is_battle_start():
                self.battle_handler.start_battle()

            self.battle_handler.win_battle()
            self.current_page = self.battle_handler.end_battle()
        # if not self.overworld_handler.is_overworld():
        #     if not self.battle_handler.battle_start_page.is_battle_start():
        #         self.battle_handler.win_battle()
        #         self.battle_handler.end_battle()
        #     else:
        #         self.battle_handler.start_battle()
        #         self.battle_handler.win_battle()
        #         self.battle_handler.end_battle()
        self.npc_handler = NpcHandler(self.current_page)
        # THIS IS NOT INITIALIZED ON THE CORRECT PAGE!!!
        self.skillpoint_spender = SkillpointHandler(self.current_page)
        self.inventory_handler = InventoryHandler()

    logger.info("Successfully created all autoplayer components!")

    def grind_battles(self, num_desired_steps: int, initial_path: str = None) -> OverworldPage:
        """
        Walk for the desired number of steps in hunting mode and fight monsters to gain gold and experience.
        """
        num_current_steps = 0
        num_completed_battles = 0
        if num_desired_steps % 2 != 0:
            raise ValueError("The number of specified steps must be even so the battler returns"
                             " to the tile it started on.")

        # If an initial path to walk is specified, follow it
        if initial_path:
            logger.info("Walking down the specified initial path before grinding...")
            self.follow_path(initial_path)

        # Enable hunting mode to find encounters
        self.overworld_handler.switch_movement_mode(OverworldHandler.MovementMode.HUNTING)

        while num_current_steps < num_desired_steps:
            if num_current_steps % 2 == 0:
                self.follow_path("3")
            else:
                self.follow_path("4")
            num_current_steps += 1
        logger.info("Grinding complete!")

        logger.info("Returning to normal movement mode...")
        self.overworld_handler.switch_movement_mode(OverworldHandler.MovementMode.NORMAL)

        if initial_path:
            logger.info("Walking back from the specified initial path...")
            inverted_path = self.overworld_handler.invert_path(initial_path)
            self.follow_path(inverted_path)

        logger.info("We have finished training!")
        return self.overworld_handler.overworld_page

    def follow_path(self, path: str) -> OverworldPage:
        """
        This method lets the user follow an arbitrary path, fighting enemies that they encounter along the way.
        :param path: a string of numbers representing the directions to follow
        :return: a string representing summary details of the path followed (steps, enemies fought, etc.)
        """
        for step in path:
            self.overworld_handler.take_step(step)
            if self.overworld_handler.is_overworld():
                # We took a step and it is still the overworld
                continue
            else:
                self.battle_handler.start_battle(self.overworld_handler.overworld_page)
                self.battle_handler.win_battle()
                self.overworld_handler.overworld_page = self.battle_handler.end_battle()
        return self.overworld_handler.overworld_page

    def get_current_page_type(self):
        """
        This method feeds the current page object's HTML to a PageParser method and passes the result to a PageFactory.
        The PageFactory returns a page object of the most specific page type
        :return: a page object representing which game page the autoplayer is on
        """
        page_type = PageParser.get_page_type(self.current_page.get_page_content())

    def complete_act1_step1_training(self) -> None:
        """
        Starts from level 1 and takes one step northeast for 30 steps, battling along the way.
        After 30 steps, continue fighting for additional 220 steps for further leveling.
        Tries to spend skillpoints when possible.
        """
        self.follow_path("3333")
        self.overworld_handler.switch_movement_mode(OverworldHandler.MovementMode.HUNTING)
        # Need a way to identify if we are low HP and go back home to heal
        # num_completed_battles = 0
        num_steps = 0
        while num_steps < 180:
            if num_steps < 30:
                # Only walk one step upwards so we can heal in the next step
                # The last step will increment to 30, making this condition False from then on
                self.follow_path("7")
                num_steps += 1
            else:
                # Should be strong enough to survive with healing from potions
                # Grind outside of town and return to original starting tile at end
                self.follow_path("12")
                num_steps += 2
            if self.overworld_handler.is_overworld():
                # Every 15 battles, try to spend a skillpoint for easier progress
                if num_steps % 15 == 0:
                    self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE,
                                                                                SkillpointHandler.RohaneSkill.MELEE_HASTE.value)
                if num_steps <= 30:
                    # We are super weak and need to go back home to heal
                    # On iteration 30 after incrementing above, we want to do the town loop one more time
                    # This puts us into starting position for the actual movement script
                    self.follow_path("2666222866333")
                    self.npc_handler.set_npc_page(self.overworld_handler.overworld_page)
                    self.npc_handler.talk_with_mother()
                    self.follow_path("3333")

            # Finally, switch back to normal mode
        self.overworld_handler.switch_movement_mode(OverworldHandler.MovementMode.NORMAL)

    def complete_act1_step2_miner_foreman(self) -> None:
        """
        Walk from outside of Trestin all the way to the Miner Foreman, stopping to train in the middle.
        Afterwards, walk to White River City.
        """
        self.follow_path("33333357111111117111111882")
        self.grind_battles(100)

        for i in range(0, 2):
            self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.MELEE_HASTE.value)

        self.follow_path("882282288884444447444477777777771777448488226663666266222222226662222266333333333336333336666662")
        # At this point, you are one tile ABOVE the Miner Foreman!
        # Walking one step down puts you into battle, one step further puts you to where he was
        self.follow_path("2222")
        # Now follow the given path to go from outside cave entrance to outside of uh... White City or something
        self.follow_path("84444444444444448444488888888444484444448")

    def complete_act1_step3_zombom(self) -> None:
        # The Underground Cave drops close to zero potions for some reason
        # Get as close as we can to level 11 as possible before moving on
        self.grind_battles(300, "7777")
        self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.MELEE_HASTE.value)
        # Sprint to Zombom and do NOT fight in the cave because the potion drops are extremely low
        self.follow_path("77777777777488844882222222622288888444447777774444488888888844888288848228444"
                         "77777771111517744362222222222222284453555511111222")
        # Finally, walk all the way back to Mipsy
        self.follow_path("222")
        self.follow_path("515155553555535533333666666333335555511117111555113555366666666666222222222222222222222226663")

    def complete_act1_step4_sand_grundo(self) -> None:
        # CANNOT IMPLEMENT UNTIL WE FIX UP THE ROHANE TURN CODE AND MIPSY TURN CODE
        pass
