from dotenv import load_dotenv

import os

load_dotenv()

baseUrl = os.getenv("BASE_URL", "https://api-jb2.integrations.ecimanufacturing.com:443/api/v1")
authUrl = os.getenv("AUTH_URL", "https://api-user.integrations.ecimanufacturing.com:443/oauth2/api-user/token")
clientId: str | None = os.getenv("CLIENT_ID")
clientSecret: str | None = os.getenv("CLIENT_SECRET")

if clientId is None:
  raise ValueError("CRITICAL ERROR: CLIENT_ID is not set as an environment variable!")

if clientSecret is None:
  raise ValueError("CRITICAL ERROR: CLIENT_SECRET is not set as an environment variable!")