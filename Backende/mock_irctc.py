import random
import uuid
import os
import pandas as pd
from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "tatkal_sathi_dataset_generated.xlsx")

df = pd.read_excel(DATA_PATH)

seat_inventory = {}

for _, row in df.iterrows():          # <-- fixed
    key = (
        str(row["train_id"]),
        str(row["date"]),
        str(row["class"]),
        str(row["quota"])
    )

    if key not in seat_inventory:
        seat_inventory[key] = int(row["seats_available_at_booking_time"])


def search_trains(source, destination, date):
    results = df[
        (df["source"].str.lower() == source.lower()) &
        (df["destination"].str.lower() == destination.lower()) &
        (df["date"].astype(str) == str(date))
    ]
    return results.to_dict(orient="records")


def book_ticket(train_id, travel_date, class_name, quota, seats_requested):
    if seats_requested <= 0:
        raise HTTPException(status_code=400, detail="Seats requested must be greater than zero")

    key = (str(train_id), str(travel_date), str(class_name), str(quota))

    if key not in seat_inventory:
        raise HTTPException(status_code=404, detail="Train or booking combination not found")

    available = seat_inventory[key]

    if random.random() < 0.10:
        return {"status": "failed", "reason": "Temporary transaction failure", "available_seats": available}

    if available < seats_requested:
        return {"status": "failed", "reason": "No sufficient seats available", "available_seats": available}

    seat_inventory[key] -= seats_requested

    return {
        "status": "success",
        "pnr": f"FAKE{random.randint(100000, 999999)}",
        "booking_id": f"MOCK-{uuid.uuid4().hex[:8].upper()}",
        "train_id": train_id,
        "travel_date": travel_date,
        "class": class_name,
        "quota": quota,
        "seats_booked": seats_requested,
        "remaining_seats": seat_inventory[key]
    }