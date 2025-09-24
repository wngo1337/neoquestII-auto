from __future__ import annotations

import logging
import re
import time
from typing import List

from playwright.sync_api import Page, Locator, TimeoutError

from src.Pages.neopets_page import NeopetsPage

logger = logging.getLogger(__name__)


class OverworldPage(NeopetsPage):
    """
    Page object model representing the NeoQuest II overworld page.
    Holds element locators and keeps references to UI buttons
    """

    SWITCH_NORMAL_NODE_URL = (
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=travel&mode=1"
    )
    SWITCH_HUNTING_MODE_URL = (
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=travel&mode=2"
    )

    MAIN_GAME_URL = r"https://www.neopets.com/games/nq2/nq2.phtml"

    MOVEMENT_URL_TEMPLATE = (
        r"https://www.neopets.com/games/nq2/nq2.phtml?act=move&dir={0}"
    )

    GAME_CONTAINER_LOCATOR = "div.phpGamesNonPortalView"
    NAVIGATION_BUTTONS_GRID_LOCATOR = r"img[src='//images.neopets.com/nq2/x/nav.gif']"

    # Class variables: selectors for elements - shared by all instances
    NORTH_LOCATOR = 'area[alt="North"]'
    SOUTH_LOCATOR = 'area[alt="South"]'
    WEST_LOCATOR = 'area[alt="West"]'
    EAST_LOCATOR = 'area[alt="East"]'
    NORTHWEST_LOCATOR = 'area[alt="Northwest"]'
    SOUTHWEST_LOCATOR = 'area[alt="Southwest"]'
    NORTHEAST_LOCATOR = 'area[alt="Northeast"]'
    SOUTHEAST_LOCATOR = 'area[alt="Southeast"]'

    NORMAL_MODE_LOCATOR = r"a[href='nq2.phtml?act=travel&mode=1']"
    HUNTING_MODE_LOCATOR = r"a[href='nq2.phtml?act=travel&mode=2']"

    INVENTORY_LOCATOR = r"a[href='nq2.phtml?act=inv']"

    OPTIONS_LOCATOR = r"a[href='nq2.phtml?act=opt']"

    def __init__(self, neopets_page_instance: Page):
        super().__init__(neopets_page_instance)

        # Instance variables: actual element handles referencing the DOM elements

        self.nav_map = self.page_instance.locator(self.NAVIGATION_BUTTONS_GRID_LOCATOR)
        self.north_button = self.page_instance.locator(self.NORTH_LOCATOR)
        self.south_button = self.page_instance.locator(self.SOUTH_LOCATOR)
        self.west_button = self.page_instance.locator(self.WEST_LOCATOR)
        self.east_button = self.page_instance.locator(self.EAST_LOCATOR)
        self.northwest_button = self.page_instance.locator(self.NORTHWEST_LOCATOR)
        self.southwest_button = self.page_instance.locator(self.SOUTHWEST_LOCATOR)
        self.northeast_button = self.page_instance.locator(self.NORTHEAST_LOCATOR)
        self.southeast_button = self.page_instance.locator(self.SOUTHEAST_LOCATOR)

        self.normal_mode_button = self.page_instance.locator(self.NORMAL_MODE_LOCATOR)
        self.hunting_mode_button = self.page_instance.locator(self.HUNTING_MODE_LOCATOR)

        self.inventory_button = self.page_instance.locator(
            OverworldPage.INVENTORY_LOCATOR
        )
        self.options_button = self.page_instance.locator(OverworldPage.OPTIONS_LOCATOR)

        # # Optionally create a mapping for easy lookup by direction name
        # self.direction_buttons = {
        #     "north": self.north_button,
        #     "south": self.south_button,
        #     "west": self.west_button,
        #     "east": self.east_button,
        #     "northwest": self.northwest_button,
        #     "southwest": self.southwest_button,
        #     "northeast": self.northeast_button,
        #     "southeast": self.southeast_button,
        # }

        self.str_to_direction_button = {
            "1": self.north_button,
            "2": self.south_button,
            "3": self.west_button,
            "4": self.east_button,
            "5": self.northwest_button,
            "6": self.southwest_button,
            "7": self.northeast_button,
            "8": self.southeast_button,
        }

    def click_direction(self, direction: str) -> None:
        """
        Click a direction button corresponding to the int that was passed in.
        Travel can result in either another overworld page, or a battle start page if a random encounter occurs.
        :param direction:
        """
        # Get the current overworld map's page HTML
        map_coords = self.get_map_coords()

        # Map direction string or enum to the corresponding locator
        direction_button = self.str_to_direction_button[direction]
        if direction_button.count() > 0:
            self.simulate_click_with_wait(direction_button, prev_map_coords=map_coords)
        else:
            raise ValueError(f"Invalid direction for path direction: {direction}")

    def go_to_movement_url_with_wait(
            self, movement_url: str, num_retries=6, prev_map_coords: List[str] = None
    ) -> None:
        """
        This method visits a URL and waits for a page reload to ensure that the action is complete,
        including fallback handling if the navigation fails. Mainly used for overworld movement.
        :param url: URL to visit
        """
        for attempt in range(num_retries):
            try:
                with self.page_instance.expect_navigation():
                    logger.info(f"Attempting to visit {movement_url} ...")
                    self.page_instance.goto(movement_url, timeout=60000)
                    self.page_instance.wait_for_load_state("load")
                return
            except TimeoutError as te:
                logger.warning(f"Attempt {attempt} to navigate failed: {te}")
                try:
                    logger.info(
                        "Attempting to reload the page and determine the result"
                    )
                    self.page_instance.goto("about:blank")
                    # This is really bad practice but it works, so eh...
                    time.sleep(3)
                    self.page_instance.goto(OverworldPage.MAIN_GAME_URL, timeout=60000)
                    # Refresh once more and wait to ensure it loaded
                    with self.page_instance.expect_navigation():
                        self.page_instance.goto(OverworldPage.MAIN_GAME_URL, timeout=60000)
                        self.page_instance.wait_for_load_state("load")
                    new_map_coords = self.get_map_coords()
                    if set(prev_map_coords) == set(new_map_coords):
                        logger.info(
                            "The previous move action did not go through. Retrying URL visit..."
                        )
                        continue
                    else:
                        logger.info(
                            "The page failed to load but the action was performed."
                        )
                        return
                except TimeoutError as reload_error:
                    logger.warning(f"Also failed to reload the page: {reload_error}")
        logger.error(f"Failed to visit URL after {num_retries} attempts.")
        # TODO: create and throw a custom exception instead of generic one here
        raise Exception("Max retries exceeded for visit_url_with_wait")

    def click_normal_movement_button(self) -> None:
        self.click_clickable_element(
            self.normal_mode_button,
            "Could not click the normal mode button. This can happen if you were already in normal mode.",
        )

    def click_hunting_movement_button(self) -> None:
        self.click_clickable_element(
            self.hunting_mode_button,
            "Could not click the hunting mode button. This can happen if you were already in hunting mode.",
        )

    def click_inventory_button(self) -> None:
        """
        This method clicks the inventory button
        :return: a Page reference to the resulting inventory page
        """

        self.click_clickable_element(
            self.inventory_button,
            "We were unable to click the inventory button. Ensure that you are on the overworld.",
        )

    def click_options_button(self) -> None:
        self.click_clickable_element(
            self.options_button,
            "We were unable to click the options button. Ensure that you are on the overworld.",
        )

    def simulate_click_with_wait(
            self,
            unclickable_element: Locator,
            num_retries=6,
            prev_map_coords: List[str] = None,
    ) -> None:
        """
        This method handles elements that perform Javascript calls when clicked physically, but NOT VIA PLAYWRIGHT.
        It sends a click event and then waits for a page reload to occur to ensure that the action has finished.
        :param unclickable_element: some element that is interactable only because of an overlaying element,
         and isn't clickable via Playwright
        """
        for attempt in range(0, num_retries):
            try:
                with self.page_instance.expect_navigation():
                    unclickable_element.dispatch_event("click")
                    logger.info(
                        "Attempting to interact with an element that Playwright cannot click normally..."
                    )
                    self.page_instance.wait_for_load_state("load")
                return
            except TimeoutError as te:
                logger.warning(f"Attempt {attempt} failed: {te}")
                try:
                    logger.info(
                        "Attempting to reload the page and determine the result"
                    )
                    self.page_instance.goto("about:blank")
                    # Wait a couple of seconds before page reload
                    time.sleep(2)
                    self.page_instance.goto(OverworldPage.MAIN_GAME_URL)
                    self.page_instance.wait_for_load_state("load")
                    # Wait a couple of seconds after page load to ensure elements loaded
                    time.sleep(2)
                    new_map_coords = self.get_map_coords()
                    # Not sure if this check fails when the page actually loaded but took us to a battle page - might be ok
                    if set(prev_map_coords) == set(new_map_coords):
                        logger.info(
                            "The previous movement action did not go through. Resubmitting action..."
                        )
                        # Then redo the action since it didn't go through
                        continue
                    else:
                        logger.info(
                            "The page failed to load but the action was performed."
                        )
                        return
                except TimeoutError as reload_err:
                    logger.warning(
                        f"Also failed to reload the page after failed simulated click: {reload_err}"
                    )
        logger.error(
            f"Failed to interact with the element after {num_retries} attempts."
        )
        raise RuntimeError("Max retries exceeded for simulate_click_with_wait")

    # Utility method to compare if page is the same
    def get_map_coords(self) -> List[str]:
        """
        Get the raw HTML of the overworld map for comparison against another overworld map HTML.
        """
        # WE HAVE IDENTIFIED THE MAJOR ISSUE HERE!!! THE LIST OF MAP COORDINATES IS ALWAYS RETURNING NOTHING
        # IT SEEMS THAT THE TABLE COUNT CHANGES DYNAMICALLY BASED ON VARIOUS GAME DATA LIKE HOW MANY CHARACTERS!!!
        # WE FIX THIS BY SIMPLY GETTING COORDS FROM THE WHOLE GAME CONTAINER ELEMENT INSTEAD
        # Thankfully, doesn't clash with the coords attribute in navmap
        container = self.page_instance.locator(OverworldPage.GAME_CONTAINER_LOCATOR)
        # map_tbody = container.locator("tbody").nth(
        #     4
        # )  # 0-based index, so 4 is the fifth tbody
        # map_html = map_tbody.inner_html()
        map_html = container.inner_html()
        coords_matches = re.findall(r"coords\((.*?)\)", map_html)
        return coords_matches
