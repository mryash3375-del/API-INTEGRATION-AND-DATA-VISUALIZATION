import os
from datetime import datetime, timedelta

import requests
from flask import Flask, jsonify, render_template, request

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional; env vars can be provided by the host
    pass


def create_app() -> Flask:
    app = Flask(__name__)

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        app.logger.warning(
            "OPENWEATHER_API_KEY is not set. The /api/weather endpoint will return an error "
            "until you configure the API key."
        )

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/weather")
    def api_weather():
        """Return current weather + 5-day forecast for a city or coordinates."""
        nonlocal api_key

        if not api_key:
            return (
                jsonify(
                    {
                        "error": "Server API key is not configured.",
                        "details": "Set the OPENWEATHER_API_KEY environment variable on the server.",
                    }
                ),
                500,
            )

        city = request.args.get("city", type=str)
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)

        if not city and (lat is None or lon is None):
            return (
                jsonify(
                    {
                        "error": "Missing location parameters.",
                        "details": "Provide either a city name or latitude and longitude.",
                    }
                ),
                400,
            )

        try:
            weather_payload = fetch_weather_and_forecast(api_key, city=city, lat=lat, lon=lon)
        except requests.RequestException:
            return (
                jsonify(
                    {
                        "error": "Network error while contacting weather service.",
                        "details": "Please try again in a moment.",
                    }
                ),
                502,
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 404
        except Exception:
            # Avoid leaking internals; log server-side in real deployments
            return (
                jsonify(
                    {
                        "error": "Unexpected server error.",
                        "details": "The weather service failed. Please try again later.",
                    }
                ),
                500,
            )

        return jsonify(weather_payload)

    return app


def fetch_weather_and_forecast(api_key: str, city: str | None = None, lat: float | None = None, lon: float | None = None) -> dict:
    """Fetch current weather and 5-day forecast from OpenWeatherMap.

    Always queries in metric units and lets the client convert units.
    """

    base_url = "https://api.openweathermap.org/data/2.5"

    params_common: dict[str, str | float] = {
        "appid": api_key,
        "units": "metric",
    }

    if city:
        params_location = {"q": city}
    else:
        params_location = {"lat": lat, "lon": lon}

    # Current weather
    current_resp = requests.get(f"{base_url}/weather", params={**params_common, **params_location}, timeout=10)
    if current_resp.status_code == 404:
        raise ValueError("City not found. Please check the spelling and try again.")
    current_resp.raise_for_status()
    current = current_resp.json()

    # 5-day / 3-hour forecast
    forecast_resp = requests.get(
        f"{base_url}/forecast", params={**params_common, **params_location}, timeout=10
    )
    forecast_resp.raise_for_status()
    forecast = forecast_resp.json()

    timezone_offset = current.get("timezone", 0)

    # Current conditions
    current_dt_utc = datetime.utcfromtimestamp(current["dt"])  # type: ignore[arg-type]
    current_local = current_dt_utc + timedelta(seconds=timezone_offset)

    sunrise_utc = datetime.utcfromtimestamp(current["sys"]["sunrise"])  # type: ignore[index]
    sunset_utc = datetime.utcfromtimestamp(current["sys"]["sunset"])  # type: ignore[index]
    sunrise_local = sunrise_utc + timedelta(seconds=timezone_offset)
    sunset_local = sunset_utc + timedelta(seconds=timezone_offset)

    is_daytime = sunrise_local <= current_local <= sunset_local

    weather_main = current["weather"][0]  # type: ignore[index]
    condition_id = weather_main.get("id", 800)
    theme = infer_theme(condition_id, is_daytime)

    current_payload = {
        "city": current.get("name"),
        "country": current.get("sys", {}).get("country"),
        "datetime": current_local.isoformat(),
        "timezone_offset": timezone_offset,
        "temp_c": current.get("main", {}).get("temp"),
        "feels_like_c": current.get("main", {}).get("feels_like"),
        "humidity": current.get("main", {}).get("humidity"),
        "pressure": current.get("main", {}).get("pressure"),
        "wind_speed_ms": current.get("wind", {}).get("speed"),
        "description": weather_main.get("description", "").title(),
        "icon": weather_main.get("icon"),
        "sunrise": sunrise_local.isoformat(),
        "sunset": sunset_local.isoformat(),
        "clouds": current.get("clouds", {}).get("all"),
    }

    daily_forecast, chart_data = build_daily_forecast_and_chart(forecast, timezone_offset)

    return {
        "location": {
            "city": current_payload["city"],
            "country": current_payload["country"],
        },
        "current": current_payload,
        "forecast_daily": daily_forecast,
        "chart": chart_data,
        "meta": {
            "theme": theme,
            "is_day": is_daytime,
        },
    }


def build_daily_forecast_and_chart(forecast: dict, timezone_offset: int) -> tuple[list[dict], dict]:
    """Collapse 3-hour forecast into daily summaries + simple chart data.

    We group by local calendar day and compute min/max temperature and avg humidity.
    """

    daily: dict[str, dict] = {}

    for entry in forecast.get("list", []):  # type: ignore[assignment]
        dt_utc = datetime.utcfromtimestamp(entry["dt"])  # type: ignore[arg-type]
        local_dt = dt_utc + timedelta(seconds=timezone_offset)
        date_key = local_dt.date().isoformat()

        main = entry.get("main", {})
        temp = main.get("temp")
        humidity = main.get("humidity")

        weather = (entry.get("weather") or [{}])[0]
        icon = weather.get("icon")
        desc = weather.get("description", "").title()

        if date_key not in daily:
            daily[date_key] = {
                "date": date_key,
                "temp_min": temp,
                "temp_max": temp,
                "humidity_sum": humidity or 0,
                "humidity_count": 1 if humidity is not None else 0,
                "icon": icon,
                "description": desc,
                "sample_hour": local_dt.hour,
            }
        else:
            d = daily[date_key]
            if temp is not None:
                if d["temp_min"] is None or temp < d["temp_min"]:
                    d["temp_min"] = temp
                if d["temp_max"] is None or temp > d["temp_max"]:
                    d["temp_max"] = temp
            if humidity is not None:
                d["humidity_sum"] += humidity
                d["humidity_count"] += 1
            # Prefer midday-ish icon and description
            if abs(local_dt.hour - 12) < abs(d["sample_hour"] - 12):
                d["icon"] = icon
                d["description"] = desc
                d["sample_hour"] = local_dt.hour

    # Sort dates, skip "today" if present, keep next 5 days
    sorted_dates = sorted(daily.keys())
    today = datetime.utcfromtimestamp(forecast.get("list", [])[0]["dt"]).date() if forecast.get("list") else None

    summaries: list[dict] = []
    labels: list[str] = []
    temp_values: list[float] = []
    humidity_values: list[float] = []

    for date_key in sorted_dates:
        date_obj = datetime.fromisoformat(date_key).date()
        if today and date_obj == today:
            continue
        day = daily[date_key]
        humidity_avg = None
        if day["humidity_count"]:
            humidity_avg = day["humidity_sum"] / day["humidity_count"]

        label = date_obj.strftime("%a %d")
        labels.append(label)
        # Use max temp and avg humidity in the trend charts
        temp_values.append(day["temp_max"] or 0)
        humidity_values.append(humidity_avg or 0)

        summaries.append(
            {
                "date": date_key,
                "label": label,
                "temp_min_c": round(day["temp_min"], 1) if day["temp_min"] is not None else None,
                "temp_max_c": round(day["temp_max"], 1) if day["temp_max"] is not None else None,
                "humidity_avg": round(humidity_avg, 1) if humidity_avg is not None else None,
                "icon": day["icon"],
                "description": day["description"],
            }
        )

        if len(summaries) >= 5:
            break

    chart = {
        "labels": labels,
        "temperature_c": temp_values,
        "humidity": humidity_values,
    }

    return summaries, chart


def infer_theme(condition_id: int, is_day: bool) -> str:
    """Return a simple theme key based on OpenWeather condition ID and day/night."""

    if 200 <= condition_id < 300:
        return "thunderstorm"
    if 300 <= condition_id < 600:
        return "rain"  # drizzle + rain
    if 600 <= condition_id < 700:
        return "snow"
    if 700 <= condition_id < 800:
        return "fog"
    if condition_id == 800:
        return "clear-day" if is_day else "clear-night"
    if 801 <= condition_id < 900:
        return "clouds"
    return "default"


app = create_app()


if __name__ == "__main__":
    # For production, use a real WSGI server (gunicorn, waitress, etc.) instead.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
