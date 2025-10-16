import httpx
from ..models import OAuthToken

BASE = "https://fantasysports.yahooapis.com/fantasy/v2"

async def yahoo_get(path: str, token: OAuthToken):
    headers = {"Authorization": f"Bearer {token.access_token}", "Accept": "application/json"}
    async with httpx.AsyncClient(base_url=BASE, headers=headers, timeout=20) as client:
        res = await client.get(path)
        res.raise_for_status()
        return res.json()