# 🎮 Steam Review Sentiment ETL Pipeline

An end-to-end ETL pipeline that extracts reviews for the **Top 50 most-reviewed Steam games**, scores them with VADER sentiment analysis, and loads structured results into a **SQLite database**.

---

## 📐 Architecture
Steam API (SteamSpy + Store Reviews)
↓  EXTRACT
Raw games + reviews (JSON)
↓  TRANSFORM (Pandas + VADER NLP)
Cleaned DataFrames + Sentiment Scores
↓  LOAD
SQLite Database (steam_etl.db)
### Tables Created

| Table | Description |
|---|---|
| `dim_games` | Game metadata (name, genre, developer, review ratio) |
| `fact_reviews` | Individual reviews with sentiment score & label |
| `agg_game_sentiment` | Per-game aggregated sentiment summary |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Pandas | Data transformation |
| VADER Sentiment | NLP sentiment scoring (-1 to +1) |
| SQLite | Local database, zero config needed |
| Steam API + SteamSpy API | Real data source |
| Docker | Used during development for PostgreSQL |

---

## 🚀 How to Run

### Step 1 — Clone the repo
```bash
git clone https://github.com/dk845/steam-etl-pipeline.git
cd steam-etl-pipeline
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the pipeline
```bash
python main.py
```

The pipeline will:
1. Fetch top 50 Steam games from SteamSpy API
2. Pull 100 reviews per game (~5000 total)
3. Score each review with VADER sentiment
4. Save all results to `steam_etl.db`

---

## 🔍 Query the Results

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///steam_etl.db")

# Top games by sentiment
df = pd.read_sql("""
    SELECT game_name, avg_sentiment_score, sentiment_category,
           positive_count, negative_count
    FROM agg_game_sentiment
    ORDER BY avg_sentiment_score DESC
""", engine)

print(df)
```

---

## 📈 Sample Output

| Game | Avg Sentiment | Category |
|---|---|---|
| Baldur's Gate 3 | 0.50 | Positive |
| Red Dead Redemption 2 | 0.46 | Positive |
| Cyberpunk 2077 | 0.45 | Positive |
| War Thunder | -0.12 | Negative |

---

## ⚙️ Configuration

Edit `config/config.yaml` to change:
- Number of games (`top_n_games`)
- Reviews per game (`reviews_per_game`)
