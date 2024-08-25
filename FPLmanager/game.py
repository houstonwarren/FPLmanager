# ---------------------------------------------------------------------------------------- #
#                                 GAME STATE REPRESENTATION                                #
# ---------------------------------------------------------------------------------------- #
from FPLmanager.utils import season_str, next_gameweeks
from FPLmanager.data.fplapi import get_gameweeks
from FPLmanager import CURRENT_SEASON
from FPLmanager.data.db import *
import datetime as dt


# --------------------------------- GAME STATE BASE CLASS -------------------------------- #
class GameState:
    """
    Base class for game state representation.

    This class represents the current state of the Fantasy Premier League (FPL) game.
    It provides a foundation for managing and updating game-related data such as
    fixtures, player prices, team information, and player statistics.

    Attributes:
        season (int): The current FPL season (e.g., 2023 for 2023-2024 season).
        gw_real (int): The current gameweek of the real-world Premier League season.
        gw (int): The current gameweek in the game state, which may differ from gw_real.
        fixtures (DataFrame): Fixture data for the current season.
        prices (DataFrame): Player price data for the current gameweek and season.
        teams (DataFrame): Team information for the current season.
        players (DataFrame): Player statistics for the current gameweek and season.

    Methods:
        solver_state(): Placeholder method for generating solver-specific state representation.
        step(n=1): Advances the game state by n gameweeks, updating relevant data.

    The class initializes with the current season and gameweek, fetching and storing
    relevant data from the FPL database. It provides functionality to step through
    gameweeks and update the game state accordingly.
    """

    def __init__(self, season=CURRENT_SEASON, gw=None):
        self.season = season
        self.gw_real = get_gameweeks(gw_id='current')['id']  # gets this seasons current gw

        if gw is None:
            # if current season, use current week, else use week 1
            if self.season == CURRENT_SEASON:
                self.gw = self.gw_real
            else:
                self.gw = 1
        else:
            self.gw = gw

        self.fixtures = get_fixtures(season=self.season, prior=False)
        self.prices = get_prices(gw=self.gw, season=self.season, prior=False)        
        self.teams = get_teams(season=self.season, prior=False)
        self.player_gws = get_player_gws(gw=self.gw, season=self.season, prior=False)
    
    def solver_state(self):
        pass

    def step(self, n=1):
        new_gw = next_gameweeks(self.gw, n)[-1]
        if self.season == CURRENT_SEASON and new_gw > self.gw_real:
            raise ValueError("Can't step into the future!")

        self.gw = new_gw
        self.prices = get_prices(gw=self.gw, season=self.season, prior=False)
        self.players = get_player_gws(gw=self.gw, season=self.season, prior=False)
