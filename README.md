#  Steam Review Sentiment ETL Pipeline

A PySpark-powered ETL pipeline that extracts reviews for the **Top 50 most-reviewed Steam games**, scores them with VADER sentiment analysis, and loads structured results into **PostgreSQL**.

---

## 📐 Architecture

```
Steam API (SteamSpy + Store Reviews)
        ↓  EXTRACT
  Raw games + reviews (JSON)
        ↓  TRANSFORM (PySpark + VADER)
  Cleaned DataFrames + Sentiment Scores
        ↓  LOAD (JDBC)
  PostgreSQL Tables
```

### Tables Created

| Table | Description |
|---|---|
| `dim_games` | Game metadata (name, genre, developer, review ratio) |
| `fact_reviews` | Individual reviews with sentiment score & label |
| `agg_game_sentiment` | Per-game aggregated sentiment summary |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Java 11+ (required for PySpark) → [Download](https://adoptium.net/)
- Docker Desktop → [Download](https://www.docker.com/products/docker-desktop/)

---

### Step 1 — Start PostgreSQL with Docker

```bash
docker-compose up -d
```

This spins up a PostgreSQL instance at `localhost:5432` with:
- **DB:** `steam_db`
- **User:** `etl_user`
- **Password:** `etl_pass`

Verify it's running:
```bash
docker ps
```

---

### Step 2 — Install Python dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install packages
pip install -r requirements.txt
```

---

### Step 3 — Download PostgreSQL JDBC Driver

PySpark needs a JDBC driver to talk to PostgreSQL:

```bash
# Mac/Linux
curl -o postgresql-42.7.3.jar https://jdbc.postgresql.org/download/postgresql-42.7.3.jar

# Or download manually from:
# https://jdbc.postgresql.org/download/
```

Set the JDBC driver path (add to your shell profile or run before executing):
```bash
export PYSPARK_SUBMIT_ARGS="--jars postgresql-42.7.3.jar pyspark-shell"
```

---

### Step 4 — Run the Pipeline

```bash
python main.py
```

You'll see logs like:
```
2024-01-15 10:23:01 | INFO     | main | [STEP 1/3] EXTRACT
2024-01-15 10:23:01 | INFO     | extractor | Fetching top 50 most reviewed games...
...
2024-01-15 10:25:44 | INFO     | main | [STEP 2/3] TRANSFORM
...
2024-01-15 10:26:10 | INFO     | main | [STEP 3/3] LOAD
...
2024-01-15 10:26:30 | INFO     | main | Pipeline completed in 209.3s
```

---

### Step 5 — Query the Results

Connect to PostgreSQL:
```bash
docker exec -it steam_etl_db psql -U etl_user -d steam_db
```

Sample queries:
```sql
-- Top 10 games by average sentiment
SELECT game_name, avg_sentiment_score, sentiment_category, total_reviews_fetched
FROM agg_game_sentiment
ORDER BY avg_sentiment_score DESC
LIMIT 10;

-- Most controversial games (mixed sentiment)
SELECT game_name, positive_count, negative_count, avg_sentiment_score
FROM agg_game_sentiment
WHERE sentiment_category = 'Mixed'
ORDER BY total_reviews_fetched DESC;

-- Reviews from heavy players only
SELECT game_name, review_text, sentiment_label, playtime_hours
FROM fact_reviews
WHERE playtime_hours > 500
ORDER BY sentiment_score ASC
LIMIT 20;
```

---

## ⚙️ Configuration

Edit `config/config.yaml` to change:
- Number of games (`top_n_games`)
- Reviews per game (`reviews_per_game`)
- Database credentials

---

## 🛑 Teardown

```bash
docker-compose down -v   # stops and removes DB volume
```
