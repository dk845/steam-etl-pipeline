import pandas as pd
from sqlalchemy import create_engine
from utils.logger import get_logger

logger = get_logger("loader")

def load_all(games_df, reviews_df, summary_df, config):
    engine = create_engine("sqlite:///steam_etl.db")
    
    logger.info("Loading dim_games...")
    games_df.to_sql("dim_games", engine, if_exists="replace", index=False)
    
    logger.info("Loading fact_reviews...")
    reviews_df.to_sql("fact_reviews", engine, if_exists="replace", index=False)
    
    logger.info("Loading agg_game_sentiment...")
    summary_df.to_sql("agg_game_sentiment", engine, if_exists="replace", index=False)
    
    logger.info("All tables loaded! ETL complete! 🎉")