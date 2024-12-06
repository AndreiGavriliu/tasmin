from fastapi import FastAPI, Form, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from models import Devices, Base # Import your Device model
from database import SessionLocal  # Assuming you have a `database.py` for session management
from modules import scan
import logging
import sys

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "": {  # Root logger
            "level": "INFO",
            "handlers": ["console"],
        },
    },
}

# FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Logging
logging.config.dictConfig(logging_config)

# SQLAlchemy
engine = create_engine("sqlite:///./db/app.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

APP_USERNAME = "admin"
APP_PASSWORD = "P3ntdr1g0n7wiuCHle"
# APP_USERNAME = os.getenv("APP_USERNAME", "default_user")
# APP_PASSWORD = os.getenv("APP_PASSWORD", "default_pass")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

########################################
# AUTH
########################################

@app.get("/debug-static")
async def debug_static():
    import os
    return {"static_files": os.listdir("static")}

def is_authenticated(request: Request):
    """Checks if a user is authenticated."""
    if "authenticated" in request.cookies and request.cookies["authenticated"] == "true":
        return request.cookies.get("username")
    # Raise HTTPException with status code 303 (See Other) and a Location header
    raise HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        detail="Redirecting to login",
        headers={"Location": f"/login?next={request.url.path}"}
    )


@app.get("/logout")
async def logout():
    """Log the user out and clear cookies."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("authenticated")
    response.delete_cookie("username")
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, next: str = "/"):
    """Render the login form."""
    return templates.TemplateResponse("auth/login.html", {"request": request, "next": next})

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/")
):
    """Handle login logic."""
    if username == APP_USERNAME and password == APP_PASSWORD:
        response = RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="authenticated", value="true")
        response.set_cookie(key="username", value=username)
        return response

    logging.error("Invalid username or password")
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "next": next, "error": "Invalid username or password"}
    )


########################################
# ROOT
########################################

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, username: str = Depends(is_authenticated), db: Session = Depends(get_db)):
    """Protected route: Render the dashboard."""
    devices = db.query(Devices).all()
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "username": username, "devices": devices}
    )

########################################
# SETTINGS
########################################

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return templates.TemplateResponse("settings/settings.html", {"request": request})

########################################
# DEVICES
########################################

@app.get("/devices", response_class=HTMLResponse)
async def get_devices(request: Request, db: Session = Depends(get_db)):
    logging.info("Retreiving all devices from DB")
    """Retrieve and display all devices from the database."""
    devices = db.query(Devices).all()
    return templates.TemplateResponse(
        "devices/devices.html", {"request": request, "devices": devices}
    )


@app.get("/devices/{unique_id}", response_class=HTMLResponse)
async def get_devices_view(request: Request, unique_id: str, db: Session = Depends(get_db)):
    """Retrieve and display all devices from the database."""
    device = Devices.get_device_by_unique_id(db, unique_id)

    if not device:
        # Return a 404 error if the device is not found
        return templates.TemplateResponse(
            "error-404.html", 
            {"request": request, "message": "Device not found"}, 
            status_code=404
        )

    # Render the device details page
    return templates.TemplateResponse(
        "devices/view.html", 
        {"request": request, "device": device}
    )

@app.get("/devices/{unique_id}/edit", response_class=HTMLResponse)
async def get_devices_edit(request: Request, unique_id: str, db: Session = Depends(get_db)):
    """Retrieve and display all devices from the database."""
    device = Devices.get_device_by_unique_id(db, unique_id)

    if not device:
        # Return a 404 error if the device is not found
        return templates.TemplateResponse(
            "error-404.html", 
            {"request": request, "message": "Device not found"}, 
            status_code=404
        )

    # Render the device details page
    return templates.TemplateResponse(
        "devices/edit.html", 
        {"request": request, "device": device}
    )

########################################
# SCAN
########################################

@app.get("/scan", response_class=HTMLResponse)
async def get_scan(request: Request):
    """
    Handle form submission for network scanning.
    """
    return templates.TemplateResponse(
        "scan/scan.html", {"request": request}
    )

@app.post("/scan", response_class=HTMLResponse)
async def post_scan(request: Request, ip_start: str = Form(...), ip_end: str = Form(...), db: Session = Depends(get_db)):
    """
    Handle form submission for network scanning.
    """
    logging.info("Send to scanner: '%s'-'%s'", ip_start, ip_end)

    result = scan.discover(ip_start=ip_start, ip_end=ip_end, db=db)

    return templates.TemplateResponse(
        "scan/scan.html", {"request": request, "result": result}
    )
