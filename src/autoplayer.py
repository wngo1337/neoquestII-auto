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
    skillpoint_handler: SkillpointHandler
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
        self.skillpoint_handler = SkillpointHandler(self.current_page)
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
                    self.skillpoint_handler.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE,
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
            self.skillpoint_handler.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.MELEE_HASTE.value)

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
        self.skillpoint_handler.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.MELEE_HASTE.value)
        # Sprint to Zombom and do NOT fight in the cave because the potion drops are extremely low
        self.follow_path("77777777777488844882222222622288888444447777774444488888888844888288848228444"
                         "77777771111517744362222222222222284453555511111222")
        # Finally, walk all the way back to Mipsy
        self.follow_path("222")
        self.follow_path("515155553555535533333666666333335555511117111555113555366666666666222222222222222222222226663")

    def complete_act1_step4_sand_grundo(self) -> None:
        pass
        # CANNOT IMPLEMENT UNTIL WE FIX UP THE ROHANE TURN CODE AND MIPSY TURN CODE
        # Recruit Mipsy and then try to invest her skillpoints into direct damage
        # self.npc_handler.recruit_mipsy()

        # Mipsy only has 58 HP at level 12 - long term investment, so put 11 into Direct Damage and don't touch it again
        # for i in range(11):
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.DIRECT_DAMAGE.value)

        # self.follow_path("48882")
        # self.grind_battles(150, "88")

        # for i in range(2):
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value)
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.MELEE_DEFENSE.value)

        # Walk from White River City to Fudra (we don't need anything from her, but you can buy)
        # self.follow_path("44444444744444448222222666666633333333366666666666666666666666663333517774")

        # Walk to Potraddo and talk to him
        # self.follow_path("33335555551155")
        # self.follow_path("41111111111111444444111111111111114444444111335333335633333333333322222")
        # self.npc_handler.talk_with_potraddo()

        # # Walk outside the town and train for a bit before heading over to the Lost City
        # self.follow_path("11177444444444478444448482633336622222222662666222222882222222888822222224444477777")
        # self.grind_battles(80)

        # We may only gain one level here, but still try to spend skillpoints
        # for i in range(2):
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value)
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.MELEE_DEFENSE.value)


        # self.follow_path("77777744488822266666666666638888")
        # # Must talk to the ghost to gain entry
        # self.npc_handler.talk_with_withered_ghost()
        # self.follow_path("888888888")
        # # Train inside the city for a bit because enemies after are quite dangerous if underleveled
        # self.grind_battles(180)

        # # Do not forget to spend skillpoints
        # for i in range(2):
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value)
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.MELEE_DEFENSE.value)
        #
        # self.follow_path("8888882844444444888882222228882222222284444444484")

        # Beat the Mutant Sand Grundo and enter the portal
        # NOTE: NOT SURE HOW MANY STEPS WE NEED TO TAKE!!!
        # self.follow_path("444")

    def complete_act1_step5_ramtor1(self) -> None:
        pass
    # self.grind_battles(200, "222")
    # for i in range(2):
    #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value)
    #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.MELEE_DEFENSE.value)
    # self.follow_path("22222222222287744447771177828448222222263333663333351151111562651111111174444477771717111111117777777447444448888888884888444444444777")

        # Lands us one tile below Uthare -> good upgrades, so buy
        # self.follow_path("1")
        # self.npc_handler.talk_with_uthare()
        # self.follow_path("2888844822")
        # self.npc_handler.talk_with_patannis()
        # self.follow_path("115533333333333")
        # self.grind_battles(200, "666")

        # self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value)
        # self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.MELEE_DEFENSE.value)

        # Now walk to Ramtor 1
        # self.follow_path("66666666666666666666666666222663633333335555555335511")

    def complete_act1_step6_ramtor2(self) -> None:
        # self.follow_path("22888888844444444")
        self.npc_handler.talk_with_guard_thyet()
        # Exit the castle, then walk to the tower
        # self.follow_path("844")
        self.follow_path("63333333333333366633333333333335555555555535335")
        # Train outside for a few levels
        self.grind_battles(100)
        self.follow_path("1111115533")
        self.grind_battles(160)
        for i in range(2):
            self.skillpoint_handler.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value)
            self.skillpoint_handler.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.MELEE_DEFENSE.value)
        self.follow_path("356228866334744477711177744477715515333666222366333551111115848888884444447446662666663332223")
        self.follow_path("33")

    def complete_act2_leximp_and_walk_cave(self) -> None:
        """
        Go to the cave and beat Leximp to get the wordstone. It is too much of a pain to actually buy stuff though.
        """
        pass
        # self.follow_path("44")
        # # Keep a reference to original path, but we don't need it
        # # self.follow_path("784444774744444488488288882288881555555555115553333636336333335644")
        # self.follow_path("7844447747444444884882888822888815555555551155533336363363333356")
        # self.grind_battles(200, "7844444")
        # self.follow_path("78444477474444441774474444444444447744444477444444444444444444444444444444477777777777771")

    def complete_act2_caves_of_terror(self) -> None:
        pass
        # self.follow_path("1")
        # self.grind_battles(300, "115")
        #
        # for i in range(4):
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE,
        #                                                  SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value)
        #     self.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.MIPSY,
        #                                                  SkillpointHandler.MipsySkill.CASTING_HASTE.value)

        # self.follow_path("1555533336663633633333555353533355777774444447444447774775553336335553353577711555177444447"
        #                  "444448447471111111117771178")
        #
        # self.follow_path("8")
        # self.npc_handler.recruit_talinia()

        # self.skillpoint_spender.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.RANGED_ATTACKS.value, 11)
        # self.skillpoint_spender.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.SHOCKWAVE.value, 11)
        # self.skillpoint_spender.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.MELEE_HASTE.value, 4)

    def complete_act2_kolvars_and_grind(self) -> None:
        pass
        # self.follow_path("553")
        # self.follow_path("55551155555555555555335333355333333555636333333355155366633336633363511777155366366626")
        # # Grind a bit to make sure we are ready for harder monsters up to camp
        # self.grind_battles(200)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value, 2)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.CASTING_HASTE.value, 2)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.MELEE_HASTE.value, 2)

        # # Fights Kolvars
        # self.follow_path("6")

        # # Walk to underneath the town
        # self.follow_path("666666666222268")

    def complete_act2_scuzzy(self) -> None:
        pass
        # # Walk all the way to beneath camp
        # self.follow_path("222822222888888888888444444444444444447444844444444888447774777747777711114")
        # Go rest at camp site to be safe
        # self.follow_path("57774")
        # self.npc_handler.talk_with_allden()
        # self.follow_path("33555111555")

        # Grind a LOT to be safe and get ready for Act 3
        # self.grind_battles(250, "555")
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value, 3)
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.CASTING_HASTE.value, 3)
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.MELEE_HASTE.value, 3)


        # Finally walk to Scuzzy
        # self.follow_path("7")
        # self.follow_path("353355553333355115355355117155553333533333333553662222266355111282844444711111115115333351"
        #                  "7447441111355555222666222888266665555555333333666666335555555355551111117171155333333333333333")
        #
        # self.follow_path("633363333636663622666228888444444444477")

        # Beat Scuzzy, but player is responsible for navigating back to the overworld
        self.follow_path("77")

    def complete_act3_siliclast(self) -> None:
        pass
        # # # Get out of the palace
        # # self.follow_path("3335553333333333")
        # # Begin walking to Siliclast
        # self.follow_path("1117777774444444444")
        # self.follow_path("1111111155335111533333333333333551118226222222844477777777777744444")
        # # Train for a bit to make sure we aren't underleveled because enemies can be quite dangerous
        # self.grind_battles(200)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.STUN.value, 4)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.GROUP_HASTE.value, 4)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.MAGIC_RESIST.value, 4)
        # self.follow_path("4444444888882222222222284826333333333351511111")

        # # Finally, beat Siliclast and step into portal
        # self.follow_path("5")
        # self.follow_path("111111")

        # EXTREMELY IMPORTANT NOTE: I DON'T THINK THIS ENDS AT THE STARTING POSITION OF THE NEXT SCRIPT!
        # MAY NEED TO WALK RIGHT TWO STEPS
        # self.follow_path("44")

    def complete_act3_gebarn(self) -> None:
        pass
        # # Walk out of palace again
        # self.follow_path("3335553333333333")
        # #
        # # # Walk to the temple
        # self.follow_path("111111111111774747711115511555155")
        # # Stop in middle to train a bit
        # self.follow_path("511111111155551111533588822228448222263336263622844444444711174777111111111177744222226333")
        # self.grind_battles(160)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.STUN.value, 2)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.GROUP_HASTE.value, 2)
        # self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.MAGIC_RESIST.value, 2)
        # self.follow_path("3335111115626822222222663335551117477715553344444448666688882222228")

        # self.follow_path("2222")
        # self.follow_path("44")

    def complete_act3_revenant(self) -> None:
        # self.follow_path("3335553333333333")
        # self.follow_path("1111111111774747711115511555")
        # self.follow_path("111111157")

        # self.follow_path("24884")

        # THIS PATH BELOW SEEMS INCORRECT!
        # # # self.follow_path("1711151144884")

        # self.npc_handler.recruit_velm()
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.HEAL.value, 11)
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.GROUP_SHIELD.value, 11)
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 11)
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.CASTING_HASTE.value, 4)

        # Leave Waset Village
        # self.follow_path("3555")
        self.follow_path("3333555555555553333666666666666666666622226223355")
