from playwright.sync_api import Page, Locator

import logging

logger = logging.getLogger(__name__)


class NeopetsPage:
    def __init__(self, page: Page) -> None:
        self.page_instance = page

    # This method basically just wraps the Page class' goto method...
    # Not sure why we are doing this tbh
    def go_to_url(self, url: str) -> Page:
        logging.info(f"Navigating to the following url: {url}")
        self.page_instance.goto(url)
        return self.page_instance

    def simulate_click_with_wait(self, unclickable_element: Locator) -> Page:
        """
        This method handles elements that perform Javascript calls when clicked physically, but NOT VIA PLAYWRIGHT.
        It sends a click event and then waits for a page reload to occur to ensure that the action has finished.
        :param unclickable_element: some element that is interactable only because of an overlaying element,
         and isn't clickable via Playwright
        :return: the resulting page
        """
        with self.page_instance.expect_navigation():
            unclickable_element.dispatch_event("click")
            logger.info(
                "Attempting to interact with an element that Playwright cannot click normally..."
            )
            self.page_instance.wait_for_load_state("load")
