import schedule
import time

from job import monitor_hint, build_report, crux

print("Starting worker...")

# Schedule tasks
# schedule.every().day.at("01:00").do(monitor_hint.run)
# schedule.every().day.at("04:00").do(monitor_hint.run)
# schedule.every().day.at("08:00").do(build_report.run)
# schedule.every().day.at("08:10").do(crux.run)

# schedule.every(1).minutes.do(build_report.run)
# schedule.every(1).minutes.do(crux.run)

build_report.run()

crux.run()
# while True:
#     schedule.run_pending()
#     # time.sleep(5 * 60) # 5 minutes
#     time.sleep(30) # 30 seconds
