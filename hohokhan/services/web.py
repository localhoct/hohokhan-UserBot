from __future__ import annotations

from dataclasses import dataclass

import httpx

USER_AGENT = "HoHoKhan/2.0 (https://github.com/localhoct/hohokhan)"


async def wikipedia_summary(query: str) -> tuple[str, str] | None:
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 1,
        "prop": "extracts|info",
        "exintro": 1,
        "explaintext": 1,
        "inprop": "url",
        "format": "json",
        "formatversion": 2,
    }
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get("https://fa.wikipedia.org/w/api.php", params=params)
        response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", [])
    if not pages:
        return None
    page = pages[0]
    summary = str(page.get("extract") or "").strip()
    if not summary:
        return None
    return summary[:3500], str(page.get("fullurl") or "")


@dataclass(frozen=True, slots=True)
class Weather:
    city: str
    description: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float


async def current_weather(city: str, api_key: str) -> Weather:
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "fa"}
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(
            "https://api.openweathermap.org/data/2.5/weather", params=params
        )
        if response.status_code == 404:
            raise ValueError("شهر پیدا نشد")
        response.raise_for_status()
    data = response.json()
    return Weather(
        city=str(data.get("name") or city),
        description=str((data.get("weather") or [{}])[0].get("description") or "نامشخص"),
        temperature=float(data["main"]["temp"]),
        feels_like=float(data["main"]["feels_like"]),
        humidity=int(data["main"]["humidity"]),
        wind_speed=float(data.get("wind", {}).get("speed", 0)),
    )
