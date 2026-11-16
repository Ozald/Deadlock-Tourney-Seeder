# Deadlock Tourney Seeder

A Streamlit frontend and FastAPI backend for balancing teams in custom *Deadlock* matches.

<p align="left">
  <img src="https://cdn2.steamgriddb.com/logo/d1555a36e55c44c60ba4dfb6b4485b82.png" alt="Deadlock Tourney Seeder Logo" width="180"/>
</p>

## Features

- **Team balancing:** Applies bell-curve weighting to player rank/MMR, then searches for an even split.
- **Statlocker profiles:** Looks up rank, MMR progress, and profile avatar using a Steam ID.
- **Manual ranks:** Players without a Steam ID can be assigned a rank and division.
- **Rank badges:** Shows Deadlock rank assets; unranked players use the Obscurus badge.
- **Roster sizes:** Supports 4, 6, 8, 10, or 12 players (2v2 through 6v6).

## Getting Started

Run these commands from the repository root. Create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, use `python3 -m venv .venv` and `source .venv/bin/activate`.

### Configure Statlocker

The backend reads `STATLOCKER_API_KEY` from the process environment or from a `.env` file in the repository root. Environment variables take precedence. For a `.env` file, add:

```dotenv
STATLOCKER_API_KEY=your-statlocker-api-key
```

Do not commit `.env` or share your API key. Without a key, or if the profile request fails, Steam-linked players are seeded as unranked.

### Start both services on Windows

Run `start_app.bat` from the repository root. It uses Python from the `py -3.13` launcher or `python` command if available; otherwise, it downloads and installs the official Python 3.13 installer for the current user. It creates the project virtual environment if needed, installs the requirements, then opens the backend and frontend in separate windows. Any path changes apply only to the launcher and its child windows.

The script needs an internet connection when Python or project dependencies need to be downloaded.

### Run locally without `start_app.bat`

Activate the virtual environment in each terminal. Start the API from the repository root in one terminal:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn backend.src.handlers.lambda_handler:app --reload
```

On macOS or Linux:

```sh
source .venv/bin/activate
python -m uvicorn backend.src.handlers.lambda_handler:app --reload
```

In a second terminal, activate the environment, set the backend URL, and start the Streamlit frontend:

```powershell
.venv\Scripts\Activate.ps1
$env:DEADLOCK_SEEDER_API_URL = "http://127.0.0.1:8000"
python -m streamlit run frontend/legacy_streamlit_app.py
```

On macOS or Linux:

```sh
source .venv/bin/activate
export DEADLOCK_SEEDER_API_URL="http://127.0.0.1:8000"
python -m streamlit run frontend/legacy_streamlit_app.py
```

Open the Streamlit URL shown in the terminal (usually `http://localhost:8501`).

## API

The FastAPI backend exposes `GET /` as a health check and `POST /seed` for team generation. The frontend sends a JSON body containing `player_list`. Each player needs a `name` and either a `steamID` or a manual `rank` and `subrank`, for example:

```json
{
  "player_list": [
    {"name": "Player One", "steamID": "76561198000000000"},
    {"name": "Player Two", "rank": "Seeker", "subrank": "III"}
  ]
}
```

The response contains `status: "success"` and `data` with `team_A` and `team_B`. Set `DEADLOCK_SEEDER_API_URL` to the deployed backend base URL before starting Streamlit; include any API Gateway stage, but do not append `/seed`.
