from page_types import PageType
from bs4 import BeautifulSoup


class PageParser:
    """
    You don't need an actual instance of this class at all.
    It just provides functionality that will parse the page HTML and tell you what kind of page you are on.
    """

    NEOPASS_EMAIL_IDENTIFIER = {"type": "email"}
    NEOPASS_PASSWORD_IDENTIFIER = {"for": "email"}

    TRADITIONAL_LOGIN_IDENTIFIER = {"class": "login-form"}

    HOME_PAGE_IDENTIFIER = {"class": "container theme-bg"}

    OVERWORLD_IDENTIFIER = {"name": "navmap"}

    @staticmethod
    def parse_html(page_html: str) -> PageType:
        # Read into bs object
        # Check for presence of specific elements unique to the page
        soup = BeautifulSoup(page_html, "html.parser")

        if PageParser.is_neopass_login_page(soup):
            return PageType.NEOPASS_LOGIN

        elif PageParser.is_traditional_login_page(soup):
            return PageType.TRADITIONAL_LOGIN
        elif PageParser.is_home_page(soup):
            return PageType.HOME

        else:
            # Extremely dumb, just want to see though
            return PageType.UNRECOGNIZED

    @staticmethod
    def is_neopass_login_page(soup: BeautifulSoup) -> bool:
        neopass_email_tag = soup.find(attrs=PageParser.NEOPASS_EMAIL_IDENTIFIER)
        neopass_password_tag = soup.find(attrs=PageParser.NEOPASS_PASSWORD_IDENTIFIER)

        return (neopass_email_tag is not None) and (neopass_password_tag is not None)

    @staticmethod
    def is_traditional_login_page(soup: BeautifulSoup) -> bool:
        traditional_login_tag = soup.find(attrs=PageParser.TRADITIONAL_LOGIN_IDENTIFIER)
        return traditional_login_tag is not None

    @staticmethod
    def is_home_page(soup: BeautifulSoup) -> bool:
        home_page_tag = soup.find(attrs=PageParser.HOME_PAGE_IDENTIFIER)
        return home_page_tag is not None

    @staticmethod
    def is_overworld_page(soup: BeautifulSoup) -> bool:
        navigation_map_tag = soup.find(attrs=PageParser.OVERWORLD_IDENTIFIER)
        return navigation_map_tag is not None
