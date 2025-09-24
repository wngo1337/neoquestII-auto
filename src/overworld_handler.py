import logging
from enum import Enum
from typing import List

from src.Pages.battle_start_page import BattleStartPage
from src.Pages.neopets_page import NeopetsPage
from src.Pages.overworld_page import OverworldPage

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
        logger.info("Initialized overworld handler with current page...")
        self.overworld_page = OverworldPage(current_page.page_instance)

    def is_overworld(self) -> bool:
        """
        Used to determine if the current page is actually on the overworld.
        """
        return self.overworld_page.nav_map.count() > 0

    # TODO: probably put this in a constant
    def is_battle_start(self) -> bool:
        """Used to determine if the result of a movement action was a random encounter."""
        return "You are attacked by" in self.overworld_page.get_page_content()

    def take_step(self, direction: str) -> OverworldPage | BattleStartPage:
        """
        Takes a single step on the overworld map.
        :param direction: a length-one string representing a direction on the navigation map
        """

        map_coords = self.get_overworld_map_coordinates()
        movement_url = OverworldPage.MOVEMENT_URL_TEMPLATE.format(direction)
        self.overworld_page.go_to_movement_url_with_wait(
            movement_url, prev_map_coords=map_coords
        )
        if self.is_overworld():
            return self.overworld_page
        else:
            return BattleStartPage(self.overworld_page.page_instance)

    @staticmethod
    def invert_path(map_path: str) -> str:
        """
        Takes a path of directions and returns a string that theoretically returns the user to their starting location.

        EXTREMELY IMPORTANT: MUST BE VERY CAREFUL WITH USAGE BECAUSE ENTERING CAVES OR STAIRS PUTS YOU ON A RANDOM TILE.
        NOT THE CAVE TILE ITSELF, SO YOU HAVE TO ACCOUNT FOR THE EXTRA STEP WHEN YOU ARE RETURNING!!!
        """
        opposite_map = {
            "1": "2",
            "2": "1",
            "3": "4",
            "4": "3",
            "5": "8",
            "6": "7",
            "7": "6",
            "8": "5",
        }
        # reversed_path = reversed(map_path)
        # inverted_path = ''
        # for step in reversed_path:
        #     inverted_path += opposite_map[step]
        # return inverted_path

        try:
            return "".join(opposite_map[step] for step in reversed(map_path))
        except KeyError as e:
            raise ValueError(f"Invalid direction '{e.args[0]}' encountered in path.")

    def switch_movement_mode(self, mode: MovementMode) -> None:
        if mode == OverworldHandler.MovementMode.NORMAL:
            logger.info("Switching to normal movement mode...")
            self.overworld_page.go_to_url_and_wait_navigation(
                OverworldPage.SWITCH_NORMAL_NODE_URL
            )
        else:
            logger.info("Switching to hunting movement mode...")
            self.overworld_page.go_to_url_and_wait_navigation(
                OverworldPage.SWITCH_HUNTING_MODE_URL
            )

    # def open_inventory(self) -> None:
    #     self.overworld_page.click_inventory_button()

    # def open_options(self) -> None:
    #     self.overworld_page.click_options_button()

    def get_overworld_map_coordinates(self) -> List[str]:
        """
        Get a list of the coordinates on the overworld map. Mainly used to determine if an action went through on page
        load fail.
        """
        map_coords = self.overworld_page.get_map_coords()
        return map_coords
