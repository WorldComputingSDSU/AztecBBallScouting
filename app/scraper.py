import requests
from bs4 import BeautifulSoup
import re
import logging
from bs4 import Comment
import json
from fastapi import APIRouter, HTTPException
from datetime import datetime
import time

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


def scrape_career_stats_totals(player: str) -> dict:
    player_slug = format_player_name(player)
    url = f"https://www.sports-reference.com/cbb/players/{player_slug}.html"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Player not found: {url}")

    soup = BeautifulSoup(response.text, "html.parser")

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        soup.append(BeautifulSoup(comment, "html.parser"))

    table = soup.find("table", {"id": "players_totals"})
    if not table:
        raise ValueError("Totals table not found.")

    rows = table.find_all("tr")
    seasons_played = 0
    for row in rows:
        row_id = row.get("id", "")
        if row_id == "players_totals.Career":
            break
        if re.match(r"players_totals\.\d{4}", row_id):
            seasons_played += 1

    career_row = table.find("tr", {"id": "players_totals.Career"})
    if not career_row:
        raise ValueError("Career totals row not found.")

    key_map = {
        "year_id": "season",
        "g": "games_played",
        "games": "games_played",
        "gs": "games_started",
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

    results = {"seasons_played": seasons_played}
    for cell in career_row.find_all(["td", "th"]):
        key = key_map.get(cell.get("data-stat"))
        if key and cell.text.strip():
            results[key] = cell.text.strip()
    return results

def slug_to_display_name(slug: str) -> str:
    return slug.replace("-", " ").title()

def scrape_basic_team_stats(team: str, season: str) -> dict:
    url = f"https://www.sports-reference.com/cbb/seasons/{season}-school-stats.html"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Player not found: {url}")

    soup = BeautifulSoup(response.text, "html.parser")

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        soup.append(BeautifulSoup(comment, "html.parser"))

    table = soup.find("tbody")
    if not table:
        # Try to find any table if tbody not found directly
        table = soup.find("table")
        if table:
            table = table.find("tbody")

    display_name = slug_to_display_name(team)
    rows = table.find_all("tr")
    row = None
    for r in rows:
        school_cell = r.find("td", {"data-stat": "school_name"})
        if school_cell and display_name.lower() in school_cell.get_text().lower():
            row = r
            break

    if not row:
        raise ValueError(f"Team {display_name} not found in {season} stats.")

    key_map ={
       "g": "games",
       "wins" : "wins",
       "losses" : "losses",
       "win_loss_pct": "win_loss_pct",
       "srs": "simple_rating_system",
       "sos": "strength_of_schedule",
       "wins_conf": "wins_conference",
       "losses_conf": "losses_conference",
       "wins_home": "wins_home",
       "losses_home": "losses_home",
       "wins_visitor": "wins_away",
       "losses_visitor": "losses_away",
       "pts": "points",
       "opp_pts": "opponent_points",
       "mp": "minutes_played",
       "fg": "field_goals",
       "fga": "field_goal_attempts",
       "fg_pct": "field_goal_percentage",
       "fg3": "three_point_field_goals",
       "fg3a": "three_point_field_goal_attempts",
       "fg3_pct": "three_point_field_goal_percentage",
       "ft": "free_throws",
       "fta": "free_throw_attempts",
       "ft_pct": "free_throw_percentage",
       "orb": "offensive_rebounds",
       "trb": "total_rebounds",
       "ast": "assists",
       "stl": "steals",
       "blk": "blocks",
       "tov": "turnovers",
       "pf": "personal_fouls",
   }
    results = {"school_name": display_name,
               "season": season}
    # Include <th> as well since "ranker" is in a <th>, not <td>
    for cell in row.find_all(["td", "th"]):
        key = key_map.get(cell.get("data-stat"))
        value = cell.text.strip()
        if key and value and value != '':  # Avoid empty or dummy cells
            results[key] = value

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

def parse_meta_description(description: str) -> tuple:
    """Parse game metadata from description."""
    try:
        if not description:
            return None, None, None
        # Example: "Box score for the Portland Trail Blazers vs. Los Angeles Lakers NBA game..."
        teams = description.split('Box score for the ')[1].split(' NBA game')[0]
        team1, team2 = teams.split(' vs. ')
        return team1.strip(), team2.strip(), None
    except:
        return None, None, None

def parse_meta_title(title: str) -> tuple:
    """Parse game scores from title."""
    try:
        if not title or '-' not in title:
            return None, None
        # Example: "Trail Blazers 109-81 Lakers"
        score_part = title.split('(')[0].strip()
        score1, score2 = score_part.split('-')
        team1_score = int(score1.split()[-1])
        team2_score = int(score2.split()[0])
        return team1_score, team2_score
    except:
        return None, None

def scrape_game_box_score(game_id: str) -> dict:
    """Scrape box score data for a specific NBA game."""
    logger = logging.getLogger("uvicorn.error")

    try:
        box_score_url = f"https://www.espn.com/nba/boxscore/_/gameId/{game_id}"
        logger.info(f"Fetching box score from: {box_score_url}")

        response = requests.get(box_score_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Initialize result structure
        result = {
            "game": {},
            "teams": {},
            "team_stats": {}
        }

        # Try to get game info from metadata first
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_title = soup.find("meta", attrs={"name": "twitter:title"})

        if meta_desc and meta_title:
            team1, team2, _ = parse_meta_description(meta_desc.get("content"))
            score1, score2 = parse_meta_title(meta_title.get("content"))

            if all([team1, team2, score1, score2]):
                result["game"] = {
                    "home_team": team2,  # Second team is usually home team
                    "away_team": team1,
                    "home_score": score2,
                    "away_score": score1
                }
                logger.info(f"Successfully parsed game info from metadata: {result['game']}")

        # Find tables with the correct classes
        box_score_tables = soup.find_all("table", class_=lambda x: x and "Table" in x)

        for table in box_score_tables:
            team_name = table.find_previous("div", class_=lambda x: x and "TeamName" in x)
            if not team_name:
                continue

            team_name = team_name.text.strip()
            starters = []
            bench = []

            # Find all player rows
            rows = table.find_all("tr", class_=lambda x: x and "Table__TR" in x)

            for row in rows:
                # Skip header rows and empty rows
                if not row.get('data-idx'):
                    continue

                cells = row.find_all("td", class_="Table__TD")
                if len(cells) < 14:  # Need minimum number of stat columns
                    continue

                # Parse player stats
                player_stats = {
                    "name": cells[0].text.strip(),
                    "minutes": cells[1].text.strip(),
                    "fg": cells[2].text.strip(),
                    "threept": cells[3].text.strip(),
                    "ft": cells[4].text.strip(),
                    "oreb": cells[5].text.strip(),
                    "dreb": cells[6].text.strip(),
                    "reb": cells[7].text.strip(),
                    "ast": cells[8].text.strip(),
                    "stl": cells[9].text.strip(),
                    "blk": cells[10].text.strip(),
                    "to": cells[11].text.strip(),
                    "pf": cells[12].text.strip(),
                    "plus_minus": cells[13].text.strip(),
                    "pts": cells[14].text.strip() if len(cells) > 14 else "0"
                }

                # Check if player is starter or bench
                if int(row.get('data-idx', 0)) <= 5:
                    starters.append(player_stats)
                else:
                    bench.append(player_stats)

            # Add team data to result
            if starters or bench:
                result["teams"][team_name] = {
                    "starters": starters,
                    "bench": bench
                }

        if not result["teams"]:
            raise ValueError("No valid player data found")

        return result

    except Exception as e:
        logger.error(f"Error scraping box score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_play_by_play(game_id: str):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event={game_id}"

    response = requests.get(url, headers=headers)
    data = response.json()

    if 'plays' not in data:
        return {"error": "No play-by-play data found for this game ID."}

    competitors = data.get('header', {}).get('competitions', [{}])[0].get('competitors', [])
    if len(competitors) < 2:
        return {"error": "Could not determine teams."}

    home_team = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
    away_team = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

    home_abbr = home_team.get('team', {}).get('abbreviation', 'HOME')
    away_abbr = away_team.get('team', {}).get('abbreviation', 'AWAY')

    plays = data['plays']
    play_by_play = []

    for play in plays:
        play_by_play.insert(0, {
            'period': play.get('period', {}).get('number', ''),
            'clock': play.get('clock', {}).get('displayValue', ''),
            'description': play.get('text', ''),
            'team': play.get('team', {}).get('displayName', ''),
            home_abbr: play.get('homeScore', ''),
            away_abbr: play.get('awayScore', '')
        })

    return play_by_play

def get_nba_play_by_play(game_id: str):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game_id}"

    response = requests.get(url, headers=headers)
    data = response.json()

    if 'plays' not in data:
        return {"error": "No play-by-play data found for this game ID."}

    competitors = data.get('header', {}).get('competitions', [{}])[0].get('competitors', [])
    if len(competitors) < 2:
        return {"error": "Could not determine teams."}

    home_team = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
    away_team = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

    home_abbr = home_team.get('team', {}).get('abbreviation', 'HOME')
    away_abbr = away_team.get('team', {}).get('abbreviation', 'AWAY')

    plays = data['plays']
    play_by_play = []

    for play in plays:
        play_by_play.insert(0, {
            'period': play.get('period', {}).get('number', ''),
            'clock': play.get('clock', {}).get('displayValue', ''),
            'description': play.get('text', ''),
            'team': play.get('team', {}).get('displayName', ''),
            home_abbr: play.get('homeScore', ''),
            away_abbr: play.get('awayScore', '')
        })

    return play_by_play


def ncaa_live_box_score(game_id: str) -> dict:
    """Return structured box score data for an NBA game using ESPN's API."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event={game_id}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    result = {
        "game": {},
        "teams": {}
    }

    # Get game info
    comp = data.get("header", {}).get("competitions", [{}])[0]
    competitors = comp.get("competitors", [])
    if len(competitors) == 2:
        home = next(c for c in competitors if c["homeAway"] == "home")
        away = next(c for c in competitors if c["homeAway"] == "away")
        result["game"] = {
            "home_team": home["team"]["displayName"],
            "away_team": away["team"]["displayName"],
            "home_score": int(home["score"]),
            "away_score": int(away["score"])
        }

    # Define stat header row
    stat_header = {
        "name": "MIN",
        "minutes": "FG",
        "fg": "3PT",
        "threept": "FT",
        "ft": "OREB",
        "oreb": "DREB",
        "dreb": "REB",
        "reb": "AST",
        "ast": "STL",
        "stl": "BLK",
        "blk": "TO",
        "to": "PF",
        "pf": "+/-",
        "plus_minus": "PTS",
        "pts": "0"
    }

    # Process player stats
    for team_data in data.get("boxscore", {}).get("players", []):
        team_name = team_data["team"]["displayName"]
        starters = [stat_header.copy()]
        bench = [stat_header.copy()]

        for stat_group in team_data.get("statistics", []):
            group_name = stat_group.get("name", "").lower()
            section = starters if group_name == "starters" else bench

            for athlete in stat_group.get("athletes", []):
                player = athlete.get("athlete", {})
                stats = athlete.get("stats", [])
                did_not_play = athlete.get("didNotPlay", False)
                reason = athlete.get("reason")

                if did_not_play:
                    section.append({
                        "name": player.get("displayName"),
                        "status": f"DNP - {reason}" if reason else "DNP"
                    })
                    continue

                stat_line = {
                    "name": player.get("displayName"),
                    "minutes": stats[0] if len(stats) > 0 else "",
                    "fg": stats[1] if len(stats) > 1 else "",
                    "threept": stats[2] if len(stats) > 2 else "",
                    "ft": stats[3] if len(stats) > 3 else "",
                    "oreb": stats[4] if len(stats) > 4 else "",
                    "dreb": stats[5] if len(stats) > 5 else "",
                    "reb": stats[6] if len(stats) > 6 else "",
                    "ast": stats[7] if len(stats) > 7 else "",
                    "stl": stats[8] if len(stats) > 8 else "",
                    "blk": stats[9] if len(stats) > 9 else "",
                    "to": stats[10] if len(stats) > 10 else "",
                    "pf": stats[11] if len(stats) > 11 else "",
                    "plus_minus": stats[12] if len(stats) > 12 else "",
                    "pts": stats[13] if len(stats) > 13 else "0"
                }

                section.append(stat_line)

        result["teams"][team_name] = {
            "starters": starters,
            "bench": bench,
            "team": []  # Will fill below
        }

    # Process team totals and percentages
    for team in data.get("boxscore", {}).get("teams", []):
        team_name = team["team"]["displayName"]
        totals = {}
        percents = {}

        for stat in team.get("statistics", []):
            label = stat.get("label")
            value = stat.get("displayValue")
            if not label or not value:
                continue
            if "%" in value:
                percents[label] = value
            else:
                totals[label] = value

        totals_row = {
            "name": "",
            "minutes": totals.get("FG", ""),
            "fg": totals.get("3PT", ""),
            "threept": totals.get("FT", ""),
            "ft": totals.get("OREB", ""),
            "oreb": totals.get("DREB", ""),
            "dreb": totals.get("REB", ""),
            "reb": totals.get("AST", ""),
            "ast": totals.get("STL", ""),
            "stl": totals.get("BLK", ""),
            "blk": totals.get("TO", ""),
            "to": totals.get("PF", ""),
            "pf": "",
            "plus_minus": totals.get("PTS", ""),
            "pts": "0"
        }

        percents_row = {
            "name": "",
            "minutes": percents.get("FG%", ""),
            "fg": percents.get("3P%", ""),
            "threept": percents.get("FT%", ""),
            "ft": "",
            "oreb": "",
            "dreb": "",
            "reb": "",
            "ast": "",
            "stl": "",
            "blk": "",
            "to": "",
            "pf": "",
            "plus_minus": "",
            "pts": "0"
        }

        result["teams"][team_name]["team"] = [totals_row, percents_row]

    # Clean empty strings from all stat rows
    for team in result["teams"].values():
        for group in ["starters", "bench", "team"]:
            cleaned = []
            for row in team.get(group, []):
                cleaned_row = {k: v for k, v in row.items() if v != ""}
                cleaned.append(cleaned_row)
            team[group] = cleaned

    return result

def nba_live_box_score(game_id: str) -> dict:
    """Return structured box score data for an NBA game using ESPN's API."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game_id}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    result = {
        "game": {},
        "teams": {}
    }

    # Get game info
    comp = data.get("header", {}).get("competitions", [{}])[0]
    competitors = comp.get("competitors", [])
    if len(competitors) == 2:
        home = next(c for c in competitors if c["homeAway"] == "home")
        away = next(c for c in competitors if c["homeAway"] == "away")
        result["game"] = {
            "home_team": home["team"]["displayName"],
            "away_team": away["team"]["displayName"],
            "home_score": int(home["score"]),
            "away_score": int(away["score"])
        }

    # Define stat header row
    stat_header = {
        "name": "MIN",
        "minutes": "FG",
        "fg": "3PT",
        "threept": "FT",
        "ft": "OREB",
        "oreb": "DREB",
        "dreb": "REB",
        "reb": "AST",
        "ast": "STL",
        "stl": "BLK",
        "blk": "TO",
        "to": "PF",
        "pf": "+/-",
        "plus_minus": "PTS",
        "pts": "0"
    }

    # Process player stats
    for team_data in data.get("boxscore", {}).get("players", []):
        team_name = team_data["team"]["displayName"]
        starters = [stat_header.copy()]
        bench = [stat_header.copy()]

        for stat_group in team_data.get("statistics", []):
            group_name = stat_group.get("name", "").lower()
            section = starters if group_name == "starters" else bench

            for athlete in stat_group.get("athletes", []):
                player = athlete.get("athlete", {})
                stats = athlete.get("stats", [])
                did_not_play = athlete.get("didNotPlay", False)
                reason = athlete.get("reason")

                if did_not_play:
                    section.append({
                        "name": player.get("displayName"),
                        "status": f"DNP - {reason}" if reason else "DNP"
                    })
                    continue

                stat_line = {
                    "name": player.get("displayName"),
                    "minutes": stats[0] if len(stats) > 0 else "",
                    "fg": stats[1] if len(stats) > 1 else "",
                    "threept": stats[2] if len(stats) > 2 else "",
                    "ft": stats[3] if len(stats) > 3 else "",
                    "oreb": stats[4] if len(stats) > 4 else "",
                    "dreb": stats[5] if len(stats) > 5 else "",
                    "reb": stats[6] if len(stats) > 6 else "",
                    "ast": stats[7] if len(stats) > 7 else "",
                    "stl": stats[8] if len(stats) > 8 else "",
                    "blk": stats[9] if len(stats) > 9 else "",
                    "to": stats[10] if len(stats) > 10 else "",
                    "pf": stats[11] if len(stats) > 11 else "",
                    "plus_minus": stats[12] if len(stats) > 12 else "",
                    "pts": stats[13] if len(stats) > 13 else "0"
                }

                section.append(stat_line)

        result["teams"][team_name] = {
            "starters": starters,
            "bench": bench,
            "team": []  # Will fill below
        }

    # Process team totals and percentages
    for team in data.get("boxscore", {}).get("teams", []):
        team_name = team["team"]["displayName"]
        totals = {}
        percents = {}

        for stat in team.get("statistics", []):
            label = stat.get("label")
            value = stat.get("displayValue")
            if not label or not value:
                continue
            if "%" in value:
                percents[label] = value
            else:
                totals[label] = value

        totals_row = {
            "name": "",
            "minutes": totals.get("FG", ""),
            "fg": totals.get("3PT", ""),
            "threept": totals.get("FT", ""),
            "ft": totals.get("OREB", ""),
            "oreb": totals.get("DREB", ""),
            "dreb": totals.get("REB", ""),
            "reb": totals.get("AST", ""),
            "ast": totals.get("STL", ""),
            "stl": totals.get("BLK", ""),
            "blk": totals.get("TO", ""),
            "to": totals.get("PF", ""),
            "pf": "",
            "plus_minus": totals.get("PTS", ""),
            "pts": "0"
        }

        percents_row = {
            "name": "",
            "minutes": percents.get("FG%", ""),
            "fg": percents.get("3P%", ""),
            "threept": percents.get("FT%", ""),
            "ft": "",
            "oreb": "",
            "dreb": "",
            "reb": "",
            "ast": "",
            "stl": "",
            "blk": "",
            "to": "",
            "pf": "",
            "plus_minus": "",
            "pts": "0"
        }

        result["teams"][team_name]["team"] = [totals_row, percents_row]

    # Clean empty strings from all stat rows
    for team in result["teams"].values():
        for group in ["starters", "bench", "team"]:
            cleaned = []
            for row in team.get(group, []):
                cleaned_row = {k: v for k, v in row.items() if v != ""}
                cleaned.append(cleaned_row)
            team[group] = cleaned

    return result