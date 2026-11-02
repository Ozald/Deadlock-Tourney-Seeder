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

## Run the frontend

Set `DEADLOCK_SEEDER_API_URL` to the deployed API base URL, then run the Streamlit app. For example, in PowerShell:

```powershell
$env:DEADLOCK_SEEDER_API_URL = "https://your-api.example.com/prod"
streamlit run frontend/legacy_streamlit_app.py
```

The frontend sends tournament data to `POST /seed` as JSON.

## Note

This is currently a work-in-progress project. Once the first version is completed, a website will be posted. Stay tuned!
