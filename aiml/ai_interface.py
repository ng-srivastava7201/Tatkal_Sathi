from route_rank import rank_alternative_routes
from preference_matcher import pick_best_fallback

from route_rank import _predict_probability as _m1_predict

def predict_seat_probability(route, train_class, quota, date,
                              seats_requested=1, total_seats=72,
                              is_holiday_or_festival=0):
    proba, distance_km, source, destination = _m1_predict(
        route, train_class, quota, date,
        seats_requested, total_seats, is_holiday_or_festival,
    )
    return {"route": route, "success_probability": round(proba, 3)}