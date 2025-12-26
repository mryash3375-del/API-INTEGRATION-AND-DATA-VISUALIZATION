from datetime import datetime
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

api_key = os.getenv("OPENWEATHER_API_KEY")
print("API key present:", bool(api_key))

if not api_key:
    raise SystemExit("No OPENWEATHER_API_KEY set")

resp = requests.get(
    "https://api.openweathermap.org/data/2.5/weather",
    params={"q": "gujrat", "appid": api_key, "units": "metric"},
    timeout=10,
)
print("Status:", resp.status_code)
print("Body prefix:", resp.text[:200])
