from enum import Enum, auto


class PageType(Enum):
    # Site navigation pages
    HOME = auto()
    NEOPASS_LOGIN = auto()
    NEOPASS_ACCOUNT_VIEW = auto()
    NEOPASS_ACCOUNT_SELECTION = auto()
    TRADITIONAL_LOGIN = auto()

    # Game navigation pages
    GAME_INDEX = auto()
    GAME_OVERWORLD = auto()
    GAME_SKILLS = auto()
    GAME_INVENTORY = auto()
    GAME_NPC_TRADE = auto()
    GAME_BATTLE_START = auto()

    UNRECOGNIZED = auto()
