from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

from booking_simulator import simulate_booking


def tatkal_booking_job():
    print("\n================================")
    print("TATKAL BOOKING AUTO-TRIGGER")
    print("Trigger Time:", datetime.now())
    print("================================")

    simulate_booking()


scheduler = BackgroundScheduler()

scheduler.add_job(
    tatkal_booking_job,
    "cron",
    hour=10,
    minute=0,
    id="tatkal_booking_trigger",
    replace_existing=True
)

scheduler.start()

print("Tatkal Sathi Scheduler Started")
print("Daily booking trigger scheduled for 10:00 AM.")
print("Waiting for scheduled trigger...")


try:
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit):
    print("\nScheduler stopped.")
    scheduler.shutdown()