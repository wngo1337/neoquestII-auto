from __future__ import annotations
from typing import Type
from playwright.sync_api import Page, Locator

import logging

logger = logging.getLogger(__name__)


class NeopetsPage:
    def __init__(self, neopets_page_instance: Page) -> None:
        # This changes over time as pages get clicked
        # However, it means we don't have to explicitly return each resulting page
        self.page_instance = neopets_page_instance

    # This method basically just wraps the Page class' goto method...
    # Not sure why we are doing this tbh
    def go_to_url(self, url: str) -> None:
        logging.info(f"Navigating to the following url: {url}")
        self.page_instance.goto(url)

    def simulate_click_with_wait(self, unclickable_element: Locator) -> None:
        """
        This method handles elements that perform Javascript calls when clicked physically, but NOT VIA PLAYWRIGHT.
        It sends a click event and then waits for a page reload to occur to ensure that the action has finished.
        :param unclickable_element: some element that is interactable only because of an overlaying element,
         and isn't clickable via Playwright
        """
        with self.page_instance.expect_navigation():
            unclickable_element.dispatch_event("click")
            logger.info(
                "Attempting to interact with an element that Playwright cannot click normally..."
            )
            self.page_instance.wait_for_load_state("load")

    def click_link_matching_text(self, link_text: str) -> None:
        """
        This is a utility method clicks a link that matches the user-specified text and returns the resulting page.
        Most of the time, this is not needed because selectors can locate the element with greater precision.
        :param link_text: exact text of the element that we are supposed to find
        """

        matching_text_xpath_format = "//*[text()='{0}']"
        matching_element = self.page_instance.locator(
            matching_text_xpath_format.format(link_text)
        )
        matching_element.click()

    def click_clickable_element(
        self,
        button: Locator,
        error_message: str,
    ) -> None:
        """
        Click an element on the current page and return a page object of the resulting page class.
        :param button: Locator object of the button to click
        :param error_message: message to return if the button was not clicked properly
        """
        # NOTE: we should be careful that the button results in an action on the calling page, but pretty sure it does
        try:
            button.click()
        except Exception as e:
            logger.info(error_message)
            # Raise the last exception we caught after logging the issue
            raise

    def get_page_content(self) -> str:
        """
        Get the HTML content of the page instance
        :return: HTML content of the page
        """
        return self.page_instance.content()
