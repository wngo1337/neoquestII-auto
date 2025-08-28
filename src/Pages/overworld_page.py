from neopets_page import NeopetsPage


class OverworldPage(NeopetsPage):
    """
    Page object model representing the NeoQuest II overworld page.
    Holds element locators and keeps references to UI buttons
    """

    NAVIGATION_BUTTONS_GRID_LOCATOR = "div.contentModule.phpGamesNonPortalView"

    # Class variables: selectors for elements - shared by all instances
    NORTH_LOCATOR = 'area[alt="North"]'
    SOUTH_LOCATOR = 'area[alt="South"]'
    WEST_LOCATOR = 'area[alt="West"]'
    EAST_LOCATOR = 'area[alt="East"]'
    NORTHWEST_LOCATOR = 'area[alt="Northwest"]'
    SOUTHWEST_LOCATOR = 'area[alt="Southwest"]'
    NORTHEAST_LOCATOR = 'area[alt="Northeast"]'
    SOUTHEAST_LOCATOR = 'area[alt="Southeast"]'

    NORMAL_MODE_LOCATOR = (
        "a[href='https://www.neopets.com/games/nq2/nq2.phtml?act=travel&mode=2']"
    )
    HUNTING_MODE_LOCATOR = (
        "a[href='https://www.neopets.com/games/nq2/nq2.phtml?act=travel&mode=1']"
    )

    def __init__(self, neopets_page: NeopetsPage):
        super().__init__(neopets_page.browser_page)

        # Instance variables: actual element handles referencing the DOM elements

        self.nav_map = self.browser_page.locator(self.NAVIGATION_BUTTONS_GRID_LOCATOR)
        self.north_button = self.browser_page.locator(self.NORTH_LOCATOR)
        self.south_button = self.browser_page.locator(self.SOUTH_LOCATOR)
        self.west_button = self.browser_page.locator(self.WEST_LOCATOR)
        self.east_button = self.browser_page.locator(self.EAST_LOCATOR)
        self.northwest_button = self.browser_page.locator(self.NORTHWEST_LOCATOR)
        self.southwest_button = self.browser_page.locator(self.SOUTHWEST_LOCATOR)
        self.northeast_button = self.browser_page.locator(self.NORTHEAST_LOCATOR)
        self.southeast_button = self.browser_page.locator(self.SOUTHEAST_LOCATOR)

        self.normal_mode_button = self.browser_page.locator(self.NORMAL_MODE_LOCATOR)
        self.hunting_mode_button = self.browser_page.locator(self.HUNTING_MODE_LOCATOR)

        # # Optionally create a mapping for easy lookup by direction name
        # self.direction_buttons = {
        #     "north": self.north_button,
        #     "south": self.south_button,
        #     "west": self.west_button,
        #     "east": self.east_button,
        #     "northwest": self.northwest_button,
        #     "southwest": self.southwest_button,
        #     "northeast": self.northeast_button,
        #     "southeast": self.southeast_button,
        # }
