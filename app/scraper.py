import json
import requests
from bs4 import BeautifulSoup, Comment
import re
import logging
from fastapi import APIRouter
from datetime import datetime

# Create router instance
router = APIRouter()

# Define the router endpoint
@router.get("/nba/schedule/{team_slug}")
async def get_team_schedule(team_slug: str):
    """Scrape the NBA team schedule from ESPN."""
    return scrape_team_schedule(team_slug)

# Add new router endpoint near the top with other routes
@router.get("/nba/game/{game_id}")
async def get_game_box_score(game_id: str):
    """Get box score for a specific NBA game."""
    return scrape_game_box_score(game_id)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


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
        "pts": "points"
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










def parse_game_date(date_str: str) -> str:
    """Convert date string to YYYY-MM-DD format."""
    if date_str == "DATE" or not date_str:
        return None
    try:
        # Add current year since the input only has month and day
        current_year = datetime.now().year
        date_obj = datetime.strptime(f"{date_str} {current_year}", "%a, %b %d %Y")
        # Adjust year if the date is in the future (meaning it's from last year)
        if date_obj > datetime.now():
            date_obj = date_obj.replace(year=current_year - 1)
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return None

def clean_game_result(result: str) -> dict:
    """Parse game result into structured format."""
    if not result or result == "RESULT":
        return None
    
    result_data = {
        "result": None,
        "score": None,
        "home_score": None,
        "away_score": None,
        "overtime": False
    }
    
    if result.startswith('W'):
        result_data["result"] = "Win"
        scores = result[1:].split('-')
    elif result.startswith('L'):
        result_data["result"] = "Loss"
        scores = result[1:].split('-')
    else:
        return result_data
    
    if len(scores) == 2:
        # Check for overtime
        if 'OT' in scores[1]:
            result_data["overtime"] = True
            scores[1] = scores[1].replace(' OT', '')
            
        try:
            result_data["home_score"] = int(scores[0])
            result_data["away_score"] = int(scores[1])
            result_data["score"] = f"{scores[0]}-{scores[1]}"
        except ValueError:
            # If score parsing fails, keep the original score string
            result_data["score"] = f"{scores[0]}-{scores[1]}"
    
    return result_data

def clean_schedule_data(raw_schedule: list) -> list:
    """Clean and structure raw schedule data."""
    cleaned = []
    
    for game in raw_schedule:
        # Skip header row
        if game["date"] == "DATE":
            continue
            
        clean_game = {
            "date": parse_game_date(game["date"]),
            "opponent": game["opponent"],
            "record": game["record"],
            "game_id": game.get("game_id"),
            "game_url": game.get("game_url")
        }
        
        # Add parsed result data
        result_data = clean_game_result(game["result"])
        if result_data:
            clean_game.update(result_data)
            
        cleaned.append(clean_game)
    
    return cleaned

def get_team_seasons(team_slug: str) -> int:
    """Get the number of seasons played by the team."""
    url = f"https://www.espn.com/nba/team/stats/_/name/{team_slug}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Look for team history in multiple possible locations
    possible_containers = [
        soup.find("div", class_="ClubhouseHeader__Team"),
        soup.find("section", class_="TeamHeader"),
        soup.find("div", class_="TeamInfo")
    ]
    
    for container in possible_containers:
        if not container:
            continue
            
        # Try different text patterns
        patterns = [
            r"(\d+)[a-z\s]*season",  # matches "74th season" or "74 seasons"
            r"established[^\d]*(\d{4})",  # matches "established in 1947"
            r"est\.[^\d]*(\d{4})"  # matches "est. 1947"
        ]
        
        text = container.get_text().lower()
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.group(1)) == 4:  # If we found a year
                    current_year = datetime.now().year
                    return current_year - int(match.group(1))
                else:  # If we found direct seasons count
                    return int(match.group(1))
    
    # If we couldn't find the information
    return None

def scrape_team_schedule(team_slug: str):
    """Scrape the NBA team schedule from ESPN."""
    url = f"https://www.espn.com/nba/team/schedule/_/name/{team_slug}/seasontype/2"
    
    # Get seasons count first
    seasons_count = get_team_seasons(team_slug)
    
    # Make the GET request with headers
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch schedule")
        return {"error": "Failed to fetch schedule"}

    # Parse the response HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    schedule_table = soup.find("table")

    if not schedule_table:
        print(" Schedule table not found")
        return {"error": "Schedule table not found"}

    schedule = []
    for row in schedule_table.find_all("tr")[1:]:  # Skip header row
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        # Find game link in the result cell (usually cell index 2)
        game_link = cells[2].find('a')
        game_url = None
        game_id = None
        
        if game_link and 'href' in game_link.attrs:
            game_url = game_link['href']
            # Extract game ID from URL using regex
            id_match = re.search(r'/gameId/(\d+)/', game_url)
            if id_match:
                game_id = id_match.group(1)

        game = {
            "date": cells[0].text.strip(),
            "opponent": cells[1].text.strip(),
            "result": cells[2].text.strip(),
            "record": cells[3].text.strip(),
            "game_id": game_id,
            "game_url": game_url
        }
        schedule.append(game)

    # Clean and format the schedule data
    cleaned_schedule = clean_schedule_data(schedule)
    return {
        "team": team_slug.upper(),
        "seasons_played": seasons_count,
        "schedule": cleaned_schedule
    }

def scrape_game_box_score(game_id: str) -> dict:
    """Scrape box score data for a specific NBA game."""
    logger = logging.getLogger("uvicorn.error")
    
    # First get the game page
    game_url = f"https://www.espn.com/nba/game/_/gameId/{game_id}"
    logger.info(f"Fetching game page from: {game_url}")
    
    response = requests.get(game_url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch game page: {response.status_code}")
        return {"error": "Failed to fetch game page"}

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find team names from the game header
    team_names = []
    team_headers = soup.find_all("div", {"class": "GameHero_TeamInfo"})  # Fixed string literal
    for team in team_headers:
        name_element = team.find("div", {"class": "GameHero_TeamName"})
        if name_element:
            team_names.append(name_element.text.strip())
    logger.info(f"Found team names: {team_names}")

    # Get box score URL
    box_score_url = f"https://www.espn.com/nba/boxscore/_/gameId/{game_id}"
    logger.info(f"Fetching box score from: {box_score_url}")

    # ...rest of existing function...