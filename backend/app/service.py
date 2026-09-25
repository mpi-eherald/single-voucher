from config import baseUrl

import time
import httpx


class JB2ClientManager:
  def __init__(
      self,
      auth_url: str,
      client_id: str | None,
      client_secret: str | None):
    self.auth_url = auth_url
    self.client_id = client_id
    self.client_secret = client_secret
    self.client = httpx.AsyncClient(base_url=baseUrl)
    self._token = None
    self._expires_at = 0

  async def _fetch_new_token(self, payload: dict):
    response = await self.client.post(self.auth_url, data=payload)
    response.raise_for_status()
    data = response.json()

    self._token = data["access_token"]
    self._expires_at = time.time() + data["expires_in"] - 60

  async def get_valid_token(self) -> str | None:
    payload = {
            "grant_type": "client_credentials",
            "scope": "openid",
            "client_id": self.client_id,
            "client_secret": self.client_secret
          }

    if time.time() >= self._expires_at or not self._token:
      await self._fetch_new_token(payload)

    return self._token

  async def close(self):
    await self.client.aclose()
