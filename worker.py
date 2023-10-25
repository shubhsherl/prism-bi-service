print("Starting worker...")
import schedule
import time

from job import monitor_hint, build_report, crux, top_page_lcp, prefetches

tz = "Asia/Kolkata"

# Schedule tasks
schedule.every(1).day.at("01:00 PM", tz).do(top_page_lcp.run)
schedule.every(1).day.at("03:00 PM", tz).do(monitor_hint.run)
schedule.every(1).day.at("06:00 PM", tz).do(monitor_hint.run)
schedule.every(1).day.at("09:00 PM", tz).do(build_report.run)
schedule.every(1).day.at("12:10 PM", tz).do(crux.run)
schedule.every(1).day.at("01:00 PM", tz).do(prefetches.run)

while True:
    schedule.run_pending()
    print("Sleeping for 5 minutes...")
    time.sleep(5 * 60) # 5 minutes

print("Worker stopped.")
