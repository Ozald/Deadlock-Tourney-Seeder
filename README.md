# Deadlock Tourney Seeder

A lightweight Streamlit web application designed to make balancing teams easier for custom matches in *Deadlock*.

<p align="left">
  <img src="https://cdn2.steamgriddb.com/logo/d1555a36e55c44c60ba4dfb6b4485b82.png" alt="Deadlock Tourney Seeder Logo" width="180"/>
</p>

## Features

- **Optimal Team Balancing:** Evaluates player MMR combinations using a bell-curve weighting algorithm to minimize skill disparity between Hidden King and Archmother.
- **Automated Rank Retrieval:** Fetches live player rank badges and flat MMR progress directly from the Deadlock API via Steam ID.
- **Manual Fallback Entry:** Allows custom rank and subrank selection for players without a linked Steam ID.
- **Dynamic Roster Sizes:** Supports custom matches ranging from 4 to 12 total players (2v2 up to 6v6).

## Getting Started

From the repository root, create and activate a virtual environment, then install the dependencies listed in `requirements.txt`:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, use `python3 -m venv .venv` and `source .venv/bin/activate` instead of the first two commands.

Start the API from the repository root in one terminal:

```powershell
python -m uvicorn backend.src.handlers.lambda_handler:app --reload
```

In a second terminal with the virtual environment activated, point the frontend at the local API and launch Streamlit:

```powershell
$env:DEADLOCK_SEEDER_API_URL = "http://127.0.0.1:8000"
python -m streamlit run frontend/legacy_streamlit_app.py
```

Open the Streamlit URL shown in the terminal (usually `http://localhost:8501`).

### Use a deployed API

Set `DEADLOCK_SEEDER_API_URL` to the deployed API base URL, including any API Gateway stage but excluding `/seed`, before launching Streamlit. For example:

```powershell
$env:DEADLOCK_SEEDER_API_URL = "https://your-api.example.com/prod"
python -m streamlit run frontend/legacy_streamlit_app.py
```

The frontend sends tournament data to `POST /seed` as JSON.

## Note

This is currently a work-in-progress project. Once the first version is completed, a website will be posted. Stay tuned!
