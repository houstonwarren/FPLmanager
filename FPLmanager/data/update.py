import requests
import pandas as pd
from FPLmanager import DATA, CURRENT_SEASON, CURRENT_SEASON_STR, POSITIONS
from FPLmanager.data.db import get_players, get_fixtures, get_prices, get_teams, \
    get_player_gws, update_table, get_team_id_map
from FPLmanager.data.fplapi import get_bootstrap_data, get_fixtures_data, \
    current_gameweek, get_player_history
from FPLmanager.utils import season_str


# --------------------------------- CURRENT SEASON TEAMS --------------------------------- #
def updated_teams(bootstrap=None):
    if bootstrap is None:
        bootstrap = get_bootstrap_data()
    teams = pd.DataFrame(bootstrap['teams'])[['id', 'name', 'code']]

    # match teams to current season
    teams['season'] = season_str(CURRENT_SEASON)
    teams = teams.rename(columns={'id': 'team', 'name': 'team_name'})
    teams = teams[['season', 'team', 'team_name']]

    return teams


# ---------------------------------------- FIXTURES ---------------------------------------- #
def updated_fixtures():
    current_fixtures = pd.DataFrame(get_fixtures_data())
    current_fixtures = current_fixtures[['id', 'event', 'kickoff_time', 'team_h', 'team_a', 'code']]
    
    teams = get_teams()
    teams = teams[teams['season'] == CURRENT_SEASON_STR].reset_index(drop=True)[['team', 'team_name']]

    # reformat to match fixture registry
    current_fixtures['season'] = CURRENT_SEASON_STR
    current_fixtures = current_fixtures.merge(
        teams, left_on='team_h', right_on='team').drop('team', axis=1)
    current_fixtures = current_fixtures.merge(
        teams, left_on='team_a', right_on='team').drop('team', axis=1)
    current_fixtures = current_fixtures.rename(
        columns={'team_name_x': 'home_team', 'team_name_y': 'away_team', 
                 'id': 'fixture', 'event': 'gw'}
    )
    current_fixtures = current_fixtures[[
        'fixture', 'gw', 'season', 'kickoff_time', 'home_team', 'away_team', 'code'
    ]]
    current_fixtures = current_fixtures.sort_values(
        by='fixture', ascending=True).reset_index(drop=True)

    return current_fixtures


# ------------------------------------ PLAYER REGISTRY ----------------------------------- #
def get_current_players(bootstrap=None):
    if bootstrap is None:
        bootstrap = get_bootstrap_data()
    current_players = pd.DataFrame(bootstrap['elements'])

    # format bootstrap data to match player registry
    current_players['season'] = season_str(CURRENT_SEASON)
    current_players['position'] = current_players['element_type'].map(POSITIONS)
    current_players['name'] = current_players['first_name'] + ' ' + current_players['second_name']
    current_players = current_players.rename(columns={'id': 'element'})
    current_players = current_players[['name', 'code', 'element', 'position', 'season']]
    return current_players


def updated_player_registry(bootstrap=None):
    current_gw, _ = current_gameweek()
    current_players = get_player_gws(prior=False)[[
        'name', 'code', 'element', 'position', 'season', 'team', 'gw'
    ]]

    # format data to match player registry
    first_weeks_on_team = current_players.groupby([
        'code', 'name', 'team'
    ])['gw'].idxmin()
    current_players = current_players.iloc[first_weeks_on_team].sort_values(
        by=['name', 'season', 'gw']
    ).reset_index(drop=True)

    return current_players


# ----------------------------------- PLAYER gw SCORES ----------------------------------- #
def updated_player_gw_scores(bootstrap=None):
    current_gw, _ = current_gameweek()
    players = get_current_players(bootstrap)
    # get data
    fixtures = get_fixtures(prior=False)[['fixture', 'home_team', 'away_team']]
    elements = players['element'].unique()
    players = players[['element', 'name', 'code', 'position']].drop_duplicates()
    
    # query api for player history
    histories = []
    for el in elements:
        player_history = get_player_history(el)
        player_gw_scores = player_history['history']
        histories.extend(player_gw_scores)

    player_gw_scores = pd.DataFrame(histories)
    player_gw_scores = player_gw_scores.dropna().reset_index(drop=True)

    # update to match player_gw table
    player_gw_scores['season'] = season_str(CURRENT_SEASON)
    player_gw_scores['gw'] = player_gw_scores['round']
    player_gw_scores = player_gw_scores.merge(
        fixtures, left_on='fixture', right_on='fixture'
    )
    player_gw_scores['team'] = player_gw_scores.apply(
        lambda x: x['home_team'] if x['was_home'] else x['away_team'], axis=1
    )
    player_gw_scores['opp_team_name'] = player_gw_scores.apply(
        lambda x: x['away_team'] if x['was_home'] else x['home_team'], axis=1
    )
    player_gw_scores = player_gw_scores.merge(
        players, on='element'
    )

    player_gw_scores = player_gw_scores.drop(
        columns=[
            'home_team', 'away_team', 'expected_assists', 'expected_goal_involvements',
            'expected_goals', 'expected_goals_conceded', 'starts'
        ]
    )
    player_gw_scores = player_gw_scores.sort_values(['name', 'gw'], ascending=True)

    return player_gw_scores


# ---------------------------------------- PRICES ---------------------------------------- #
def updated_prices():
    player_gws = get_player_gws(prior=False)
    prices = player_gws[['code', 'gw', 'price']]

    # subset only to times when player value changes
    player_value = player_gws.copy()[['name', 'value', 'element', 'season', 'code', 'gw']].sort_values(
        by=['season', 'gw', 'name']
    ).reset_index(drop=True)
    player_value['value_delta'] = player_value.groupby(['code', 'season'])['value'].diff()
    price_changes = player_value[
        (player_value['value_delta'].isna()) | (player_value['value_delta'] != 0)
    ].reset_index(drop=True)
    price_changes = price_changes.drop(columns=['value_delta'])

    return prices


# -------------------------------------- FULL UPDATE ------------------------------------- #
def update_database(): 
    # bootstrap data
    bootstrap = get_bootstrap_data()

    # teams
    teams = updated_teams()
    update_table('teams', teams)

    # fixtures
    fixtures = updated_fixtures()
    update_table('fixtures', fixtures)  # overwrites this season's data
    
    # player gw scores
    player_gw_scores = updated_player_gw_scores()
    update_table('player_gw', player_gw_scores)  # overwrites this season's data

    # current players
    players = updated_player_registry(bootstrap)
    update_table('players', players)  # overwrites this season's data

    # prices




if __name__ == "__main__":
    update_database()
