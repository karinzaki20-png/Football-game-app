# Football-game-app
# ⚽ Ultimate Football

Ultimate Football is a Python + Streamlit football game prototype.

The project simulates football matches between clubs and national teams, with support for men's and women's teams, player data, ratings, match statistics, events, team logos, player images, and saved match history.

---

## ⚽ Features

- Football match simulation
- Home team vs Away team
- Clubs and national teams
- Men's and women's teams
- Player rosters
- Player ratings
- Team ratings
- Joblib / Scikit-learn rating model
- Match statistics
- Match events
- Player photos
- Team logos
- Team search
- Player search
- SQLite match history
- Match controls
- 90-minute match simulation

### Match Controls

- +1 MINUTE — Advance the match by one minute
- HOME SHOOT — Create an attack for the home team
- AWAY SHOOT — Create an attack for the away team
- PASS — Change the current possession

---

# 📁 Project Structure

```text
UltimateFootball/
│
├── app.py
├── data.py
├── database.py
├── train_model.py
├── player_model.joblib
├── football.db
├── requirements.txt
├── README.md
│
└── assets/
    │
    ├── players/
    │   ├── lionel_messi.png
    │   ├── lamine_yamal.png
    │   ├── marta.png
    │   ├── alex_morgan.png
    │   └── ...
    │
    ├── teams/
    │   ├── brazil.png
    │   ├── france.png
    │   ├── italy.png
    │   └── ...
    │
    └── flags/
