# ---------------------------------------------------------------------------------------- #
#                                 TEAM STATE DATA CONSTRUCT                                #
# ---------------------------------------------------------------------------------------- #
from FPLmanager.data.fplapi import get_gameweeks, get_entry_history, \
    get_entry_transfers, get_entry_picks
from FPLmanager import CURRENT_SEASON
from FPLmanager.utils import season_str, next_gameweeks
import pandas as pd


# ----------------------------------- ENTRY BASE CLASS ----------------------------------- #
class Entry:
    def __init__(
            self, entry_id, 
            game_state,
            history={},
            **kwargs
        ):

        self.entry_id = entry_id
        
        # information on current state of the gameweek
        self.game_state = game_state
        self.history = self.construct_entry_history(history)

    @property
    def season(self):
        return self.game_state.season

    @property
    def gw(self):
        return self.game_state.gw

    def construct_entry_history(self, history):
        """
        Take the fplapi stateful responses and modify them to reflect an entry state
        at a given point in time.

        Defaults to history up to the current gameweek.
        """
        
        # week by week season summary
        if 'current' not in history:
            weekly = get_entry_history(self.entry_id)
            history['current'] = [
                week for week in weekly['current'] if week['event'] < self.gw
            ]

        # chips
        if 'chips' not in history:
            history['chips'] = get_entry_history(self.entry_id)['chips']
            for chip in history['chips']:
                if chip['event'] > self.gw:
                    history['chips'].remove(chip)

        if 'transfers' not in history:
            transfers = get_entry_transfers(self.entry_id)
            transfers = [
                transfer for transfer in transfers if transfer['event'] < self.gw
            ]
            history['transfers'] = transfers

        if 'picks' not in history:
            gw_range = range(1, self.gw)
            picks = {_gw: get_entry_picks(self.entry_id, _gw)['picks'] for _gw in gw_range}
            history['picks'] = picks

        return history

    def step(self, n=1):
        self.game_state.step(n)
        self.history = self.construct_entry_history({})


# ------------------------------------ SIMULATED ENTRY ----------------------------------- #
class EntrySim(Entry):
    def __init__(self, picks, entry_id, game_state, history={}):
        picks = self.validate_team(picks)

        # super().__init__(season, gw, simulated=True, sim_data=sim_data)

    def construct_entry_history(self, sim_data):
        pass

    def step(self, n=1):
        pass