from enum import Enum

from .neopets_page import NeopetsPage

import logging

logger = logging.getLogger(__name__)


class OverworldPage(NeopetsPage):
    """
    Page object model representing the NeoQuest II overworld page.
    Holds element locators and keeps references to UI buttons
    """

    NAVIGATION_BUTTONS_GRID_LOCATOR = "div.contentModule.phpGamesNonPortalView"

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

    def __init__(self, neopets_page: NeopetsPage):
        super().__init__(neopets_page.page_instance)

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

        self.int_to_direction_button = {
            1: self.north_button,
            2: self.south_button,
            3: self.west_button,
            4: self.east_button,
            5: self.northwest_button,
            6: self.southwest_button,
            7: self.northeast_button,
            8: self.southeast_button,
        }

    def click_direction(self, direction: int) -> NeopetsPage:
        # Map direction string or enum to the corresponding locator
        direction_button = self.int_to_direction_button[direction]
        if direction_button:
            # Need this context manager otherwise, Playwright's dispatch_event can't tell when page is ready to click again
            with self.page_instance.expect_navigation():
                # direction_button.dispatch_event("click")
                # # logger.info(
                # #     f"Attempting to move {direction_selector} and waiting for page load..."
                # # )
                # self.page_instance.wait_for_load_state("load")
                self.simulate_click_with_wait(direction_button)
        else:
            raise ValueError(f"Invalid direction for path direction: {direction}")

        return NeopetsPage(self.page_instance)

    def click_normal_movement_button(self) -> NeopetsPage:
        if self.normal_mode_button:
            self.normal_mode_button.click()
        else:
            logger.info(
                "Could not click the normal mode button. This can happen if you were already in normal mode."
            )
        return NeopetsPage(self.page_instance)

    def click_hunting_movement_button(self) -> NeopetsPage:
        if self.hunting_mode_button:
            self.hunting_mode_button.click()
        else:
            logger.info(
                "Could not click the hunting mode button. This can happen if you were already in hunting mode."
            )
        return NeopetsPage(self.page_instance)
