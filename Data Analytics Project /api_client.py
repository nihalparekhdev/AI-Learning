"""
api_client.py - Real-time data layer.

Pulls live weather + air-quality data from the free Open-Meteo APIs
(no API key needed). If the network/API is unreachable it falls back to
simulated data so the lab never breaks (the dashboard shows a warning).
"""
import numpy as np
import pandas as pd
import requests

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

WEATHER_VARS = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m",
                "surface_pressure", "precipitation"]
AIR_VARS = ["pm2_5", "pm10", "us_aqi"]

# column -> (display label, unit)
LABELS = {
    "temperature_2m": ("Temperature", "°C"),
    "relative_humidity_2m": ("Humidity", "%"),
    "wind_speed_10m": ("Wind speed", "km/h"),
    "surface_pressure": ("Pressure", "hPa"),
    "precipitation": ("Precipitation", "mm"),
    "pm2_5": ("PM2.5", "µg/m³"),
    "pm10": ("PM10", "µg/m³"),
    "us_aqi": ("US AQI", ""),
}

CITIES = {
    "Vadodara": (22.31, 73.18),
    "Mumbai": (19.08, 72.88),
    "Delhi": (28.61, 77.21),
    "London": (51.51, -0.13),
    "New York": (40.71, -74.01),
    "Tokyo": (35.68, 139.69),
    "Sydney": (-33.87, 151.21),
}


def label(col: str) -> str:
    name, unit = LABELS.get(col, (col, ""))
    return f"{name} ({unit})" if unit else name


def _get(url: str, params: dict, timeout: int = 10) -> dict:
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_live_data(lat: float, lon: float, past_days: int = 14):
    """
    Returns (df, current, source, note)
      df      : hourly DataFrame, DatetimeIndex, up to the current hour
      current : dict with the latest reading (15-min fresh from the API)
      source  : "live" or "simulated"
      note    : human-readable status message
    """
    try:
        w = _get(WEATHER_URL, {
            "latitude": lat, "longitude": lon,
            "hourly": ",".join(WEATHER_VARS),
            "current": ",".join(WEATHER_VARS),
            "past_days": past_days, "forecast_days": 1, "timezone": "auto",
        })
        df = pd.DataFrame(w["hourly"])
        df["time"] = pd.to_datetime(df["time"])
        df = df.set_index("time")
        now = pd.to_datetime(w["current"]["time"])
        df = df[df.index <= now.floor("h")]
        current = {k: w["current"].get(k) for k in WEATHER_VARS}
        current["time"] = now

        note = "Weather: Open-Meteo live API."
        try:  # air quality is optional - don't fail the whole load
            a = _get(AIR_URL, {
                "latitude": lat, "longitude": lon,
                "hourly": ",".join(AIR_VARS),
                "past_days": past_days, "forecast_days": 1, "timezone": "auto",
            })
            air = pd.DataFrame(a["hourly"])
            air["time"] = pd.to_datetime(air["time"])
            df = df.join(air.set_index("time"), how="left")
            note += " Air quality: Open-Meteo Air Quality API."
        except Exception as exc:
            note += f" (Air-quality unavailable: {type(exc).__name__})"

        df = df.dropna(axis=1, how="all").ffill(limit=3).dropna()
        for c in AIR_VARS:  # latest air-quality value for the KPI row
            if c in df.columns:
                current[c] = float(df[c].iloc[-1])
        return df, current, "live", note
    except Exception as exc:
        df = synthetic_data(past_days)
        current = {c: float(df[c].iloc[-1]) for c in df.columns}
        current["time"] = df.index[-1]
        return df, current, "simulated", (
            f"Could not reach the live API ({type(exc).__name__}). "
            "Showing simulated data instead.")


def synthetic_data(past_days: int = 14) -> pd.DataFrame:
    """Realistic-looking hourly data with a daily cycle, noise and a few spikes."""
    end = pd.Timestamp.now().floor("h")
    idx = pd.date_range(end=end, periods=past_days * 24, freq="h")
    n = len(idx)
    rng = np.random.default_rng(int(end.timestamp() // 3600))  # stable within an hour
    hour, t = idx.hour.values, np.arange(n)

    temp = 28 + 6 * np.sin((hour - 9) / 24 * 2 * np.pi) \
        + 1.5 * np.sin(t / 24 / 7 * 2 * np.pi) + rng.normal(0, 0.6, n)
    hum = 60 - 2.2 * (temp - 28) + rng.normal(0, 3, n)
    wind = 8 + 3 * np.abs(np.sin(t / 17)) + rng.normal(0, 1, n)
    pres = 1008 + 3 * np.sin(t / 60) + rng.normal(0, 0.4, n)
    rain = np.where(rng.random(n) < 0.07, rng.gamma(2, 1.2, n), 0.0)
    pm25 = 45 + 15 * np.sin((hour - 20) / 24 * 2 * np.pi) - 0.8 * wind + rng.normal(0, 4, n)

    spikes = rng.choice(n, 5, replace=False)  # inject anomalies
    temp[spikes] += rng.choice([-1, 1], 5) * 6
    pm25[spikes] += 60

    return pd.DataFrame({
        "temperature_2m": temp.round(1),
        "relative_humidity_2m": np.clip(hum, 5, 100).round(0),
        "wind_speed_10m": np.clip(wind, 0, None).round(1),
        "surface_pressure": pres.round(1),
        "precipitation": rain.round(1),
        "pm2_5": np.clip(pm25, 2, None).round(1),
    }, index=idx.rename("time"))
