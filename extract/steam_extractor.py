import requests
import time
from typing import List, Dict, Any
import yaml
from utils.logger import get_logger

logger = get_logger("extractor")


def load_config() -> dict:
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def fetch_top_games(config: dict) -> List[Dict[str, Any]]:
    """
    Fetch top N most reviewed games from SteamSpy.
    Returns a list of dicts with appid, name, total reviews.
    """
    url = config["steam_api"]["top_games_url"]
    top_n = config["steam_api"]["top_n_games"]

    logger.info(f"Fetching top {top_n} most reviewed games from SteamSpy...")

    params = {"request": "top100in2weeks"}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # Sort by total reviews descending
    games = sorted(
        [
            {
                "appid": str(appid),
                "name": info.get("name", "Unknown"),
                "total_reviews": info.get("positive", 0) + info.get("negative", 0),
                "positive": info.get("positive", 0),
                "negative": info.get("negative", 0),
                "owners": info.get("owners", "0"),
                "genre": info.get("genre", "Unknown"),
                "developer": info.get("developer", "Unknown"),
            }
            for appid, info in data.items()
        ],
        key=lambda x: x["total_reviews"],
        reverse=True,
    )[:top_n]

    logger.info(f"Fetched {len(games)} games successfully.")
    return games


def fetch_reviews_for_game(
    appid: str, game_name: str, config: dict
) -> List[Dict[str, Any]]:
    """
    Fetch reviews for a single game using Steam's public review API.
    """
    base_url = config["steam_api"]["base_url"]
    num_reviews = config["steam_api"]["reviews_per_game"]

    url = f"{base_url}/{appid}"
    params = {
        "json": 1,
        "language": "english",
        "review_type": "all",
        "purchase_type": "all",
        "num_per_page": min(num_reviews, 100),  # Steam caps at 100
        "filter": "recent",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        reviews = []
        for r in data.get("reviews", []):
            reviews.append(
                {
                    "appid": appid,
                    "game_name": game_name,
                    "review_id": r.get("recommendationid", ""),
                    "author_steamid": r.get("author", {}).get("steamid", ""),
                    "playtime_hours": round(
                        r.get("author", {}).get("playtime_forever", 0) / 60, 2
                    ),
                    "review_text": r.get("review", "").strip(),
                    "voted_up": r.get("voted_up", False),
                    "votes_helpful": r.get("votes_helpful", 0),
                    "timestamp_created": r.get("timestamp_created", 0),
                    "received_for_free": r.get("received_for_free", False),
                    "written_during_early_access": r.get(
                        "written_during_early_access", False
                    ),
                }
            )
        return reviews

    except Exception as e:
        logger.warning(f"Failed to fetch reviews for {game_name} (appid={appid}): {e}")
        return []


def extract_all(config: dict) -> tuple[List[Dict], List[Dict]]:
    """
    Main extraction function.
    Returns (games_list, reviews_list)
    """
    games = fetch_top_games(config)

    all_reviews = []
    for i, game in enumerate(games, 1):
        logger.info(
            f"[{i}/{len(games)}] Fetching reviews for: {game['name']} (appid={game['appid']})"
        )
        reviews = fetch_reviews_for_game(game["appid"], game["name"], config)
        all_reviews.extend(reviews)
        logger.info(f"  → {len(reviews)} reviews fetched")
        time.sleep(1.2)  # Respectful rate limiting

    logger.info(
        f"Extraction complete. Total reviews: {len(all_reviews)} across {len(games)} games."
    )
    return games, all_reviews
