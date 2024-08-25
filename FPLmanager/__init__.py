import os
import yaml


# ----------------------------------- GLOBAL VARIABLES ----------------------------------- #
CURRENT_SEASON = 2024
CURRENT_SEASON_STR = str(CURRENT_SEASON) + '-' + str(CURRENT_SEASON + 1)[2:]

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(PACKAGE_DIR, 'data', 'clean')

POSITIONS = {
    1: 'GK',
    2: 'DEF',
    3: 'MID',
    4: 'FWD'
}


def get_postgres_url():
    """
    Read the PostgreSQL URL from the config.yaml file.
    
    Returns:
    str: The PostgreSQL URL from the config file.
    """
    config_path = os.path.join(os.path.dirname(PACKAGE_DIR), 'config.yaml')
    
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    return config.get('postgres_url')


DB_URL = get_postgres_url()