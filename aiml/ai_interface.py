from route_rank import rank_alternative_routes
from preference_matcher import pick_best_fallback
from seat_probability import predict_seat_probability as _m1_predict


def predict_seat_probability(
    route,
    train_class,
    quota,
    date,
    seats_requested=1,
    total_seats=72,
    is_holiday_or_festival=0,
):
    return _m1_predict(
        route=route,
        train_class=train_class,
        quota=quota,
        date=date,
        seats_requested=seats_requested,
        total_seats=total_seats,
        is_holiday_or_festival=is_holiday_or_festival,
    )
