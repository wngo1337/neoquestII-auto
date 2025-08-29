import logging
import os

import click
from autoplayer import Autoplayer
from playwright.sync_api import sync_playwright

from Pages.neopets_page import NeopetsPage

import logging_config
from overworld_handler import OverworldHandler

logger = logging.getLogger(__name__)


class AutoplayerLauncher:
    """
    This is the highest level class for the project. It handles launching of the autoplayer and any
    flags or parameters that might be required.
    """

    autoplayer: Autoplayer

    def __init__(self, page: NeopetsPage, use_neopass: bool = False):
        self.autoplayer = Autoplayer(page, use_neopass)


@click.command()
@click.option(
    "--use-neopass",
    is_flag=True,
    default=False,
    help="Use Neopass login method instead of traditional",
)
def main(use_neopass: bool) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = browser.new_page()
        page.goto("https://www.neopets.com/")
        neopets_page = NeopetsPage(page)

        if use_neopass:
            logger.info("Launching autoplayer with Neopass authentication...")
            launcher = AutoplayerLauncher(use_neopass=True, page=neopets_page)
        else:
            logger.info("Launching autoplayer with traditional authentication...")
            launcher = AutoplayerLauncher(use_neopass=False, page=neopets_page)

        # TODO: call method to win battle and ensure we are on overworld page

        # What we will do is create a run method and then let the autoplayer be responsible for
        # launcher.autoplayer.run_autoplayer()
        launcher.autoplayer.overworld_handler.take_step("1")
        launcher.autoplayer.overworld_handler.take_step("2")
        launcher.autoplayer.overworld_handler.take_step("1")
        launcher.autoplayer.overworld_handler.take_step("2")

        launcher.autoplayer.overworld_handler.switch_movement_mode(
            OverworldHandler.MovementMode.HUNTING
        )
        launcher.autoplayer.overworld_handler.switch_movement_mode(
            OverworldHandler.MovementMode.NORMAL
        )

        # NEED TO GO TO GAME MAIN PAGE AND CONFIRM OVERWORLD???JJ

        # At this point, we are authenticated and can retrieve page from login_handler
        # Should be on the game index page

        # Since we initialize the login_handler here
        # Should navigate to the Neopets home page


if __name__ == "__main__":
    main()
