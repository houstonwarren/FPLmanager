# ---------------------------------------------------------------------------------------- #
#                                      FPL API ACCESS                                      #
# ---------------------------------------------------------------------------------------- #
import requests
import json
from FPLmanager import CURRENT_SEASON


__all__ = [
    'ENDPOINTS',
    'get_bootstrap_data', 
    'get_fixtures_data', 
    'get_gw_entry_data',
    'get_player_history',
    'get_gw_player_data',
    'get_gameweeks',
    'get_entry_history', 
    'get_entry_transfers',
    'get_entry_picks',
    'current_gameweek'
]


# --------------------------------------- ENDPOINTS -------------------------------------- #
BASE_URL = "https://fantasy.premierleague.com/api/"
ENDPOINTS = {
    'bootstrap': f"{BASE_URL}bootstrap-static/",
    'fixtures': f"{BASE_URL}fixtures/",
    'event': f"{BASE_URL}event/",
    'entry': f"{BASE_URL}entry/",
    'league': f"{BASE_URL}leagues-classic/",
    'element': f"{BASE_URL}element-summary/",
}


# ------------------------------------ BASIC GAME INFO ----------------------------------- #
def get_bootstrap_data():
    response = requests.get(ENDPOINTS['bootstrap'])
    return response.json()


def get_fixtures_data():
    response = requests.get(ENDPOINTS['fixtures'])
    return response.json()


def get_gameweeks(gw_id):
    response = requests.get(ENDPOINTS['bootstrap']).json()
    events = response['events']
    if type(gw_id) == int:
        events = [event for event in events if event['id'] == gw_id][-1]
    elif gw_id == 'current':
        events = [event for event in events if event['is_current']][0]

    return events


def current_gameweek():
    return get_gameweeks('current')['id'], CURRENT_SEASON


# ---------------------------------------- PLAYERS --------------------------------------- #
def get_gw_player_data(gw):
    response = requests.get(f"{ENDPOINTS['event']}{gw}/live/")
    return response.json()


def get_player_history(player_id):
    response = requests.get(f"{ENDPOINTS['element']}{player_id}/")
    return response.json()


# ---------------------------------------- ENTRIES --------------------------------------- #
def get_gw_entry_data(entry_id, gw):
    response = requests.get(f"{ENDPOINTS['entry']}{entry_id}/event/{gw}/picks/")
    return response.json()


def get_entry_history(entry_id):
    response = requests.get(f"{ENDPOINTS['entry']}{entry_id}/history/")
    return response.json()


def get_entry_transfers(entry_id):
    response = requests.get(f"{ENDPOINTS['entry']}{entry_id}/transfers/")
    return response.json()


def get_entry_picks(entry_id, gw):
    response = requests.get(f"{ENDPOINTS['entry']}{entry_id}/event/{gw}/picks/")
    return response.json()

