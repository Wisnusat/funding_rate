import time
import schedule
from datetime import datetime, timedelta

from platforms.aevo import Aevo
from platforms.bybit import Bybit
from platforms.hyperliquid import Hyperliquid
from platforms.gateio import Gateio

def run_scrapers():
    try:
        # Jalankan AEVO scraper
        print("\n\nRunning AEVO scraper...\n")
        Aevo().run('1h')
        print("\nAEVO scraper completed.\n")

        # Jalankan Bybit scraper
        print("\nRunning Bybit scraper...\n")
        Bybit().run('1h')
        print("\nBybit scraper completed.\n")

        # Jalankan Hyperliquid scraper
        print("\nRunning Hyperliquid scraper...\n")
        Hyperliquid().run('1h')
        print("\nHyperliquid scraper completed.\n")

        # Jalankan Gate.io scraper
        print("\nRunning Gate.io scraper...\n")
        Gateio().run(10)
        print("\nGate.io scraper completed.\n")

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
    # Schedule the scrapers to run every 10 seconds
    # schedule.every(10).seconds.do(run_scrapers)

    # Schedule the scrapers to run every hour
    schedule.every().hour.at(":30").do(run_scrapers)
    
    # Keep the script running and check for scheduled tasks
    while True:
        next_run_time = schedule.next_run()
        print(f"\nNext run scheduled at: {next_run_time}")
        countdown_to_next_run(next_run_time)
        schedule.run_pending()

if __name__ == "__main__":
    main()
