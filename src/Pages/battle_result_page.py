from __future__ import annotations
from enum import Enum
from typing import List

from playwright.sync_api import Page, Locator

from .neopets_page import NeopetsPage

import logging

logger = logging.getLogger(__name__)


class BattleResultPage(NeopetsPage):
    BATTLE_END_LOCATOR = r"a[href='nq2.phtml?finish=1']"
    # This is NOT the button itself and cannot be clicked
    SPECIAL_CONTINUE_ELEMENT_LOCATOR = r"img[src='//images.neopets.com/nq2/x/cont.gif']"

    # SPECIAL_CONTINUE_LINK_URL = "https://www.neopets.com/games/nq2/nq2.phtml?finish=1"

    def __init__(self, neopets_page_instance: Page):
        super().__init__(neopets_page_instance)

        self.return_to_map_button = self.page_instance.locator(
            BattleResultPage.BATTLE_END_LOCATOR
        )

    def click_return_to_map_link(self) -> None:
        self.click_clickable_element(
            self.return_to_map_button,
            "We were unable to click the return to map button."
            "Ensure that you are on a post battle page!",
        )

    def click_special_continue_button(self) -> None:
        self.click_clickable_element(
            self.return_to_map_button,
            "We tried to click a special battle end page continue button, but it did not work!",
        )
