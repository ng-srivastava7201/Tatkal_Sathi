import os
import sys
import time
import random
import uuid
from datetime import datetime

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backende"))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

try:
    from database import log_automation_execution
except ImportError:
    log_automation_execution = None

SIMULATION_HISTORY = []


def simulate_booking(booking_details: dict = None):
    """
    Simulates high-speed Tatkal automated booking attempt at the 10:00 AM window.
    Addresses key issues highlighted in project architecture:
    - Eliminates session timeout (pre-warmed IRCTC session)
    - Automates pre-filled passenger credentials & instant payment dispatch
    - Fallback route auto-switching if primary train tatkal quota exhausts
    """
    start_time = time.time()
    trigger_ts = datetime.now()

    params = booking_details or {}
    train_name = params.get("train_name", "Bhopal Shatabdi (12002)")
    train_id = params.get("train_id", "12002")
    source = params.get("source", "Bhopal")
    destination = params.get("destination", "New Delhi")
    travel_class = params.get("class_name", "3A")
    quota = params.get("quota", "Tatkal")
    seats = int(params.get("seats", 1))

    sim_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
    pnr = f"PNR{random.randint(10000000, 99999999)}"

    time_prefix = trigger_ts.strftime("%H:%M:%S")
    logs = [
        f"{time_prefix}.014 - [Auto-Trigger] Tatkal Booking Window opened for {quota} ({travel_class})",
        f"{time_prefix}.042 - [Session Engine] Pre-authenticated IRCTC session active (Session timeout prevented)",
        f"{time_prefix}.098 - [Form Injection] Auto-filled passenger data for {seats} traveler(s)",
        f"{time_prefix}.180 - [Payment Setup] Pre-authorized UPI/Auto-Debit payment dispatched instantly",
    ]
    is_success = random.random() < 0.92
    fallback_used = False

    if is_success:
        logs.append(f"{time_prefix}.284 - [Seat Allocation] Successfully secured {seats} Tatkal seat(s) on {train_name}")
        logs.append(f"{time_prefix}.320 - [Transaction Done] PNR generated: {pnr}. Status: CONFIRMED")
        status = "SUCCESS"
    else:
        fallback_used = True
        backup_train = "Shaan-e-Bhopal Express (12155)"
        pnr = f"PNR{random.randint(10000000, 99999999)}"
        logs.append(f"{time_prefix}.240 - [Quota Full] Primary train {train_name} Tatkal seats exhausted")
        logs.append(f"{time_prefix}.295 - [Alternate Route Engine] Auto-switched to backup option: {backup_train}")
        logs.append(f"{time_prefix}.360 - [Transaction Done] Fallback ticket confirmed. PNR: {pnr}")
        status = "FALLBACK_CONFIRMED"
        train_name = backup_train

    latency_ms = int((time.time() - start_time) * 1000) + random.randint(280, 420)

    result = {
        "simulation_id": sim_id,
        "trigger_time": trigger_ts.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "pnr": pnr,
        "train_name": train_name,
        "source": source,
        "destination": destination,
        "class": travel_class,
        "quota": quota,
        "seats_booked": seats,
        "latency_ms": latency_ms,
        "fallback_route_used": fallback_used,
        "session_protected": True,
        "logs": logs
    }

    SIMULATION_HISTORY.insert(0, result)
    if len(SIMULATION_HISTORY) > 50:
        SIMULATION_HISTORY.pop()

    try:
        if log_automation_execution:
            log_automation_execution(
                trigger_type=params.get("trigger_type", "10:00 AM Tatkal Auto-Trigger"),
                status=status,
                pnr=pnr,
                train_name=train_name,
                latency_ms=latency_ms,
                details=" | ".join(logs)
            )
    except Exception as e:
        print(f"[booking_simulator] Warning: Database log failed: {e}")

    # Console display
    print("\n--------------------------------")
    print(f"TATKAL AUTOMATION TRIGGER: {status}")
    print(f"Time: {trigger_ts} | Latency: {latency_ms}ms")
    print(f"Train: {train_name} | PNR: {pnr}")
    print("--------------------------------")

    return result


def get_simulation_history():
    """Return past simulation records."""
    return SIMULATION_HISTORY
