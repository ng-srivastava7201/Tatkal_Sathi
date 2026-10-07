import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix,
)
import os

RANDOM_STATE = 42

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "tatkal_sathi_dataset_generated.xlsx")
MODEL_PATH = os.path.join(BASE_DIR, "model1_seat_probability.pkl")

_df = None

def get_df():
    global _df
    if _df is None:
        if os.path.exists(DATA_PATH):
            _df = pd.read_excel(DATA_PATH)
        else:
            _df = pd.DataFrame()
    return _df


def train_model():
    df = get_df()
    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.day_name()
    df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)
    df["seat_pressure"] = df["seats_requested"] / df["total_seats"]

    features = [
        "route", "class", "quota", "day_of_week", "month",
        "is_weekend", "is_holiday_or_festival", "distance_km",
        "seats_requested", "total_seats", "seat_pressure",
    ]
    categorical = ["route", "class", "quota", "day_of_week"]

    X = df[features]
    y = (df["booking_outcome"] == "success").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ],
        remainder="passthrough",
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
    pipe.fit(X_train, y_train)
    joblib.dump(pipe, MODEL_PATH)
    return pipe


if os.path.exists(MODEL_PATH):
    try:
        pipeline = joblib.load(MODEL_PATH)
    except Exception:
        pipeline = train_model()
else:
    pipeline = train_model()



def predict_seat_probability(
    route: str,
    train_class: str,
    quota: str,
    date: str,             
    seats_requested: int = 1,
    total_seats: int = 72,
    is_holiday_or_festival: int = 0,
) -> dict:
    """
    Given a booking request, return the probability of getting a Tatkal seat.

    Example:
        predict_seat_probability(
            route="Mumbai-Delhi",
            train_class="SL",
            quota="Tatkal",
            date="2026-12-25",
            seats_requested=2,
        )
        -> {"success_probability": 0.18, "recommendation": "low"}
    """
    dt = pd.to_datetime(date)
    day_name = dt.day_name()

    row = pd.DataFrame([{
        "route": route,
        "class": train_class,
        "quota": quota,
        "day_of_week": day_name,
        "month": dt.month,
        "is_weekend": int(day_name in ["Saturday", "Sunday"]),
        "is_holiday_or_festival": is_holiday_or_festival,
        "distance_km": df.loc[df["route"] == route, "distance_km"].mode().get(0, 0),
        "seats_requested": seats_requested,
        "total_seats": total_seats,
        "seat_pressure": seats_requested / total_seats,
    }])

    proba = pipeline.predict_proba(row)[0, 1]

    if proba >= 0.5:
        recommendation = "high"
    elif proba >= 0.25:
        recommendation = "medium"
    else:
        recommendation = "low"

    return {
        "route": route,
        "success_probability": round(float(proba), 3),
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    print("\n--- Example prediction ---")
    example = predict_seat_probability(
        route="Mumbai-Delhi",
        train_class="SL",
        quota="Tatkal",
        date="2026-12-25",
        seats_requested=2,
    )
    print(example)