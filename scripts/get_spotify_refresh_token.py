"""
One-time helper to get a Spotify refresh token.
Run locally: python get_spotify_refresh_token.py
Requires: pip install requests
"""

import base64
import urllib.parse

import requests

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-currently-playing user-read-recently-played"

client_id = input("Spotify Client ID: ").strip()
client_secret = input("Spotify Client Secret: ").strip()

auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
    {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
)

print("\n1. Abre este link, faz login e clica Agree:\n")
print(auth_url)
print(
    "\n2. Vais ser redirecionado para um URL que dá erro 'site can't be reached' "
    "— isso é normal. Copia esse URL da barra de endereços e cola abaixo.\n"
)
redirected = input("URL de redirecionamento: ").strip()
code = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query)["code"][0]

auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
resp = requests.post(
    "https://accounts.spotify.com/api/token",
    headers={"Authorization": f"Basic {auth_header}"},
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    },
    timeout=10,
)
resp.raise_for_status()
tokens = resp.json()

print("\nGuarda isto como o secret SPOTIFY_REFRESH_TOKEN no teu repo:\n")
print(tokens["refresh_token"])
