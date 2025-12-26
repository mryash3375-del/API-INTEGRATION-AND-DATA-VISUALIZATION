# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project overview

This repository contains **SkyGlass Weather**, a small Flask web application that serves a single-page weather dashboard backed by the OpenWeatherMap API.

- **Backend**: Python + Flask app in `app.py` exposing an HTML UI and a JSON weather API.
- **Frontend**: Vanilla JavaScript in `static/js/app.js` rendering the dashboard, forecast cards, and Chart.js-based trend chart.
- **Templates & styles**: Jinja2 templates in `templates/` and custom styles in `static/css/styles.css` on top of Bootstrap and Weather Icons.
- **Configuration**: Environment-based `OPENWEATHER_API_KEY` loaded from the OS or a local `.env` file (see `.env.example`).

## Backend architecture (Flask)

The Flask app is defined in `app.py`:

- `create_app() -> Flask`
  - Creates the Flask application instance.
  - Reads `OPENWEATHER_API_KEY` from environment (optionally via `python-dotenv`).
  - Warns at startup if the key is missing; in that case the `/api/weather` route will return a 500 with a helpful error payload.
  - Registers routes:
    - `GET /` → renders `templates/index.html`.
    - `GET /api/weather` → JSON API used by the frontend.

- `GET /api/weather` route
  - Accepts either a `city` query parameter **or** `lat` and `lon` query parameters.
  - Validates that at least one form of location is provided; otherwise returns HTTP 400 with a JSON error.
  - Calls `fetch_weather_and_forecast(...)` to talk to OpenWeatherMap and build a structured payload.
  - Handles errors explicitly:
    - Network issues (`requests.RequestException`) → HTTP 502 with a user-friendly message.
    - Unknown city (`ValueError` from the helper) → HTTP 404 with an explanatory message.
    - Missing API key or any other unexpected error → HTTP 500 with a generic, non-leaky JSON error.

- `fetch_weather_and_forecast(api_key, city=None, lat=None, lon=None) -> dict`
  - Core integration with OpenWeatherMap's **Current weather** and **5-day / 3‑hour forecast** endpoints.
  - Always requests **metric units** from the API; the frontend is responsible for converting to imperial when needed.
  - Determines location parameters based on `city` vs `lat`/`lon`.
  - Builds a `current_payload` dict including:
    - Location (`city`, `country`).
    - Local datetime and timezone offset.
    - Temperature, feels-like, humidity, pressure, wind speed, clouds.
    - Sunrise and sunset timestamps converted to local time.
    - Primary weather description and icon code.
  - Computes local time using the API's `timezone` offset and marks whether it's currently day or night at that location.
  - Calls `infer_theme(condition_id, is_daytime)` to derive a simple theme key (e.g. `clear-day`, `rain`, `clouds`) from OpenWeather condition codes and day/night state.
  - Calls `build_daily_forecast_and_chart(forecast, timezone_offset)` to reduce the 3‑hour forecast series into daily summaries and compact chart data.
  - Returns a JSON-serializable structure consumed directly by the frontend:
    - `location`: `{ city, country }`.
    - `current`: flattened current-conditions payload described above.
    - `forecast_daily`: list of up to 5 daily summary objects.
    - `chart`: `{ labels, temperature_c, humidity }` arrays used by Chart.js.
    - `meta`: `{ theme, is_day }` for theming.

- `build_daily_forecast_and_chart(forecast, timezone_offset) -> (list[dict], dict)`
  - Iterates over the 3‑hour forecast list and groups entries by **local calendar day**.
  - For each day it tracks:
    - `temp_min` / `temp_max` over all entries.
    - Running sum and count of humidity to compute a daily average.
    - A representative icon/description, biased toward midday entries.
  - Produces:
    - `summaries`: ordered list (skipping "today" if present) of up to 5 days, each with `temp_min_c`, `temp_max_c`, `humidity_avg`, and icon/description.
    - `chart` data: `labels` (e.g. `Mon 23`), `temperature_c` (max temp per day), and `humidity` (avg humidity per day).

- `infer_theme(condition_id: int, is_day: bool) -> str`
  - Maps OpenWeather condition ID ranges plus day/night into coarse-grained theme keys like `thunderstorm`, `rain`, `snow`, `fog`, `clear-day`, `clear-night`, `clouds`, and `default`.
  - The frontend uses these theme keys to apply CSS classes (`theme-<key>`) to the `<body>`.

- Entrypoint
  - At the bottom of `app.py`, `app = create_app()` is instantiated at module import time.
  - When run as a script (`python app.py`), the app starts a development server on `0.0.0.0` and port `PORT` (default `5000`) with `debug=True`.

- `debug_openweather.py`
  - Small standalone helper script to validate OpenWeather API access:
    - Loads `OPENWEATHER_API_KEY`.
    - Fails fast if it is missing.
    - Issues a sample request for the city `gujrat` and prints status and body prefix for manual inspection.

## Frontend architecture (templates, JS, and theming)

- Templates
  - `templates/base.html`
    - Global HTML skeleton: includes Bootstrap, Weather Icons, Google Fonts, and `static/css/styles.css`.
    - Defines the navbar with:
      - Unit toggle (`#unitToggle` + `#unitLabel`) to switch between metric and imperial.
      - Theme toggle (`#themeToggle`) to switch dark/light mode via the `data-theme` attribute on `<html>` and `<body>`.
    - Includes a loading overlay (`#loadingOverlay`) used while weather data is being fetched.
    - Loads Chart.js and the main frontend script `static/js/app.js` at the bottom.
  - `templates/index.html`
    - Extends `base.html` and defines the main page content (single-view SPA style).
    - Contains:
      - City search input and buttons for manual search and "Use my location".
      - Placeholders for current conditions (city, time, temperature, description, humidity, wind, pressure, sunrise/sunset, updated timestamp).
      - A horizontal list container `#forecastList` for daily forecast cards.
      - A `canvas#trendChart` element for the temperature/humidity trend chart.

- JavaScript controller (`static/js/app.js`)
  - Central state:
    - `state.raw`: last JSON response from `/api/weather` (metric-based data from the backend).
    - `state.unit`: `'metric'` or `'imperial'`, controlling conversions and labels.
    - `state.chart`: cached Chart.js instance for incremental updates.
  - DOM wiring:
    - `selectElements()` caches references to all dynamic DOM nodes (inputs, buttons, metric/imperial & theme toggles, alerts, display elements, forecast container, chart canvas).
    - `init()`:
      - Calls `selectElements()`, attaches event listeners, restores preferences from `localStorage`.
      - Attempts geolocation on load; if allowed, immediately fetches weather by coordinates, otherwise leaves the UI idle for manual search.
  - Event handling:
    - Search button click / Enter key in the search input triggers `fetchWeather({ city })`.
    - "Use my location" button triggers navigator geolocation and then `fetchWeather({ lat, lon })`.
    - Unit toggle updates `state.unit`, label text (°C/°F), re-renders the view from existing data, and persists preferences.
    - Theme toggle switches `data-theme` attributes, which the CSS uses to adjust dark/light styling, and persists preferences.
  - Data loading (`fetchWeather({ city, lat, lon })`):
    - Shows the loading overlay and hides any previous error alert.
    - Builds query parameters for `/api/weather` from city and/or coordinates.
    - Parses the JSON response and checks `response.ok`:
      - On error, displays the server-provided `error` message if present.
      - On success, stores `data` into `state.raw` and calls `renderAll()`.
    - On network failures, emits a generic "Network error" message.
  - Rendering pipeline (`renderAll()`):
    - `renderCurrentWeather()`:
      - Reads `location` and `current` from `state.raw`.
      - Converts temperatures, wind speed, and units based on `state.unit`.
      - Formats local datetime, sunrise/sunset, and various metrics into the DOM.
      - Maps the backend's icon code + `meta.is_day` into a Weather Icons CSS class via `mapIconToClass(...)`.
    - `renderForecast()`:
      - Iterates over `forecast_daily` and builds forecast cards per day.
      - Applies per-day descriptions, min/max temps (converted to current unit), humidity, and icon mapping.
    - `renderChart()`:
      - Reads `chart.labels`, `chart.temperature_c`, and `chart.humidity` from `state.raw`.
      - Converts temperature series to °F when `state.unit === 'imperial'`.
      - Creates or updates a dual-axis Chart.js line chart with temperature and humidity datasets.
      - Dynamically updates y-axis label text when the unit changes.
    - `applyTheme()`:
      - Reads `meta.theme` from the backend payload.
      - Clears any previous `theme-*` class from `<body>` and adds a new `theme-<theme>` class.
      - Combined with `data-theme` and `styles.css`, this drives the "SkyGlass" background and color scheme.
  - Preferences persistence:
    - `savePreferences()` stores `{ unit, theme }` under the `skyglass_prefs` key in `localStorage`.
    - `restorePreferences()` reads this key on load and restores unit selection and dark/light mode.

## Environment and configuration

- Dependencies (`requirements.txt`)
  - `Flask>=3.0.0` — web framework for the backend.
  - `requests>=2.31.0` — HTTP client used for OpenWeather API calls.
  - `python-dotenv>=1.0.0` — optional helper to load environment variables from a `.env` file during development.

- Environment variables / secrets
  - **API key**:
    - The app expects `OPENWEATHER_API_KEY` to be set in the environment.
    - During local development you can copy `.env.example` to `.env` and fill in your actual key; `python-dotenv` will load it automatically when `app.py` or `debug_openweather.py` are imported.
  - The `.env.example` file documents the expected variable and serves as a template; do not commit your actual `.env` with real keys.

## Common commands

All commands below assume you are running them from the repository root and have a suitable Python installed.

### Set up a virtual environment and install dependencies

```bash path=null start=null
python -m venv .venv
# Activate the environment:
#   On Linux/macOS: source .venv/bin/activate
#   On Windows (PowerShell): .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

### Run the development server

```bash path=null start=null
# With OPENWEATHER_API_KEY set in the environment (or via .env):
python app.py
```

- The app listens on `0.0.0.0` and port `5000` by default (or on the port specified in the `PORT` environment variable).
- Open `http://localhost:5000` in a browser to use the SkyGlass Weather UI.

### Debug OpenWeather API connectivity

```bash path=null start=null
python debug_openweather.py
```

- Verifies that `OPENWEATHER_API_KEY` is present and that the OpenWeather API is reachable, printing HTTP status and the beginning of the response body.

### Linting and tests

- This repository does **not** currently define any linting or testing tooling (no test files or lint-related dependencies are present).
- Before assuming commands like `pytest`, `flake8`, or `black` exist, check that the corresponding tools have been added to the environment and update this `WARP.md` with any new standardized commands.
