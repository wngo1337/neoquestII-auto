from __future__ import annotations
from typing import Type
from playwright.sync_api import Page, Locator

import logging

logger = logging.getLogger(__name__)


class NeopetsPage:
    def __init__(self, neopets_page_instance: Page) -> None:
        # The playwright Page object tracks a tab and the pages that it visits
        # This means we don't have to worry about stale references like in Selenium
        self.page_instance = neopets_page_instance

    # Was designed to be a wrapper for built-in goto method, but we also built in automatic retries
    def go_to_url_and_wait_navigation(self, url: str, max_retries: int = 5) -> None:
        """
        Navigates to a URL, retries on failure, and explicitly waits for navigation to complete.
        :param url: The destination URL.
        :param max_retries: Number of times to retry navigation.
        """
        for attempt in range(0, max_retries):
            try:
                self.page_instance.goto(url)
                self.page_instance.wait_for_load_state("load")
                return  # Success, so exit
            except Exception as e:
                logger.warning(f"Navigation attempt {attempt} failed: {e}")
                try:
                    self.page_instance.goto("about:blank")
                    self.page_instance.wait_for_load_state("load")
                except Exception as reload_error:
                    logger.warning(
                        f"Also failed to navigate to blank page before trying navigation again: {reload_error}"
                    )
        logger.error(f"Failed to navigate to {url} after {max_retries} attempts.")
        raise Exception(
            f"Max retries exceeded for go_to_url_and_wait_navigation at {url}"
        )

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
        max_retries: int = 5,
    ) -> None:
        """
        Click an element on the current page, retry clicking if it fails by reloading the page.
        :param button: Locator object of the button to click
        :param error_message: message to log if clicking fails
        :param max_retries: number of retry attempts before final failure
        :param delay: delay in seconds between retries
        """
        for attempt in range(1, max_retries + 1):
            try:
                button.click()
                return  # Successfully clicked, exit the function
            except Exception as e:
                logger.warning(f"{error_message} Attempt {attempt} failed: {e}")
                try:
                    self.page_instance.reload()
                    self.page_instance.wait_for_load_state("load")
                except Exception as reload_exc:
                    logger.warning(
                        f"Reload attempt failed during click retry: {reload_exc}"
                    )
        logger.error(f"Failed to click element after {max_retries} attempts.")
        raise Exception(
            f"Max retries exceeded for click_clickable_element on locator {button}"
        )

    def get_page_content(self) -> str:
        """
        Get the HTML content of the page instance
        :return: HTML content of the page
        """
        return self.page_instance.content()
