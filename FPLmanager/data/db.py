# ---------------------------------------------------------------------------------------- #
#                                 FUNCTIONS TO ACCESS DATA                                 #
# ---------------------------------------------------------------------------------------- #
from FPLmanager import DATA, CURRENT_SEASON, CURRENT_SEASON_STR, DB_URL
import pandas as pd
import sqlite3
import functools
from FPLmanager import data
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Table, MetaData
from sqlalchemy import inspect


# ------------------------------------ DB CONNECTIONS ------------------------------------ #
def get_engine():
    return create_engine(DB_URL)


def query_to_dataframe(table_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            engine = get_engine()
            conn = engine.connect()
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
            conn.close()

            kwargs['df'] = df
            return func(*args, **kwargs)
        return wrapper
    return decorator


def update_table(table_name, df, replace=False):
    """
    Update a PostgreSQL table with data from a pandas DataFrame using SQLAlchemy.
    Automatically detects primary keys from the table schema.
    """
    engine = get_engine()
    
    with engine.connect() as connection:
        if replace:
            # Drop the table if it exists and create a new one
            df.to_sql(table_name, connection, if_exists='replace', index=False)
        else:
            # Get table metadata and primary keys
            table = Table(table_name, MetaData(), autoload_with=engine)
            primary_keys = [
                pk.name for pk in inspect(table).primary_key
            ]

            # Create an insert statement
            stmt = insert(table).values(df.to_dict(orient='records'))

            # Add ON CONFLICT clause to update existing rows
            update_dict = {c.name: c for c in stmt.excluded if c.name not in primary_keys}
            stmt = stmt.on_conflict_do_update(
                index_elements=primary_keys,
                set_=update_dict
            )

            # Execute the statement
            result = connection.execute(stmt)
            connection.commit()

    print(f"Updated {result.rowcount} rows in table '{table_name}'")


# ----------------------------------------- UTILS ---------------------------------------- #
def filter_gw_season(df, gw=None, season=CURRENT_SEASON, prior=True):
    """
    Filter a DataFrame by gameweek and season.
    """
    df['season_num'] = df['season'].apply(lambda x: int(x.split('-')[0]))
    current_df = df[df['season_num'] == season]

    if gw is not None:
        current_df = current_df[current_df['gw'] <= gw]

    if prior:
        prior_df = df[df['season_num'] < season]
        df = pd.concat([prior_df, current_df]).reset_index(drop=True)
    else:
        df = current_df.reset_index(drop=True)

    df = df.drop(columns=['season_num'])
    return df


# ---------------------------------------- GETTERS --------------------------------------- #
@query_to_dataframe('player_gw')
def get_player_gws(df=None, gw=None, season=CURRENT_SEASON, prior=True):
    return filter_gw_season(df, gw, season, prior)


@query_to_dataframe('fixtures')
def get_fixtures(df=None, gw=None, season=CURRENT_SEASON, prior=True):
    return filter_gw_season(df, gw, season, prior)


@query_to_dataframe('prices')
def get_prices(df=None, gw=None, season=CURRENT_SEASON, prior=True):
    return filter_gw_season(df, gw, season, prior)


@query_to_dataframe('teams')
def get_teams(df=None, gw=None, season=CURRENT_SEASON, prior=True):
    return filter_gw_season(df, gw, season, prior)


@query_to_dataframe('players')
def get_players(df=None, gw=None, season=CURRENT_SEASON, prior=True):
    players = filter_gw_season(df, gw, season, prior)
    players = players.sort_values(by=['name', 'gw']).reset_index(drop=True)
    return players


# ----------------------------------- ADVANCED GETTERS ----------------------------------- #
def get_most_recent_prices(gw, season=CURRENT_SEASON):
    prices = get_prices(gw, season, prior=False)
    prices = prices[prices['gw'] <= gw]
    most_recent_idx = prices[['code', 'gw']].groupby('code')['gw'].idxmax()
    prices = prices.loc[most_recent_idx].reset_index(drop=True)

    return prices


def get_most_recent_player_info(gw, season=CURRENT_SEASON):
    players = get_players(gw, season, prior=False)
    players = players[players['gw'] <= gw]
    most_recent_idx = players[['code', 'gw']].groupby('code')['gw'].idxmax()
    players = players.loc[most_recent_idx].reset_index(drop=True)

    return players


def get_team_id_map(season=CURRENT_SEASON, prior=True, reverse=False):
    teams = get_teams(season=season, prior=prior)
    if reverse:
        season_maps = teams.groupby(
            ['team_name', 'season']
        )['team'].apply(lambda x: x.iloc[0]).unstack().to_dict()
    
        for season in season_maps.keys():
            season_maps[season] = {k: int(v) for k, v in season_maps[season].items() if not np.isnan(v)}

    else:
        season_maps = teams.groupby(
            ['team', 'season']
        )['team_name'].apply(lambda x: x.iloc[0]).unstack().to_dict()

    if prior is False:
        return season_maps[CURRENT_SEASON_STR]
    return season_maps