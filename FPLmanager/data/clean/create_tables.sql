DROP TABLE IF EXISTS player_gw;

CREATE TABLE player_gw (
    season VARCHAR(10),
    code INTEGER,
    gw INTEGER,
    opp_team_name VARCHAR(50),
    name VARCHAR(100),
    position VARCHAR(20),
    team VARCHAR(50),
    assists INTEGER,
    bonus INTEGER,
    bps INTEGER,
    clean_sheets INTEGER,
    creativity FLOAT,
    element INTEGER,
    fixture INTEGER,
    goals_conceded INTEGER,
    goals_scored INTEGER,
    ict_index FLOAT,
    influence FLOAT,
    kickoff_time VARCHAR(20),
    minutes INTEGER,
    opponent_team INTEGER,
    own_goals INTEGER,
    penalties_missed INTEGER,
    penalties_saved INTEGER,
    red_cards INTEGER,
    round INTEGER,
    saves INTEGER,
    selected INTEGER,
    team_a_score INTEGER,
    team_h_score INTEGER,
    threat FLOAT,
    total_points INTEGER,
    transfers_balance INTEGER,
    transfers_in INTEGER,
    transfers_out INTEGER,
    value FLOAT,
    was_home BOOLEAN,
    yellow_cards INTEGER,
    PRIMARY KEY (season, code, gw, opp_team_name)
);

DROP TABLE IF EXISTS fixtures;

CREATE TABLE fixtures (
    fixture INTEGER,
    gw INTEGER,
    season VARCHAR(10),
    kickoff_time VARCHAR(20),
    home_team VARCHAR(50),
    away_team VARCHAR(50),
    PRIMARY KEY (code)
);

DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    season VARCHAR(10),
    team INTEGER,
    team_name VARCHAR(50),
    PRIMARY KEY (season, team, team_name)
);

DROP TABLE IF EXISTS players;

CREATE TABLE players (
    name VARCHAR(100),
    code INTEGER,
    element INTEGER,
    position VARCHAR(3),
    season VARCHAR(10),
    team VARCHAR(50),
    gw INTEGER,
    PRIMARY KEY (code, season, team, gw)
);

DROP TABLE IF EXISTS prices;

CREATE TABLE prices (
    name VARCHAR(100),
    value INTEGER,
    element INTEGER,
    season VARCHAR(10),
    code INTEGER,
    gw INTEGER,
    PRIMARY KEY (code, season, gw, value)
);