import time
import schedule
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from platforms.aevo import Aevo
from platforms.bybit import Bybit
from platforms.hyperliquid import Hyperliquid
from platforms.gateio import Gateio

def run_scrapers_sequential(interval='1h'):
    """Run the scrapers sequentially."""
    try:
        print("\n\nRunning AEVO scraper...\n")
        Aevo().run(interval)
        print("\nAEVO scraper completed.\n")

        print("\nRunning Bybit scraper...\n")
        Bybit().run(interval)
        print("\nBybit scraper completed.\n")

        print("\nRunning Hyperliquid scraper...\n")
        Hyperliquid().run(interval)
        print("\nHyperliquid scraper completed.\n")

        print("\nRunning Gate.io scraper...\n")
        Gateio().run(10 if interval != '1y' else 100)
        print("\nGate.io scraper completed.\n")

    except Exception as e:
        print(f"Error occurred: {e}")

def run_scrapers_parallel(interval='1h'):
    """Run the scrapers in parallel."""
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(Aevo().run, interval),
                executor.submit(Bybit().run, interval),
                executor.submit(Hyperliquid().run, interval),
                executor.submit(Gateio().run, 10 if interval != '1y' else 100)
            ]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error occurred: {e}")

    except Exception as e:
        print(f"Error occurred: {e}")

def countdown_to_next_run(next_run_time):
    while True:
        now = datetime.now()
        remaining_time = next_run_time - now
        if remaining_time.total_seconds() <= 0:
            break
        print(f"\rTime until next run: {str(remaining_time).split('.')[0]}", end="")
        time.sleep(1)
    print("\n")

import schedule

def main():
    first_run = input("First running? (y/n): ").strip().lower()
    interval_scrapper = '1y' if first_run in ['y', 'yes'] else '1h' if first_run in ['n', 'no'] else None
    if interval_scrapper is None:
        print("Invalid choice. Exiting.")
        return

    print("\nSelect execution mode:")
    print("1. Sequential")
    print("2. Parallel")
    mode = input("Enter the number of your choice (1 or 2): ")

    if mode not in ['1', '2']:
        print("Invalid choice. Exiting.")
        return

    # Prompt for the next interval and scheduler setup
    if first_run in ['y', 'yes']:
        print("\nThe first run will be done with a 1 year interval.") 
        print("\nSelect interval for future scrapes after the first run:")
    else:
        print("\nSelect the interval for running the scrapers:")

    print("1. 1 Hour (1h)")
    print("2. 1 Day (1d)")
    print("3. 7 Days (7d)")
    print("4. 1 Month (1M)")
    print("5. 1 Year (1y)")
    interval_choice = input("Enter the number of your choice: ")

    next_interval_scrapper = {
        '1': '1h',
        '2': '1d',
        '3': '7d',
        '4': '1M',
        '5': '1y'
    }.get(interval_choice)

    if not next_interval_scrapper:
        print("Invalid interval choice. Exiting.")
        return

    print("\nSelect the interval for scheduling the scrapers:")
    print("1. Every few seconds")
    print("2. Every hour at a specific minute")
    schedule_choice = input("Enter the number of your choice (1 or 2): ")

    if schedule_choice == '1':
        interval_value = int(input("Enter the interval in seconds: "))
        schedule_interval = schedule.every(interval_value).seconds
    elif schedule_choice == '2':
        minute = input("Enter the minute (00-59) when the scrapers should run every hour: ").zfill(2)
        if not minute.isdigit() or not (0 <= int(minute) < 60):
            print("Invalid minute value. Exiting.")
            return
        schedule_interval = schedule.every().hour.at(f":{minute}")
        print(f"Scrapers will run every hour at minute :{minute}.")
        print("\n")
    else:
        print("Invalid scheduling choice. Exiting.")
        return

    # Schedule the selected mode and interval for future runs
    if mode == '1':
        schedule_interval.do(run_scrapers_sequential, next_interval_scrapper)
    elif mode == '2':
        schedule_interval.do(run_scrapers_parallel, next_interval_scrapper)

    # Run the scraper with '1y' interval first if it's the first run
    if first_run in ['y', 'yes']:
        if mode == '1':
            run_scrapers_sequential('1y')
        elif mode == '2':
            run_scrapers_parallel('1y')

    # Keep the script running and check for scheduled tasks
    while True:
        next_run_time = schedule.next_run()
        print(f"\nNext run scheduled at: {next_run_time}")
        countdown_to_next_run(next_run_time)
        schedule.run_pending()

if __name__ == "__main__":
    main()

