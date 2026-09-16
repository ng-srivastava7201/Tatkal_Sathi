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
df = pd.read_excel(DATA_PATH)

print(f"Loaded {len(df)} rows, {df.shape[1]} columns")
print(df["booking_outcome"].value_counts(normalize=True))

df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.month
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

df["seat_pressure"] = df["seats_requested"] / df["total_seats"]

FEATURES = [
    "route",
    "class",
    "quota",
    "day_of_week",
    "month",
    "is_weekend",
    "is_holiday_or_festival",
    "distance_km",
    "seats_requested",
    "total_seats",
    "seat_pressure",
]
TARGET = "booking_outcome"

X = df[FEATURES]
y = (df[TARGET] == "success").astype(int)  

CATEGORICAL = ["route", "class", "quota", "day_of_week"]
NUMERIC = [c for c in FEATURES if c not in CATEGORICAL]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ],
    remainder="passthrough",  
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=6,
    class_weight="balanced",
    random_state=RANDOM_STATE,
)

pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

print("\n--- Evaluation ---")
print(classification_report(y_test, y_pred, target_names=["fail", "success"]))
print("ROC-AUC:", round(roc_auc_score(y_test, y_proba), 3))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

ohe = pipeline.named_steps["preprocess"].named_transformers_["cat"]
cat_names = ohe.get_feature_names_out(CATEGORICAL)
all_feature_names = list(cat_names) + NUMERIC
importances = pipeline.named_steps["model"].feature_importances_

print("\n--- Top 10 most important features ---")
imp_df = pd.DataFrame(
    {"feature": all_feature_names, "importance": importances}
).sort_values("importance", ascending=False)
print(imp_df.head(10).to_string(index=False))

joblib.dump(pipeline, "model1_seat_probability.pkl")
print("\nSaved model to model1_seat_probability.pkl")


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