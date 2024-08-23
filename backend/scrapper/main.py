import time
import schedule
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from platforms.aevo import Aevo
from platforms.bybit import Bybit
from platforms.hyperliquid import Hyperliquid
from platforms.gateio import Gateio

def run_scrapers_sequential():
    """Run the scrapers sequentially."""
    try:
        # print("\n\nRunning AEVO scraper...\n")
        # Aevo().run('1h')
        # print("\nAEVO scraper completed.\n")

        print("\nRunning Bybit scraper...\n")
        Bybit().run('1d')
        print("\nBybit scraper completed.\n")

        # print("\nRunning Hyperliquid scraper...\n")
        # Hyperliquid().run('1h')
        # print("\nHyperliquid scraper completed.\n")

        # print("\nRunning Gate.io scraper...\n")
        # Gateio().run(10)
        # print("\nGate.io scraper completed.\n")

    except Exception as e:
        print(f"Error occurred: {e}")

def run_scrapers_parallel():
    """Run the scrapers in parallel."""
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                # executor.submit(Aevo().run, '1h'),
                executor.submit(Bybit().run, '1h'),
                # executor.submit(Hyperliquid().run, '1h'),
                # executor.submit(Gateio().run, 10)
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

def main():
    print("Select execution mode:")
    print("1. Sequential")
    print("2. Parallel")
    mode = input("Enter the number of your choice (1 or 2): ")

    if mode not in ['1', '2']:
        print("Invalid choice. Exiting.")
        return

    print("\nSelect the interval for running the scrapers:")
    print("1. Every few seconds")
    print("2. Every hour at a specific minute")
    interval_choice = input("Enter the number of your choice (1 or 2): ")

    if interval_choice == '1':
        interval_value = int(input("Enter the interval in seconds: "))
        schedule_interval = schedule.every(interval_value).seconds
    elif interval_choice == '2':
        minute = input("Enter the minute (00-59) when the scrapers should run every hour: ").zfill(2)
        if not minute.isdigit() or not (0 <= int(minute) < 60):
            print("Invalid minute value. Exiting.")
            return
        schedule_interval = schedule.every().hour.at(f":{minute}")
    else:
        print("Invalid interval choice. Exiting.")
        return

    if mode == '1':
        schedule_interval.do(run_scrapers_sequential)
    elif mode == '2':
        schedule_interval.do(run_scrapers_parallel)

    # Keep the script running and check for scheduled tasks
    while True:
        next_run_time = schedule.next_run()
        print(f"\nNext run scheduled at: {next_run_time}")
        countdown_to_next_run(next_run_time)
        schedule.run_pending()

if __name__ == "__main__":
    main()
