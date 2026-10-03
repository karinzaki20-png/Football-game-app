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
        .main-title {
            font-size: 48px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            font-size: 18px;
            margin-bottom: 30px;
        }

        .team-card {
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #ddd;
            text-align: center;
            margin-bottom: 15px;
        }

        .score {
            font-size: 48px;
            font-weight: 800;
            text-align: center;
        }

        .winner {
            font-size: 25px;
            font-weight: 700;
            text-align: center;
        }

        .section-title {
            font-size: 28px;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 15px;
        }

        div.stButton > button {
            width: 100%;
            font-weight: 700;
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

if "team_a" not in st.session_state:
    st.session_state.team_a = None

if "team_b" not in st.session_state:
    st.session_state.team_b = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def calculate_team_rating(team_name):
    """
    Calculate the average overall rating of a team.
    """
    players = TEAMS[team_name]["players"]

    if not players:
        return 0

    ratings = []

    for player in players:
        attributes = [
            player["speed"],
            player["shooting"],
            player["passing"],
            player["dribbling"],
            player["defense"],
            player["physical"],
            player["stamina"],
        ]

        ratings.append(sum(attributes) / len(attributes))

    return round(sum(ratings) / len(ratings), 1)


def calculate_attack(team_name):
    players = TEAMS[team_name]["players"]

    if not players:
        return 0

    values = []

    for player in players:
        values.append(
            (
                player["speed"]
                + player["shooting"]
                + player["dribbling"]
            )
            / 3
        )

    return sum(values) / len(values)


def calculate_defense(team_name):
    players = TEAMS[team_name]["players"]

    if not players:
        return 0

    values = []

    for player in players:
        values.append(
            (
                player["defense"]
                + player["physical"]
                + player["stamina"]
            )
            / 3
        )

    return sum(values) / len(values)


def simulate_match(team_a, team_b):
    """
    Simple football match simulation.

    The result is based on team ratings and random variation.
    """

    rating_a = calculate_team_rating(team_a)
    rating_b = calculate_team_rating(team_b)

    attack_a = calculate_attack(team_a)
    attack_b = calculate_attack(team_b)

    defense_a = calculate_defense(team_a)
    defense_b = calculate_defense(team_b)

    # Overall strength
    strength_a = (
        rating_a * 0.5
        + attack_a * 0.3
        + defense_a * 0.2
    )

    strength_b = (
        rating_b * 0.5
        + attack_b * 0.3
        + defense_b * 0.2
    )

    # Random football variation
    performance_a = strength_a + random.uniform(-12, 12)
    performance_b = strength_b + random.uniform(-12, 12)

    # Base goals
    goals_a = max(
        0,
        int(
            random.gauss(
                1.4 + (performance_a - performance_b) / 35,
                1.1,
            )
        ),
    )

    goals_b = max(
        0,
        int(
            random.gauss(
                1.4 + (performance_b - performance_a) / 35,
                1.1,
            )
        ),
    )

    # Prevent unrealistic huge scores
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


def display_logo(team_name):
    """
    Display team logo if the image exists.
    """

    logo_file = TEAM_LOGO_FILES.get(team_name)

    if not logo_file:
        return

    logo_path = Path(__file__).resolve().parent / logo_file

    if logo_path.exists():
        st.image(str(logo_path), width=120)
    else:
        st.info(f"Logo not found: {logo_file}")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">⚽ Ultimate Football</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Football Match Simulator</div>',
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Game Menu")

    page = st.radio(
        "Choose a page:",
        [
            "🏠 Home",
            "⚽ Start Match",
            "👥 Teams & Players",
            "📊 Match History",
        ],
    )

    st.divider()

    st.write("### Available Teams")

    for team_name in TEAMS:
        team_type = TEAMS[team_name]["type"]
        gender = TEAMS[team_name]["gender"]

        st.write(
            f"**{team_name}**  \n"
            f"{gender} • {team_type}"
        )


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.markdown(
        '<div class="section-title">Welcome to Ultimate Football</div>',
        unsafe_allow_html=True,
    )

    st.write(
        """
        Welcome to **Ultimate Football**, a football match simulator
        built with Python and Streamlit.

        Choose two teams, compare their players and ratings,
        simulate a football match, and save the result to the
        match history.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Teams",
            len(TEAMS),
        )

    with col2:
        total_players = sum(
            len(TEAMS[name]["players"])
            for name in TEAMS
        )

        st.metric(
            "Players",
            total_players,
        )

    with col3:
        st.metric(
            "Database",
            "SQLite",
        )

    st.divider()

    st.subheader("Available Teams")

    columns = st.columns(len(TEAMS))

    for index, team_name in enumerate(TEAMS):

        with columns[index]:

            st.markdown(
                f"### {team_name}"
            )

            display_logo(team_name)

            st.write(
                f"**Type:** {TEAMS[team_name]['type']}"
            )

            st.write(
                f"**Gender:** {TEAMS[team_name]['gender']}"
            )

            rating = calculate_team_rating(team_name)

            st.metric(
                "Team Rating",
                rating,
            )


# =========================================================
# START MATCH
# =========================================================

elif page == "⚽ Start Match":

    st.markdown(
        '<div class="section-title">Start a Match</div>',
        unsafe_allow_html=True,
    )

    team_names = list(TEAMS.keys())

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Home Team")

        team_a = st.selectbox(
            "Select Home Team",
            team_names,
            key="home_team",
        )

        display_logo(team_a)

        st.metric(
            "Rating",
            calculate_team_rating(team_a),
        )

    with col2:

        st.subheader("Away Team")

        team_b_options = [
            team for team in team_names
            if team != team_a
        ]

        team_b = st.selectbox(
            "Select Away Team",
            team_b_options,
            key="away_team",
        )

        display_logo(team_b)

        st.metric(
            "Rating",
            calculate_team_rating(team_b),
        )

    st.divider()

    # Team comparison

    st.subheader("Team Comparison")

    comparison_col1, comparison_col2, comparison_col3 = st.columns(3)

    with comparison_col1:

        st.metric(
            "Overall Rating",
            calculate_team_rating(team_a),
            delta=round(
                calculate_team_rating(team_a)
                - calculate_team_rating(team_b),
                1,
            ),
        )

    with comparison_col2:

        st.metric(
            "Attack",
            round(calculate_attack(team_a), 1),
            delta=round(
                calculate_attack(team_a)
                - calculate_attack(team_b),
                1,
            ),
        )

    with comparison_col3:

        st.metric(
            "Defense",
            round(calculate_defense(team_a), 1),
            delta=round(
                calculate_defense(team_a)
                - calculate_defense(team_b),
                1,
            ),
        )

    st.divider()

    if st.button(
        "⚽ START MATCH",
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

    # Match result

    if st.session_state.match_result:

        result = st.session_state.match_result

        st.divider()

        st.subheader("🏆 Match Result")

        result_col1, result_col2, result_col3 = st.columns(3)

        with result_col1:

            display_logo(result["team_a"])

            st.markdown(
                f"<h3 style='text-align:center;'>"
                f"{result['team_a']}"
                f"</h3>",
                unsafe_allow_html=True,
            )

        with result_col2:

            st.markdown(
                f"""
                <div class="score">
                    {result['score_a']} - {result['score_b']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with result_col3:

            display_logo(result["team_b"])

            st.markdown(
                f"<h3 style='text-align:center;'>"
                f"{result['team_b']}"
                f"</h3>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="winner">
                Winner: {result['winner']}
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# TEAMS & PLAYERS
# =========================================================

elif page == "👥 Teams & Players":

    st.markdown(
        '<div class="section-title">Teams & Players</div>',
        unsafe_allow_html=True,
    )

    selected_team = st.selectbox(
        "Choose a team",
        list(TEAMS.keys()),
    )

    team = TEAMS[selected_team]

    col1, col2 = st.columns([1, 3])

    with col1:

        display_logo(selected_team)

        st.metric(
            "Team Rating",
            calculate_team_rating(selected_team),
        )

        st.write(
            f"**Gender:** {team['gender']}"
        )

        st.write(
            f"**Type:** {team['type']}"
        )

    with col2:

        st.subheader(
            f"{selected_team} Players"
        )

        for player_data in team["players"]:

            with st.expander(
                f"{player_data['name']} — "
                f"{player_data['position']}"
            ):

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.metric(
                        "Speed",
                        player_data["speed"],
                    )

                with c2:
                    st.metric(
                        "Shooting",
                        player_data["shooting"],
                    )

                with c3:
                    st.metric(
                        "Passing",
                        player_data["passing"],
                    )

                with c4:
                    st.metric(
                        "Dribbling",
                        player_data["dribbling"],
                    )

                c5, c6, c7 = st.columns(3)

                with c5:
                    st.metric(
                        "Defense",
                        player_data["defense"],
                    )

                with c6:
                    st.metric(
                        "Physical",
                        player_data["physical"],
                    )

                with c7:
                    st.metric(
                        "Stamina",
                        player_data["stamina"],
                    )

                if player_data["legend"]:
                    st.success("⭐ Legend Player")


# =========================================================
# MATCH HISTORY
# =========================================================

elif page == "📊 Match History":

    st.markdown(
        '<div class="section-title">Match History</div>',
        unsafe_allow_html=True,
    )

    matches = get_recent_matches(20)

    if not matches:

        st.info(
            "No matches have been played yet."
        )

    else:

        for match in matches:

            played_at, team_a, team_b, score_a, score_b = match

            st.markdown(
                f"""
                ### ⚽ {team_a} {score_a} - {score_b} {team_b}

                Played at: `{played_at}`
                """
            )

            st.divider()


        

       
