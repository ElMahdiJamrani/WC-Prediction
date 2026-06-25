# ⚽ FIFA World Cup 2026 — Score Predictor

<div align="center">

![WC 2026](https://img.shields.io/badge/FIFA-World%20Cup%202026-00e676?style=for-the-badge&logo=fifa&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

### 🚀 [Live Demo → wc-prediction.streamlit.app](https://wc-prediction.streamlit.app/)

*AI-powered match score predictor & full tournament simulator for the 2026 FIFA World Cup*

</div>

---

## 📸 Preview

> Stadium atmosphere · Dark theme · Real 2026 bracket structure

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Head-to-Head Predictor** | Predict the exact score between any two national teams |
| 📊 **Probability Heatmap** | Full scoreline probability matrix (0–6 goals each) |
| 🏆 **Tournament Simulator** | Simulate the complete 2026 World Cup from groups to final |
| 🌍 **326 Teams** | All national teams with real Elo ratings |
| 🏟️ **Official Bracket** | Real FIFA 2026 Round of 32 slot structure (M73–M88) |
| 🎲 **Monte Carlo** | Every simulation is a unique random outcome |

---

## 🧠 How It Works

```
Match History (30+ years)
        ↓
  Elo Rating System
        ↓
 Poisson GLM Model  ←  Form, Goals, Elo diff
        ↓
 λ_home  &  λ_away   (expected goals)
        ↓
 Score Matrix  →  Win / Draw / Loss probabilities
        ↓
 Monte Carlo Simulation  →  Full bracket
```

### Model Features
- **Elo Rating** — team strength updated after every match
- **Home advantage** — built into the Poisson regression
- **Tournament weight** — World Cup matches weighted higher
- **Form** — recent average goals scored/conceded
- **Opponent strength** — opponent Elo and form factored in

---

## 🗂️ Project Structure

```
WC Prediction/
├── app/
│   ├── main.py                  # Streamlit app (UI + pages)
│   ├── model_utils.py           # Poisson model + simulation logic
│   ├── ui_components.py         # Bracket & group stage rendering
│   ├── world_cup_groups.py      # Official 2026 group draw
│   ├── constants.py             # Flag URLs, country codes
│   ├── requirements.txt         # Python dependencies
│   └── models/
│       ├── poisson_model.pkl    # Trained GLM model
│       └── team_elo_ratings.json
├── notebooks/
│   └── 01_data_exploration.ipynb
└── README.md
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/ElMahdiJamrani/WC-Prediction.git
cd WC-Prediction

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r app/requirements.txt

# 4. Run the app
streamlit run app/main.py
```

---

## 📦 Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web app framework
- **[statsmodels](https://www.statsmodels.org/)** — Poisson GLM regression
- **[Plotly](https://plotly.com/)** — Interactive heatmaps & charts
- **[NumPy](https://numpy.org/) / [Pandas](https://pandas.pydata.org/)** — Data processing
- **[SciPy](https://scipy.org/)** — Poisson distribution math

---

## 🏟️ Official 2026 Bracket Logic

The Round of 32 follows the **exact official FIFA 2026 bracket** :


The 8 best 3rd-place teams are assigned to open slots greedily by rank, respecting the no-same-group rule.

---

## 👨‍💻 Author

**El Mahdi Jamrani**
- GitHub: [@ElMahdiJamrani](https://github.com/ElMahdiJamrani)

---

<div align="center">
  Made with ❤️ and ⚽ · <a href="https://wc-prediction.streamlit.app/">wc-prediction.streamlit.app</a>
</div>
