from __future__ import annotations
from enum import Enum
from typing import List

from playwright.sync_api import Page, Locator

from .neopets_page import NeopetsPage

import logging

logger = logging.getLogger(__name__)


class BattleStartPage(NeopetsPage):
    BATTLE_START_LOCATOR = "img[alt='Begin the Fight!']"

    def __init__(self, neopets_page_instance: Page):
        super().__init__(neopets_page_instance)

        self.start_battle_button = self.page_instance.locator(
            BattleStartPage.BATTLE_START_LOCATOR
        )

    def is_battle_start(self) -> bool:
        """
        Method to determine how to initialize the battle handler depending on if battle is in progress or starting.
        :return: True if we are actually on a battle start page, else False
        """
        if self.start_battle_button.count() > 0:
            return True
        else:
            return False

    def click_start_battle_button(self) -> None:
        """
        Click the starts battle button to enter the battle.
        This results in a page suited for BattlePage class, so be sure to handle the context accordingly.
        """
        # click the battle start button
        self.click_clickable_element(
            self.start_battle_button,
            "We were unable to click the start battle button. Ensure that you are on a battle start page!",
        )
