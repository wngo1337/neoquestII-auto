import os.path

from playwright.sync_api import Page
from Pages.neopets_page import NeopetsPage
from Pages.neopass_login_page import NeopassLoginPage
from Pages.traditional_login_page import TraditionalLoginPage

from page_parser import PageParser
from typing import Union
from page_types import PageType

import logging

logger = logging.getLogger(__name__)


# This class is not part of the game, so it does not warrant page objects for login pages


class LoginHandler:
    NEOPASS_LOGIN_URL: str = "https://neopass.neopets.com/login"
    TRADITIONAL_LOGIN_URL: str = "https://www.neopets.com/login/"
    NEOPASS_LOGIN_BUTTON_LOCATOR: str = "text='Create A Free NeoPass'"
    TRADITIONAL_LOGIN_BUTTON_LOCATOR: str = "form.login-form"
    NEOPASS_LAUNCH_BUTTON_LOCATOR: str = "//button[text()='Launch']"
    NEOPASS_CONTINUE_BUTTON_LOCATOR: str = "//button[text()='Continue']"
    NEOPASS_USERNAME_BUTTON_LOCATOR_TEMPLATE: str = (
        "//button[.//h4[contains(text(), '{0}')]]"
    )
    NEOPASS_EMAIL_LOCATOR: str = "input[type = 'email'][name = 'email']"
    NEOPASS_PASSWORD_LOCATOR: str = "input[type='password'][name='password']"
    NEOPASS_SIGN_IN_LOCATOR = "button[type='submit']:has-text('Sign In')"
    TRADITIONAL_USERNAME_LOCATOR: str = "input#loginUsername"
    TRADITIONAL_PASSWORD_LOCATOR: str = "input#loginPassword"
    TRADITIONAL_SIGN_IN_LOCATOR: str = "button#loginButton"

    GAME_PAGE = "https://www.neopets.com/games/nq2/nq2.phtml"

    TEXT_FILES_DIR_NAME = "TextFiles"
    USER_INFO_FILE_NAME = "user_info.txt"

    def __init__(self, neopets_page: NeopetsPage, use_neopass: bool = False) -> None:
        self.use_neopass = use_neopass
        # Not sure if this is even necessary since we return the page at end of every method
        self.neopets_page = neopets_page

        base_dir = os.path.dirname(os.path.abspath(__file__))

        with open(
                os.path.join(
                    base_dir,
                    LoginHandler.TEXT_FILES_DIR_NAME,
                    LoginHandler.USER_INFO_FILE_NAME,
                ),
                "r",
        ) as f:
            if self.use_neopass:
                self.neopass_email = f.readline()
                self.neopass_password = f.readline()
                self.username = f.readline()

                logger.info("Reading Neopass login info...")
            else:
                self.username = f.readline()
                self.user_password = f.readline()

                logger.info("Reading traditional login info...")

    def login_and_go_to_game(self) -> NeopetsPage:
        """
        This method logs into Neopets based on the login method passed to the launcher.
        It keeps a reference to the page instance after logging in.
        """
        if self.use_neopass:
            logger.info("Attempting login with Neopass...")
            self.login_with_neopass()
        else:
            logger.info("Attempting login with traditional login...")
            self.login_traditional()

        self.neopets_page.page_instance.goto(LoginHandler.GAME_PAGE)

        return self.neopets_page

    def login_with_neopass(self) -> NeopetsPage:
        self.neopets_page.page_instance.goto(url=self.NEOPASS_LOGIN_URL)
        self.neopets_page.page_instance.wait_for_selector(
            self.NEOPASS_LOGIN_BUTTON_LOCATOR
        )

        email_field = self.neopets_page.page_instance.locator(
            self.NEOPASS_EMAIL_LOCATOR
        )
        password_field = self.neopets_page.page_instance.locator(
            self.NEOPASS_PASSWORD_LOCATOR
        )
        email_field.fill(self.neopass_email)
        password_field.fill(self.neopass_password)

        sign_in_button = self.neopets_page.page_instance.locator(
            self.NEOPASS_SIGN_IN_LOCATOR
        )
        sign_in_button.click()

        # Handle new tab opened by launch button click
        with self.neopets_page.page_instance.context.expect_page() as new_page_info:
            launch_button = self.neopets_page.page_instance.locator(
                self.NEOPASS_LAUNCH_BUTTON_LOCATOR
            )
            launch_button.click()
        account_selection_tab = new_page_info.value
        account_selection_tab.wait_for_load_state()

        username_button = account_selection_tab.locator(
            self.NEOPASS_USERNAME_BUTTON_LOCATOR_TEMPLATE.format(self.username)
        )
        username_button.click()

        continue_button = account_selection_tab.locator(
            self.NEOPASS_CONTINUE_BUTTON_LOCATOR
        )
        with account_selection_tab.expect_navigation(
                wait_until="domcontentloaded", timeout=30000
        ):
            continue_button.click()

        logger.info(
            "Login with Neopass should be complete. Returning control to autoplayer"
        )
        self.neopets_page = NeopetsPage(account_selection_tab)

        return self.neopets_page

    def login_traditional(self) -> NeopetsPage:
        # Note: we didn't actually test if this works because we don't have an account available to do that
        self.neopets_page.page_instance.goto(url=self.TRADITIONAL_LOGIN_URL)
        self.neopets_page.page_instance.wait_for_selector(
            self.TRADITIONAL_LOGIN_BUTTON_LOCATOR
        )

        username_field = self.neopets_page.page_instance.locator(
            self.TRADITIONAL_USERNAME_LOCATOR
        )
        password_field = self.neopets_page.page_instance.locator(
            self.TRADITIONAL_PASSWORD_LOCATOR
        )
        username_field.fill(self.username)
        password_field.fill(self.user_password)

        sign_in_button = self.neopets_page.page_instance.locator(
            self.TRADITIONAL_SIGN_IN_LOCATOR
        )
        with self.neopets_page.page_instance.expect_navigation(
                wait_until="domcontentloaded", timeout=30000
        ):
            sign_in_button.click()
        logger.info(
            "Login with traditional login should be complete. Returning control to autoplayer"
        )

        return self.neopets_page
