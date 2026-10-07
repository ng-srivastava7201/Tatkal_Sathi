import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# & "..\env\Scripts\python.exe" -m uvicorn main:app --reload --port 8000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

AIML_DIR = os.path.join(PROJECT_ROOT, "aiml")
if AIML_DIR not in sys.path:
    sys.path.insert(0, AIML_DIR)

AUTOMATION_DIR = os.path.join(PROJECT_ROOT, "Automation and Scheduling")
if AUTOMATION_DIR not in sys.path:
    sys.path.insert(0, AUTOMATION_DIR)

from mock_irctc import search_trains, book_ticket, MASTER_TRAINS
from database import init_db, register_user, authenticate_user, get_all_users

try:
    from ai_interface import (
        predict_seat_probability,
        rank_alternative_routes,
        pick_best_fallback,
    )
except Exception as e:
    print(f"[main.py] Warning loading AI interface: {e}")
    predict_seat_probability = None
    rank_alternative_routes = None
    pick_best_fallback = None
try:
    from scheduler import (
        start_scheduler,
        stop_scheduler,
        get_scheduler_status,
        trigger_immediate_booking,
        update_schedule,
        get_simulation_history,
    )
except Exception as e:
    print(f"[main.py] Warning loading Automation Scheduler: {e}")
    start_scheduler = lambda: False
    stop_scheduler = lambda: False
    get_scheduler_status = lambda: {"scheduler_running": False, "error": str(e)}
    trigger_immediate_booking = lambda x=None: {"status": "error", "message": str(e)}
    update_schedule = lambda h, m: {"error": str(e)}
    get_simulation_history = lambda: []


app = FastAPI(
    title="Tatkal Sathi Backend API",
    description="Backend services for Tatkal automation, database auth, multi-route train booking, and AI predictions.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize SQLite database and start APScheduler background engine."""
    print("\n[Tatkal Sathi] Starting Backend Services...")
    try:
        init_db()
        print("[Database] SQLite Database initialized successfully.")
    except Exception as e:
        print(f"[Database] Error initializing database: {e}")

    try:
        start_scheduler()
        print("[Automation] Background APScheduler engine started.")
    except Exception as e:
        print(f"[Automation] Error starting scheduler: {e}")


@app.on_event("shutdown")
def on_shutdown():
    """Gracefully shutdown background tasks."""
    try:
        stop_scheduler()
        print("[Automation] APScheduler stopped.")
    except Exception as e:
        print(f"[Automation] Error stopping scheduler: {e}")


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = ""
    phone: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str  
    password: str


class SearchRequest(BaseModel):
    source: str
    destination: str
    date: str
    class_name: Optional[str] = "3A"
    quota: Optional[str] = "Tatkal"


class BookingRequest(BaseModel):
    train_id: str
    travel_date: str
    class_name: str
    quota: str
    seats_requested: int = 1
    passenger_info: Optional[Dict[str, Any]] = None


class ScheduleUpdateRequest(BaseModel):
    hour: int = 10
    minute: int = 0


class SimulationTriggerRequest(BaseModel):
    train_name: Optional[str] = "Bhopal Shatabdi (12002)"
    train_id: Optional[str] = "12002"
    source: Optional[str] = "Bhopal"
    destination: Optional[str] = "New Delhi"
    class_name: Optional[str] = "3A"
    quota: Optional[str] = "Tatkal"
    seats: Optional[int] = 1


class PredictRequest(BaseModel):
    route: str
    class_name: str
    quota: str
    date: str
    seats_requested: int = 1


class FallbackRequest(PredictRequest):
    preferences: dict = {}



@app.get("/")
def home():
    return {
        "project": "Tatkal Sathi",
        "team": "Team 35 - Tatkal Automation Booking and Ticket Tracking",
        "status": "Online",
        "database": "SQLite (SQLAlchemy)",
        "automation_scheduler": "APScheduler (10:00 AM Auto-Trigger Connected)",
        "ai_engine": "RandomForest / XGBoost Seat Probability"
    }


@app.get("/hello")
def hello():
    return {"message": "Hello, welcome to the Tatkal Train booking backend!"}



@app.post("/api/auth/signup")
def signup(req: SignupRequest):
    """Register a new user account into SQLite database."""
    if not req.username or not req.email or not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username, email, and password are required."
        )

    if len(req.password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 4 characters long."
        )

    success, result = register_user(
        username=req.username,
        email=req.email,
        password=req.password,
        full_name=req.full_name or "",
        phone=req.phone or ""
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )

    return {
        "status": "success",
        "message": "Account created successfully! You can now log in.",
        "user": result
    }


@app.post("/api/auth/login")
def login(req: LoginRequest):
    """Authenticate existing user against SQLite database credentials."""
    if not req.username or not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email and password are required."
        )

    success, result = authenticate_user(
        identifier=req.username,
        password=req.password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result
        )

    return {
        "status": "success",
        "message": "Login successful. Welcome back!",
        "user": result
    }


@app.get("/api/auth/users")
def list_users():
    """Retrieve list of registered users (for demonstration/admin)."""
    return {
        "status": "success",
        "users": get_all_users()
    }


@app.get("/mock-irctc/stations")
def get_supported_stations():
    """Return all supported origin & destination stations."""
    stations = set()
    for t in MASTER_TRAINS:
        stations.add(t["source"])
        stations.add(t["destination"])
    return {
        "status": "success",
        "stations": sorted(list(stations))
    }


@app.post("/mock-irctc/search")
def search(request: SearchRequest):
    """Search trains across diverse routes with dynamic availability & AI probabilities."""
    results = search_trains(
        source=request.source,
        destination=request.destination,
        date=request.date,
        class_name=request.class_name or "3A",
        quota=request.quota or "Tatkal"
    )
    return results


@app.post("/mock-irctc/book")
def book(request: BookingRequest):
    """Execute Tatkal/General booking, update inventory, and persist ticket in database."""
    return book_ticket(
        train_id=request.train_id,
        travel_date=request.travel_date,
        class_name=request.class_name,
        quota=request.quota,
        seats_requested=request.seats_requested,
        passenger_info=request.passenger_info
    )



@app.get("/api/automation/status")
def automation_status():
    """Check live status of the APScheduler and daily 10:00 AM auto-trigger."""
    status_info = get_scheduler_status()
    return {
        "status": "success",
        "scheduler": status_info
    }


@app.post("/api/automation/trigger")
def automation_trigger_test(req: Optional[SimulationTriggerRequest] = None):
    """
    Manually trigger the 10:00 AM Tatkal automated booking simulation immediately.
    Demonstrates instant session holding, automated payment dispatch,
    and fallback route auto-switching.
    """
    details = req.dict() if req else {}
    details["trigger_type"] = "Manual API Trigger"
    simulation_result = trigger_immediate_booking(details)
    return {
        "status": "success",
        "message": "Tatkal automation booking sequence executed.",
        "result": simulation_result
    }


@app.post("/api/automation/schedule")
def automation_update_schedule(req: ScheduleUpdateRequest):
    """Update scheduled auto-trigger time (default 10:00 AM for AC, 11:00 AM for Sleeper)."""
    updated = update_schedule(hour=req.hour, minute=req.minute)
    return {
        "status": "success",
        "message": f"Daily auto-trigger updated to {req.hour:02d}:{req.minute:02d}",
        "scheduler": updated
    }


@app.get("/api/automation/history")
def automation_history():
    """Retrieve history of automated Tatkal simulation triggers."""
    return {
        "status": "success",
        "history": get_simulation_history()
    }



@app.post("/api/predict")
def predict(request: PredictRequest):
    if not predict_seat_probability:
        raise HTTPException(status_code=500, detail="AI engine not initialized.")
    return predict_seat_probability(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
    )


@app.post("/api/alternatives")
def alternatives(request: PredictRequest):
    if not rank_alternative_routes:
        raise HTTPException(status_code=500, detail="AI engine not initialized.")
    return rank_alternative_routes(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
    )


@app.post("/api/fallback")
def fallback(request: FallbackRequest):
    if not pick_best_fallback:
        raise HTTPException(status_code=500, detail="AI engine not initialized.")
    return pick_best_fallback(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
        preferences=request.preferences,
    )
