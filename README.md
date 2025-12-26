# API-INTEGRATION-AND-DATA-VISUALIZATION
# Weather-Application

# SkyGlass Weather — API Integration & Data Visualization

A small, single-page Flask app that fetches weather and 5-day forecasts from OpenWeatherMap and visualizes them with a lightweight frontend. This repository demonstrates API integration, data processing, and simple charting for educational projects or quick prototypes.

## Features

- Fetches current weather and 5-day / 3-hour forecast from OpenWeatherMap.
- Consolidates 3-hour forecasts into daily summaries and chart data.
- Theme inference from OpenWeather condition codes (day/night aware).
- Simple, responsive single-page UI served by Flask (`index.html`).
- Minimal dependencies and easy local setup.

![image alt]()

## Tech stack

- Python 3.10+
- Flask
- requests (for OpenWeather API)
- python-dotenv (optional, for local `.env` files)
- Vanilla JS + CSS for the frontend (in `static/`)

## Repository structure

- [app.py](app.py) — Flask application and core weather integration logic.
- [debug_openweather.py](debug_openweather.py) — helper to validate OpenWeather access.
- [templates/index.html](templates/index.html) — frontend single-page app.
- [static/js/app.js](static/js/app.js) — frontend logic and charting hooks.
- [static/css/styles.css](static/css/styles.css) — frontend styles.
- [.env](.env) — local environment file (not committed; copy from `.env.example` if present).
- [requirements.txt](requirements.txt) — Python dependencies.
- [WARP.md](WARP.md) — project notes and design rationale.

## Environment variables

The app requires an OpenWeatherMap API key to function:

- `OPENWEATHER_API_KEY` — Your OpenWeatherMap API key (required).
- `PORT` — Optional port for local run (default: `5000`).

For local development you can create a `.env` file in the project root with:

```
OPENWEATHER_API_KEY=your_api_key_here
PORT=5000
```

`python-dotenv` is included as an optional dependency so the `.env` file will be loaded automatically when running locally.

> Note: The repository includes a sample `.env` file with a placeholder key. Replace it with your own key.

## Quick start (local)

1. Create and activate a virtual environment (Windows PowerShell example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add your API key to `.env` (or set the environment variable).

4. Run the app locally:

```powershell
python app.py
```

Open http://127.0.0.1:5000/ in your browser and use the search/controls to fetch weather.

## API

- `GET /api/weather` — returns JSON with `current`, `forecast_daily`, and `chart` sections.
	- Query parameters:
		- `city` (string) — e.g. `q=London` (preferred)
		- `lat` and `lon` (floats) — coordinates alternative

If the API key is missing, `/api/weather` returns an error explaining how to configure `OPENWEATHER_API_KEY`.

## Debugging & validation

Use `debug_openweather.py` to validate your API key and see raw responses from OpenWeather.

```powershell
python debug_openweather.py
```

## Tests & extensions

- The app includes clear separation between data fetching (`fetch_weather_and_forecast`) and presentation (`templates` + `static`). This makes it straightforward to:
	- Add unit tests for the data-processing functions.
	- Swap the frontend for a React/Vue app while keeping the Flask API.
	- Add caching (Redis) or rate-limiting for production.

## Deployment notes

- For production use a WSGI server (gunicorn, waitress, etc.) instead of the built-in Flask server.
- Provide `OPENWEATHER_API_KEY` securely via your host's environment variable mechanism.
- Consider caching forecast responses to reduce API calls and latency.

## License & attribution

This project is provided as-is for learning and demonstration. Check `WARP.md` for history and design notes.

---

If you'd like, I can also:

- Add a short CONTRIBUTING guide
- Create a `.env.example` file with the required variables
- Add a sample screenshot to the README

Tell me which of the above you'd like next.



