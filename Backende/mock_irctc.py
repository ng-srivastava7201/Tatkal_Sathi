import os
import sys
import random
import uuid
from datetime import datetime
import pandas as pd
from fastapi import HTTPException

AIML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aiml"))
if AIML_DIR not in sys.path:
    sys.path.append(AIML_DIR)

try:
    from ai_interface import predict_seat_probability as ai_predict
except Exception:
    ai_predict = None

try:
    from database import record_booking
except ImportError:
    record_booking = None
MASTER_TRAINS = [
    {
        "train_id": "12952",
        "train_number": "12952",
        "train_name": "New Delhi - Mumbai Tejas Rajdhani",
        "source": "New Delhi",
        "destination": "Mumbai",
        "departure_time": "04:55 PM",
        "arrival_time": "08:35 AM",
        "duration": "15h 40m",
        "distance_km": 1384,
        "running_days": ["Daily"],
        "classes": ["3A", "2A", "1A"],
        "fares": {"3A": 1650, "2A": 2450, "1A": 4150},
        "popularity": 0.95
    },
    {
        "train_id": "12951",
        "train_number": "12951",
        "train_name": "Mumbai - New Delhi Tejas Rajdhani",
        "source": "Mumbai",
        "destination": "New Delhi",
        "departure_time": "05:00 PM",
        "arrival_time": "08:32 AM",
        "duration": "15h 32m",
        "distance_km": 1384,
        "running_days": ["Daily"],
        "classes": ["3A", "2A", "1A"],
        "fares": {"3A": 1650, "2A": 2450, "1A": 4150},
        "popularity": 0.95
    },
    {
        "train_id": "12954",
        "train_number": "12954",
        "train_name": "August Kranti Rajdhani Express",
        "source": "New Delhi",
        "destination": "Mumbai",
        "departure_time": "05:15 PM",
        "arrival_time": "10:05 AM",
        "duration": "16h 50m",
        "distance_km": 1377,
        "running_days": ["Daily"],
        "classes": ["3A", "2A", "1A"],
        "fares": {"3A": 1580, "2A": 2350, "1A": 3950},
        "popularity": 0.92
    },
    {
        "train_id": "12926",
        "train_number": "12926",
        "train_name": "Paschim Superfast Express",
        "source": "New Delhi",
        "destination": "Mumbai",
        "departure_time": "04:30 PM",
        "arrival_time": "02:45 PM",
        "duration": "22h 15m",
        "distance_km": 1384,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A"],
        "fares": {"SL": 580, "3A": 1420, "2A": 2100},
        "popularity": 0.82
    },
    {
        "train_id": "12925",
        "train_number": "12925",
        "train_name": "Paschim Superfast Express",
        "source": "Mumbai",
        "destination": "New Delhi",
        "departure_time": "11:25 AM",
        "arrival_time": "10:40 AM",
        "duration": "23h 15m",
        "distance_km": 1384,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A"],
        "fares": {"SL": 580, "3A": 1420, "2A": 2100},
        "popularity": 0.82
    },

    {
        "train_id": "12002",
        "train_number": "12002",
        "train_name": "New Delhi - Bhopal Shatabdi Express",
        "source": "New Delhi",
        "destination": "Bhopal",
        "departure_time": "06:00 AM",
        "arrival_time": "02:25 PM",
        "duration": "8h 25m",
        "distance_km": 707,
        "running_days": ["Daily"],
        "classes": ["CC", "EC", "3A"],
        "fares": {"CC": 1240, "EC": 2120, "3A": 1150},
        "popularity": 0.91
    },
    {
        "train_id": "12001",
        "train_number": "12001",
        "train_name": "Bhopal - New Delhi Shatabdi Express",
        "source": "Bhopal",
        "destination": "New Delhi",
        "departure_time": "03:10 PM",
        "arrival_time": "11:50 PM",
        "duration": "8h 40m",
        "distance_km": 707,
        "running_days": ["Daily"],
        "classes": ["CC", "EC", "3A"],
        "fares": {"CC": 1240, "EC": 2120, "3A": 1150},
        "popularity": 0.91
    },
    {
        "train_id": "20172",
        "train_number": "20172",
        "train_name": "Vande Bharat Express (Rani Kamlapati - Hazrat Nizamuddin)",
        "source": "Bhopal",
        "destination": "New Delhi",
        "departure_time": "05:40 AM",
        "arrival_time": "01:10 PM",
        "duration": "7h 30m",
        "distance_km": 708,
        "running_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 1450, "EC": 2680},
        "popularity": 0.94
    },
    {
        "train_id": "20171",
        "train_number": "20171",
        "train_name": "Vande Bharat Express (Hazrat Nizamuddin - Rani Kamlapati)",
        "source": "New Delhi",
        "destination": "Bhopal",
        "departure_time": "02:40 PM",
        "arrival_time": "10:10 PM",
        "duration": "7h 30m",
        "distance_km": 708,
        "running_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 1450, "EC": 2680},
        "popularity": 0.94
    },
    {
        "train_id": "12156",
        "train_number": "12156",
        "train_name": "Shaan-e-Bhopal SF Express",
        "source": "New Delhi",
        "destination": "Bhopal",
        "departure_time": "08:55 PM",
        "arrival_time": "07:05 AM",
        "duration": "10h 10m",
        "distance_km": 701,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 420, "3A": 1050, "2A": 1510, "1A": 2550},
        "popularity": 0.88
    },
    {
        "train_id": "12155",
        "train_number": "12155",
        "train_name": "Shaan-e-Bhopal SF Express",
        "source": "Bhopal",
        "destination": "New Delhi",
        "departure_time": "10:40 PM",
        "arrival_time": "07:50 AM",
        "duration": "9h 10m",
        "distance_km": 701,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 420, "3A": 1050, "2A": 1510, "1A": 2550},
        "popularity": 0.88
    },

    {
        "train_id": "12138",
        "train_number": "12138",
        "train_name": "Punjab Mail (Via Bhopal)",
        "source": "Bhopal",
        "destination": "Mumbai",
        "departure_time": "04:50 PM",
        "arrival_time": "07:35 AM",
        "duration": "14h 45m",
        "distance_km": 837,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 460, "3A": 1180, "2A": 1690, "1A": 2850},
        "popularity": 0.85
    },
    {
        "train_id": "12137",
        "train_number": "12137",
        "train_name": "Punjab Mail (Mumbai to Bhopal)",
        "source": "Mumbai",
        "destination": "Bhopal",
        "departure_time": "07:35 PM",
        "arrival_time": "09:45 AM",
        "duration": "14h 10m",
        "distance_km": 837,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 460, "3A": 1180, "2A": 1690, "1A": 2850},
        "popularity": 0.85
    },
    {
        "train_id": "12533",
        "train_number": "12533",
        "train_name": "Pushpak Express (Bhopal to Mumbai)",
        "source": "Bhopal",
        "destination": "Mumbai",
        "departure_time": "07:15 AM",
        "arrival_time": "08:15 PM",
        "duration": "13h 00m",
        "distance_km": 837,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A"],
        "fares": {"SL": 470, "3A": 1210, "2A": 1720},
        "popularity": 0.89
    },

    {
        "train_id": "12724",
        "train_number": "12724",
        "train_name": "Telangana Superfast Express",
        "source": "New Delhi",
        "destination": "Hyderabad",
        "departure_time": "04:00 PM",
        "arrival_time": "05:10 PM",
        "duration": "25h 10m",
        "distance_km": 1672,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 690, "3A": 1790, "2A": 2620, "1A": 4480},
        "popularity": 0.86
    },
    {
        "train_id": "12723",
        "train_number": "12723",
        "train_name": "Telangana Superfast Express",
        "source": "Hyderabad",
        "destination": "New Delhi",
        "departure_time": "06:00 AM",
        "arrival_time": "07:40 AM",
        "duration": "25h 40m",
        "distance_km": 1672,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 690, "3A": 1790, "2A": 2620, "1A": 4480},
        "popularity": 0.86
    },
    {
        "train_id": "12722",
        "train_number": "12722",
        "train_name": "Dakshin Superfast Express",
        "source": "New Delhi",
        "destination": "Hyderabad",
        "departure_time": "10:50 PM",
        "arrival_time": "02:50 AM",
        "duration": "28h 00m",
        "distance_km": 1675,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A"],
        "fares": {"SL": 670, "3A": 1750, "2A": 2550},
        "popularity": 0.78
    },

    {
        "train_id": "12302",
        "train_number": "12302",
        "train_name": "Howrah Rajdhani Express",
        "source": "New Delhi",
        "destination": "Kolkata",
        "departure_time": "04:55 PM",
        "arrival_time": "09:55 AM",
        "duration": "17h 00m",
        "distance_km": 1450,
        "running_days": ["Daily"],
        "classes": ["3A", "2A", "1A"],
        "fares": {"3A": 1720, "2A": 2550, "1A": 4350},
        "popularity": 0.93
    },
    {
        "train_id": "12301",
        "train_number": "12301",
        "train_name": "Howrah Rajdhani Express",
        "source": "Kolkata",
        "destination": "New Delhi",
        "departure_time": "04:50 PM",
        "arrival_time": "10:05 AM",
        "duration": "17h 15m",
        "distance_km": 1450,
        "running_days": ["Daily"],
        "classes": ["3A", "2A", "1A"],
        "fares": {"3A": 1720, "2A": 2550, "1A": 4350},
        "popularity": 0.93
    },
    {
        "train_id": "12382",
        "train_number": "12382",
        "train_name": "Poorva Express",
        "source": "New Delhi",
        "destination": "Kolkata",
        "departure_time": "05:40 PM",
        "arrival_time": "05:00 PM",
        "duration": "23h 20m",
        "distance_km": 1530,
        "running_days": ["Monday", "Tuesday", "Friday"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 610, "3A": 1590, "2A": 2320, "1A": 3950},
        "popularity": 0.81
    },

    {
        "train_id": "12628",
        "train_number": "12628",
        "train_name": "Karnataka Express",
        "source": "New Delhi",
        "destination": "Bengaluru",
        "departure_time": "08:20 PM",
        "arrival_time": "12:00 PM",
        "duration": "39h 40m",
        "distance_km": 2408,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 860, "3A": 2260, "2A": 3340, "1A": 5680},
        "popularity": 0.84
    },
    {
        "train_id": "12627",
        "train_number": "12627",
        "train_name": "Karnataka Express",
        "source": "Bengaluru",
        "destination": "New Delhi",
        "departure_time": "07:20 PM",
        "arrival_time": "10:30 AM",
        "duration": "39h 10m",
        "distance_km": 2408,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 860, "3A": 2260, "2A": 3340, "1A": 5680},
        "popularity": 0.84
    },

    {
        "train_id": "12007",
        "train_number": "12007",
        "train_name": "Chennai - Mysuru Shatabdi Express",
        "source": "Chennai",
        "destination": "Bengaluru",
        "departure_time": "06:00 AM",
        "arrival_time": "10:45 AM",
        "duration": "4h 45m",
        "distance_km": 360,
        "running_days": ["Daily"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 780, "EC": 1420},
        "popularity": 0.89
    },
    {
        "train_id": "12008",
        "train_number": "12008",
        "train_name": "Bengaluru - Chennai Shatabdi Express",
        "source": "Bengaluru",
        "destination": "Chennai",
        "departure_time": "04:25 PM",
        "arrival_time": "09:30 PM",
        "duration": "5h 05m",
        "distance_km": 360,
        "running_days": ["Daily"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 780, "EC": 1420},
        "popularity": 0.89
    },
    {
        "train_id": "20608",
        "train_number": "20608",
        "train_name": "Mysuru - Chennai Vande Bharat",
        "source": "Bengaluru",
        "destination": "Chennai",
        "departure_time": "02:50 PM",
        "arrival_time": "07:20 PM",
        "duration": "4h 30m",
        "distance_km": 360,
        "running_days": ["Monday", "Tuesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 995, "EC": 1885},
        "popularity": 0.96
    },

    {
        "train_id": "12786",
        "train_number": "12786",
        "train_name": "Kacheguda Superfast Express",
        "source": "Bengaluru",
        "destination": "Hyderabad",
        "departure_time": "06:20 PM",
        "arrival_time": "05:40 AM",
        "duration": "11h 20m",
        "distance_km": 618,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 390, "3A": 1020, "2A": 1460, "1A": 2420},
        "popularity": 0.83
    },
    {
        "train_id": "12785",
        "train_number": "12785",
        "train_name": "Bangalore Superfast Express",
        "source": "Hyderabad",
        "destination": "Bengaluru",
        "departure_time": "07:05 PM",
        "arrival_time": "06:25 AM",
        "duration": "11h 20m",
        "distance_km": 618,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A", "1A"],
        "fares": {"SL": 390, "3A": 1020, "2A": 1460, "1A": 2420},
        "popularity": 0.83
    },
    {
        "train_id": "20704",
        "train_number": "20704",
        "train_name": "Vande Bharat Express (Kacheguda - Yesvantpur)",
        "source": "Hyderabad",
        "destination": "Bengaluru",
        "departure_time": "05:30 AM",
        "arrival_time": "02:00 PM",
        "duration": "8h 30m",
        "distance_km": 618,
        "running_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 1540, "EC": 2865},
        "popularity": 0.95
    },

    {
        "train_id": "20901",
        "train_number": "20901",
        "train_name": "Vande Bharat Express (Mumbai - Gandhinagar)",
        "source": "Mumbai",
        "destination": "Ahmedabad",
        "departure_time": "06:10 AM",
        "arrival_time": "11:25 AM",
        "duration": "5h 15m",
        "distance_km": 491,
        "running_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 1280, "EC": 2450},
        "popularity": 0.95
    },
    {
        "train_id": "12933",
        "train_number": "12933",
        "train_name": "Karnavati Superfast Express",
        "source": "Mumbai",
        "destination": "Ahmedabad",
        "departure_time": "01:40 PM",
        "arrival_time": "09:05 PM",
        "duration": "7h 25m",
        "distance_km": 491,
        "running_days": ["Daily"],
        "classes": ["CC", "2S"],
        "fares": {"CC": 660, "2S": 195},
        "popularity": 0.80
    },

    {
        "train_id": "12015",
        "train_number": "12015",
        "train_name": "Ajmer Shatabdi Express",
        "source": "New Delhi",
        "destination": "Jaipur",
        "departure_time": "06:10 AM",
        "arrival_time": "10:40 AM",
        "duration": "4h 30m",
        "distance_km": 308,
        "running_days": ["Daily"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 720, "EC": 1360},
        "popularity": 0.90
    },
    {
        "train_id": "12986",
        "train_number": "12986",
        "train_name": "Delhi Sarai Rohilla - Jaipur Double Decker",
        "source": "New Delhi",
        "destination": "Jaipur",
        "departure_time": "05:35 PM",
        "arrival_time": "10:05 PM",
        "duration": "4h 30m",
        "distance_km": 303,
        "running_days": ["Daily"],
        "classes": ["CC"],
        "fares": {"CC": 540},
        "popularity": 0.85
    },

    {
        "train_id": "12004",
        "train_number": "12004",
        "train_name": "Lucknow Swarna Shatabdi Express",
        "source": "New Delhi",
        "destination": "Lucknow",
        "departure_time": "06:10 AM",
        "arrival_time": "12:40 PM",
        "duration": "6h 30m",
        "distance_km": 512,
        "running_days": ["Daily"],
        "classes": ["CC", "EC"],
        "fares": {"CC": 1165, "EC": 1890},
        "popularity": 0.92
    },
    {
        "train_id": "12420",
        "train_number": "12420",
        "train_name": "Gomti Superfast Express",
        "source": "New Delhi",
        "destination": "Lucknow",
        "departure_time": "12:20 PM",
        "arrival_time": "09:30 PM",
        "duration": "9h 10m",
        "distance_km": 512,
        "running_days": ["Daily"],
        "classes": ["2S", "CC", "2A"],
        "fares": {"2S": 210, "CC": 720, "2A": 1390},
        "popularity": 0.77
    },

    {
        "train_id": "12263",
        "train_number": "12263",
        "train_name": "Hazrat Nizamuddin AC Duronto Express",
        "source": "Pune",
        "destination": "New Delhi",
        "departure_time": "11:10 AM",
        "arrival_time": "06:55 AM",
        "duration": "19h 45m",
        "distance_km": 1515,
        "running_days": ["Tuesday", "Friday"],
        "classes": ["3A", "2A", "1A"],
        "fares": {"3A": 1920, "2A": 2840, "1A": 4820},
        "popularity": 0.88
    },
    {
        "train_id": "12779",
        "train_number": "12779",
        "train_name": "Goa Superfast Express (Via Pune)",
        "source": "Pune",
        "destination": "New Delhi",
        "departure_time": "04:30 AM",
        "arrival_time": "06:25 AM",
        "duration": "25h 55m",
        "distance_km": 1515,
        "running_days": ["Daily"],
        "classes": ["SL", "3A", "2A"],
        "fares": {"SL": 630, "3A": 1650, "2A": 2410},
        "popularity": 0.79
    },

    {
        "train_id": "19303",
        "train_number": "19303",
        "train_name": "Indore - Bhopal Intercity Express",
        "source": "Indore",
        "destination": "Bhopal",
        "departure_time": "06:00 AM",
        "arrival_time": "10:00 AM",
        "duration": "4h 00m",
        "distance_km": 217,
        "running_days": ["Daily"],
        "classes": ["2S", "CC"],
        "fares": {"2S": 115, "CC": 420},
        "popularity": 0.85
    },
    {
        "train_id": "19304",
        "train_number": "19304",
        "train_name": "Bhopal - Indore Intercity Express",
        "source": "Bhopal",
        "destination": "Indore",
        "departure_time": "05:30 PM",
        "arrival_time": "09:30 PM",
        "duration": "4h 00m",
        "distance_km": 217,
        "running_days": ["Daily"],
        "classes": ["2S", "CC"],
        "fares": {"2S": 115, "CC": 420},
        "popularity": 0.85
    },
]

seat_inventory = {}


def _get_inventory_key(train_id: str, date: str, class_name: str, quota: str) -> tuple:
    return (str(train_id), str(date), str(class_name).upper(), str(quota).capitalize())


def _initialize_seat_count(train: dict, class_name: str, quota: str) -> int:
    """Initialize realistic seat inventory count for train/class/quota."""
    quota_clean = quota.capitalize()
    class_clean = class_name.upper()

    if quota_clean == "Tatkal":
        if class_clean in ("1A", "EC"):
            return random.randint(2, 6)
        elif class_clean in ("2A",):
            return random.randint(6, 16)
        elif class_clean in ("3A", "CC"):
            return random.randint(14, 34)
        else:  # SL, 2S
            return random.randint(22, 52)
    else:  # General
        if class_clean in ("1A", "EC"):
            return random.randint(10, 24)
        elif class_clean in ("2A",):
            return random.randint(24, 46)
        elif class_clean in ("3A", "CC"):
            return random.randint(48, 96)
        else:
            return random.randint(80, 180)


def calculate_ai_seat_probability(route: str, train_class: str, quota: str, date: str, seats: int = 1) -> dict:
    """Compute AI Tatkal probability using the trained ML model or dynamic formulation."""
    try:
        if ai_predict:
            res = ai_predict(route, train_class, quota, date, seats_requested=seats)
            prob = float(res.get("success_probability", 0.75))
            rec = res.get("recommendation", "high")
            return {"probability": round(prob * 100), "label": rec.capitalize()}
    except Exception as e:
        pass

    p = 0.85
    if quota.lower() == "tatkal":
        p -= 0.15
    if train_class.upper() in ("SL", "2S"):
        p -= 0.10
    elif train_class.upper() in ("1A", "EC"):
        p += 0.08

    try:
        day = pd.to_datetime(date).day_name()
        if day in ("Saturday", "Sunday"):
            p -= 0.08
    except Exception:
        pass

    p = max(0.18, min(0.96, p + random.uniform(-0.04, 0.04)))
    label = "High" if p >= 0.75 else ("Medium" if p >= 0.45 else "Low")
    return {"probability": round(p * 100), "label": label}


def search_trains(source: str, destination: str, date: str, class_name: str = "3A", quota: str = "Tatkal"):
    """
    Search direct trains and suggest alternate route trains if needed.
    """
    src_norm = source.strip().lower()
    dst_norm = destination.strip().lower()

    try:
        requested_day = pd.to_datetime(date).strftime("%A")
    except Exception:
        requested_day = "Monday"

    matched_direct = []
    alternatives = []

    for t in MASTER_TRAINS:
        t_src = t["source"].strip().lower()
        t_dst = t["destination"].strip().lower()

        runs_today = "Daily" in t["running_days"] or requested_day in t["running_days"]
        if not runs_today:
            continue

        is_direct = (t_src == src_norm and t_dst == dst_norm) or (
            src_norm in t_src and dst_norm in t_dst
        )

        selected_class = class_name if class_name in t["classes"] else t["classes"][0]
        inv_key = _get_inventory_key(t["train_id"], date, selected_class, quota)
        if inv_key not in seat_inventory:
            seat_inventory[inv_key] = _initialize_seat_count(t, selected_class, quota)

        available_seats = seat_inventory[inv_key]
        fare = t["fares"].get(selected_class, t["fares"].get(list(t["fares"].keys())[0], 1200))

        route_str = f"{t['source']}-{t['destination']}"
        ai_stat = calculate_ai_seat_probability(route_str, selected_class, quota, date, 1)

        train_item = {
            "train_id": t["train_id"],
            "train_number": t["train_number"],
            "train_name": t["train_name"],
            "source": t["source"],
            "destination": t["destination"],
            "departure_time": t["departure_time"],
            "arrival_time": t["arrival_time"],
            "duration": t["duration"],
            "distance_km": t["distance_km"],
            "travel_date": date,
            "running_days": ", ".join(t["running_days"]),
            "class": selected_class,
            "quota": quota,
            "fare": fare,
            "seats_available": available_seats,
            "seat_probability": f"{ai_stat['probability']}%",
            "probability_value": ai_stat["probability"],
            "probability_label": ai_stat["label"],
            "is_direct": is_direct
        }

        if is_direct:
            matched_direct.append(train_item)
        elif (t_src == src_norm or t_dst == dst_norm):
            alternatives.append(train_item)

    matched_direct.sort(key=lambda x: (x["probability_value"], x["seats_available"]), reverse=True)
    alternatives.sort(key=lambda x: (x["probability_value"], x["seats_available"]), reverse=True)

    return {
        "status": "success",
        "count": len(matched_direct),
        "source": source,
        "destination": destination,
        "date": date,
        "trains": matched_direct,
        "alternatives": alternatives[:3]
    }


def book_ticket(train_id: str, travel_date: str, class_name: str, quota: str,
                seats_requested: int, passenger_info: dict = None):
    """
    Execute booking, decrement inventory, and record in SQLite database.
    """
    if seats_requested <= 0:
        raise HTTPException(status_code=400, detail="Seats requested must be greater than zero")

    key = _get_inventory_key(train_id, travel_date, class_name, quota)

    if key not in seat_inventory:
        # Initialize if not searched first
        seat_inventory[key] = random.randint(12, 35)

    available = seat_inventory[key]

    if available < seats_requested:
        return {
            "status": "failed",
            "reason": "Tatkal quota full for this train",
            "available_seats": available,
            "suggestion": "We recommend choosing an alternative route train."
        }

    seat_inventory[key] -= seats_requested

    matched_train = next((t for t in MASTER_TRAINS if str(t["train_id"]) == str(train_id)), None)
    train_name = matched_train["train_name"] if matched_train else f"Express Train {train_id}"
    source = matched_train["source"] if matched_train else "Source"
    destination = matched_train["destination"] if matched_train else "Destination"
    fare_each = matched_train["fares"].get(class_name, 1200) if matched_train else 1200
    total_fare = fare_each * seats_requested

    pnr = f"PNR{random.randint(10000000, 99999999)}"
    booking_id = f"TS-{uuid.uuid4().hex[:8].upper()}"

    booking_payload = {
        "status": "success",
        "booking_id": booking_id,
        "pnr": pnr,
        "train_id": train_id,
        "train_name": train_name,
        "source": source,
        "destination": destination,
        "travel_date": travel_date,
        "class_name": class_name,
        "quota": quota,
        "seats_booked": seats_requested,
        "remaining_seats": seat_inventory[key],
        "fare": total_fare,
        "passenger_info": passenger_info or {}
    }

    try:
        if record_booking:
            record_booking(booking_payload)
    except Exception as e:
        print(f"[mock_irctc] Warning: Failed to record booking in DB: {e}")

    return booking_payload
