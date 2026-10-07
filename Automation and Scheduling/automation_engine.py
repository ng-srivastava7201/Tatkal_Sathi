import time
from datetime import datetime
from automation_config import (
    MAX_ATTEMPTS,
    BACKOFF_SECONDS,
    TIME_CAP_SECONDS,
    USER_REQUEST
)
from api_client import (
    predict_probability,
    attempt_book,
    get_best_fallback,
    resolve_train_id
)


def log_final_failure(reason):
    print(f"[{datetime.now()}] FINAL FAILURE — {reason}")
    print("Status: FAILED | user/dashboard notified | no further auto-retry")


def try_fallback(user_request, start_time):
    if time.time() - start_time >= TIME_CAP_SECONDS:
        log_final_failure("time cap hit before fallback could run")
        return None

    best = get_best_fallback(user_request)

    if not best:
        log_final_failure("no alternative available")
        return None

    train_id = resolve_train_id(
        best["route"],
        best["source"],
        best["destination"],
        user_request["travel_date"]
    )

    if not train_id:
        log_final_failure(
            f"could not resolve train_id for route {best['route']}"
        )
        return None

    # Check time cap immediately before fallback booking attempt
    if time.time() - start_time >= TIME_CAP_SECONDS:
        log_final_failure("time cap hit before fallback booking attempt")
        return None

    print(f"Trying fallback: {best['route']} / {train_id} (1 attempt)")

    result = attempt_book(
        train_id,
        {**user_request, "train_id": train_id}
    )

    if result.get("status") == "success":
        print("CONFIRMED on fallback train.")
        return result

    log_final_failure(
        f"fallback train also failed ({result.get('reason')})"
    )
    return None


def run_booking_automation(user_request=None):
    user_request = user_request or USER_REQUEST
    start_time = time.time()

    print(
        f"\n==== TATKAL BOOKING TRIGGERED at "
        f"{datetime.now()} ===="
    )

    prediction = predict_probability(user_request)
    print(f"Predicted: {prediction}")

    # Low probability → directly use fallback
    if prediction.get("recommendation") == "low":
        print(
            "Probability low — skipping preferred-train retries, "
            "going to fallback."
        )
        return try_fallback(user_request, start_time)

    # Preferred train: MAX_ATTEMPTS = 3 total attempts
    attempt = 1

    while attempt <= MAX_ATTEMPTS:

        # Check time cap before every attempt
        if time.time() - start_time >= TIME_CAP_SECONDS:
            log_final_failure(
                "time cap hit during preferred-train attempts"
            )
            return None

        print(
            f"Preferred train — attempt "
            f"{attempt}/{MAX_ATTEMPTS}"
        )

        result = attempt_book(
            user_request["train_id"],
            user_request
        )

        if result.get("status") == "success":
            print("CONFIRMED on preferred train.")
            return result

        print(
            f"Attempt {attempt} failed: "
            f"{result.get('reason')}"
        )

        attempt += 1

        if attempt <= MAX_ATTEMPTS:
            remaining = TIME_CAP_SECONDS - (
                time.time() - start_time
            )

            if remaining <= BACKOFF_SECONDS:
                log_final_failure(
                    "time cap would be exceeded before next retry"
                )
                return None

            time.sleep(BACKOFF_SECONDS)

    # All 3 preferred attempts failed → one fallback attempt
    print("Preferred train exhausted — trying fallback.")
    return try_fallback(user_request, start_time)