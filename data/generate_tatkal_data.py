"""
Tatkal Sathi - Synthetic Training Data Generator
--------------------------------------------------
Fixes the two problems found in the uploaded datasets:
  1. `seats_available_at_booking_time` must always be present (never blank).
  2. Success/fail ratio must be realistic (Tatkal mostly FAILS), not 99% success.

Design principle (discussed with the AI/ML engineer):
  - Faker is used ONLY for cosmetic fields (PNR numbers) - it has no concept
    of real-world booking patterns.
  - The actual success/fail pattern is RULE-BASED, driven by factors that
    genuinely affect real Tatkal outcomes:
        route popularity (metro-to-metro routes are harder)
        class (higher class = more seats = easier)
        quota (Tatkal is harder than General)
        festival/holiday proximity (demand spikes, harder)
        seats_requested (asking for more seats is harder)

"""

import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

RANDOM_SEED = 42
N_ROWS = 3000

rng = np.random.default_rng(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# 1. Reference data: routes with a realistic "popularity tier"
#    Higher popularity -> more demand -> harder to get a Tatkal seat.
# ---------------------------------------------------------------------------
ROUTES = [
    # (train_id, route, source, destination, distance_km, popularity 0-1)
    ("T001", "Delhi-Mumbai",      "New Delhi", "Mumbai",     1384, 0.95),
    ("T002", "Mumbai-Delhi",      "Mumbai",    "New Delhi",  1384, 0.95),
    ("T003", "Delhi-Kolkata",     "New Delhi", "Kolkata",    1450, 0.85),
    ("T004", "Kolkata-Delhi",     "Kolkata",   "New Delhi",  1450, 0.85),
    ("T005", "Chennai-Bangalore", "Chennai",   "Bangalore",   350, 0.75),
    ("T006", "Bangalore-Chennai", "Bangalore", "Chennai",     350, 0.75),
    ("T007", "Hyderabad-Mumbai",  "Hyderabad", "Mumbai",      711, 0.70),
    ("T008", "Pune-Delhi",        "Pune",      "New Delhi",  1486, 0.65),
    ("T009", "Jaipur-Delhi",      "Jaipur",    "New Delhi",   308, 0.55),
    ("T010", "Ahmedabad-Mumbai",  "Ahmedabad", "Mumbai",      491, 0.60),
    ("T011", "Delhi-Lucknow",     "New Delhi", "Lucknow",     512, 0.65),
    ("T012", "Lucknow-Delhi",     "Lucknow",   "New Delhi",   512, 0.65),
    ("T013", "Delhi-Jaipur",      "New Delhi", "Jaipur",      308, 0.55),
    ("T014", "Bangalore-Hyderabad","Bangalore","Hyderabad",    570, 0.50),
    ("T015", "Chennai-Delhi",     "Chennai",   "New Delhi",  2180, 0.60),
]

CLASSES = {
    # class: (total_seats, base_ease 0-1 -> higher = easier to get a seat)
    "SL": (72, 0.35),
    "3A": (64, 0.45),
    "2A": (46, 0.60),
    "1A": (24, 0.75),
}

QUOTA_EASE = {"Tatkal": 0.30, "General": 0.65}

# A handful of known Indian festival/holiday dates for 2026-2027 (extend as needed)
FESTIVAL_DATES = {
    "2026-01-26", "2026-03-14", "2026-04-14", "2026-08-15", "2026-10-02",
    "2026-10-20", "2026-11-08", "2026-12-25",
    "2027-01-26", "2027-03-04", "2027-04-14", "2027-08-15", "2027-10-02",
    "2027-11-01", "2027-12-25",
}

DATE_RANGE_START = datetime(2026, 1, 1)
DATE_RANGE_END = datetime(2027, 12, 31)


def random_date():
    delta_days = (DATE_RANGE_END - DATE_RANGE_START).days
    return DATE_RANGE_START + timedelta(days=int(rng.integers(0, delta_days)))


def is_near_festival(date: datetime, window_days: int = 3) -> bool:
    for f in FESTIVAL_DATES:
        fdate = datetime.strptime(f, "%Y-%m-%d")
        if abs((date - fdate).days) <= window_days:
            return True
    return False


def booking_hour(quota: str) -> int:
    """Tatkal opens at 10 (AC) / 11 (non-AC); most attempts cluster right then,
    with a long tail through the day for people who keep retrying."""
    if quota == "Tatkal":
        return int(np.clip(rng.normal(loc=10.5, scale=1.8), 9, 21))
    return int(rng.integers(8, 21))


# ---------------------------------------------------------------------------
# 2. Generate rows
# ---------------------------------------------------------------------------
rows = []
for _ in range(N_ROWS):
    train_id, route, source, dest, distance, popularity = ROUTES[
        rng.integers(0, len(ROUTES))
    ]
    train_class = rng.choice(list(CLASSES.keys()), p=[0.40, 0.32, 0.18, 0.10])
    total_seats, class_ease = CLASSES[train_class]
    quota = rng.choice(["Tatkal", "General"], p=[0.68, 0.32])
    quota_ease = QUOTA_EASE[quota]

    date = random_date()
    day_name = date.strftime("%A")
    is_weekend = day_name in ("Saturday", "Sunday")
    is_festival = is_near_festival(date)

    seats_requested = int(rng.choice([1, 2, 3, 4], p=[0.55, 0.30, 0.10, 0.05]))

    # --- Core probability model (this is the "learnable pattern") ---
    p_success = (
        0.55 * class_ease
        + 0.30 * quota_ease
        + 0.15 * (1 - popularity)
    )
    if is_festival:
        p_success *= 0.55
    if is_weekend:
        p_success *= 0.85
    p_success *= max(0.25, 1 - 0.15 * (seats_requested - 1))  # more seats = harder
    p_success = float(np.clip(p_success + rng.normal(0, 0.05), 0.02, 0.97))

    outcome = "success" if rng.random() < p_success else "fail"

    # seats_available_at_booking_time must be consistent with the outcome
    if outcome == "success":
        seats_available = int(rng.integers(seats_requested, max(seats_requested + 1, int(total_seats * 0.25))))
    else:
        # either genuinely 0, or fewer than requested
        if rng.random() < 0.7:
            seats_available = 0
        else:
            seats_available = int(rng.integers(0, seats_requested))

    hour = booking_hour(quota)
    minute = int(rng.integers(0, 60))
    # booking attempt happens same day the Tatkal window opens (1 day before travel date, typically)
    attempt_dt = date - timedelta(days=1)
    attempt_dt = attempt_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

    rows.append({
        "train_id": train_id,
        "route": route,
        "source": source,
        "destination": dest,
        "distance_km": distance,
        "class": train_class,
        "quota": quota,
        "date": date.strftime("%Y-%m-%d"),
        "day_of_week": day_name,
        "is_holiday_or_festival": int(is_festival),
        "total_seats": total_seats,
        "seats_requested": seats_requested,
        "seats_available_at_booking_time": seats_available,
        "booking_outcome": outcome,
        "booking_attempt_timestamp": attempt_dt,
        "pnr_number": fake.bothify(text="PNR########"),  # cosmetic only, via Faker
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# 3. Sanity checks before saving
# ---------------------------------------------------------------------------
print("Generated rows:", len(df))
print("\nOverall outcome distribution:")
print(df["booking_outcome"].value_counts(normalize=True).round(3))

print("\nSuccess rate by quota:")
print(df.groupby("quota")["booking_outcome"].apply(lambda s: (s == "success").mean()).round(3))

print("\nSuccess rate by class:")
print(df.groupby("class")["booking_outcome"].apply(lambda s: (s == "success").mean()).round(3))

print("\nSuccess rate: festival vs non-festival:")
print(df.groupby("is_holiday_or_festival")["booking_outcome"].apply(lambda s: (s == "success").mean()).round(3))

print("\nConsistency check (seats_available < seats_requested must ALWAYS mean fail):")
inconsistent = df[
    (df["seats_available_at_booking_time"] < df["seats_requested"])
    & (df["booking_outcome"] == "success")
]
print("Inconsistent rows:", len(inconsistent), "(should be 0)")

# ---------------------------------------------------------------------------
# 4. Save
# ---------------------------------------------------------------------------
OUT_PATH = "tatkal_sathi_dataset_generated.xlsx"
df.to_excel(OUT_PATH, index=False)
print(f"\nSaved {len(df)} rows to {OUT_PATH}")