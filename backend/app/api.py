from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import authUrl, clientId, clientSecret
from .service import JB2ClientManager

import httpx
import platform
import config


@asynccontextmanager
async def lifespan(app: FastAPI):
  app_name = app.title
  startup_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
  python_version = platform.python_version()

  jb2_manager = JB2ClientManager(
     auth_url=authUrl,
     client_id=clientId,
     client_secret=clientSecret
  )

  try:
    await jb2_manager.get_valid_token()
  except Exception as e:
    print(f"Warning: Failed to fetch initial token.\n{e}")

  app.state.jb2_manager = jb2_manager
  
  print(
      "\n=========================================\n"
      "          Application Startup            \n"
      "=========================================\n"
      f"App Name        : {app_name}\n"
      f"Startup Time    : {startup_time}\n"
      f"Python Version  : {python_version}\n"
      "=========================================\n"
  )

  yield

  await app.state.jb2_manager.close()

  shutdown_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

  print(
      "\n=========================================\n"
      "          Application Shutdown           \n"
      "=========================================\n"
      f"Shutdown Time   : {shutdown_time}\n"
      "=========================================\n"
  )

app = FastAPI(title="Single Voucher Into JB2", lifespan=lifespan, root_path="/api/v1")

origins = [
  "http://localhost:5173",
  "localhost:5173"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)


async def get_auth_client(request: Request) -> httpx.AsyncClient:
  manager: JB2ClientManager = request.app.state.jb2_manager

  token = await manager.get_valid_token()

  manager.client.headers.update({"Authorization": f"Bearer {token}"})

  return manager.client


@app.get("/", tags=["root"], include_in_schema=False)
async def read_root():
  return {"message": "Entry for JB2 single voucher creation"}


@app.post("/voucher", tags=["voucher"])
async def post_vouchers(client: httpx.AsyncClient = Depends(get_auth_client)):
    payload = {
      "timeTicketDetails": [
        {
          "cycleTime": 10,
          "jobNumber": "999997-01",
          "operationNumber": 13,
          "piecesFinished": 1,
          "stepNumber": 10,
          "timeEnd": "15:50",
          "timeStart": "16:00",
          "workCenter": 4000
        }
      ],
      "employeeCode": 963,
      "ticketDate": "2026-09-24"
    }
    response = await client.post("/time-tickets", data=payload)

