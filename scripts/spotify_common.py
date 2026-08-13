"""Shared helpers for the Spotify README widgets."""

import base64
import os

import requests

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]

TOKEN_URL = "https://accounts.spotify.com/api/token"

ACCENT = "#00E5FF"
MINT = "#7dffea"
BG = "#000000"


def get_access_token() -> str:
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_album_art_b64(url: str | None) -> str | None:
    if not url:
        return None
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    b64 = base64.b64encode(r.content).decode()
    return f"data:image/jpeg;base64,{b64}"


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def track_from_item(item: dict, playing: bool = False) -> dict:
    images = item.get("album", {}).get("images") or []
    return {
        "id": item.get("id"),
        "playing": playing,
        "title": item["name"],
        "artist": ", ".join(a["name"] for a in item["artists"]),
        "album_art": images[-1]["url"] if images else None,  # smallest image is enough
        "url": item["external_urls"]["spotify"],
    }
