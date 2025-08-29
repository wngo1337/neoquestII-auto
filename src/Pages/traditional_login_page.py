from playwright.sync_api import Page
from .neopets_page import NeopetsPage


class TraditionalLoginPage(NeopetsPage):
    # USERNAME_SELECTOR = "input[name='password']"
    # EMAIL_SELECTOR = "input[name='email']"

    def __init__(self, page: Page):
        super().__init__(page)
