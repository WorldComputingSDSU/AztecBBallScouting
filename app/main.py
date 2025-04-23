from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query
from app.scraper import test_scrape, scrape_season_stats, scrape_team_schedule, router
from app.schema import PlayerStats


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/player-stats/")
def get_player_stats(player: str = Query(...)):
    stats = scrape_player_data(player)
    return {"player": player, "stats": stats}


# player name formatting in url can be the following ways:
# lamont-butler
# lamont%20butler
@app.get("/players/{name}")
def get_player_stats(name: str):
    raw_stats = test_scrape(name)
    print(raw_stats)
    return PlayerStats(**raw_stats)


@app.get("/players/{name}/season/{year}")
def get_season_stats(name: str, year: str):
    raw_stats = scrape_season_stats(name, year)
    return PlayerStats(**raw_stats)


@app.get("/team-schedule/")
def get_team_schedule(team: str = Query("lal", description="NBA team slug, e.g., 'lal' for Lakers")):
    return scrape_team_schedule(team)

# Include the router
app.include_router(router)