import logging
import os
import sys
from unittest import case

import click
from autoplayer import Autoplayer
from playwright.sync_api import sync_playwright, BrowserContext

from Pages.neopets_page import NeopetsPage

# from page_parser import PageParser

import logging_config
from overworld_handler import OverworldHandler
from skillpoint_handler import SkillpointHandler

logger = logging.getLogger(__name__)

REQUIRED_DATA_DIR = "RequiredData"
ADBLOCK_DIR = "AdblockDir"
USER_DATA_DIR = "UserDataDir"

adblock_container_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", REQUIRED_DATA_DIR, ADBLOCK_DIR)
)

# List directories inside AdblockDir
subdirs = [
    dir_name
    for dir_name in os.listdir(adblock_container_path)
    if os.path.isdir(os.path.join(adblock_container_path, dir_name))
]

if len(subdirs) == 1:
    actual_adblock_folder_name = subdirs[0]
    full_adblock_path = os.path.join(adblock_container_path, actual_adblock_folder_name)
    logger.info(f"Full Adblock directory path: {full_adblock_path}")
else:
    logger.info(
        "AdblockDir contains multiple or no directories. It should only contain the Adblock extension folder!"
    )

full_user_data_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", REQUIRED_DATA_DIR, USER_DATA_DIR)
)
logger.info(f"Full user data directory for storage is: {full_user_data_path}")


class AutoplayerLauncher:
    """
    This is the highest level class for the project. It handles launching of the autoplayer and any
    flags or parameters that might be required.
    """

    autoplayer: Autoplayer

    def __init__(self, page: NeopetsPage, use_neopass: bool = False):
        self.autoplayer = Autoplayer(page, use_neopass)

    def show_menu(self, context: BrowserContext, autoplayer: Autoplayer) -> None:
        while True:
            print("Select a game section to complete or q to quit")
            print("1. Act 1 sections")
            print("2. Act 2 sections")
            print("3. Act 3 sections")
            print("4. Act 4 sections")
            print("5. Act 5 sections")
            print("6. Follow a custom path:")
            print("7. Grind battles")

            choice = input("Enter your choice: ").lower()

            match choice:
                case "q":
                    logger.info("Closing the autoplayer...")
                    context.close()
                    sys.exit(0)
                case "1":
                    print("Select an Act 1 subsection to complete: ")
                    print("1. Initial training grind")
                    print("2. Defeat Miner Foreman")
                    print("3. Defeat Zombom")
                    print("4. Defeat Mutant Sand Grundo")
                    print("5. Defeat Ramtor - first encounter")
                    print("6. Defeat Ramtor - second encounter")

                    subchoice = input(
                        "Enter your choice from Act 1 options or enter anything else to go back to menu: "
                    )

                    match subchoice:
                        case "1":
                            autoplayer.complete_act1_initial_training()
                        case "2":
                            autoplayer.complete_act2_miner_foreman()
                        case "3":
                            autoplayer.complete_act1_zombom()
                        case "4":
                            autoplayer.complete_act1_sand_grundo()
                        case "5":
                            autoplayer.complete_act1_ramtor1()
                        case "6":
                            autoplayer.complete_act1_ramtor2()
                        case _:
                            print(
                                "You did not select a valid option. Returning to main menu..."
                            )
                case "2":
                    print("Enter an Act 2 subsection to complete: ")
                    print("1. Defeat Leximp")
                    print("2. Caves of Terror + Talinia")
                    subchoice = input(
                        "Enter your choice from Act 2 options or enter anything else to go back to menu: "
                    )

                    match subchoice:
                        case "1":
                            self.autoplayer.complete_act2_leximp_and_walk_cave()


@click.command()
@click.option(
    "--use-neopass",
    is_flag=True,
    default=False,
    help="Use Neopass login method instead of traditional",
)
def main(use_neopass: bool) -> None:
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        context = p.chromium.launch_persistent_context(
            full_user_data_path,
            channel="chromium",
            headless=False,
            args=[
                f"--disable-extensions-except={full_adblock_path}",
                f"--load-extension={full_adblock_path}",
            ],
        )

        page = context.new_page()
        # page = browser.new_page()
        page.goto("https://www.neopets.com/games/nq2/nq2.phtml")
        neopets_page = NeopetsPage(page)

        if use_neopass:
            logger.info("Launching autoplayer with Neopass authentication...")
            launcher = AutoplayerLauncher(use_neopass=True, page=neopets_page)
        else:
            logger.info("Launching autoplayer with traditional authentication...")
            launcher = AutoplayerLauncher(use_neopass=False, page=neopets_page)

        prev_coordinates = (
            launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        )
        current_coordinates = (
            launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        )

        print(
            f"Do coordinates match after page refresh but no movement? {prev_coordinates == current_coordinates}"
        )

        launcher.autoplayer.follow_path("3")
        updated_coordinates = (
            launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        )

        print(
            f"Now do coordinates match after page refresh AND movement? {prev_coordinates == updated_coordinates}"
        )

        launcher.show_menu(context, launcher.autoplayer)

        # while True:
        #     launcher.autoplayer.follow_path(
        #         "78444477474444441774474444444444447744444477444444444444444444444444444444477777777777771"
        #     )
        #     launcher.autoplayer.follow_path(
        #         launcher.autoplayer.overworld_handler.invert_path(
        #             "78444477474444441774474444444444447744444477444444444444444444444444444444477777777777771"
        #         )
        #     )

        # while True:
        #     launcher.autoplayer.follow_path("3241")
        #     logger.info(
        #         "Completed an iteration of debugging movement! If we don't end up under the sign, something went wrong"
        #     )

        # coords1 = launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # launcher.autoplayer.overworld_handler.overworld_page.page_instance.reload()
        # coords2 = launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # if coords1 == coords2:
        #     logger.info("Overworld map HTML doesn't change even on page refresh, which is good.")

        # TODO: call method to win battle and ensure we are on overworld page

        # launcher.autoplayer.complete_act1_step1_training()
        # THIS METHOD DOESN'T HAVE THE FIGHTING OF THE MINER FOREMAN YET!!!
        # launcher.autoplayer.complete_act1_step1_training()
        # launcher.autoplayer.complete_act1_step2_miner_foreman()
        # launcher.autoplayer.complete_act1_step3_zombom()
        # launcher.autoplayer.complete_act1_step4_sand_grundo()
        # launcher.autoplayer.complete_act1_step6_ramtor2()
        # launcher.autoplayer.complete_act2_leximp_and_walk_cave()
        # launcher.autoplayer.complete_act2_caves_of_terror()
        # launcher.autoplayer.complete_act2_kolvars_and_grind()
        # launcher.autoplayer.complete_act2_scuzzy()
        # launcher.autoplayer.complete_act3_siliclast()
        # launcher.autoplayer.complete_act3_gebarn()
        # launcher.autoplayer.complete_act3_revenant()
        # launcher.autoplayer.complete_act3_coltzan()
        # launcher.autoplayer.complete_act3_pyramid()
        # launcher.autoplayer.complete_act4_meuka()
        # launcher.autoplayer.complete_act4_spider_grundo()
        # launcher.autoplayer.complete_act4_faeries()
        # launcher.autoplayer.complete_act4_hubrid_nox()
        # launcher.autoplayer.complete_act4_esophagor()
        # launcher.autoplayer.complete_act5_fallen_angel()
        # launcher.autoplayer.complete_act5_devilpuss()
        # launcher.autoplayer.complete_act5_faerie_thief()
        # launcher.autoplayer.complete_act5_finale()

        context.close()

        # coords = launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # launcher.autoplayer.overworld_handler.overworld_page.page_instance.reload()
        # new_coords = launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        #
        # print(f"Coords list is: {coords}")
        # print(f"New coords list after refresh is: {new_coords}")
        # print(f"Are they equal? -> {set(coords) == set(new_coords)}")

        # launcher.autoplayer.grind_battles(100, "7777")

        # launcher.autoplayer.follow_path("3333")
        # launcher.autoplayer.overworld_handler.switch_movement_mode(OverworldHandler.MovementMode.HUNTING)
        # # Need a way to identify if we are low HP and go back home to heal
        # # num_completed_battles = 0
        # num_steps = 0
        # while num_steps < 250:
        #     if num_steps < 30:
        #         # Only walk one step upwards so we can heal in the next step
        #         # The last step will increment to 30, making this condition False from then on
        #         launcher.autoplayer.follow_path("7")
        #         num_steps += 1
        #     else:
        #         # Should be strong enough to survive with healing from potions
        #         # Grind outside of town and return to original starting tile at end
        #         launcher.autoplayer.follow_path("12")
        #         num_steps += 2
        #     if launcher.autoplayer.overworld_handler.is_overworld():
        #         # Every 15 battles, try to spend a skillpoint for easier progress
        #         if num_steps % 15 == 0:
        #             launcher.autoplayer.skillpoint_spender.try_spend_skillpoint(SkillpointHandler.AllyType.ROHANE,
        #                                                                     SkillpointHandler.RohaneSkill.MELEE_HASTE.value)
        #         if num_steps <= 30:
        #             # We are super weak and need to go back home to heal
        #             # On iteration 30 after incrementing above, we want to do the town loop one more time
        #             # This puts us into starting position for the actual movement script
        #             launcher.autoplayer.follow_path("2666222866333")
        #             launcher.autoplayer.npc_handler.set_npc_page(launcher.autoplayer.overworld_handler.overworld_page)
        #             launcher.autoplayer.npc_handler.talk_with_mother()
        #             launcher.autoplayer.follow_path("3333")

        # else:
        #     continue
        # else:
        #     launcher.autoplayer.battle_handler.start_battle(launcher.autoplayer.overworld_handler.overworld_page)
        #     launcher.autoplayer.battle_handler.win_battle()
        #     launcher.autoplayer.overworld_handler.overworld_page = launcher.autoplayer.battle_handler.end_battle()
        #     num_completed_battles += 1

        # launcher.autoplayer.grind_battles(num_desired_battles=50)
        # launcher.autoplayer.follow_path("34343434")

        # print(
        #     launcher.autoplayer.battle_handler.battle_page.get_available_healing_potions()
        # )
        #
        # launcher.autoplayer.battle_handler.battle_page.get_character_hp_vals()
        # launcher.autoplayer.battle_handler.win_battle()
        # launcher.autoplayer.battle_handler.end_battle()

        # launcher.autoplayer.battle_handler.handle_rohane_turn()
        # launcher.autoplayer.battle_handler.battle_page.get_character_hp_vals()
        # print(launcher.autoplayer.battle_handler.battle_page.get_next_actor_id())
        # launcher.autoplayer.battle_handler.start_battle()
        # launcher.autoplayer.battle_handler.battle_page.get_character_hp_vals()
        # launcher.autoplayer.battle_handler.get_actor_turn_type()

        # What we will do is create a run method and then let the autoplayer be responsible for
        # launcher.autoplayer.run_autoplayer()
        # launcher.autoplayer.overworld_handler.take_step("1")
        # launcher.autoplayer.overworld_handler.take_step("2")
        # launcher.autoplayer.overworld_handler.take_step("1")
        # launcher.autoplayer.overworld_handler.take_step("2")
        #
        # launcher.autoplayer.overworld_handler.switch_movement_mode(
        #     OverworldHandler.MovementMode.HUNTING
        # )
        # launcher.autoplayer.overworld_handler.switch_movement_mode(
        #     OverworldHandler.MovementMode.NORMAL
        # )
        #
        # launcher.autoplayer.overworld_handler.open_inventory()
        # Needs a page reset to prev page
        # launcher.autoplayer.overworld_handler.open_options()

        # print(
        #     PageParser.parse_html(
        #         launcher.autoplayer.current_page.page_instance.content()
        #     )
        # )

        # Since we initialize the login_handler here
        # Should navigate to the Neopets home page


if __name__ == "__main__":
    main()
