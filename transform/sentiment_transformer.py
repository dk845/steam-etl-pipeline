import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils.logger import get_logger

logger = get_logger("transformer")
analyzer = SentimentIntensityAnalyzer()

def score_sentiment(text):
    if not text or len(str(text)) < 10:
        return 0.0
    return analyzer.polarity_scores(str(text))["compound"]

def label_sentiment(score):
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"

def transform_all(spark, games, reviews):
    logger.info("Transforming with Pandas...")
    games_df = pd.DataFrame(games)
    games_df["positive_ratio"] = round(games_df["positive"] / (games_df["total_reviews"] + 1), 4)
    reviews_df = pd.DataFrame(reviews)
    reviews_df = reviews_df[reviews_df["review_text"].str.len() > 10]
    reviews_df["sentiment_score"] = reviews_df["review_text"].apply(score_sentiment)
    reviews_df["sentiment_label"] = reviews_df["sentiment_score"].apply(label_sentiment)
    reviews_df["review_date"] = pd.to_datetime(reviews_df["timestamp_created"], unit="s").dt.date
    reviews_df["review_length"] = reviews_df["review_text"].str.len()
    reviews_df = reviews_df.drop(columns=["timestamp_created"])
    summary_df = reviews_df.groupby(["appid", "game_name"]).agg(
        total_reviews_fetched=("review_id", "count"),
        avg_sentiment_score=("sentiment_score", "mean"),
        avg_reviewer_playtime_hrs=("playtime_hours", "mean"),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum()),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        thumbs_up_count=("voted_up", "sum"),
        avg_review_length_chars=("review_length", "mean"),
    ).reset_index()
    summary_df["sentiment_category"] = summary_df["avg_sentiment_score"].apply(
        lambda s: "Positive" if s >= 0.05 else ("Negative" if s <= -0.05 else "Mixed")
    )
    logger.info(f"Transform complete. Games: {len(games_df)}, Reviews: {len(reviews_df)}, Summary: {len(summary_df)}")
    return games_df, reviews_df, summary_df
