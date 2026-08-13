"""
Generates assets/spotify-now-playing.svg from the real Spotify API
(current track if playing, otherwise the most recently played one).

Requires env vars: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN
Run via the GitHub Action in .github/workflows/spotify.yml on a schedule.
"""

import os

import requests

from spotify_common import ACCENT, BG, MINT, escape_xml, fetch_album_art_b64, get_access_token, track_from_item

NOW_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"
RECENTLY_PLAYED_URL = "https://api.spotify.com/v1/me/player/recently-played?limit=1"


def get_track(token: str) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(NOW_PLAYING_URL, headers=headers, timeout=10)
    if r.status_code == 200 and r.content:
        data = r.json()
        if data.get("is_playing") and data.get("item"):
            return track_from_item(data["item"], playing=True)

    r = requests.get(RECENTLY_PLAYED_URL, headers=headers, timeout=10)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    return track_from_item(items[0]["track"], playing=False)


def build_svg(track: dict) -> str:
    status = "now-playing" if track["playing"] else "last-played"
    title = escape_xml(track["title"])[:34]
    artist = escape_xml(track["artist"])[:42]
    art = fetch_album_art_b64(track["album_art"])

    art_tag = (
        f'<image href="{art}" x="14" y="14" width="52" height="52" clip-path="url(#clip)"/>'
        if art
        else f'<rect x="14" y="14" width="52" height="52" rx="4" fill="{ACCENT}"/>'
    )

    bars = ""
    if track["playing"]:
        for i in range(4):
            x = 350 + i * 8
            dur = 0.6 + i * 0.15
            delay = i * 0.1
            bars += (
                f'<rect x="{x}" y="34" width="4" height="12" rx="1" fill="{ACCENT}">'
                f'<animate attributeName="height" values="4;22;4" dur="{dur}s" '
                f'repeatCount="indefinite" begin="{delay}s"/>'
                f'<animate attributeName="y" values="38;29;38" dur="{dur}s" '
                f'repeatCount="indefinite" begin="{delay}s"/>'
                f"</rect>"
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="80" viewBox="0 0 400 80" role="img">
  <title>Spotify {status}: {title} by {artist}</title>
  <defs>
    <clipPath id="clip"><rect x="14" y="14" width="52" height="52" rx="4"/></clipPath>
  </defs>
  <rect width="400" height="80" rx="8" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="399" height="79" rx="8" fill="none" stroke="{ACCENT}" stroke-width="1"/>
  {art_tag}
  <text x="80" y="32" font-family="monospace" font-size="11" fill="{ACCENT}"># spotify --{status}</text>
  <text x="80" y="50" font-family="monospace" font-size="13" fill="#e6edf3">{title}</text>
  <text x="80" y="66" font-family="monospace" font-size="11" fill="{MINT}">{artist}</text>
  {bars}
</svg>"""


def build_empty_svg() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="80" viewBox="0 0 400 80" role="img">
  <title>No recent Spotify activity</title>
  <rect width="400" height="80" rx="8" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="399" height="79" rx="8" fill="none" stroke="{ACCENT}" stroke-width="1"/>
  <text x="20" y="45" font-family="monospace" font-size="13" fill="{ACCENT}"># no recent spotify activity</text>
</svg>"""


def main() -> None:
    token = get_access_token()
    track = get_track(token)
    svg = build_svg(track) if track else build_empty_svg()

    os.makedirs("assets", exist_ok=True)
    with open("assets/spotify-now-playing.svg", "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
