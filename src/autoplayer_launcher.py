import logging
import os
import sys

import click
from playwright.sync_api import sync_playwright, BrowserContext

import src.logging_config
from src.Pages.neopets_page import NeopetsPage
from src.autoplayer import Autoplayer

# Hack to keep Pycharm from deleting my import...
_ = src.logging_config
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
    raise ValueError(
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

                    act1_subchoice = input(
                        "Enter your choice from Act 1 options or enter anything else to go back to menu: "
                    )

                    match act1_subchoice:
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
                    print("Enter an Act 2 subsection to complete:")
                    print("1. Defeat Leximp")
                    print("2. Caves of Terror + Talinia")
                    print("3. Kolvars + grind")
                    print("4. Lost Caves grind + Scuzzy")

                    act2_subchoice = input(
                        "Enter your choice from Act 2 options or enter anything else to go back to menu: "
                    )

                    match act2_subchoice:
                        case "1":
                            self.autoplayer.complete_act2_leximp_and_walk_cave()
                        case "2":
                            self.autoplayer.complete_act2_caves_of_terror()
                        case "3":
                            self.autoplayer.complete_act2_kolvars_and_grind()
                        case "4":
                            self.autoplayer.complete_act2_scuzzy()
                        case _:
                            print(
                                "You did not select a valid option. Returning to main menu..."
                            )

                case "3":
                    print("Enter and Act 3 subsection to complete:")
                    print("1. Grind + defeat Siliclast")
                    print("2. Grind + defeat Gebarn II")
                    print("3. GET VELM + defeat Revenant + gemstone stuff?")
                    print("4. Defeat Coltzan + do gemstone stuff")
                    print("5. Go to pyramid and fight Anubits")

                    act3_subchoice = input(
                        "Enter your choice from Act 3 options or enter anything else to go back to menu: "
                    )

                    match act3_subchoice:
                        case "1":
                            self.autoplayer.complete_act3_siliclast()
                        case "2":
                            self.autoplayer.complete_act3_gebarn()
                        case "3":
                            self.autoplayer.complete_act3_revenant()
                        case "4":
                            self.autoplayer.complete_act3_coltzan()
                        case "5":
                            self.autoplayer.complete_act3_pyramid()
                        case _:
                            print(
                                "You did not select a valid option from Act 3 choices. Returning to main menu..."
                            )

                case "4":
                    print("Select an Act 4 subsection to complete:")
                    print("1. Defeat Meuka")
                    print("2. Defeat Spider Grundo")
                    print("3. Complete Four Faeries sequence + boss fight")
                    print("4. Defeat Hubrid Nox")
                    print("5. Defeat Esophagor")

                    act4_subchoice = input(
                        "Enter your choice from Act 4 options or enter anything else to go back to menu: "
                    )

                    match act4_subchoice:
                        case "1":
                            self.autoplayer.complete_act4_meuka()
                        case "2":
                            self.autoplayer.complete_act4_spider_grundo()
                        case "3":
                            self.autoplayer.complete_act4_faeries()
                        case "4":
                            self.autoplayer.complete_act4_hubrid_nox()
                        case "5":
                            self.autoplayer.complete_act4_esophagor()
                        case _:
                            print(
                                "You did not select a valid Act 4 option. Returning to main menu..."
                            )

                case "5":
                    print("Select an Act 5 subsection to complete:")
                    print("1. Defeat the Fallen Angel")
                    print("2. Defeat Devilpuss")
                    print("3. Complete Faerie Thief questline and all running around")
                    print(
                        "4. Complete act 5 Finale -> does NOT include King Terask II fight"
                    )

                    act5_subchoice = input(
                        "Enter your choice from Act 5 options or enter anything else to go back to menu: "
                    )

                    match act5_subchoice:
                        case "1":
                            self.autoplayer.complete_act5_fallen_angel()
                        case "2":
                            self.autoplayer.complete_act5_devilpuss()
                        case "3":
                            self.autoplayer.complete_act5_faerie_thief()
                        case "4":
                            self.autoplayer.complete_act5_finale()
                        case _:
                            print(
                                "You did not select a valid Act 5 option. Returning to main menu..."
                            )

                case "6":
                    movement_path = input("Enter the path that you would like to follow: ")
                    if movement_path.isnumeric():
                        self.autoplayer.follow_path(movement_path)
                    else:
                        print("You did not enter a valid movement path. Returning to main menu...")

                case "7":
                    num_steps = input("Enter the number of steps that you would like to train for: ")
                    if num_steps.isnumeric():
                        num_steps_val = int(num_steps)
                        if int(num_steps_val) > 0 and int(num_steps_val) < 1000:
                            self.autoplayer.grind_battles(num_steps_val)
                        else:
                            print(
                                "That number of steps seems to large or too small. You would never need to train more than 1000 steps!")
                    else:
                        print("You did not enter a numeric value. Returning to main menu...")


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

        launcher.show_menu(context, launcher.autoplayer)

        # prev_coordinates = (
        #     launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # )
        # current_coordinates = (
        #     launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # )
        #
        # print(
        #     f"Do coordinates match after page refresh but no movement? {prev_coordinates == current_coordinates}"
        # )
        #
        # launcher.autoplayer.follow_path("3")
        # updated_coordinates = (
        #     launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # )
        #
        # print(
        #     f"Now do coordinates match after page refresh AND movement? {prev_coordinates == updated_coordinates}"
        # )

        # coords1 = launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # launcher.autoplayer.overworld_handler.overworld_page.page_instance.reload()
        # coords2 = launcher.autoplayer.overworld_handler.get_overworld_map_coordinates()
        # if coords1 == coords2:
        #     logger.info("Overworld map HTML doesn't change even on page refresh, which is good.")


if __name__ == "__main__":
    main()
