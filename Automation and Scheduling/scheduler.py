import os
import sys
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if CURR_DIR not in sys.path:
    sys.path.append(CURR_DIR)

from booking_simulator import simulate_booking, get_simulation_history

scheduler = BackgroundScheduler(daemon=True)
_is_running = False
_scheduled_hour = 10
_scheduled_minute = 0


def tatkal_booking_job():
    """Scheduled 10:00 AM Tatkal automated booking job."""
    print("\n================================")
    print("TATKAL BOOKING AUTO-TRIGGER FIRED")
    print("Trigger Time:", datetime.now())
    print("================================")

    simulate_booking({
        "trigger_type": "10:00 AM Tatkal Auto-Trigger",
        "train_name": "Bhopal Shatabdi (12002)",
        "train_id": "12002",
        "source": "Bhopal",
        "destination": "New Delhi",
        "class_name": "3A",
        "quota": "Tatkal",
        "seats": 2
    })


def start_scheduler():
    """Start APScheduler in background without blocking."""
    global _is_running
    if not _is_running:
        scheduler.add_job(
            tatkal_booking_job,
            "cron",
            hour=_scheduled_hour,
            minute=_scheduled_minute,
            id="tatkal_booking_trigger",
            replace_existing=True
        )
        scheduler.start()
        _is_running = True
        print(f"[Scheduler] Tatkal Sathi Scheduler started. Daily trigger set for {_scheduled_hour:02d}:{_scheduled_minute:02d}.")
    return True


def stop_scheduler():
    """Safely shut down the scheduler."""
    global _is_running
    if _is_running:
        scheduler.shutdown(wait=False)
        _is_running = False
        print("[Scheduler] Tatkal Sathi Scheduler stopped.")
    return True


def get_scheduler_status():
    """Get live telemetry and status of the background scheduler."""
    job = scheduler.get_job("tatkal_booking_trigger")
    next_run = None
    if job and job.next_run_time:
        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "scheduler_running": _is_running,
        "job_id": "tatkal_booking_trigger",
        "scheduled_time": f"{_scheduled_hour:02d}:{_scheduled_minute:02d}",
        "next_run_time": next_run,
        "total_simulations_recorded": len(get_simulation_history()),
        "description": "APScheduler 10:00 AM Tatkal auto-trigger engine"
    }


def trigger_immediate_booking(booking_details: dict = None):
    """Manually trigger booking simulation right now."""
    details = booking_details or {}
    details.setdefault("trigger_type", "Manual Test Trigger")
    return simulate_booking(details)


def update_schedule(hour: int = 10, minute: int = 0):
    """Update scheduled trigger time."""
    global _scheduled_hour, _scheduled_minute
    _scheduled_hour = int(hour)
    _scheduled_minute = int(minute)

    if _is_running:
        scheduler.add_job(
            tatkal_booking_job,
            "cron",
            hour=_scheduled_hour,
            minute=_scheduled_minute,
            id="tatkal_booking_trigger",
            replace_existing=True
        )
        print(f"[Scheduler] Updated trigger time to {_scheduled_hour:02d}:{_scheduled_minute:02d}.")

    return get_scheduler_status()

if __name__ == "__main__":
    start_scheduler()
    print("Tatkal Sathi Scheduler Running Standalone.")
    print("Daily booking trigger scheduled for 10:00 AM.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        stop_scheduler()
        print("\nScheduler terminated.")