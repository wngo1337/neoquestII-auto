from .neopets_page import NeopetsPage
from playwright.sync_api import Page


class NeopassLoginPage(NeopetsPage):
    def __init__(self, page: Page):
        super().__init__(page)
