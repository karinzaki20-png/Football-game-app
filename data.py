# =========================================================
# ULTIMATE FOOTBALL - TEAMS & PLAYERS DATA
# =========================================================


def player(
    name,
    position,
    speed,
    shooting,
    passing,
    dribbling,
    defense,
    physical,
    stamina,
    legend=False,
):
    return {
        "name": name,
        "position": position,
        "speed": speed,
        "shooting": shooting,
        "passing": passing,
        "dribbling": dribbling,
        "defense": defense,
        "physical": physical,
        "stamina": stamina,
        "legend": legend,
    }


def add_team(name, gender, team_type, players):
    TEAMS[name] = {
        "gender": gender,
        "type": team_type,
        "players": players,
    }


# =========================================================
# DATA
# =========================================================

TEAMS = {}
TEAM_LOGO_FILES = {}


# =========================================================
# FC BARCELONA - MEN
# =========================================================

BARCELONA_MEN = [
    player(
        "Marc-Andre ter Stegen",
        "GK",
        70, 20, 92, 55, 91, 82, 88
    ),
    player(
        "Jules Kounde",
        "DEF",
        91, 40, 90, 82, 93, 84, 95
    ),
    player(
        "Pedri",
        "MID",
        82, 82, 98, 97, 60, 72, 92
    ),
    player(
        "Lamine Yamal",
        "FWD",
        97, 91, 94, 99, 35, 71, 94
    ),
    player(
        "Robert Lewandowski",
        "FWD",
        82, 97, 87, 89, 30, 91, 87
    ),
]


# =========================================================
# REAL MADRID - MEN
# =========================================================

REAL_MADRID_MEN = [
    player(
        "Thibaut Courtois",
        "GK",
        65, 20, 87, 48, 97, 91, 87
    ),
    player(
        "Dani Carvajal",
        "DEF",
        84, 55, 87, 81, 89, 84, 91
    ),
    player(
        "Federico Valverde",
        "MID",
        94, 82, 91, 90, 75, 91, 98
    ),
    player(
        "Vinicius Jr",
        "FWD",
        99, 94, 88, 99, 35, 82, 96
    ),
    player(
        "Kylian Mbappe",
        "FWD",
        99, 98, 91, 99, 35, 88, 97
    ),
]


# =========================================================
# FC BARCELONA - WOMEN
# =========================================================

BARCELONA_WOMEN = [
    player(
        "Cata Coll",
        "GK",
        76, 20, 88, 58, 91, 78, 91
    ),
    player(
        "Mapi Leon",
        "DEF",
        79, 45, 91, 78, 94, 83, 92
    ),
    player(
        "Aitana Bonmati",
        "MID",
        88, 91, 98, 97, 62, 76, 94
    ),
    player(
        "Caroline Graham Hansen",
        "FWD",
        96, 92, 95, 99, 35, 74, 93
    ),
    player(
        "Alexia Putellas",
        "MID",
        82, 94, 97, 96, 55, 79, 91,
        legend=True
    ),
]


# =========================================================
# REAL MADRID - WOMEN
# =========================================================

REAL_MADRID_WOMEN = [
    player(
        "Misa Rodriguez",
        "GK",
        78, 20, 87, 56, 90, 79, 90
    ),
    player(
        "Olga Carmona",
        "DEF",
        90, 72, 88, 84, 91, 80, 94
    ),
    player(
        "Linda Caicedo",
        "FWD",
        97, 90, 88, 98, 38, 75, 94
    ),
    player(
        "Athenea del Castillo",
        "FWD",
        95, 87, 90, 96, 35, 72, 93
    ),
    player(
        "Caroline Weir",
        "MID",
        84, 91, 96, 94, 52, 78, 90
    ),
]


# =========================================================
# REGISTER TEAMS
# =========================================================

add_team(
    "FC Barcelona",
    "Men",
    "Club",
    BARCELONA_MEN,
)

add_team(
    "Real Madrid",
    "Men",
    "Club",
    REAL_MADRID_MEN,
)

add_team(
    "FC Barcelona Women",
    "Women",
    "Club",
    BARCELONA_WOMEN,
)

add_team(
    "Real Madrid Women",
    "Women",
    "Club",
    REAL_MADRID_WOMEN,
)


# =========================================================
# TEAM LOGOS
# =========================================================

TEAM_LOGO_FILES["FC Barcelona"] = "barcelona.png"
TEAM_LOGO_FILES["Real Madrid"] = "real_madrid.png"

# Optional:
# If you have women's team logos, put these PNG files
# in the same folder as app.py.

TEAM_LOGO_FILES["FC Barcelona Women"] = "barcelona_women.png"
TEAM_LOGO_FILES["Real Madrid Women"] = "real_madrid_women.png"
