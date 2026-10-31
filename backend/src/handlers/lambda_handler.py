from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="Deadlock Tourney Seeder API")

@app.get("/")
def read_root():
    return {"message": "Deadlock Tourney Seeder API connection success!"}

@app.get("/seed")
def seed_tournament(player_list: dict):
    return {
        "status": "success",
        "message": "Not implemented yet",
        "data": player_list
    }

handler = Mangum(app)