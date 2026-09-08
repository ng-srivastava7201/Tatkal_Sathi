from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

from booking_simulator import simulate_booking


def tatkal_booking_job():
    print("\n10:00 AM AUTO-TRIGGER EXECUTED")
    print("Trigger time:", datetime.now())

    simulate_booking()


scheduler = BackgroundScheduler()

scheduler.add_job(
    tatkal_booking_job,
    "cron",
    hour=10,
    minute=0
)

scheduler.start()

print("Tatkal Sathi Scheduler Started")
print("Waiting for 10:00 AM auto-trigger...")

try:
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit):
    print("Scheduler stopped.")
    scheduler.shutdown()