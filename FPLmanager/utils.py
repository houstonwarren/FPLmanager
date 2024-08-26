# ---------------------------------------------------------------------------------------- #
#                                         UTILITIES                                        #
# ---------------------------------------------------------------------------------------- #

# ----------------------------------- HELPER FUNCTIONS ----------------------------------- #
def season_str(season_st: int) -> str:
    season_st_str = str(season_st)
    season_end_str = str(season_st + 1)[-2:]

    return f"{season_st_str}-{season_end_str}" 


def next_gameweeks(gw, n=1):
    next_gw = [_gw for _gw in range(
        gw + 1, gw + n + 1
    ) if _gw <= 38]

    return next_gw


def full_name(df, first_name_col='first_name', last_name_col='second_name'):
    return df[first_name_col] + ' ' + df[last_name_col]
