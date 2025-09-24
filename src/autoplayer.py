"""
This is the top level class of the autoplayer itself. May need one level higher for the program
launcher. It is composed of all individual components.

It should have a PageFactory instance so that it can generate and return pages based on what it
sees, and probably also a PageParser for handling the extraction of page info.
"""

import logging

from src.Pages.neopets_page import NeopetsPage
from src.Pages.overworld_page import OverworldPage
from src.battle_handler import BattleHandler
from src.inventory_handler import InventoryHandler
from src.login_handler import LoginHandler
from src.npc_handler import NpcHandler
from src.overworld_handler import OverworldHandler
from src.skillpoint_handler import SkillpointHandler

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
            # Need to actually ensure that we are on the overworld to use any game section completion methods

            self.battle_handler = BattleHandler(self.current_page, in_battle=False)
        else:
            self.battle_handler = BattleHandler(self.overworld_handler.overworld_page)
            if self.battle_handler.is_battle_start():
                self.battle_handler.start_battle()

            self.battle_handler.win_battle()
            self.current_page = self.battle_handler.end_battle()
        self.npc_handler = NpcHandler(self.current_page)
        self.skillpoint_handler = SkillpointHandler(self.current_page)
        self.inventory_handler = InventoryHandler(self.current_page)
        # self.inventory_handler = InventoryHandler()

    logger.info("Successfully created all autoplayer components!")

    def grind_battles(
            self, num_desired_steps: int, initial_path: str = None
    ) -> OverworldPage:
        """
        Walk for the desired number of steps in hunting mode and fight monsters to gain gold and experience.
        :param num_desired_steps: Number of steps to walk before stopping
        :param initial_path: Optional initial path to walk to training area - walk back after training is done
        """
        num_current_steps = 0
        if num_desired_steps % 2 != 0:
            raise ValueError(
                "The number of specified steps must be even so the battler returns"
                " to the tile it started on."
            )

        # If an initial path to walk is specified, follow it
        if initial_path:
            logger.info("Walking down the specified initial path before grinding...")
            self.follow_path(initial_path)

        # Enable hunting mode to find encounters
        self.overworld_handler.switch_movement_mode(
            OverworldHandler.MovementMode.HUNTING
        )

        while num_current_steps < num_desired_steps:
            if num_current_steps % 2 == 0:
                self.follow_path("3")
            else:
                self.follow_path("4")
            num_current_steps += 1
        logger.info("Finished grinding battles!")

        self.overworld_handler.switch_movement_mode(
            OverworldHandler.MovementMode.NORMAL
        )

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
                logger.info("Still on an overworld page after movement action")
                # We took a step and it is still the overworld
            elif self.overworld_handler.is_battle_start():
                logger.info("Entering a battle...")
                # We landed on a battle start page, so initialize the BattleHandler pages and win battle
                self.battle_handler.start_battle(self.overworld_handler.overworld_page)
                self.battle_handler.win_battle()
                self.overworld_handler.overworld_page = self.battle_handler.end_battle()
            else:
                # TODO: create and throw a new exception when movement results in an unknown page type
                raise Exception(
                    "We are not on either an overworld page or battle start page after a movement action!!!")
        return self.overworld_handler.overworld_page

    # def get_current_page_type(self):
    #     """
    #     This method feeds the current page object's HTML to a PageParser method and passes the result to a PageFactory.
    #     The PageFactory returns a page object of the most specific page type
    #     :return: a page object representing which game page the autoplayer is on
    #     """
    #     page_type = PageParser.get_page_type(self.current_page.get_page_content())

    def complete_act1_initial_training(self) -> None:
        """
        Starts from level 1 and takes one step northeast for 30 steps, battling along the way.
        After 30 steps, continue fighting for additional 220 steps for further leveling.
        Tries to spend skillpoints when possible.
        """
        self.follow_path("3333")
        self.overworld_handler.switch_movement_mode(
            OverworldHandler.MovementMode.HUNTING
        )
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
                # Should reach about level 5 here?
                if num_steps % 15 == 0:
                    self.skillpoint_handler.try_spend_skillpoint(
                        SkillpointHandler.AllyType.ROHANE,
                        SkillpointHandler.RohaneSkill.STUN.value,
                    )
                if num_steps <= 30:
                    # We are super weak and need to go back home to heal
                    # On iteration 30 after incrementing above, we want to do the town loop one more time
                    # This puts us into starting position for the actual movement script
                    self.follow_path("2666222866333")
                    self.npc_handler.set_npc_page(self.overworld_handler.overworld_page)
                    self.npc_handler.talk_with_mother()
                    self.follow_path("3333")

            # Finally, switch back to normal mode
        self.overworld_handler.switch_movement_mode(
            OverworldHandler.MovementMode.NORMAL
        )

    def complete_act2_miner_foreman(self) -> None:
        """
        Walk from outside of Trestin all the way to the Miner Foreman, stopping to train in the middle.
        Afterwards, walk to White River City.
        """
        self.follow_path("33333357111111117111111882")
        self.grind_battles(100)

        # Rohane: 7 stun
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.STUN.value,
            2,
        )

        self.follow_path(
            "882282288884444447444477777777771777448488226663666266222222226662222266333333333336333336666662"
        )
        # At this point, you are one tile ABOVE the Miner Foreman!
        # Walking one step down puts you into battle, one step further puts you to where he was
        self.follow_path("2222")
        # Now follow the given path to go from outside cave entrance to outside of uh... White City or something
        self.follow_path("84444444444444448444488888888444484444448")

    def complete_act1_zombom(self) -> None:
        # The Underground Cave drops close to zero potions for some reason
        # Get as close as we can to level 11 as possible before moving on
        # Pretty sure you can grind for hundreds of battles and still only reach level 11
        self.grind_battles(600, "7777")

        # Rohane: 10 stun
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.STUN.value,
            3,
        )
        # Sprint to Zombom and do NOT fight in the cave because the potion drops are extremely low
        # Go buy gear from Tebor
        self.follow_path("2666333")
        self.npc_handler.talk_with_tebor()
        self.inventory_handler.equip_equipment(
            InventoryHandler.IRON_SHORTSWORD_ID, InventoryHandler.AllyId.ROHANE.value
        )
        self.inventory_handler.equip_equipment(
            InventoryHandler.RUSTY_CHAIN_TUNIC_ID, InventoryHandler.AllyId.ROHANE.value
        )
        # Walk to the cave
        self.follow_path("447777")
        # Head all the way through to Zombom
        self.follow_path(
            "77777777777488844882222222622288888444447777774444488888888844888288848228444"
            "77777771111517744362222222222222284453555511111222"
        )
        # Finally, walk all the way back to Mipsy
        self.follow_path("222")
        self.follow_path(
            "515155553555535533333666666333335555511117111555113555366666666666222222222222222222222226663"
        )

        # Recruit Mipsy and then try to invest her skillpoints into direct damage
        self.npc_handler.recruit_mipsy()

        # Mipsy only has 58 HP at level 12 - can't get full value of direct damage right away
        # Mipsy: 11 direct damage - gained a level from Zombom I think
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.DIRECT_DAMAGE.value,
            11,
        )

    def complete_act1_sand_grundo(self) -> None:
        # Train in grass area for a bit
        self.follow_path("48882")
        self.grind_battles(200, "88")

        # Rohane: 13 stun
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.STUN.value,
            2,
        )
        # Mipsy: 13 direct damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.DIRECT_DAMAGE.value,
            2,
        )

        # Walk from White River City to Fudra (we don't need anything from her, but you can buy)
        self.follow_path(
            "44444444744444448222222666666633333333366666666666666666666666663333517774"
        )

        # Walk to Potraddo and talk to him
        self.follow_path("33335555551155")
        self.follow_path(
            "41111111111111444444111111111111114444444111335333335633333333333322222"
        )
        self.npc_handler.talk_with_potraddo()

        # Walk outside the town and train for a bit before heading over to the Lost City
        self.follow_path(
            "11177444444444478444448482633336622222222662666222222882222222888822222224444477777"
        )
        # I don't actually think we need to grind here, but ok
        self.grind_battles(100)

        self.follow_path("77777744488822266666666666638888")
        # Must talk to the ghost to gain entry
        self.npc_handler.talk_with_withered_ghost()
        self.follow_path("888888888")
        # Train inside the city for a bit because enemies after are quite dangerous if underleveled
        self.grind_battles(160)

        # Rohane: 13 stun, 2 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.MELEE_HASTE.value,
            2,
        )
        # Mipsy: 13 direct damage, 2 melee defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.MELEE_DEFENSE.value,
            2,
        )
        self.follow_path("8888882844444444888882222228882222222284444444484")

        # Beat the Mutant Sand Grundo and enter the portal
        self.follow_path("444")

    def complete_act1_ramtor1(self) -> None:
        self.grind_battles(200, "222")

        # Rohane: 13 stun, 4 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.MELEE_HASTE.value,
            2,
        )
        # Mipsy: 13 direct damage, 4 melee defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.MELEE_DEFENSE.value,
            2,
        )

        # Exit the tower and walk all the way to next town
        self.follow_path(
            "22222222222287744447771177828448222222263333663333351151111562651111111174444477771717111111117777777447"
            "444448888888884888444444444777"
        )

        # Lands us one tile below Uthare -> good upgrades, so buy
        self.follow_path("1")
        self.npc_handler.talk_with_uthare()
        self.follow_path("2888844822")
        self.npc_handler.talk_with_patannis()
        self.follow_path("115533333333333")
        self.grind_battles(100, "666")

        # Rohane: 13 stun, 5 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.MELEE_HASTE.value,
            1,
        )
        # Mipsy: 13 direct damage, 5 melee defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.MELEE_DEFENSE.value,
            1,
        )

        # Now walk to Ramtor 1
        self.follow_path("66666666666666666666666666222663633333335555555335511")

    def complete_act1_ramtor2(self) -> None:
        self.follow_path("22888888844444444")
        self.npc_handler.talk_with_guard_thyet()
        # Exit the castle, then walk to the tower
        self.follow_path("844")
        self.follow_path("63333333333333366633333333333335555555555535335")
        self.follow_path("1111115533")
        self.grind_battles(160)

        # Rohane: 13 stun, 7 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.MELEE_HASTE.value,
            2,
        )
        # Mipsy: 13 direct damage, 7 melee defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.MELEE_DEFENSE.value,
            2,
        )

        # Navigate through tower all the way to Ramtor
        self.follow_path(
            "356228866334744477711177744477715515333666222366333551111115848888884444447446662666663332223"
        )
        self.follow_path("33")

    def complete_act2_leximp_and_walk_cave(self) -> None:
        """
        Go to the cave and beat Leximp to get the wordstone. It is too much of a pain to actually buy stuff though.
        """

        self.follow_path("44")
        self.follow_path(
            "7844447747444444884882888822888815555555551155533336363363333356"
        )
        self.grind_battles(200, "7844444")

        # Rohane: 13 stun, 9 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.MELEE_HASTE.value,
            2,
        )
        # Mipsy: 13 direct damage, 9 melee defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.MELEE_DEFENSE.value,
            2,
        )

        # Walk through Terror Mountain overworld to cave entrance
        self.follow_path(
            "78444477474444441774474444444444447744444477444444444444444444444444444444477777777777771"
        )

    def complete_act2_caves_of_terror(self) -> None:
        self.follow_path("1")
        self.grind_battles(300, "115")

        # Rohane: 13 stun, 11 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.MELEE_HASTE.value,
            2,
        )
        # Mipsy: 13 direct damage, 11 melee defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.MELEE_DEFENSE.value,
            2,
        )

        # Long walk through cave and all the way out to Talinia at inn
        self.follow_path(
            "1555533336663633633333555353533355777774444447444447774775553336335553353577711555177444447"
            "444448447471111111117771178"
        )

        self.follow_path("8")
        self.npc_handler.recruit_talinia()

        # Talinia: 13 ranged attacks, 11 shockwave
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.RANGED_ATTACKS.value,
            13,
        )
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.SHOCKWAVE.value,
            11,
        )

    def complete_act2_kolvars_and_grind(self) -> None:
        # Leave town and walk to Kolvars
        self.follow_path("553")
        self.follow_path(
            "55551155555555555555335333355333333555636333333355155366633336633363511777155366366626"
        )
        # Grind a bit to make sure we are ready for harder monsters up to camp
        # Rohane 3 damage increase, mipsy 3 haste, talinia 2 haste so far
        self.grind_battles(200)

        # Rohane: 13 stun, 13 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.MELEE_HASTE.value,
            2,
        )
        # Mipsy: 13 direct damage, 13 melee defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.MELEE_DEFENSE.value,
            2,
        )
        # Talinia: 13 ranged attacks, 13 shockwave
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.SHOCKWAVE.value,
            2,
        )

        # Fights Kolvars
        self.follow_path("6")

        # Walk to underneath the town
        self.follow_path("666666666222268")

    def complete_act2_scuzzy(self) -> None:
        # # Walk all the way to beneath camp
        self.follow_path(
            "222822222888888888888444444444444444447444844444444888447774777747777711114"
        )
        # Go rest at camp site to be safe
        self.follow_path("57774")
        self.npc_handler.talk_with_allden()
        self.follow_path("33555111555")

        # Grind a LOT to be safe and get ready for Act 3
        self.grind_battles(250, "555")

        # Rohane: 13 stun, 13 haste, 3 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value,
            3,
        )
        # Mipsy: 13 direct damage, 13 melee defense, 3 group haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.GROUP_HASTE.value,
            3,
        )
        # Talinia: 13 ranged attacks, 13 shockwave, 3 melee haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.MELEE_HASTE.value,
            3,
        )

        # Finally walk to Scuzzy
        self.follow_path("7")
        self.follow_path(
            "353355553333355115355355117155553333533333333553662222266355111282844444711111115115333351"
            "7447441111355555222666222888266665555555333333666666335555555355551111117171155333333333333333"
        )

        self.follow_path("633363333636663622666228888444444444477")

        # Beat Scuzzy, but player is responsible for navigating back to the overworld
        self.follow_path("77")

    def complete_act3_siliclast(self) -> None:
        # # Get out of the palace
        self.follow_path("333555333333333")

        # Walk to equipment shop and buy welfare upgrades
        self.follow_path("3364")
        self.npc_handler.talk_with_sabaliz()

        # Return to next starting position
        self.follow_path("337444")

        # Equip the new equipment
        self.inventory_handler.equip_equipment(
            InventoryHandler.IRON_LONGSWORD_ID,
            InventoryHandler.AllyId.ROHANE.value,
        )
        self.inventory_handler.equip_equipment(
            InventoryHandler.STEEL_SPLINT_MAIL_ID, InventoryHandler.AllyId.ROHANE.value
        )

        self.inventory_handler.equip_equipment(
            InventoryHandler.ACOLYTE_ROBE_ID, InventoryHandler.AllyId.MIPSY.value
        )

        self.inventory_handler.equip_equipment(
            InventoryHandler.ASH_SHORT_BOW_ID, InventoryHandler.AllyId.TALINIA.value
        )
        self.inventory_handler.equip_equipment(
            InventoryHandler.REINFORCED_LEATHER_TUNIC_ID,
            InventoryHandler.AllyId.TALINIA.value,
        )

        # Begin walking to Siliclast
        self.follow_path("111777777")
        # Grind in the desert for a bit to make sure we aren't underleveled
        self.grind_battles(100)
        # Invest skillpoints if we have them

        # Rohane: 13 stun, 13 haste, 5 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value,
            2,
        )
        # Mipsy: 13 direct damage, 13 melee defense, 5 group haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.GROUP_HASTE.value,
            2,
        )
        # Talinia: 13 ranged attacks, 13 shockwave, 5 melee haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.MELEE_HASTE.value,
            2,
        )

        # Continue walking to Siliclast
        self.follow_path("4444444444")
        # Walk from entrance all the way to Siliclast
        self.follow_path(
            "1111111155335111533333333333333551118226222222844477777777777744444"
        )
        # Train for a bit to make sure we aren't underleveled because enemies can be quite dangerous
        self.grind_battles(150)

        # Rohane: 13 stun, 13 haste, 7 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value,
            2,
        )
        # Mipsy: 13 direct damage, 13 melee defense, 7 group haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.GROUP_HASTE.value,
            2,
        )
        # Talinia: 13 ranged attacks, 13 shockwave, 7 melee haste,
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.MELEE_HASTE.value,
            2,
        )
        self.follow_path("4444444888882222222222284826333333333351511111")

        # # Finally, beat Siliclast and step into portal
        self.follow_path("5")
        self.follow_path("111111")

        # MAY NEED TO WALK RIGHT TWO STEPS TO NEXT STARTING LOCATION
        self.follow_path("44")

    def complete_act3_gebarn(self) -> None:
        # Walk out of palace again
        self.follow_path("333555333333333")
        #
        # # Walk to the temple
        self.follow_path("111111111111774747711115511555155")
        # Stop in middle to train a bit
        self.follow_path(
            "511111111155551111533588822228448222263336263622844444444711174777111111111177744222226333"
        )
        self.grind_battles(100)

        # Rohane: 13 stun, 13 haste, 8 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value,
            1,
        )
        # Mipsy: 13 direct damage, 13 melee defense, 8 group haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.CASTING_HASTE.value,
            1,
        )
        # Talinia: 13 ranged attacks, 13 shockwave, 8 melee haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.MELEE_HASTE.value,
            1,
        )

        self.follow_path(
            "3335111115626822222222663335551117477715553344444448666688882222228"
        )

        self.follow_path("2222")
        self.follow_path("44")

    def complete_act3_revenant(self) -> None:
        # Walk from Gebarn portal exit to Velm
        self.follow_path("333555333333333")
        self.follow_path("11111111117747477111155115551711151144884")

        # Velm: 13 single heal, 13 group shield, 8 haste
        self.npc_handler.recruit_velm()
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.HEAL.value, 13
        )
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM,
            SkillpointHandler.VelmSkill.GROUP_SHIELD.value,
            13,
        )
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM,
            SkillpointHandler.VelmSkill.CASTING_HASTE.value,
            8,
        )

        # Leave Waset Village
        self.follow_path("3555")
        self.follow_path("3333555555555553333666666666666666666622226223355")
        # Small leadup to the actual temple entrance
        self.follow_path("53")
        self.follow_path(
            "555511155553335555111111753666371117748471777111111111111111111111111"
        )
        # Fight the revenant
        self.follow_path("1")

        # # NEED TO TALK TO THE PRINCESS BEFORE LEAVING!!!
        self.follow_path("17747")
        self.npc_handler.talk_with_lifira()
        # Walk one step below Lifira to next movement location
        self.follow_path("2")
        self.follow_path(
            "33333331544447777777777777777777111778848888888484444444744828477"
        )

        # This actually overshoots by quite a bit, but it is okay. Just walk backwards a bit...
        self.follow_path("6633")

        # Now talk with Lifira again
        self.follow_path("744828477")
        self.npc_handler.talk_with_lifira_part2()
        # Walk back out
        self.follow_path("663353552")

    def complete_act3_coltzan(self) -> None:
        self.follow_path("33355555555555511111111111111115555555333333333333332")
        self.npc_handler.talk_with_bukaru()
        # DON'T FORGET TO PICK UP MEDALLION HERE
        self.follow_path("77777777777777774444444444")
        self.npc_handler.get_medallion()
        self.grind_battles(100, "333")

        # Rohane: 13 stun, 13 haste, 9 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value,
            1,
        )
        # Mipsy: 13 direct damage, 13 melee defense, 9 group haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.GROUP_HASTE.value,
            1,
        )
        # Talinia: 13 ranged attacks, 13 shockwave, 9 melee haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.MELEE_HASTE.value,
            1,
        )
        # Velm: 13 single heal, 13 group shield, 9 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM,
            SkillpointHandler.VelmSkill.CASTING_HASTE.value,
            1,
        )

        # Walk from medallion location all the way to Coltzan
        self.follow_path(
            "22888888888888888888822222222228888888888444488888888882222222266663333355533551111111111111111111111111111555533333551111153351"
        )
        # Now fight Coltzan
        self.follow_path("1")
        # NOT SURE WE EVEN NEED TO TALK TO COLTZAN
        self.npc_handler.talk_with_coltzan()
        self.follow_path("75")
        self.npc_handler.get_medallion_centrepiece()
        # Back to second medallion location?
        self.follow_path(
            "2222848882222844884488822222222222222222222222262288884844444477771111111155555555555555511111111"
        )
        # Need to grab the medallion still
        self.npc_handler.get_medallion_gemstone()

    def complete_act3_pyramid(self) -> None:
        # # Walk from the gemstone spot to pyramid
        self.follow_path(
            "5515555333333335533666666666666622222222222888444888882222226666666666666666662222"
        )
        # DON'T FORGET TO GRIND A BIT INSIDE THE PYRAMID!
        self.follow_path(
            "33333511111111153333333333663333333553333333333622222222288444488444"
        )
        self.grind_battles(100)

        # Rohane: 13 stun, 13 haste, 11 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value,
            2,
        )
        # Mipsy: 13 direct damage, 13 melee defense, 11 group haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.GROUP_HASTE.value,
            2,
        )
        # Talinia: 13 ranged attacks, 13 shockwave, 11 melee haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.MELEE_HASTE.value,
            2,
        )
        # Velm: 13 single heal, 13 group shield, 11 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM,
            SkillpointHandler.VelmSkill.CASTING_HASTE.value,
            2,
        )

        self.follow_path(
            "444774884488848244488444488226633366223333333333333333333333333333111111115577712228844444444715333335511111782888747111111"
        )

        # Fight Anubits!
        self.follow_path("11")

    def complete_act4_meuka(self) -> None:
        # Walk to starting tile
        self.follow_path("628")

        # # Walk to Meuka
        self.follow_path("2628822222222822888844444477774777111111555111")
        self.follow_path("1111111111444444444444444444488222488844444444444711535533336251533363335111174448444")
        self.grind_battles(100)

        # Rohane: 13 stun, 13 haste, 13 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.DAMAGE_INCREASE.value, 2)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.CASTING_HASTE.value, 2)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.MELEE_HASTE.value, 2)
        # Velm: 13 single heal, 13 group shield, 13 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.CASTING_HASTE.value, 2)

        # I think this actually fights Meuka for you lol
        self.follow_path("448444888771115333311333")
        # Walk to Von Roo for next script start location
        self.follow_path("55")

    def complete_act4_spider_grundo(self) -> None:
        # Walk to the cave
        self.follow_path("5755774444444844844444474488222222222228884444777778844444444828844447115174448888447772")
        # Grind in the middle
        self.follow_path("4444448888888884444477777777488888822222228828222822626663363335355177474711533633333333333")
        self.grind_battles(100)

        # Rohane: 13 stun, 13 haste, 13 damage, 2 crit
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value, 2)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 2 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.CASTING_HASTE.value, 2)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 2 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.INCREASE_BOW_DAMAGE.value, 2)
        # Velm: 13 single heal, 13 group shield, 13 haste, 2 defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 2)

        self.follow_path("3333333333333333333388888888844444488844444882")
        # Beat Spider Grundo and then walk up to him again
        self.follow_path("22")

    def complete_act4_faeries(self) -> None:
        # Walk to Balthazar in the forest
        self.follow_path("63363333333333333633333622226662226662222222888226666663333333333335553")
        # Walk through the fun house and grind a lot to prep for faeries
        self.follow_path("5171111111111177747533")
        self.grind_battles(200)

        # Rohane: 13 stun, 13 haste, 13 damage, 4 crit
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value, 2)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 4 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.CASTING_HASTE.value, 2)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 4 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.INCREASE_BOW_DAMAGE.value, 2)
        # Velm: 13 single heal, 13 group shield, 13 haste, 4 defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 2)

        # Walk all the way through the rest of the funhouse and talk to everyone
        self.follow_path(
            "336633555117884444447777753366333553336222284862662844444717488847115117111111533663336263511174444411111")
        # NEED TO TALK TO THE BRAIN TREE!!!
        self.npc_handler.talk_with_brain_tree()
        # Now buy from Auger
        self.follow_path("33")
        self.npc_handler.talk_with_augur_faunt()
        self.follow_path("633336622222222222222222882222226265")
        # Walk left to fight the faeries -> might be too risky on InSaNe
        self.follow_path("3")

    def complete_act4_hubrid_nox(self) -> None:
        # Walk to Tower of Nox
        self.follow_path("55555555555555555533333333333333333336666666333555333666622288844747")
        # Enter and grind in the middle
        self.follow_path("111533351111784556222222228745562265111174475574444")
        self.grind_battles(60)

        # Rohane: 13 stun, 13 haste, 13 damage, 5 crit
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value, 1)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 5 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.CASTING_HASTE.value, 1)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 5 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.INCREASE_BOW_DAMAGE.value, 1)
        # Velm: 13 single heal, 13 group shield, 13 haste, 5 defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 1)

        # Walk up all the stairs to Nox
        self.follow_path(
            "4442226336663366447557753351114482222633628444444777115512263622226555111717748888226715333335")

        # Now fight Hubrid Nox
        # Ends in position that we need for next script
        self.follow_path("5")

    def complete_act4_esophagor(self) -> None:
        self.follow_path("3518826666666628888884444444444488478848888448488884")
        self.follow_path("44")

    def complete_act5_fallen_angel(self) -> None:
        # Walk from starting location to Fallen Angel
        self.follow_path("2222228888288888844444888888822222228688")
        self.follow_path("71")
        self.follow_path("66622222626262622666222288228222266633662888888447744482")
        # Should be at the Fallen Angel I think
        self.follow_path("84")

        # Start off where we beat Fallen Angel
        self.follow_path("4444884888222668282622288882282222286633")
        self.grind_battles(100)

        # Rohane: 13 stun, 13 haste, 13 damage, 7 crit
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE, SkillpointHandler.RohaneSkill.CRIT.value, 3)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 7 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY, SkillpointHandler.MipsySkill.CASTING_HASTE.value, 3)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 7 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA, SkillpointHandler.TaliniaSkill.INCREASE_BOW_DAMAGE.value, 3)
        # Velm: 13 single heal, 13 group shield, 13 haste, 7 defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM, SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 3)

        self.follow_path("33662222228882662226222844444474884447774482274777444488884")

    def complete_act5_devilpuss(self) -> None:
        # Walk halfway through Devilpuss location and train
        self.follow_path("48888444471117711747153333333335111111111174444444444444444444444444444822266222226333")
        self.grind_battles(80)
        # Rohane: 13 stun, 13 haste, 13 damage, 10 crit
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.ROHANE,
            SkillpointHandler.RohaneSkill.CRIT.value, 3)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 10 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.MIPSY,
            SkillpointHandler.MipsySkill.CASTING_HASTE.value, 3)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 10 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.TALINIA,
            SkillpointHandler.TaliniaSkill.INCREASE_BOW_DAMAGE.value,
            3)
        # Velm: 13 single heal, 13 group shield, 13 haste, 10 defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(
            SkillpointHandler.AllyType.VELM,
            SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 3)

        # Walk the rest of the location and fight
        self.follow_path(
            "3336622226636362222663333622288444482222844444444444444444444444447111111115333351111111774444")
        self.follow_path("4")

    def complete_act5_faerie_thief(self) -> None:
        # Walk to next town
        self.follow_path("4444477744447771555553535711777771144448")
        self.follow_path("2263")
        # Don't really want to buy weapon upgrades here... but we can pick them up for Rohane and Talinia to be safe
        self.npc_handler.talk_with_caereli()
        self.follow_path("477744822")
        # Whoops, this is just resting at the inn
        self.npc_handler.talk_with_deleri()
        self.follow_path("11536662222263")
        self.npc_handler.talk_with_mekava()
        self.follow_path("477711111144444444444446")

        # Go to Faerie Thief location
        # I think that surely you will get the Cybunny avatar from random encounters even on normal mode here
        self.follow_path("4477115555717177111151511117744488848884844747777771111111")
        self.npc_handler.talk_with_lusina()
        self.follow_path("711777774444447117444771111551111174482536263362228888866636224444")
        self.grind_battles(80)

        # Rohane: 13 stun, 13 haste, 13 damage, 12 crit
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.ROHANE,
                                                               SkillpointHandler.RohaneSkill.CRIT.value, 2)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 12 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.MIPSY,
                                                               SkillpointHandler.MipsySkill.CASTING_HASTE.value, 2)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 12 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA,
                                                               SkillpointHandler.TaliniaSkill.INCREASE_BOW_DAMAGE.value,
                                                               2)
        # Velm: 13 single heal, 13 group shield, 13 haste, 12 defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.VELM,
                                                               SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 2)
        self.follow_path("4448226333333333353")

        # Walk one step to fight Faerie Thief first encounter
        self.follow_path("3")
        self.follow_path("44844444444447115515357755555111744717484533622222882222223333362263333366633622263333333333")
        self.grind_battles(60)

        # Rohane: 13 stun, 13 haste, 13 damage, 13 crit
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.ROHANE,
                                                               SkillpointHandler.RohaneSkill.CRIT.value, 1)
        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 13 haste
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.MIPSY,
                                                               SkillpointHandler.MipsySkill.CASTING_HASTE.value, 1)
        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 13 damage
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA,
                                                               SkillpointHandler.TaliniaSkill.INCREASE_BOW_DAMAGE.value,
                                                               1)
        # Velm: 13 single heal, 13 group shield, 13 haste, 13 defense
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.VELM,
                                                               SkillpointHandler.VelmSkill.MELEE_DEFENSE.value, 1)
        self.follow_path("333333351115555117111744777111777748448222222447482666333362222217482222")
        self.follow_path("6")

        self.follow_path("7111153622111174444777156335711153356336622226663362262228888228444444444")
        self.grind_battles(80)

        # Use up all our remaining skill points here

        # Rohane: 13 stun, 13 haste, 13 damage, 13 crit, 7 magic resist
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.ROHANE,
                                                               SkillpointHandler.RohaneSkill.MAGIC_RESIST.value, 7)

        # Mipsy: 13 direct damage, 13 melee defense, 13 group haste, 13 haste, 7 damage shields
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.MIPSY,
                                                               SkillpointHandler.MipsySkill.DAMAGE_SHIELDS.value, 7)

        # Talinia: 13 ranged attacks, 13 shockwave, 13 melee haste, 13 damage, 7 magic resist
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.TALINIA,
                                                               SkillpointHandler.TaliniaSkill.MAGIC_RESIST.value,
                                                               7)
        # Velm: 13 single heal, 13 group shield, 13 haste, 13 defense, 7 celestial hammer
        self.skillpoint_handler.try_spend_multiple_skillpoints(SkillpointHandler.AllyType.VELM,
                                                               SkillpointHandler.VelmSkill.CELESTIAL_HAMMER.value, 7)
        self.follow_path("4444444851111111111535111111111111111111151171111177771")

        # Finally, fight the Faerie Thief last time
        self.follow_path("1")
        self.follow_path("11111111")

    def complete_act5_finale(self) -> None:
        self.npc_handler.talk_with_stenvela()
        # Walk through the huge maze to the next floor and to the next NPC
        self.follow_path(
            "44444447111177774471557444828711111533335555335111744444444447111111111153333333362222226333622222636636266263533368222284482222222"
            "63366333333335551111111111744784471111533351774877111555336665111111782877711174444447448444488211")
        self.npc_handler.talk_with_vitrini()
        # Go to right pant devil
        self.follow_path(
            "44444448882228444475335744444471115626335156222265351533688634477166632755744828487111178284471782226333333684486333355511153333333")
        # Go to left pant devil
        self.follow_path(
            "333333333333666222633335744753333335111782844717822447174482266284335518884251771153362633315626335156222844444486336844447111777444444444444")
        # IMPORTANT: must assemble key!
        self.npc_handler.talk_with_vitrini_key()
        self.follow_path(
            "44444448882228884444822222222226663333333333622222222228717444444444486334822636217884751533511533688226336211147")
        self.follow_path("11")
        # Centre between pillars
        self.follow_path("4")
        # Now walk all the way over
        self.follow_path(
            "1111111111111111117744444444447771111111111533335551115553333333333333333333666222666333362222222222888444444444482"
            "222222222263515711571533362222666226535511111111144863622284444822228444444451111111551533622222222263336")
        # Rest with Lyra - no need to buy potions since we are maxed from before
        self.npc_handler.talk_with_lyra()
        # One step before Terask II - leave to user to fight
        self.follow_path("511111111111528888888")
