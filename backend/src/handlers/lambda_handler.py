from fastapi import FastAPI
from mangum import Mangum
import backend.src.core.seeder as seeder

app = FastAPI(title="Deadlock Tourney Seeder API")

@app.get("/")
def read_root():
    return {"message": "Deadlock Tourney Seeder API connection success!"}

@app.get("/seed")
def seed_tournament(data: dict):
    player_list = data["player_list"]
    teams = seeder.generate_teams(player_list)
        
    return {
        "status": "success",
        "data": teams
    }

handler = Mangum(app)