import time, httpx
from datetime import datetime, timedelta
from ..config import settings

AUTH_BASE = "https://api.login.yahoo.com"
TOKEN_URL = f"{AUTH_BASE}/oauth2/get_token"
AUTH_URL = f"{AUTH_BASE}/oauth2/request_auth"

class YahooOAuth:
    def __init__(self):
        self.client_id = settings.YAHOO_CLIENT_ID
        self.client_secret = settings.YAHOO_CLIENT_SECRET
        self.redirect_uri = settings.YAHOO_REDIRECT_URI
        self.scope = settings.YAHOO_SCOPE

    def auth_url(self, state: str):
        return (
            f"{AUTH_URL}?client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&response_type=code&scope={self.scope}&state={state}"
        )

    async def exchange_code(self, code: str):
        async with httpx.AsyncClient() as client:
            res = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                    "code": code,
                },
                auth=(self.client_id, self.client_secret),
            )
            res.raise_for_status()
            data = res.json()
            return data

    async def refresh(self, refresh_token: str):
        async with httpx.AsyncClient() as client:
            res = await client.post(
                TOKEN_URL,
                data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                auth=(self.client_id, self.client_secret),
            )
            res.raise_for_status()
            return res.json()