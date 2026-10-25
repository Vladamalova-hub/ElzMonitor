from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import APP_LOGIN, APP_PASSWORD, APP_TITLE
from app.db import latest_news

app = FastAPI(title=APP_TITLE)
app.add_middleware(SessionMiddleware, secret_key="kamchat-monitor-secret")

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def require_auth(request: Request) -> bool:
    return bool(request.session.get("authorized"))


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": APP_TITLE})


@app.post("/login")
def do_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == APP_LOGIN and password == APP_PASSWORD:
        request.session["authorized"] = True
        return RedirectResponse("/", status_code=303)
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if not require_auth(request):
        return RedirectResponse("/login", status_code=303)
    items = latest_news(200)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": APP_TITLE,
            "items": items,
            "count": len(items),
        },
    )
