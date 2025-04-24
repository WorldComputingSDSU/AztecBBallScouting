from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from app.scraper import test_scrape, scrape_season_stats, scrape_team_schedule, router
from app.schema import PlayerStats


app = FastAPI()

# Update CORS middleware configuration with explicit origins
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add error handling middleware
@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Mount the project directory for static files
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse("teamdata.html")

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