import schedule
import time
import logging

from job import monitor_hint, build_report, crux, top_page_lcp, prefetches

# Set up the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger instance
logger = logging.getLogger('worker')
logger.info("Starting worker...")

tz = "Asia/Kolkata"

# Schedule tasks
schedule.every(1).day.at("13:00", tz).do(monitor_hint.run)
schedule.every(1).day.at("18:00", tz).do(build_report.run)
schedule.every(1).day.at("19:00", tz).do(crux.run)
schedule.every(1).day.at("20:00", tz).do(top_page_lcp.run)
schedule.every(1).day.at("23:00", tz).do(prefetches.run)

while True:
    schedule.run_pending()
    logger.info("Sleeping for 5 minutes...")
    time.sleep(5 * 60) # 5 minutes
