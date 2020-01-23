import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import httpx
from urllib.parse import urlencode
import os
from pprint import pformat

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

OAUTH_SERVER_BASE_PATH = os.environ.get(
    "OAUTH_SERVER_BASE_PATH", "https://emea-demo8-test.apigee.net/oauth2/v1/"
)
REDIRECT_URI = os.environ.get(
    "REDIRECT_URI", "https://acme-health.herokuapp.com/callback"
)
OAUTH_SCOPES = os.environ.get("OAUTH_SCOPES", "read")

CLIENT_ID = os.environ["CLIENT_ID"]  # App API Key in Apigee
CLIENT_SECRET = os.environ["CLIENT_SECRET"]  # App API Secret in Apigee


@app.get("/")
def read_root(request: Request):
    query_params = {
        "client_id": CLIENT_ID,
        "scope": OAUTH_SCOPES,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "state": "1234567890",
    }
    signin_url = OAUTH_SERVER_BASE_PATH + "authorize?" + urlencode(query_params)

    return templates.TemplateResponse(
        "login.html", {"request": request, "signin_url": signin_url}
    )


@app.get("/callback")
def do_callback(request: Request, code: str, state: str, scope: str):
    formdata = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = httpx.post(
        OAUTH_SERVER_BASE_PATH + "token",
        data=formdata,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    return templates.TemplateResponse(
        "callback.html",
        {
            "request": request,
            "response": r,
            "formdata": formdata,
            "pretty_response": pformat(r.json()),
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
