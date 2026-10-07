from apscheduler.schedulers.background import BackgroundScheduler
import time

from automation_engine import run_booking_automation

scheduler = BackgroundScheduler()
scheduler.add_job(
    run_booking_automation,
    "cron",
    hour=10,
    minute=0,
    id="tatkal_booking_trigger",
    replace_existing=True,
)
scheduler.start()

print("Tatkal Sathi Scheduler Started — daily trigger at 10:00 AM")

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    print("\nScheduler stopped.")
    scheduler.shutdown()