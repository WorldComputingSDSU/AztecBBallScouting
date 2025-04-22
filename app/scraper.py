import requests
from bs4 import BeautifulSoup
import re
import logging
from bs4 import Comment

def format_player_name(name):
    if re.fullmatch(r"[a-z\-]+-\d+", name.lower()):
        return name.lower()
    parts = name.lower().split()
    return '-'.join(parts) + "-1"

def scrape_season_stats(player: str, season: str) -> dict:
    """Scrape stats for a given NCAA player and a specific season (e.g., '2023' for 2022–23)."""
    logger = logging.getLogger("uvicorn.error")
    player_slug = format_player_name(player)
    url = f"https://www.sports-reference.com/cbb/players/{player_slug}.html"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise ValueError(f"Player not found or URL failed: {url}")

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try to find tables in both regular HTML and comments
    tables = {
        'per_game': soup.find("table", {"id": "players_per_game"}),
        'totals': soup.find("table", {"id": "players_totals"})
    }
    
    # Check comments for hidden tables
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, "html.parser")
        if not tables['per_game']:
            tables['per_game'] = comment_soup.find("table", {"id": "players_per_game"})
        if not tables['totals']:
            tables['totals'] = comment_soup.find("table", {"id": "players_totals"})

    # Look for season data in both tables
    row_data = None
    for table_type, table in tables.items():
        if not table:
            continue
        row = table.find("tr", {"id": f"players_{table_type}.{season}"})
        if row:
            row_data = row
            break

    if not row_data:
        raise ValueError(f"No stats found for season {season}")

    # Unified field mapping
    key_map = {
        "year_id": "season",
        "team_name_abbr": "team",
        "conf_abbr": "conference",
        "class": "class_year",
        "pos": "position",
        "g": "games_played",
        "gs": "games_started",
        "mp": "minutes_played",
        "fg": "field_goals_made",
        "fga": "field_goal_attempts",
        "fg_pct": "fg_percentage",
        "fg3": "three_pt_made",
        "fg3a": "three_pt_attempts",
        "fg3_pct": "three_pt_percentage",
        "fg2": "two_pt_made",
        "fg2a": "two_pt_attempts",
        "fg2_pct": "two_pt_percentage",
        "efg_pct": "effective_fg_percentage",
        "ft": "free_throws_made",
        "fta": "free_throw_attempts",
        "ft_pct": "free_throw_percentage",
        "orb": "offensive_rebounds",
        "drb": "defensive_rebounds",
        "trb": "total_rebounds",
        "ast": "assists",
        "stl": "steals",
        "blk": "blocks",
        "tov": "turnovers",
        "pf": "personal_fouls",
        "pts": "points",
        "awards": "awards"
    }

    results = {}
    cells = row_data.find_all(["td", "th"])
    for cell in cells:
        raw_key = cell.get("data-stat")
        mapped_key = key_map.get(raw_key, raw_key)
        val = cell.text.strip()
        results[mapped_key] = val if val else None

    logger.info(f"Scraped {season} stats for {player}: {results}")
    return results

def test_scrape(player):
    logger = logging.getLogger("uvicorn.error")
    player_slug = format_player_name(player)
    logger.info(f"PLAYER_SLUG: {player_slug}")
    url = f"https://www.sports-reference.com/cbb/players/{player_slug}.html"
    response = requests.get(url)
    logger.info(f"URL: {url}")

    if response.status_code != 200:
        raise ValueError(f"Player not found or URL failed: {url}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    totals_table = soup.find("table", {"id": "players_totals"})
    if not totals_table:
        raise ValueError("No totals table found.")
    
    row_2025 = totals_table.find("tr", {"id": "players_totals.2025"})
    if not row_2025:
        raise ValueError("No 2024–25 season stats found.")
    
    key_map = {
        "year_id": "season",
        "team_name_abbr": "team",
        "conf_abbr": "conference",
        "class": "class_year",
        "pos": "position",
        "games": "games_played",
        "games_started": "games_started",
        "mp": "minutes_played",
        "fg": "field_goals_made",
        "fga": "field_goal_attempts",
        "fg_pct": "fg_percentage",
        "fg3": "three_pt_made",
        "fg3a": "three_pt_attempts",
        "fg3_pct": "three_pt_percentage",
        "fg2": "two_pt_made",
        "fg2a": "two_pt_attempts",
        "fg2_pct": "two_pt_percentage",
        "efg_pct": "effective_fg_percentage",
        "ft": "free_throws_made",
        "fta": "free_throw_attempts",
        "ft_pct": "free_throw_percentage",
        "orb": "offensive_rebounds",
        "drb": "defensive_rebounds",
        "trb": "total_rebounds",
        "ast": "assists",
        "stl": "steals",
        "blk": "blocks",
        "tov": "turnovers",
        "pf": "personal_fouls",
        "pts": "points",
        "awards": "awards"
    }

    results = {}
    cells = row_2025.find_all(["td", "th"])
    logger.info(f"# of cells found in row: {len(cells)}")

    for cell in cells:
        raw_key = cell.get("data-stat")
        mapped_key = key_map.get(raw_key, raw_key)
        val = cell.text.strip()
        results[mapped_key] = val if val else None

    logger.info(f"SCRAPED STATS: {results}")
    return results