from enum import Enum, StrEnum, auto
from typing import List

from Pages.neopets_page import NeopetsPage

import logging

from Pages.overworld_page import OverworldPage
from src.Pages.battle_page import BattlePage
from src.Pages.battle_start_page import BattleStartPage

logger = logging.getLogger(__name__)


class OverworldHandler:
    # NAVIGATION_BUTTONS_GRID_LOCATOR = "div.contentModule.phpGamesNonPortalView"

    class Direction(Enum):
        NORTH = "1"
        SOUTH = "2"
        WEST = "3"
        EAST = "4"
        NORTHWEST = "5"
        SOUTHWEST = "6"
        NORTHEAST = "7"
        SOUTHEAST = "8"

    # Map each direction to its corresponding CSS selector
    # I WANTED TO USE THESE BUT THEY JUST AREN'T AS RELIABLE
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
        logger.info("Yeah baby, an overworld handler")
        self.overworld_page = OverworldPage(current_page.page_instance)

    def is_overworld(self) -> bool:
        """
        Used to determine if the current page is actually on the overworld.
        """
        return self.overworld_page.nav_map.count() > 0

    def take_step(self, direction: str) -> OverworldPage | BattleStartPage:
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
        map_coords = self.get_overworld_map_coordinates()
        movement_url = OverworldPage.MOVEMENT_URL_TEMPLATE.format(direction)
        self.overworld_page.go_to_movement_url_with_wait(movement_url, prev_map_coords=map_coords)
        if self.is_overworld():
            return self.overworld_page
        else:
            return BattleStartPage(self.overworld_page.page_instance)

    def invert_path(self, map_path: str) -> str:
        """
        Takes a path of directions and returns a string that theoretically returns the user to their starting location.

        EXTREMELY IMPORTANT: MUST BE VERY CAREFUL WITH USAGE BECAUSE ENTERING CAVES OR STAIRS PUTS YOU ON A RANDOM TILE.
        NOT THE CAVE TILE ITSELF, SO YOU HAVE TO ACCOUNT FOR THE EXTRA STEP WHEN YOU ARE RETURNING!!!
        """
        opposite_map = {
            '1': '2', '2': '1', '3': '4', '4': '3',
            '5': '8', '6': '7', '7': '6', '8': '5',
        }
        # reversed_path = reversed(map_path)
        # inverted_path = ''
        # for step in reversed_path:
        #     inverted_path += opposite_map[step]
        # return inverted_path

        try:
            return ''.join(opposite_map[step] for step in reversed(map_path))
        except KeyError as e:
            raise ValueError(f"Invalid direction '{e.args[0]}' encountered in path.")

    def switch_movement_mode(self, mode: MovementMode) -> None:
        if mode == OverworldHandler.MovementMode.NORMAL:
            self.overworld_page.go_to_url_and_wait_navigation(OverworldPage.SWITCH_NORMAL_NODE_URL)
        else:
            self.overworld_page.go_to_url_and_wait_navigation(OverworldPage.SWITCH_HUNTING_MODE_URL)

    def open_inventory(self) -> None:
        self.overworld_page.click_inventory_button()

    def open_options(self) -> None:
        self.overworld_page.click_options_button()

    def get_overworld_map_coordinates(self) -> List[str]:
        map_coords = self.overworld_page.get_map_coords()
        return map_coords