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
 
AVG_SPEED_KMPH = 60 
 
def _predict_probability(route, train_class, quota, date, seats_requested, total_seats, is_holiday_or_festival):
    dt = pd.to_datetime(date)
    day_name = dt.day_name()
    match = route_ref.loc[route_ref["route"] == route]
    distance_km = float(match["distance_km"].iloc[0]) if len(match) else 0.0
    source = match["source"].iloc[0] if len(match) else None
    destination = match["destination"].iloc[0] if len(match) else None
 
    row = pd.DataFrame([{
        "route": route, "class": train_class, "quota": quota, "day_of_week": day_name,
        "month": dt.month, "is_weekend": int(day_name in ["Saturday", "Sunday"]),
        "is_holiday_or_festival": is_holiday_or_festival, "distance_km": distance_km,
        "seats_requested": seats_requested, "total_seats": total_seats,
        "seat_pressure": seats_requested / total_seats,
    }])
    proba = float(pipeline.predict_proba(row)[0, 1])
    return proba, distance_km, source, destination
 
 
def _switching_level(orig_source, orig_destination, cand_source, cand_destination):
    """
    0 = identical source AND destination (no switching needed)
    1 = shares ONE of source/destination (partial switch - e.g. different source station)
    2 = shares NEITHER (a fully different journey)
    """
    matches = int(cand_source == orig_source) + int(cand_destination == orig_destination)
    return 2 - matches
 
def pick_best_fallback(
    original_route: str,
    train_class: str,
    quota: str,
    date: str,
    seats_requested: int = 1,
    total_seats: int = 72,
    is_holiday_or_festival: int = 0,
    preferences: dict = None,
    top_n: int = 1,
) -> dict:
    
    preferences = preferences or {}
    w_prob = preferences.get("probability_weight", 0.5)
    w_dist = preferences.get("distance_weight", 0.2)
    w_time = preferences.get("time_weight", 0.15)
    w_station = preferences.get("station_weight", 0.15)
    max_switching = preferences.get("max_switching", 1)
 
    orig_proba, orig_distance, orig_source, orig_destination = _predict_probability(
        original_route, train_class, quota, date, seats_requested, total_seats, is_holiday_or_festival,
    )
    orig_time_hr = orig_distance / AVG_SPEED_KMPH
 
    candidates = route_ref[route_ref["route"] != original_route].copy()
    scored = []
 
    for _, cand in candidates.iterrows():
        proba, distance_km, source, destination = _predict_probability(
            cand["route"], train_class, quota, date, seats_requested, total_seats, is_holiday_or_festival,
        )
 
        switching = _switching_level(orig_source, orig_destination, source, destination)
        if switching > max_switching:
            continue
 
        distance_fit = 1 - (abs(distance_km - orig_distance) / MAX_DISTANCE_SPREAD)
        time_hr = distance_km / AVG_SPEED_KMPH
        time_fit = 1 - min(abs(time_hr - orig_time_hr) / max(orig_time_hr, 1), 1)
        station_fit = 1 - (switching / 2)  # 0 switching -> 1.0, 2 switching -> 0.0
 
        combined_score = (
            w_prob * proba
            + w_dist * distance_fit
            + w_time * time_fit
            + w_station * station_fit
        )
 
        scored.append({
            "route": cand["route"],
            "source": source,
            "destination": destination,
            "distance_km": distance_km,
            "success_probability": round(proba, 3),
            "distance_fit": round(distance_fit, 3),
            "time_fit": round(time_fit, 3),
            "station_fit": round(station_fit, 3),
            "switching_level": switching,
            "combined_score": round(combined_score, 3),
        })
 
    ranked = sorted(scored, key=lambda r: r["combined_score"], reverse=True)[:top_n]
 
    for r in ranked:
        if r["switching_level"] == 0:
            r["reason"] = "Same stations, strong overall fit"
        elif r["success_probability"] > orig_proba:
            r["reason"] = "Meaningfully higher success chance, close in distance/time"
        else:
            r["reason"] = "Best balance of distance, time, and station match"
 
    return {
        "original_route": original_route,
        "original_success_probability": round(orig_proba, 3),
        "preferences_used": {
            "probability_weight": w_prob, "distance_weight": w_dist,
            "time_weight": w_time, "station_weight": w_station,
            "max_switching": max_switching,
        },
        "best_fallback": ranked[0] if ranked else None,
        "alternatives": ranked,
    }
 
 
if __name__ == "__main__":
    result = pick_best_fallback(
        original_route="Mumbai-Delhi",
        train_class="SL",
        quota="Tatkal",
        date="2026-12-25",
        seats_requested=2,
        preferences={
            "probability_weight": 0.6,
            "distance_weight": 0.2,
            "time_weight": 0.1,
            "station_weight": 0.1,
            "max_switching": 1,  
        },
        top_n=3,
    )
 
    print(f"Original route: {result['original_route']}")
    print(f"Original success probability: {result['original_success_probability']}\n")
 
    if result["best_fallback"]:
        best = result["best_fallback"]
        print(f"BEST FALLBACK: {best['route']} "
              f"(prob={best['success_probability']}, score={best['combined_score']})")
        print(f"Reason: {best['reason']}\n")
 
    print("All ranked candidates considered:")
    for alt in result["alternatives"]:
        print(f"  {alt['route']:<22} prob={alt['success_probability']:<6} "
              f"switching={alt['switching_level']} score={alt['combined_score']}")
 