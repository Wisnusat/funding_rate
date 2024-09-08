import os
import time
import schedule
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from platforms.aevo import Aevo
from platforms.bybit import Bybit
from platforms.hyperliquid import Hyperliquid
from platforms.gateio import Gateio
from dotenv import load_dotenv
from app.logger import logger

# KOYEB PURPOSE
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

def run_http_server():
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('0.0.0.0', 8000), handler)
    httpd.serve_forever()

server_thread = threading.Thread(target=run_http_server)
server_thread.daemon = True
server_thread.start()
# ===============================================================

load_dotenv()
FIRST_RUN = os.getenv('FIRST_RUN', 'n').lower()
EXECUTION_MODE = os.getenv('EXECUTION_MODE', '2')
INTERVAL_CHOICE = os.getenv('INTERVAL_CHOICE', '1')
SCHEDULE_CHOICE = os.getenv('SCHEDULE_CHOICE', '1')
SCHEDULE_INTERVAL_SECONDS = int(os.getenv('SCHEDULE_INTERVAL_SECONDS', 10))
SCHEDULE_MINUTE = os.getenv('SCHEDULE_MINUTE', '00')
interval_mapping = {
    '1': '1h',
    '2': '1d',
    '3': '7d',
    '4': '1M',
    '5': '1y'
}

def run_scrapers_sequential(interval):
    """Run the scrapers sequentially."""
    scrapers = [Aevo(), Bybit(), Hyperliquid(), Gateio()]
    logger.info("WILL SCRAPE: AEVO, BYBIT, HYPERLIQUID, GATEIO")
    for scraper in scrapers:
        try:
            logger.info(f"Running {scraper.__class__.__name__} scraper...")
            scraper.run(interval)
            logger.info(f"{scraper.__class__.__name__} scraper completed.")
        except Exception as e:
            logger.error(f"Error occurred in {scraper.__class__.__name__} scraper: {e}")

def run_scrapers_parallel(interval):
    """Run the scrapers in parallel."""
    scrapers = [Aevo(), Bybit(), Hyperliquid(), Gateio()]
    logger.info("WILL SCRAPE: AEVO, BYBIT, HYPERLIQUID, GATEIO")
    with ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
        futures = [executor.submit(scraper.run, interval) for scraper in scrapers]
        for future in as_completed(futures):
            try:
                future.result()
                logger.info("Scraper completed successfully.")
            except Exception as e:
                logger.error(f"Error occurred: {e}")

def countdown_to_next_run(next_run_time):
    while True:
        now = datetime.now()
        remaining_time = next_run_time - now
        if remaining_time.total_seconds() <= 0:
            break
        logger.info(f"Time until next run: {str(remaining_time).split('.')[0]}")
        time.sleep(1)

def schedule_scrapers():
    """Set up the schedule based on environment variables."""
    selected_interval = interval_mapping.get(INTERVAL_CHOICE, '1h')
    if EXECUTION_MODE == '1':
        run_mode = run_scrapers_sequential
    elif EXECUTION_MODE == '2':
        run_mode = run_scrapers_parallel

    if SCHEDULE_CHOICE == '1':
        schedule_interval = schedule.every(SCHEDULE_INTERVAL_SECONDS).seconds
    elif SCHEDULE_CHOICE == '2':
        schedule_interval = schedule.every().hour.at(f":{SCHEDULE_MINUTE}")

    schedule_interval.do(run_mode, selected_interval)
    return schedule_interval

def main():
    first_run_interval = '1y' if FIRST_RUN == 'y' else interval_mapping.get(INTERVAL_CHOICE, '1h')

    logger.info(f"Starting the first run with interval: {first_run_interval}")
    if EXECUTION_MODE == '1':
        logger.info("Running with SEQUENTIAL mode")
        run_scrapers_sequential(first_run_interval)
    elif EXECUTION_MODE == '2':
        logger.info("Running with PARALLEL mode")
        run_scrapers_parallel(first_run_interval)
    
    schedule_task = schedule_scrapers()
    next_run_time = schedule.next_run()
    logger.info(f"Next run scheduled at: {next_run_time}")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()


# OLD - with terminal commands
# import time
# import schedule
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor, as_completed

# from platforms.aevo import Aevo
# from platforms.bybit import Bybit
# from platforms.hyperliquid import Hyperliquid
# from platforms.gateio import Gateio

# def run_scrapers_sequential(interval='1h'):
#     """Run the scrapers sequentially."""
#     try:
#         print("\n\nRunning AEVO scraper...\n")
#         Aevo().run(interval)
#         print("\nAEVO scraper completed.\n")

#         print("\nRunning Bybit scraper...\n")
#         Bybit().run(interval)
#         print("\nBybit scraper completed.\n")

#         print("\nRunning Hyperliquid scraper...\n")
#         Hyperliquid().run(interval)
#         print("\nHyperliquid scraper completed.\n")

#         print("\nRunning Gate.io scraper...\n")
#         Gateio().run(10 if interval != '1y' else 100)
#         print("\nGate.io scraper completed.\n")

#     except Exception as e:
#         print(f"Error occurred: {e}")

# def run_scrapers_parallel(interval='1h'):
#     """Run the scrapers in parallel."""
#     try:
#         with ThreadPoolExecutor(max_workers=4) as executor:
#             futures = [
#                 executor.submit(Aevo().run, interval),
#                 executor.submit(Bybit().run, interval),
#                 executor.submit(Hyperliquid().run, interval),
#                 executor.submit(Gateio().run, 10 if interval != '1y' else 100)
#             ]

#             for future in as_completed(futures):
#                 try:
#                     future.result()
#                 except Exception as e:
#                     print(f"Error occurred: {e}")

#     except Exception as e:
#         print(f"Error occurred: {e}")

# def countdown_to_next_run(next_run_time):
#     while True:
#         now = datetime.now()
#         remaining_time = next_run_time - now
#         if remaining_time.total_seconds() <= 0:
#             break
#         print(f"\rTime until next run: {str(remaining_time).split('.')[0]}", end="")
#         time.sleep(1)
#     print("\n")

# import schedule

# def main():
#     first_run = input("First running? (y/n): ").strip().lower()
#     interval_scrapper = '1y' if first_run in ['y', 'yes'] else '1h' if first_run in ['n', 'no'] else None
#     if interval_scrapper is None:
#         print("Invalid choice. Exiting.")
#         return

#     print("\nSelect execution mode:")
#     print("1. Sequential")
#     print("2. Parallel")
#     mode = input("Enter the number of your choice (1 or 2): ")

#     if mode not in ['1', '2']:
#         print("Invalid choice. Exiting.")
#         return

#     # Prompt for the next interval and scheduler setup
#     if first_run in ['y', 'yes']:
#         print("\nThe first run will be done with a 1 year interval.") 
#         print("\nSelect interval for future scrapes after the first run:")
#     else:
#         print("\nSelect the interval for running the scrapers:")

#     print("1. 1 Hour (1h)")
#     print("2. 1 Day (1d)")
#     print("3. 7 Days (7d)")
#     print("4. 1 Month (1M)")
#     print("5. 1 Year (1y)")
#     interval_choice = input("Enter the number of your choice: ")

#     next_interval_scrapper = {
#         '1': '1h',
#         '2': '1d',
#         '3': '7d',
#         '4': '1M',
#         '5': '1y'
#     }.get(interval_choice)

#     if not next_interval_scrapper:
#         print("Invalid interval choice. Exiting.")
#         return

#     print("\nSelect the interval for scheduling the scrapers:")
#     print("1. Every few seconds")
#     print("2. Every hour at a specific minute")
#     schedule_choice = input("Enter the number of your choice (1 or 2): ")

#     if schedule_choice == '1':
#         interval_value = int(input("Enter the interval in seconds: "))
#         schedule_interval = schedule.every(interval_value).seconds
#     elif schedule_choice == '2':
#         minute = input("Enter the minute (00-59) when the scrapers should run every hour: ").zfill(2)
#         if not minute.isdigit() or not (0 <= int(minute) < 60):
#             print("Invalid minute value. Exiting.")
#             return
#         schedule_interval = schedule.every().hour.at(f":{minute}")
#         print(f"Scrapers will run every hour at minute :{minute}.")
#         print("\n")
#     else:
#         print("Invalid scheduling choice. Exiting.")
#         return

#     # Schedule the selected mode and interval for future runs
#     if mode == '1':
#         schedule_interval.do(run_scrapers_sequential, next_interval_scrapper)
#     elif mode == '2':
#         schedule_interval.do(run_scrapers_parallel, next_interval_scrapper)

#     # Run the scraper with '1y' interval first if it's the first run
#     if first_run in ['y', 'yes']:
#         if mode == '1':
#             run_scrapers_sequential('1y')
#         elif mode == '2':
#             run_scrapers_parallel('1y')

#     # Keep the script running and check for scheduled tasks
#     while True:
#         next_run_time = schedule.next_run()
#         print(f"\nNext run scheduled at: {next_run_time}")
#         countdown_to_next_run(next_run_time)
#         schedule.run_pending()

# if __name__ == "__main__":
#     main()

