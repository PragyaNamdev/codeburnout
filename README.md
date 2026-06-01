# 🔥 CodeBurnout — Developer Burnout Risk Predictor

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-green)](https://github.com)

> An AI-powered tool that analyzes GitHub commit history and predicts developer burnout risk using Machine Learning and NLP.

---

## 🚨 The Problem

Developer burnout is a silent epidemic. Late-night commits, weekend coding marathons, declining commit quality — the signs are in your GitHub history. But no one's watching.

**CodeBurnout watches.**

---

## 🧠 What It Does

- 🔍 Analyzes your GitHub commit history via GitHub API
- 🕐 Detects late-night and weekend commit patterns
- 💬 Runs sentiment analysis on your commit messages using VADER NLP
- 📉 Identifies frequency drops and streak breaks
- 🎯 Predicts burnout risk: **Low / Medium / High**
- 📊 Visualizes your developer health on an interactive dashboard

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| Risk Score | Low / Medium / High burnout prediction |
| Commit Heatmap | Visual pattern of your coding activity |
| Sentiment Timeline | Mood trend from your commit messages |
| Late-Night Detector | % of commits made between 10 PM – 4 AM |
| Weekend Warrior Check | Detects unhealthy work-life balance |
| Streak Analysis | Finds dangerous overwork or underwork patterns |

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Frontend:** Streamlit
- **Data Source:** GitHub REST API (PyGithub)
- **ML Model:** Scikit-learn (Isolation Forest + Rule-based scoring)
- **NLP:** VADER Sentiment Analysis
- **Visualization:** Plotly
- **CI/CD:** GitHub Actions
- **Deployment:** Streamlit Cloud

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- GitHub Personal Access Token ([Generate here](https://github.com/settings/tokens))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/codeburnout.git
cd codeburnout

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/main.py
```

### Usage

1. Open the app in your browser
2. Enter any GitHub username
3. Click **Analyze**
4. View your burnout risk dashboard

---

## 📁 Project Structure

codeburnout/
├── app/
│   ├── main.py          # Streamlit UI entry point
│   ├── analyzer.py      # GitHub API data fetching
│   ├── features.py      # Feature engineering
│   ├── model.py         # ML burnout prediction model
│   └── visualizer.py    # Plotly chart functions
├── data/
│   └── sample_commits.json
├── notebooks/
│   └── EDA.ipynb
├── tests/
│   └── test_features.py
├── .github/workflows/
│   └── ci.yml
├── requirements.txt
└── README.md

---

## 🗓️ Development Roadmap

- [x] Day 1 — Project setup & repository structure
- [ ] Day 2 — GitHub API integration
- [ ] Day 3 — Feature engineering
- [ ] Day 4 — ML model & risk scoring
- [ ] Day 5 — Streamlit dashboard
- [ ] Day 6 — Deploy to Streamlit Cloud
- [ ] Day 7 — Final submission

---

## 👩‍💻 Built By

**Pragya Namdev**
B.Tech CSE | Quantum University, Roorkee
[LinkedIn](https://www.linkedin.com/in/pragya-namdev-183ba7325/)
 · [GitHub](https://github.com/PragyaNamdev?tab=stars)

---

## 📄 License

This project is licensed under the MIT License.

---

*Built with ❤️ for Open Source Hackathon 2026 by Elite Coders*

