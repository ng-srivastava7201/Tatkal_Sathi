import requests
from automation_config import BASE_URL

REQUEST_TIMEOUT = 10  # seconds per HTTP call — keeps 90s cap meaningful

def predict_probability(user_request):
    payload = {
        "route": user_request["route"],
        "class_name": user_request["class_name"],
        "quota": user_request["quota"],
        "date": user_request["travel_date"],
        "seats_requested": user_request["seats_requested"],
    }
    r = requests.post(f"{BASE_URL}/api/predict", json=payload, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def attempt_book(train_id, user_request):
    payload = {
        "train_id": train_id,
        "travel_date": user_request["travel_date"],
        "class_name": user_request["class_name"],
        "quota": user_request["quota"],
        "seats_requested": user_request["seats_requested"],
    }
    r = requests.post(f"{BASE_URL}/mock-irctc/book", json=payload, timeout=REQUEST_TIMEOUT)
    if r.status_code == 404:
        return {"status": "failed", "reason": "train/date/class/quota combo not found"}
    r.raise_for_status()
    return r.json()


def get_best_fallback(user_request):
    payload = {
        "route": user_request["route"],
        "class_name": user_request["class_name"],
        "quota": user_request["quota"],
        "date": user_request["travel_date"],
        "seats_requested": user_request["seats_requested"],
        "preferences": {},
    }
    r = requests.post(f"{BASE_URL}/api/fallback", json=payload, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json().get("best_fallback")


def resolve_train_id(route, source, destination, travel_date):
    r = requests.post(f"{BASE_URL}/mock-irctc/search", json={
        "source": source, "destination": destination, "date": travel_date,
    }, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    trains = r.json().get("trains", [])
    for t in trains:
        if t.get("route") == route:
            return t.get("train_id")
    return None