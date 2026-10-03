import os
import re
import random
import unicodedata

import streamlit as st
import joblib


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Ultimate Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# IMPORT YOUR DATA
# ============================================================

try:
    from data import TEAMS
except Exception as e:
    st.error("❌ Could not load data.py")
    st.code(str(e))
    st.stop()


# Optional database
try:
    from database import init_db, save_match, get_recent_matches

    DATABASE_AVAILABLE = True

    try:
        init_db()
    except Exception:
        pass

except Exception:
    DATABASE_AVAILABLE = False


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)

PLAYERS_DIR = os.path.join(
    ASSETS_DIR,
    "players"
)

TEAMS_DIR = os.path.join(
    ASSETS_DIR,
    "teams"
)

FLAGS_DIR = os.path.join(
    ASSETS_DIR,
    "flags"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "player_model.joblib"
)


# ============================================================
# LOAD JOBLIB MODEL
# ============================================================

@st.cache_resource
def load_model():

    if not os.path.exists(MODEL_PATH):
        return None

    try:
        return joblib.load(MODEL_PATH)

    except Exception:
        return None


MODEL = load_model()


# ============================================================
# DATA HELPERS
# ============================================================

def get_team_data(team_name):

    data = TEAMS.get(team_name, {})

    if not isinstance(data, dict):
        return {}

    return data


def get_players(team_name):

    data = get_team_data(team_name)

    roster = data.get(
        "players",
        []
    )

    if isinstance(roster, list):
        return roster

    return []


def get_player_name(player):

    if isinstance(player, dict):

        return str(
            player.get(
                "name",
                "Unknown Player"
            )
        )

    return str(player)


def get_position(player):

    if isinstance(player, dict):

        return str(
            player.get(
                "position",
                "MID"
            )
        )

    return "MID"


def get_gender(team_name):

    return get_team_data(team_name).get(
        "gender",
        "Men"
    )


def get_type(team_name):

    return get_team_data(team_name).get(
        "type",
        "National"
    )


def get_country(team_name):

    return get_team_data(team_name).get(
        "country",
        ""
    )


def slugify(text):

    text = unicodedata.normalize(
        "NFKD",
        str(text)
    )

    text = (
        text
        .encode(
            "ascii",
            "ignore"
        )
        .decode()
    )

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    )

    return text.strip("_")


# ============================================================
# IMAGE HELPERS
# ============================================================

def find_player_image(player):

    name = get_player_name(player)

    slug = slugify(name)

    extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]

    for ext in extensions:

        path = os.path.join(
            PLAYERS_DIR,
            slug + ext
        )

        if os.path.exists(path):
            return path

    return None


def find_team_logo(team_name):

    data = get_team_data(team_name)

    logo = data.get("logo")

    if logo:

        path = os.path.join(
            TEAMS_DIR,
            logo
        )

        if os.path.exists(path):
            return path

    # fallback:
    # try team name automatically

    slug = slugify(team_name)

    for ext in [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]:

        path = os.path.join(
            TEAMS_DIR,
            slug + ext
        )

        if os.path.exists(path):
            return path

    return None


def find_flag(team_name):

    data = get_team_data(team_name)

    flag = data.get("flag")

    if flag:

        path = os.path.join(
            FLAGS_DIR,
            flag
        )

        if os.path.exists(path):
            return path

    return None


# ============================================================
# PLAYER RATINGS
# ============================================================

def calculate_rating(player):

    if not isinstance(player, dict):
        return 75

    # Existing rating
    if "rating" in player:

        try:
            return int(
                player["rating"]
            )

        except Exception:
            pass

    attributes = [
        player.get("speed", 75),
        player.get("shooting", 75),
        player.get("passing", 75),
        player.get("dribbling", 75),
        player.get("defense", 75),
        player.get("physical", 75),
        player.get("stamina", 75),
    ]

    try:

        values = [
            float(x)
            for x in attributes
        ]

        return round(
            sum(values) / len(values)
        )

    except Exception:

        return 75


def model_rating(player):

    if MODEL is None:
        return calculate_rating(player)

    if not isinstance(player, dict):
        return calculate_rating(player)

    features = [[
        player.get("speed", 75),
        player.get("shooting", 75),
        player.get("passing", 75),
        player.get("dribbling", 75),
        player.get("defense", 75),
        player.get("physical", 75),
        player.get("stamina", 75),
    ]]

    try:

        result = MODEL.predict(
            features
        )[0]

        return round(
            max(
                1,
                min(
                    99,
                    result
                )
            )
        )

    except Exception:

        return calculate_rating(player)


def team_rating(team_name):

    roster = get_players(
        team_name
    )

    if not roster:
        return 75

    ratings = [
        model_rating(player)
        for player in roster
    ]

    return round(
        sum(ratings) / len(ratings)
    )


# ============================================================
# TEAM LIST
# ============================================================

ALL_TEAMS = sorted(
    list(TEAMS.keys())
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {

    "home_team": None,
    "away_team": None,

    "home_score": 0,
    "away_score": 0,

    "minute": 0,

    "started": False,
    "finished": False,

    "possession": "home",

    "events": [],

    "home_shots": 0,
    "away_shots": 0,

    "home_passes": 0,
    "away_passes": 0,

    "home_possession": 50,
    "away_possession": 50,

    "selected_player": None,
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# RESET MATCH
# ============================================================

def reset_match():

    st.session_state.home_score = 0
    st.session_state.away_score = 0

    st.session_state.minute = 0

    st.session_state.started = False
    st.session_state.finished = False

    st.session_state.possession = "home"

    st.session_state.events = []

    st.session_state.home_shots = 0
    st.session_state.away_shots = 0

    st.session_state.home_passes = 0
    st.session_state.away_passes = 0

    st.session_state.home_possession = 50
    st.session_state.away_possession = 50

    st.session_state.selected_player = None


# ============================================================
# EVENT SYSTEM
# ============================================================

def add_event(text):

    event = (
        f"{st.session_state.minute}' — {text}"
    )

    st.session_state.events.insert(
        0,
        event
    )

    st.session_state.events = (
        st.session_state.events[:30]
    )


# ============================================================
# START MATCH
# ============================================================

def start_match():

    home = st.session_state.home_team
    away = st.session_state.away_team

    reset_match()

    st.session_state.home_team = home
    st.session_state.away_team = away

    st.session_state.started = True

    add_event(
        f"⚽ Kick-off: {home} vs {away}"
    )


# ============================================================
# POSSESSION
# ============================================================

def update_possession():

    home_strength = team_rating(
        st.session_state.home_team
    )

    away_strength = team_rating(
        st.session_state.away_team
    )

    total = (
        home_strength +
        away_strength
    )

    if total <= 0:
        return

    home_base = (
        home_strength / total
    ) * 100

    variation = random.randint(
        -5,
        5
    )

    home_possession = round(
        max(
            35,
            min(
                65,
                home_base + variation
            )
        )
    )

    away_possession = (
        100 -
        home_possession
    )

    st.session_state.home_possession = (
        home_possession
    )

    st.session_state.away_possession = (
        away_possession
    )


# ============================================================
# ATTACK ENGINE
# ============================================================

def attack(team):

    if not st.session_state.started:
        return

    if st.session_state.finished:
        return

    if team == "home":

        attacking_team = (
            st.session_state.home_team
        )

        defending_team = (
            st.session_state.away_team
        )

        st.session_state.home_shots += 1

    else:

        attacking_team = (
            st.session_state.away_team
        )

        defending_team = (
            st.session_state.home_team
        )

        st.session_state.away_shots += 1


    attack_power = team_rating(
        attacking_team
    )

    defense_power = team_rating(
        defending_team
    )

    difference = (
        attack_power -
        defense_power
    )

    chance = (
        0.12 +
        difference * 0.006
    )

    chance = max(
        0.04,
        min(
            0.35,
            chance
        )
    )


    if random.random() < chance:

        roster = get_players(
            attacking_team
        )

        if roster:

            scorer = random.choice(
                roster
            )

            scorer_name = get_player_name(
                scorer
            )

        else:

            scorer_name = "Unknown Player"


        if team == "home":

            st.session_state.home_score += 1

        else:

            st.session_state.away_score += 1


        add_event(
            f"⚽ GOAL! "
            f"{scorer_name} "
            f"scored for "
            f"{attacking_team}"
        )


    else:

        result = random.choice(
            [
                "Goalkeeper save!",
                "Shot went wide!",
                "Defender blocked the shot!",
                "Off the post!",
                "Shot was too weak!",
            ]
        )

        add_event(
            f"❌ {attacking_team}: {result}"
        )


# ============================================================
# ADVANCE MATCH
# ============================================================

def advance_minute():

    if not st.session_state.started:
        return

    if st.session_state.finished:
        return

    st.session_state.minute += 1

    update_possession()


    if random.random() < 0.5:

        st.session_state.possession = "home"

    else:

        st.session_state.possession = "away"


    current_team = (

        st.session_state.home_team
        if st.session_state.possession == "home"
        else
        st.session_state.away_team
    )


    # passes
    if st.session_state.possession == "home":

        st.session_state.home_passes += (
            random.randint(1, 5)
        )

    else:

        st.session_state.away_passes += (
            random.randint(1, 5)
        )


    # attack
    if random.random() < 0.42:

        attack(
            st.session_state.possession
        )

    else:

        add_event(
            f"🔵 {current_team} "
            f"keeps possession."
        )


    # End match
    if st.session_state.minute >= 90:

        st.session_state.minute = 90

        st.session_state.finished = True

        add_event(
            "🏁 FULL TIME!"
        )


# ============================================================
# MANUAL SHOOT
# ============================================================

def manual_shoot(team):

    if not st.session_state.started:
        return

    if st.session_state.finished:
        return

    attack(team)


# ============================================================
# PASS
# ============================================================

def pass_ball(team):

    if not st.session_state.started:
        return

    if st.session_state.finished:
        return


    st.session_state.possession = team


    if team == "home":

        st.session_state.home_passes += 1

        team_name = (
            st.session_state.home_team
        )

    else:

        st.session_state.away_passes += 1

        team_name = (
            st.session_state.away_team
        )


    add_event(
        f"🔵 {team_name} completed a pass."
    )


# ============================================================
# SAVE MATCH
# ============================================================

def save_current_match():

    if not DATABASE_AVAILABLE:
        return False

    if not st.session_state.started:
        return False

    try:

        save_match(
            st.session_state.home_team,
            st.session_state.away_team,
            st.session_state.home_score,
            st.session_state.away_score
        )

        return True

    except Exception:

        return False


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {

    background:
    radial-gradient(
        circle at top,
        #182945 0%,
        #0a111d 45%,
        #05080e 100%
    );

}


/* Main title */

.ultimate-title {

    text-align: center;

    font-size: 48px;

    font-weight: 900;

    letter-spacing: 2px;

    margin-top: 5px;

    margin-bottom: 2px;

}


.ultimate-subtitle {

    text-align: center;

    opacity: .65;

    margin-bottom: 25px;

}


/* Scoreboard */

.scoreboard {

    background:
    linear-gradient(
        135deg,
        rgba(30,45,70,.96),
        rgba(7,12,21,.96)
    );

    border:
    1px solid
    rgba(255,255,255,.12);

    border-radius: 25px;

    padding: 30px;

    text-align: center;

    box-shadow:
    0 15px 50px
    rgba(0,0,0,.35);

    margin-bottom: 20px;

}


.score {

    font-size: 62px;

    font-weight: 900;

    line-height: 1;

}


.team-title {

    font-size: 23px;

    font-weight: 800;

}


.minute {

    opacity: .7;

    margin-top: 8px;

}


/* Cards */

.card {

    background:
    rgba(255,255,255,.055);

    border:
    1px solid
    rgba(255,255,255,.10);

    border-radius: 18px;

    padding: 18px;

    margin-bottom: 12px;

}


/* Player */

.player-card {

    background:
    rgba(255,255,255,.04);

    border:
    1px solid
    rgba(255,255,255,.08);

    border-radius: 15px;

    padding: 10px;

    margin-bottom: 8px;

}


/* Rating */

.rating {

    font-size: 27px;

    font-weight: 900;

}


/* Event */

.event {

    background:
    rgba(255,255,255,.045);

    border-radius: 12px;

    padding: 11px 14px;

    margin-bottom: 6px;

}


/* Sidebar */

section[data-testid="stSidebar"] {

    background:
    linear-gradient(
        180deg,
        #111c30,
        #080d16
    );

}


/* Buttons */

.stButton > button {

    border-radius: 12px;

    font-weight: 700;

}


/* Search */

input {

    border-radius: 12px !important;

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="ultimate-title">'
    '⚽ ULTIMATE FOOTBALL'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="ultimate-subtitle">'
    '🌍 Clubs • National Teams • Men • Women'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🎮 MATCH SETUP"
    )


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    gender_filter = st.selectbox(
        "👤 Gender",
        [
            "All",
            "Men",
            "Women"
        ]
    )


    # --------------------------------------------------------
    # TYPE
    # --------------------------------------------------------

    type_filter = st.selectbox(
        "🏟️ Team Type",
        [
            "All",
            "National",
            "Club"
        ]
    )


    # --------------------------------------------------------
    # FILTER TEAMS
    # --------------------------------------------------------

    filtered_teams = []

    for team in ALL_TEAMS:

        if gender_filter != "All":

            if get_gender(team) != gender_filter:
                continue


        if type_filter != "All":

            if get_type(team) != type_filter:
                continue


        filtered_teams.append(team)


    if len(filtered_teams) < 2:

        st.warning(
            "Not enough teams for these filters."
        )

        filtered_teams = ALL_TEAMS


    # --------------------------------------------------------
    # HOME
    # --------------------------------------------------------

    home_default = 0


    if (
        st.session_state.home_team
        in filtered_teams
    ):

        home_default = (
            filtered_teams.index(
                st.session_state.home_team
            )
        )


    home_choice = st.selectbox(
        "🏠 HOME TEAM",
        filtered_teams,
        index=home_default,
        key="home_team_selector"
    )


    # --------------------------------------------------------
    # AWAY
    # --------------------------------------------------------

    away_default = (
        1 if len(filtered_teams) > 1 else 0
    )


    if (
        st.session_state.away_team
        in filtered_teams
    ):

        away_default = (
            filtered_teams.index(
                st.session_state.away_team
            )
        )


    away_choice = st.selectbox(
        "✈️ AWAY TEAM",
        filtered_teams,
        index=away_default,
        key="away_team_selector"
    )


    st.divider()


    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    if st.button(
        "🚀 START MATCH",
        use_container_width=True,
        type="primary"
    ):

        if home_choice == away_choice:

            st.error(
                "❌ Choose two different teams."
            )

        else:

            st.session_state.home_team = (
                home_choice
            )

            st.session_state.away_team = (
                away_choice
            )

            start_match()

            st.rerun()


    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    if st.button(
        "🔄 RESET MATCH",
        use_container_width=True
    ):

        reset_match()

        st.rerun()


# ============================================================
# DEFAULT TEAMS
# ============================================================

if st.session_state.home_team is None:

    st.session_state.home_team = (
        home_choice
    )


if st.session_state.away_team is None:

    st.session_state.away_team = (
        away_choice
    )


home = st.session_state.home_team
away = st.session_state.away_team


# ============================================================
# TOP TEAM DISPLAY
# ============================================================

home_col, center_col, away_col = st.columns(
    [2, 1, 2]
)


# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------

with home_col:

    logo = find_team_logo(home)

    if logo:

        st.image(
            logo,
            width=95
        )

    st.markdown(
        f'<div class="team-title">'
        f'🏠 {home}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"{get_gender(home)} • "
        f"{get_type(home)}"
    )

    st.metric(
        "⭐ Rating",
        team_rating(home)
    )


# ------------------------------------------------------------
# VS
# ------------------------------------------------------------

with center_col:

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:30px;
            font-weight:900;
            padding-top:45px;
        ">
        VS
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# AWAY
# ------------------------------------------------------------

with away_col:

    logo = find_team_logo(away)

    if logo:

        st.image(
            logo,
            width=95
        )

    st.markdown(
        f'<div class="team-title">'
        f'✈️ {away}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"{get_gender(away)} • "
        f"{get_type(away)}"
    )

    st.metric(
        "⭐ Rating",
        team_rating(away)
    )


# ============================================================
# SCOREBOARD
# ============================================================

st.markdown(
    '<div class="scoreboard">',
    unsafe_allow_html=True
)


s1, s2, s3 = st.columns(
    [2, 1, 2]
)


with s1:

    st.markdown(
        f'<div class="team-title">'
        f'{home}'
        f'</div>',
        unsafe_allow_html=True
    )


with s2:

    st.markdown(
        f'<div class="score">'
        f'{st.session_state.home_score}'
        f' - '
        f'{st.session_state.away_score}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="minute">'
        f'⏱️ {st.session_state.minute}\''
        f'</div>',
        unsafe_allow_html=True
    )


with s3:

    st.markdown(
        f'<div class="team-title">'
        f'{away}'
        f'</div>',
        unsafe_allow_html=True
    )


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# MATCH STATUS
# ============================================================

if not st.session_state.started:

    st.info(
        "🎮 Select your teams and press "
        "*START MATCH*."
    )


elif st.session_state.finished:

    if (
        st.session_state.home_score
        >
        st.session_state.away_score
    ):

        st.success(
            f"🏆 {home} WIN "
            f"{st.session_state.home_score}-"
            f"{st.session_state.away_score}"
        )


    elif (
        st.session_state.away_score
        >
        st.session_state.home_score
    ):

        st.success(
            f"🏆 {away} WIN "
            f"{st.session_state.away_score}-"
            f"{st.session_state.home_score}"
        )


    else:

        st.info(
            f"🤝 DRAW "
            f"{st.session_state.home_score}-"
            f"{st.session_state.away_score}"
        )


else:

    possession_team = (

        home
        if st.session_state.possession == "home"
        else
        away
    )

    st.info(
        f"🔵 Possession: *{possession_team}*"
    )


# ============================================================
# GAME CONTROLS
# ============================================================

st.subheader(
    "🎮 Match Controls"
)


b1, b2, b3, b4 = st.columns(4)


with b1:

    if st.button(
        "⏱️ +1 MINUTE",
        use_container_width=True
    ):

        advance_minute()

        st.rerun()


with b2:

    if st.button(
        "⚽ HOME SHOOT",
        use_container_width=True
    ):

        manual_shoot("home")

        st.rerun()


with b3:

    if st.button(
        "⚽ AWAY SHOOT",
        use_container_width=True
    ):

        manual_shoot("away")

        st.rerun()


with b4:

    if st.button(
        "🔵 PASS",
        use_container_width=True
    ):

        pass_ball(
            st.session_state.possession
        )

        st.rerun()


# ============================================================
# LAST EVENT
# ============================================================

if st.session_state.events:

    st.markdown(
        f"""
        <div class="card">

        <b>🎙️ LAST EVENT</b>

        <br><br>

        {st.session_state.events[0]}

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TABS
# ============================================================

tab_match, tab_teams, tab_players, tab_stats, tab_events = st.tabs(
    [
        "⚽ MATCH",
        "🌍 TEAMS",
        "👥 PLAYERS",
        "📊 STATS",
        "📜 EVENTS"
    ]
)


# ============================================================
# MATCH TAB
# ============================================================

with tab_match:

    st.markdown(
        "### 🟢 LIVE MATCH"
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            f"### 🏠 {home}"
        )

        st.metric(
            "Goals",
            st.session_state.home_score
        )

        st.metric(
            "Shots",
            st.session_state.home_shots
        )

        st.metric(
            "Possession",
            f"{st.session_state.home_possession}%"
        )


    with c2:

        st.markdown(
            f"### ✈️ {away}"
        )

        st.metric(
            "Goals",
            st.session_state.away_score
        )

        st.metric(
            "Shots",
            st.session_state.away_shots
        )

        st.metric(
            "Possession",
            f"{st.session_state.away_possession}%"
        )


    st.divider()


    st.markdown(
        "### 🏟️ Match Information"
    )


    info1, info2, info3 = st.columns(3)


    with info1:

        st.metric(
            "Home Rating",
            team_rating(home)
        )


    with info2:

        st.metric(
            "Match Time",
            f"{st.session_state.minute}'"
        )


    with info3:

        st.metric(
            "Away Rating",
            team_rating(away)
        )


# ============================================================
# ALL TEAMS TAB
# ============================================================

with tab_teams:

    st.markdown(
        "## 🌍 ALL TEAMS"
    )


    st.caption(
        f"{len(ALL_TEAMS)} teams loaded from data.py"
    )


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = st.text_input(
        "🔎 Search for a team",
        placeholder="Barcelona, Brazil, France..."
    )


    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    team_gender_filter = st.selectbox(
        "Gender",
        [
            "All",
            "Men",
            "Women"
        ],
        key="all_team_gender"
    )


    team_type_filter = st.selectbox(
        "Type",
        [
            "All",
            "National",
            "Club"
        ],
        key="all_team_type"
    )


    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    displayed_teams = []


    for team in ALL_TEAMS:

        if search:

            if search.lower() not in team.lower():
                continue


        if team_gender_filter != "All":

            if get_gender(team) != team_gender_filter:
                continue


        if team_type_filter != "All":

            if get_type(team) != team_type_filter:
                continue


        displayed_teams.append(team)


    st.write(
        f"Showing *{len(displayed_teams)}* teams"
    )


    # --------------------------------------------------------
    # TEAM GRID
    # --------------------------------------------------------

    for i in range(
        0,
        len(displayed_teams),
        3
    ):

        row = displayed_teams[
            i:i + 3
        ]

        cols = st.columns(3)


        for col, team in zip(
            cols,
            row
        ):

            with col:

                logo = find_team_logo(
                    team
                )


                if logo:

                    st.image(
                        logo,
                        width=70
                    )


                st.markdown(
                    f"### {team}"
                )


                st.caption(
                    f"{get_gender(team)} • "
                    f"{get_type(team)}"
                )


                st.write(
                    f"⭐ {team_rating(team)}"
                )


                st.write(
                    f"👥 {len(get_players(team))} players"
                )


                if st.button(
                    f"Use {team}",
                    key=f"use_team_{i}_{team}",
                    use_container_width=True
                ):

                    st.session_state.home_team = team

                    st.rerun()


# ============================================================
# PLAYERS TAB
# ============================================================

with tab_players:

    st.markdown(
        "## 👥 PLAYERS"
    )


    player_search = st.text_input(
        "🔎 Search player",
        placeholder="Messi, Marta, Yamal..."
    )


    # --------------------------------------------------------
    # CURRENT TEAM
    # --------------------------------------------------------

    st.markdown(
        f"### {home}"
    )


    roster = get_players(home)


    filtered_players = []


    for player in roster:

        name = get_player_name(
            player
        )


        if player_search:

            if (
                player_search.lower()
                not in name.lower()
            ):
                continue


        filtered_players.append(
            player
        )


    st.caption(
        f"{len(filtered_players)} players"
    )


    # --------------------------------------------------------
    # PLAYER CARDS
    # --------------------------------------------------------

    for i in range(
        0,
        len(filtered_players),
        3
    ):

        row = filtered_players[
            i:i + 3
        ]


        cols = st.columns(3)


        for col, player in zip(
            cols,
            row
        ):

            with col:

                name = get_player_name(
                    player
                )

                position = get_position(
                    player
                )

                rating = model_rating(
                    player
                )

                photo = find_player_image(
                    player
                )


                if photo:

                    st.image(
                        photo,
                        width=110
                    )

                else:

                    initials = "".join(
                        [
                            part[0]
                            for part in name.split()
                            if part
                        ]
                    )[:2].upper()


                    st.markdown(
                        f"""
                        <div style="
                            width:100px;
                            height:100px;
                            border-radius:50%;
                            background:#17243a;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            font-size:30px;
                            font-weight:900;
                            margin-bottom:10px;
                        ">
                        {initials}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                st.markdown(
                    f"*{name}*"
                )


                st.caption(
                    f"{position} • ⭐ {rating}"
                )


# ============================================================
# STATS TAB
# ============================================================

with tab_stats:

    st.markdown(
        "## 📊 MATCH STATISTICS"
    )


    stats1, stats2 = st.columns(2)


    with stats1:

        st.markdown(
            f"### 🏠 {home}"
        )

        st.metric(
            "Goals",
            st.session_state.home_score
        )

        st.metric(
            "Shots",
            st.session_state.home_shots
        )

        st.metric(
            "Passes",
            st.session_state.home_passes
        )

        st.metric(
            "Possession",
            f"{st.session_state.home_possession}%"
        )

        st.metric(
            "Team Rating",
            team_rating(home)
        )


    with stats2:

        st.markdown(
            f"### ✈️ {away}"
        )

        st.metric(
            "Goals",
            st.session_state.away_score
        )

        st.metric(
            "Shots",
            st.session_state.away_shots
        )

        st.metric(
            "Passes",
            st.session_state.away_passes
        )

        st.metric(
            "Possession",
            f"{st.session_state.away_possession}%"
        )

        st.metric(
            "Team Rating",
            team_rating(away)
        )


# ============================================================
# EVENTS TAB
# ============================================================

with tab_events:

    st.markdown(
        "## 📜 MATCH EVENTS"
    )


    if not st.session_state.events:

        st.info(
            "No events yet."
        )

    else:

        for event in (
            st.session_state.events
        ):

            st.markdown(
                f'<div class="event">'
                f'{event}'
                f'</div>',
                unsafe_allow_html=True
            )


# ============================================================
# SAVE MATCH
# ============================================================

if (
    st.session_state.finished
    and
    st.session_state.started
):

    st.divider()


    st.subheader(
        "💾 Match Result"
    )


    if DATABASE_AVAILABLE:

        if st.button(
            "💾 SAVE MATCH RESULT",
            use_container_width=True
        ):

            success = save_current_match()

            if success:

                st.success(
                    "✅ Match saved successfully!"
                )

            else:

                st.error(
                    "Could not save the match."
                )

    else:

        st.info(
            "database.py is not available."
        )


# ============================================================
# MATCH HISTORY
# ============================================================

if DATABASE_AVAILABLE:

    with st.expander(
        "📚 Recent Match History"
    ):

        try:

            matches = get_recent_matches(
                15
            )


            if not matches:

                st.caption(
                    "No saved matches yet."
                )


            else:

                for match in matches:

                    played_at = match[0]
                    team_a = match[1]
                    team_b = match[2]
                    score_a = match[3]
                    score_b = match[4]


                    st.write(
                        f"**{team_a} "
                        f"{score_a} - "
                        f"{score_b} "
                        f"{team_b}**"
                    )

                    st.caption(
                        played_at
                    )

                    st.divider()


        except Exception:

            st.caption(
                "Could not load match history."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚽ Ultimate Football • Streamlit Web Edition"
)
