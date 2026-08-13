"""
Generates assets/spotify-recently-played.svg — a list card of the last
tracks played on Spotify, built directly from the Spotify Web API.

Requires env vars: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN
Run via the GitHub Action in .github/workflows/spotify.yml on a schedule.
"""

import os

import requests

from spotify_common import ACCENT, BG, MINT, escape_xml, fetch_album_art_b64, get_access_token, track_from_item

TRACK_COUNT = 10
RECENTLY_PLAYED_URL = f"https://api.spotify.com/v1/me/player/recently-played?limit=50"


def get_recent_tracks(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(RECENTLY_PLAYED_URL, headers=headers, timeout=10)
    r.raise_for_status()
    items = r.json().get("items", [])

    tracks: list[dict] = []
    last_id = None
    for entry in items:
        track = track_from_item(entry["track"])
        # skip consecutive replays of the same track so the list feels varied
        if track["id"] == last_id:
            continue
        tracks.append(track)
        last_id = track["id"]
        if len(tracks) >= TRACK_COUNT:
            break
    return tracks


def build_svg(tracks: list[dict]) -> str:
    row_h = 30
    top_pad = 32
    bottom_pad = 10
    width = 400
    height = top_pad + row_h * len(tracks) + bottom_pad

    defs = ""
    rows = ""
    for i, t in enumerate(tracks):
        y = top_pad + i * row_h
        art_y = y + 4
        title = escape_xml(t["title"])[:32]
        artist = escape_xml(t["artist"])[:30]
        art = fetch_album_art_b64(t["album_art"])

        defs += f'<clipPath id="clip{i}"><rect x="14" y="{art_y}" width="22" height="22" rx="3"/></clipPath>'
        art_tag = (
            f'<image href="{art}" x="14" y="{art_y}" width="22" height="22" clip-path="url(#clip{i})"/>'
            if art
            else f'<rect x="14" y="{art_y}" width="22" height="22" rx="3" fill="{ACCENT}"/>'
        )

        rows += art_tag
        rows += f'<text x="46" y="{y + 13}" font-family="monospace" font-size="10" fill="#e6edf3">{title}</text>'
        rows += f'<text x="46" y="{y + 25}" font-family="monospace" font-size="9" fill="{MINT}">{artist}</text>'
        if i < len(tracks) - 1:
            rows += f'<line x1="14" y1="{y + row_h - 1}" x2="386" y2="{y + row_h - 1}" stroke="#0a2e33" stroke-width="1"/>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <title>Spotify recently played tracks</title>
  <defs>{defs}</defs>
  <rect width="{width}" height="{height}" rx="8" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="none" stroke="{ACCENT}" stroke-width="1"/>
  <text x="14" y="21" font-family="monospace" font-size="11" fill="{ACCENT}"># spotify --recently-played</text>
  {rows}
</svg>"""


def build_empty_svg() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="60" viewBox="0 0 400 60" role="img">
  <title>No recent Spotify activity</title>
  <rect width="400" height="60" rx="8" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="399" height="59" rx="8" fill="none" stroke="{ACCENT}" stroke-width="1"/>
  <text x="20" y="35" font-family="monospace" font-size="13" fill="{ACCENT}"># no recent spotify activity</text>
</svg>"""


def main() -> None:
    token = get_access_token()
    tracks = get_recent_tracks(token)
    svg = build_svg(tracks) if tracks else build_empty_svg()

    os.makedirs("assets", exist_ok=True)
    with open("assets/spotify-recently-played.svg", "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
