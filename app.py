import random
from pathlib import Path

import streamlit as st

from data import TEAMS, TEAM_LOGO_FILES
from database import init_db, save_match, get_recent_matches


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Ultimate Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DATABASE
# =========================================================

init_db()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(139, 92, 246, 0.25),
                transparent 30%
            ),
            radial-gradient(
                circle at top right,
                rgba(236, 72, 153, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #0f172a 0%,
                #172554 45%,
                #312e81 100%
            );

        color: white;
    }


    /* Main content */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* Main title */
    .main-title {
        font-size: 58px;
        font-weight: 900;
        text-align: center;

        background:
            linear-gradient(
                90deg,
                #22d3ee,
                #a78bfa,
                #f472b6,
                #facc15
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        margin-bottom: 0;
    }


    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #cbd5e1;
        margin-bottom: 30px;
    }


    /* Cards */
    .football-card {
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.12),
                rgba(255,255,255,0.04)
            );

        border: 1px solid rgba(255,255,255,0.15);

        border-radius: 22px;

        padding: 25px;

        box-shadow:
            0 10px 30px rgba(0,0,0,0.25);

        margin-bottom: 20px;
    }


    /* Team card */
    .team-card {
        background:
            linear-gradient(
                145deg,
                rgba(99,102,241,0.30),
                rgba(236,72,153,0.18)
            );

        border: 1px solid rgba(255,255,255,0.18);

        border-radius: 20px;

        padding: 25px;

        text-align: center;

        min-height: 250px;

        box-shadow:
            0 12px 30px rgba(0,0,0,0.25);
    }


    /* Match score */
    .score {
        font-size: 70px;
        font-weight: 900;
        text-align: center;

        background:
            linear-gradient(
                90deg,
                #facc15,
                #f472b6,
                #a78bfa
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }


    /* Winner */
    .winner {
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        color: #facc15;

        padding: 15px;
    }


    /* Section titles */
    .section-title {
        font-size: 34px;
        font-weight: 850;
        margin-top: 20px;
        margin-bottom: 20px;

        color: #f8fafc;
    }


    /* Gender badges */
    .men-badge {
        display: inline-block;

        background:
            linear-gradient(
                90deg,
                #2563eb,
                #06b6d4
            );

        color: white;

        padding: 7px 16px;

        border-radius: 30px;

        font-weight: 700;
    }


    .women-badge {
        display: inline-block;

        background:
            linear-gradient(
                90deg,
                #ec4899,
                #a855f7
            );

        color: white;

        padding: 7px 16px;

        border-radius: 30px;

        font-weight: 700;
    }


    /* Buttons */
    div.stButton > button {
        width: 100%;

        border: none;

        border-radius: 14px;

        padding: 12px;

        font-weight: 800;

        font-size: 17px;

        background:
            linear-gradient(
                90deg,
                #6366f1,
                #ec4899
            );

        color: white;

        box-shadow:
            0 5px 20px rgba(99,102,241,0.35);

        transition: 0.2s;
    }


    div.stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 8px 25px rgba(236,72,153,0.45);
    }


    /* Metrics */
    div[data-testid="stMetric"] {
        background:
            rgba(255,255,255,0.08);

        border:
            1px solid rgba(255,255,255,0.12);

        padding: 15px;

        border-radius: 15px;
    }


    /* Sidebar */
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #111827,
                #1e1b4b,
                #312e81
            );
    }


    /* Sidebar title */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white;
    }


    /* Divider */
    hr {
        border-color:
            rgba(255,255,255,0.15);
    }


    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "match_result" not in st.session_state:
    st.session_state.match_result = None


if "gender_filter" not in st.session_state:
    st.session_state.gender_filter = "All"


# =========================================================
# FUNCTIONS
# =========================================================

def get_teams_by_gender(gender):
    if gender == "All":
        return list(TEAMS.keys())

    return [
        team_name
        for team_name in TEAMS
        if TEAMS[team_name]["gender"] == gender
    ]


def calculate_team_rating(team_name):
    players = TEAMS[team_name]["players"]

    if not players:
        return 0

    ratings = []

    for player_data in players:
        attributes = [
            player_data["speed"],
            player_data["shooting"],
            player_data["passing"],
            player_data["dribbling"],
            player_data["defense"],
            player_data["physical"],
            player_data["stamina"],
        ]

        ratings.append(
            sum(attributes) / len(attributes)
        )

    return round(
        sum(ratings) / len(ratings),
        1,
    )


def calculate_attack(team_name):
    players = TEAMS[team_name]["players"]

    if not players:
        return 0

    values = []

    for player_data in players:
        values.append(
            (
                player_data["speed"]
                + player_data["shooting"]
                + player_data["dribbling"]
            )
            / 3
        )

    return sum(values) / len(values)


def calculate_defense(team_name):
    players = TEAMS[team_name]["players"]

    if not players:
        return 0

    values = []

    for player_data in players:
        values.append(
            (
                player_data["defense"]
                + player_data["physical"]
                + player_data["stamina"]
            )
            / 3
        )

    return sum(values) / len(values)


def simulate_match(team_a, team_b):
    rating_a = calculate_team_rating(team_a)
    rating_b = calculate_team_rating(team_b)

    attack_a = calculate_attack(team_a)
    attack_b = calculate_attack(team_b)

    defense_a = calculate_defense(team_a)
    defense_b = calculate_defense(team_b)

    strength_a = (
        rating_a * 0.50
        + attack_a * 0.30
        + defense_a * 0.20
    )

    strength_b = (
        rating_b * 0.50
        + attack_b * 0.30
        + defense_b * 0.20
    )

    performance_a = (
        strength_a
        + random.uniform(-12, 12)
    )

    performance_b = (
        strength_b
        + random.uniform(-12, 12)
    )

    goals_a = max(
        0,
        int(
            random.gauss(
                1.4
                + (performance_a - performance_b) / 35,
                1.1,
            )
        ),
    )

    goals_b = max(
        0,
        int(
            random.gauss(
                1.4
                + (performance_b - performance_a) / 35,
                1.1,
            )
        ),
    )

    goals_a = min(goals_a, 7)
    goals_b = min(goals_b, 7)

    if goals_a > goals_b:
        winner = team_a

    elif goals_b > goals_a:
        winner = team_b

    else:
        winner = "Draw"

    return {
        "team_a": team_a,
        "team_b": team_b,
        "score_a": goals_a,
        "score_b": goals_b,
        "winner": winner,
    }


def display_logo(team_name, width=130):
    logo_file = TEAM_LOGO_FILES.get(team_name)

    if not logo_file:
        return

    logo_path = (
        Path(__file__).resolve().parent
        / logo_file
    )

    if logo_path.exists():
        st.image(
            str(logo_path),
            width=width,
        )

    else:
        st.markdown(
            f"""
            <div style="
                font-size:60px;
                text-align:center;
                padding:15px;
            ">
                ⚽
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_gender_badge(gender):
    if gender == "Women":
        st.markdown(
            '<span class="women-badge">'
            '👩 WOMEN'
            '</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="men-badge">'
            '👨 MEN'
            '</span>',
            unsafe_allow_html=True,
        )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '⚽ ULTIMATE FOOTBALL'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    '🏆 Colorful Football Match Simulator '
    '• Men & Women'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <h1 style="text-align:center;">
        ⚽ Ultimate Football
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "GAME MENU",
        [
            "🏠 Home",
            "⚽ Start Match",
            "👩 Women's Football",
            "👥 Teams & Players",
            "📊 Match History",
        ],
    )

    st.divider()

    st.markdown("### 🏟️ Teams")

    for team_name in TEAMS:

        gender = TEAMS[team_name]["gender"]

        if gender == "Women":
            icon = "👩"
        else:
            icon = "👨"

        st.write(
            f"{icon} **{team_name}**"
        )


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.markdown(
        '<div class="section-title">'
        'Welcome to Ultimate Football ⚽'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="football-card">

        <h2>🏆 Welcome!</h2>

        <p style="font-size:18px;">
        Create exciting football matches between
        men's and women's teams.
        </p>

        <p>
        Choose your teams, compare their ratings,
        simulate the match and check your history.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # Statistics

    total_players = sum(
        len(TEAMS[team]["players"])
        for team in TEAMS
    )

    men_teams = len(
        get_teams_by_gender("Men")
    )

    women_teams = len(
        get_teams_by_gender("Women")
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚽ Total Teams",
            len(TEAMS),
        )

    with col2:
        st.metric(
            "👨 Men's Teams",
            men_teams,
        )

    with col3:
        st.metric(
            "👩 Women's Teams",
            women_teams,
        )

    with col4:
        st.metric(
            "👥 Players",
            total_players,
        )

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '🏟️ Available Teams'
        '</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(2)

    for index, team_name in enumerate(TEAMS):

        with columns[index % 2]:

            gender = TEAMS[team_name]["gender"]

            st.markdown(
                '<div class="team-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"<h2>{team_name}</h2>",
                unsafe_allow_html=True,
            )

            display_logo(
                team_name,
                width=110,
            )

            display_gender_badge(gender)

            st.write("")

            st.metric(
                "⭐ Team Rating",
                calculate_team_rating(
                    team_name
                ),
            )

            st.write(
                f"👥 {len(TEAMS[team_name]['players'])} players"
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True,
            )


# =========================================================
# START MATCH
# =========================================================

elif page == "⚽ Start Match":

    st.markdown(
        '<div class="section-title">'
        '⚽ Start a Match'
        '</div>',
        unsafe_allow_html=True,
    )

    # Gender selection

    gender = st.radio(
        "Choose football category",
        [
            "Men",
            "Women",
            "All",
        ],
        horizontal=True,
    )

    available_teams = get_teams_by_gender(
        gender
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="football-card">',
            unsafe_allow_html=True,
        )

        st.subheader("🏠 Home Team")

        team_a = st.selectbox(
            "Select Home Team",
            available_teams,
            key="home_team_select",
        )

        display_logo(
            team_a,
            width=140,
        )

        display_gender_badge(
            TEAMS[team_a]["gender"]
        )

        st.metric(
            "⭐ Rating",
            calculate_team_rating(team_a),
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="football-card">',
            unsafe_allow_html=True,
        )

        st.subheader("✈️ Away Team")

        away_options = [
            team
            for team in available_teams
            if team != team_a
        ]

        if not away_options:

            st.warning(
                "You need at least two teams "
                "in this category."
            )

            st.stop()

        team_b = st.selectbox(
            "Select Away Team",
            away_options,
            key="away_team_select",
        )

        display_logo(
            team_b,
            width=140,
        )

        display_gender_badge(
            TEAMS[team_b]["gender"]
        )

        st.metric(
            "⭐ Rating",
            calculate_team_rating(team_b),
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Comparison

    st.markdown(
        '<div class="section-title">'
        '📊 Team Comparison'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "⭐ Overall Rating",
            calculate_team_rating(team_a),
            delta=round(
                calculate_team_rating(team_a)
                - calculate_team_rating(team_b),
                1,
            ),
        )

    with c2:

        st.metric(
            "⚡ Attack",
            round(
                calculate_attack(team_a),
                1,
            ),
            delta=round(
                calculate_attack(team_a)
                - calculate_attack(team_b),
                1,
            ),
        )

    with c3:

        st.metric(
            "🛡️ Defense",
            round(
                calculate_defense(team_a),
                1,
            ),
            delta=round(
                calculate_defense(team_a)
                - calculate_defense(team_b),
                1,
            ),
        )

    st.divider()

    if st.button(
        "🏆 START MATCH",
        type="primary",
        use_container_width=True,
    ):

        result = simulate_match(
            team_a,
            team_b,
        )

        st.session_state.match_result = result

        save_match(
            result["team_a"],
            result["team_b"],
            result["score_a"],
            result["score_b"],
        )

        st.balloons()

    # Result

    if st.session_state.match_result:

        result = st.session_state.match_result

        st.divider()

        st.markdown(
            '<div class="section-title">'
            '🏆 Match Result'
            '</div>',
            unsafe_allow_html=True,
        )

        r1, r2, r3 = st.columns(3)

        with r1:

            display_logo(
                result["team_a"],
                width=150,
            )

            st.markdown(
                f"""
                <h2 style="
                    text-align:center;
                ">
                {result['team_a']}
                </h2>
                """,
                unsafe_allow_html=True,
            )

        with r2:

            st.markdown(
                f"""
                <div class="score">
                    {result['score_a']}
                    -
                    {result['score_b']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="winner">
                    🏆 {result['winner']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with r3:

            display_logo(
                result["team_b"],
                width=150,
            )

            st.markdown(
                f"""
                <h2 style="
                    text-align:center;
                ">
                {result['team_b']}
                </h2>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# WOMEN'S FOOTBALL
# =========================================================

elif page == "👩 Women's Football":

    st.markdown(
        '<div class="section-title">'
        '👩 Women\'s Football'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="football-card">

        <h2>👩 Women's Football</h2>

        <p style="font-size:18px;">
        Explore the women's teams, their players
        and their football ratings.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    women_teams = get_teams_by_gender(
        "Women"
    )

    columns = st.columns(2)

    for index, team_name in enumerate(
        women_teams
    ):

        with columns[index]:

            st.markdown(
                '<div class="team-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"<h2>{team_name}</h2>",
                unsafe_allow_html=True,
            )

            display_logo(
                team_name,
                width=130,
            )

            display_gender_badge(
                "Women"
            )

            st.write("")

            st.metric(
                "⭐ Team Rating",
                calculate_team_rating(
                    team_name
                ),
            )

            st.write(
                f"👩 {len(TEAMS[team_name]['players'])} players"
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    st.subheader(
        "👩 Featured Women's Players"
    )

    for team_name in women_teams:

        st.markdown(
            f"### 🏟️ {team_name}"
        )

        for player_data in TEAMS[
            team_name
        ]["players"]:

            st.write(
                f"**{player_data['name']}** "
                f"— {player_data['position']}"
            )


# =========================================================
# TEAMS & PLAYERS
# =========================================================

elif page == "👥 Teams & Players":

    st.markdown(
        '<div class="section-title">'
        '👥 Teams & Players'
        '</div>',
        unsafe_allow_html=True,
    )

    gender_filter = st.selectbox(
        "Filter by gender",
        [
            "All",
            "Men",
            "Women",
        ],
    )

    available_teams = get_teams_by_gender(
        gender_filter
    )

    selected_team = st.selectbox(
        "Choose a team",
        available_teams,
    )

    team = TEAMS[selected_team]

    col1, col2 = st.columns(
        [1, 3]
    )

    with col1:

        st.markdown(
            '<div class="football-card">',
            unsafe_allow_html=True,
        )

        display_logo(
            selected_team,
            width=150,
        )

        st.markdown(
            f"<h2>{selected_team}</h2>",
            unsafe_allow_html=True,
        )

        display_gender_badge(
            team["gender"]
        )

        st.write("")

        st.metric(
            "⭐ Team Rating",
            calculate_team_rating(
                selected_team
            ),
        )

        st.write(
            f"👥 Players: "
            f"{len(team['players'])}"
        )

        st.write(
            f"🏟️ Type: "
            f"{team['type']}"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

    with col2:

        st.subheader(
            f"Players — {selected_team}"
        )

        for player_data in team[
            "players"
        ]:

            with st.expander(
                f"⚽ {player_data['name']} "
                f"— {player_data['position']}"
            ):

                c1, c2, c3, c4 = st.columns(
                    4
                )

                with c1:
                    st.metric(
                        "⚡ Speed",
                        player_data["speed"],
                    )

                with c2:
                    st.metric(
                        "🎯 Shooting",
                        player_data["shooting"],
                    )

                with c3:
                    st.metric(
                        "🎯 Passing",
                        player_data["passing"],
                    )

                with c4:
                    st.metric(
                        "🔥 Dribbling",
                        player_data["dribbling"],
                    )

                c5, c6, c7 = st.columns(
                    3
                )

                with c5:
                    st.metric(
                        "🛡️ Defense",
                        player_data["defense"],
                    )

                with c6:
                    st.metric(
                        "💪 Physical",
                        player_data["physical"],
                    )

                with c7:
                    st.metric(
                        "🔋 Stamina",
                        player_data["stamina"],
                    )

                if player_data["legend"]:
                    st.success(
                        "⭐ LEGEND PLAYER"
                    )


# =========================================================
# MATCH HISTORY
# =========================================================

elif page == "📊 Match History":

    st.markdown(
        '<div class="section-title">'
        '📊 Match History'
        '</div>',
        unsafe_allow_html=True,
    )

    matches = get_recent_matches(
        20
    )

    if not matches:

        st.info(
            "⚽ No matches have been played yet."
        )

    else:

        for match in matches:

            (
                played_at,
                team_a,
                team_b,
                score_a,
                score_b,
            ) = match

            gender_a = TEAMS.get(
                team_a,
                {}
            ).get(
                "gender",
                "Unknown",
            )

            if gender_a == "Women":
                icon = "👩"
            else:
                icon = "⚽"

            st.markdown(
                f"""
                <div class="football-card">

                <h3>
                    {icon}
                    {team_a}
                    &nbsp;&nbsp;

                    <strong>
                    {score_a} - {score_b}
                    </strong>

                    &nbsp;&nbsp;
                    {team_b}
                </h3>

                <p>
                    🕐 Played at:
                    {played_at}
                </p>

                </div>
                """,
                unsafe_allow_html=True,
            )
