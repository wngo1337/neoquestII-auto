from enum import Enum, auto

from Pages.neopets_page import NeopetsPage

import logging

from Pages.overworld_page import OverworldPage

logger = logging.getLogger(__name__)


class OverworldHandler:
    NAVIGATION_BUTTONS_GRID_LOCATOR = "div.contentModule.phpGamesNonPortalView"

    class Direction(Enum):
        NORTH = 1
        SOUTH = 2
        WEST = 3
        EAST = 4
        NORTHWEST = 5
        SOUTHWEST = 6
        NORTHEAST = 7
        SOUTHEAST = 8

    # Map each direction to its corresponding CSS selector
    DIRECTION_TO_LOCATOR = {
        Direction.NORTH: 'area[alt="North"]',
        Direction.SOUTH: 'area[alt="South"]',
        Direction.WEST: 'area[alt="West"]',
        Direction.EAST: 'area[alt="East"]',
        Direction.NORTHWEST: 'area[alt="Northwest"]',
        Direction.SOUTHWEST: 'area[alt="Southwest"]',
        Direction.NORTHEAST: 'area[alt="Northeast"]',
        Direction.SOUTHEAST: 'area[alt="Southeast"]',
    }

    class MovementMode(Enum):
        NORMAL = 1
        HUNTING = 2

    def __init__(self, current_page: NeopetsPage) -> None:
        print("Yeah baby, an overworld handler")
        self.overworld_page = OverworldPage(current_page.page_instance)

    def is_overworld(self) -> bool:
        return self.overworld_page.nav_map is not None

    def take_step(self, direction: str) -> None:
        """
        Takes a single step on the overworld map.
        :param direction: a length-one string representing a direction on the navigation map
        """

        # We can either expect a string and convert, or expect an int directly
        # direction_as_enum = OverworldHandler.Direction(int(direction))
        # direction_selector = OverworldHandler.DIRECTION_TO_LOCATOR[direction_as_enum]
        # direction_button = self.neopets_page.browser_page.locator(direction_selector)
        # # Need this context manager otherwise, Playwright's dispatch_event can't tell when page is ready to click again
        # with self.neopets_page.browser_page.expect_navigation():
        #     direction_button.dispatch_event("click")
        #     logger.info(
        #         f"Attempting to move {direction_selector} and waiting for page load..."
        #     )
        #
        #     self.neopets_page.browser_page.wait_for_load_state("load")
        # return self.neopets_page
        direction_int = int(direction)
        self.overworld_page.click_direction(direction_int)

    def switch_movement_mode(self, mode: MovementMode) -> None:
        if mode == OverworldHandler.MovementMode.NORMAL:
            self.overworld_page.click_normal_movement_button()
        else:
            self.overworld_page.click_hunting_movement_button()

    def open_inventory(self) -> None:
        self.overworld_page.click_inventory_button()

    def open_options(self) -> None:
        self.overworld_page.click_options_button()
