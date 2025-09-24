from abc import ABC


class AutoplayerBaseHandler(ABC):
    # Literally have every handler inherit just to have access to this value lol
    MAIN_GAME_URL = "https://www.neopets.com/games/nq2/nq2.phtml"
