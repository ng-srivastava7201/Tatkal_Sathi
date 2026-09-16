import os
import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model1_seat_probability.pkl")
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "tatkal_sathi_dataset_generated.xlsx")

pipeline = joblib.load(MODEL_PATH)
df = pd.read_excel(DATA_PATH)

route_ref = (
    df.groupby("route")
    .agg(
        distance_km=("distance_km", "first"),
        source=("source", "first"),
        destination=("destination", "first"),
    )
    .reset_index()
)

MAX_DISTANCE_SPREAD = route_ref["distance_km"].max() - route_ref["distance_km"].min()
MAX_DISTANCE_SPREAD = MAX_DISTANCE_SPREAD if MAX_DISTANCE_SPREAD > 0 else 1


def _predict_probability(
    route: str,
    train_class: str,
    quota: str,
    date: str,
    seats_requested: int,
    total_seats: int,
    is_holiday_or_festival: int,
) -> float:
    dt = pd.to_datetime(date)
    day_name = dt.day_name()

    match = route_ref.loc[route_ref["route"] == route, "distance_km"]
    distance_km = float(match.iloc[0]) if len(match) else 0.0

    row = pd.DataFrame([{
        "route": route,
        "class": train_class,
        "quota": quota,
        "day_of_week": day_name,
        "month": dt.month,
        "is_weekend": int(day_name in ["Saturday", "Sunday"]),
        "is_holiday_or_festival": is_holiday_or_festival,
        "distance_km": distance_km,
        "seats_requested": seats_requested,
        "total_seats": total_seats,
        "seat_pressure": seats_requested / total_seats,
    }])

    proba = pipeline.predict_proba(row)[0, 1]
    return float(proba), distance_km


def rank_alternative_routes(
    original_route: str,
    train_class: str,
    quota: str,
    date: str,
    seats_requested: int = 1,
    total_seats: int = 72,
    is_holiday_or_festival: int = 0,
    top_n: int = 3,
    prob_weight: float = 0.65,
    distance_fit_weight: float = 0.35,
) -> dict:
    orig_proba, orig_distance = _predict_probability(
        original_route, train_class, quota, date,
        seats_requested, total_seats, is_holiday_or_festival,
    )

    candidates = route_ref[route_ref["route"] != original_route].copy()

    results = []
    for _, cand in candidates.iterrows():
        proba, distance_km = _predict_probability(
            cand["route"], train_class, quota, date,
            seats_requested, total_seats, is_holiday_or_festival,
        )
        distance_diff = abs(distance_km - orig_distance)
        distance_fit = 1 - (distance_diff / MAX_DISTANCE_SPREAD)
        combined_score = prob_weight * proba + distance_fit_weight * distance_fit

        results.append({
            "route": cand["route"],
            "source": cand["source"],
            "destination": cand["destination"],
            "distance_km": distance_km,
            "success_probability": round(proba, 3),
            "distance_fit": round(distance_fit, 3),
            "combined_score": round(combined_score, 3),
        })

    ranked = sorted(results, key=lambda r: r["combined_score"], reverse=True)[:top_n]

    return {
        "original_route": original_route,
        "original_success_probability": round(orig_proba, 3),
        "alternatives": ranked,
    }


if __name__ == "__main__":
    result = rank_alternative_routes(
        original_route="Mumbai-Delhi",
        train_class="SL",
        quota="Tatkal",
        date="2026-12-25",   
        seats_requested=2,
        top_n=3,
    )

    print(f"Original route: {result['original_route']}")
    print(f"Original success probability: {result['original_success_probability']}")
    print("\nTop alternatives:")
    for alt in result["alternatives"]:
        print(
            f"  {alt['route']:<22} "
            f"prob={alt['success_probability']:<6} "
            f"dist_fit={alt['distance_fit']:<6} "
            f"score={alt['combined_score']}"
        )