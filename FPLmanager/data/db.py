# ---------------------------------------------------------------------------------------- #
#                                 FUNCTIONS TO ACCESS DATA                                 #
# ---------------------------------------------------------------------------------------- #
from FPLmanager import DATA, CURRENT_SEASON
import pandas as pd


# ----------------------------------------- UTILS ---------------------------------------- #
def data_str(dataset):
    return f"{DATA}/{dataset}.csv"


def filter_gw_season(df, gw=None, season=CURRENT_SEASON, prior=True):
    df['season_num'] = df['season'].apply(lambda x: int(x.split('-')[0]))
    current_df = df[df['season_num'] == season]

    if gw is not None:
        current_df = current_df[current_df['GW'] <= gw]

    if prior:
        prior_df = df[df['season_num'] < season]
        df = pd.concat([prior_df, current_df]).reset_index(drop=True)
    else:
        df = current_df.reset_index(drop=True)

    df = df.drop(columns=['season_num'])
    return df


# ---------------------------------------- GETTERS --------------------------------------- #
def get_players(gw=None, season=CURRENT_SEASON, prior=True):
    players = pd.read_csv(data_str('players'))
    return filter_gw_season(players, gw, season, prior)


def get_fixtures(gw=None, season=CURRENT_SEASON, prior=True):
    fixtures = pd.read_csv(data_str('fixtures'))
    return filter_gw_season(fixtures, gw, season, prior)


def get_prices(gw=None, season=CURRENT_SEASON, prior=True):
    prices = pd.read_csv(data_str('prices'))
    return filter_gw_season(prices, gw, season, prior)


def get_teams(gw=None, season=CURRENT_SEASON, prior=True):
    teams = pd.read_csv(data_str('teams'))
    return filter_gw_season(teams, gw, season, prior)


def get_player_info(gw=None, season=CURRENT_SEASON, prior=True):
    player_info = pd.read_csv(data_str('player_info'))
    return filter_gw_season(player_info, gw, season, prior)


# ----------------------------------- ADVANCED GETTERS ----------------------------------- #
def get_most_recent_prices(gw, season=CURRENT_SEASON):
    prices = get_prices(gw, season, prior=False)
    prices = prices[prices['GW'] <= gw]
    most_recent_idx = prices[['code', 'GW']].groupby('code')['GW'].idxmax()
    prices = prices.loc[most_recent_idx].reset_index(drop=True)

    return prices


def get_most_recent_player_info(gw, season=CURRENT_SEASON):
    player_info = get_player_info(gw, season, prior=False)
    player_info = player_info[player_info['GW'] <= gw]
    most_recent_idx = player_info[['code', 'GW']].groupby('code')['GW'].idxmax()
    player_info = player_info.loc[most_recent_idx].reset_index(drop=True)

    return player_info