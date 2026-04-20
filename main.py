"""
Steam Review Sentiment ETL Pipeline
=====================================
Orchestrates Extract → Transform → Load

Usage:
    python main.py
"""

import sys
import time
import yaml
from utils.logger import get_logger

logger = get_logger("main")


def load_config() -> dict:
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    start = time.time()
    logger.info("=" * 60)
    logger.info("  Steam Review Sentiment ETL Pipeline — Starting")
    logger.info("=" * 60)

    config = load_config()

    # ── EXTRACT ──────────────────────────────────────────────────
    logger.info("\n[STEP 1/3] EXTRACT")
    from extract.steam_extractor import extract_all
    games, reviews = extract_all(config)

    if not games:
        logger.error("No games fetched. Aborting.")
        sys.exit(1)

    if not reviews:
        logger.error("No reviews fetched. Aborting.")
        sys.exit(1)

    # ── TRANSFORM ─────────────────────────────────────────────────
    logger.info("\n[STEP 2/3] TRANSFORM")
    from transform.sentiment_transformer import transform_all
    games_df, reviews_df, summary_df = transform_all(None, games, reviews)

    # Preview in terminal
    logger.info("\nSample — Top games by sentiment score:")
    print(summary_df[["game_name", "avg_sentiment_score", "sentiment_category", "positive_count", "negative_count"]].head(10).to_string())

    # ── LOAD ──────────────────────────────────────────────────────
    logger.info("\n[STEP 3/3] LOAD")
    from load.postgres_loader import load_all
    load_all(games_df, reviews_df, summary_df, config)

    elapsed = round(time.time() - start, 2)
    logger.info("=" * 60)
    logger.info(f"  Pipeline completed in {elapsed}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()