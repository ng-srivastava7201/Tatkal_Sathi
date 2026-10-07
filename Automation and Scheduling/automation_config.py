BASE_URL = "http://127.0.0.1:8000"

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 7
TIME_CAP_SECONDS = 90

USER_REQUEST = {
    "train_id": "T002",
    "route": "Mumbai-Delhi",
    "travel_date": "2026-12-25",
    "class_name": "SL",
    "quota": "Tatkal",
    "seats_requested": 1,
}