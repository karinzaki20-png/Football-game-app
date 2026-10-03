# =========================================================
# ULTIMATE FOOTBALL - DATA
# =========================================================


def player(name, position, speed, shooting, passing, dribbling, defense, physical, stamina, legend=False):
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


TEAMS = {}
TEAM_LOGO_FILES = {}

BARCELONA = [
    player("Marc-Andre ter Stegen", "GK", 70, 20, 92, 55, 91, 82, 88),
    player("Jules Kounde", "DEF", 91, 40, 90, 82, 93, 84, 95),
    player("Pedri", "MID", 82, 82, 98, 97, 60, 72, 92),
    player("Lamine Yamal", "FWD", 97, 91, 94, 99, 35, 71, 94),
    player("Robert Lewandowski", "FWD", 82, 97, 87, 89, 30, 91, 87),
]

REAL_MADRID = [
    player("Thibaut Courtois", "GK", 65, 20, 87, 48, 97, 91, 87),
    player("Dani Carvajal", "DEF", 84, 55, 87, 81, 89, 84, 91),
    player("Federico Valverde", "MID", 94, 82, 91, 90, 75, 91, 98),
    player("Vinicius Jr", "FWD", 99, 94, 88, 99, 35, 82, 96),
    player("Kylian Mbappe", "FWD", 99, 98, 91, 99, 35, 88, 97),
]

add_team("FC Barcelona", "Men", "Club", BARCELONA)
add_team("Real Madrid", "Men", "Club", REAL_MADRID)
TEAM_LOGO_FILES["FC Barcelona"] = "barcelona.png"
TEAM_LOGO_FILES["Real Madrid"] = "real_madrid.png"
