import requests
import time
import json
from fake_useragent import UserAgent  # For rotating user agents
from app.db.models import AevoDB
from app.utils import get_timestamp_for_interval
from app.logger import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.db.operations import save_to_database, delete_all_data, count_rows

class Aevo:
    @staticmethod
    def run(interval='1h'):
        """
        Run the AEVO scraper process for the given interval.

        This method fetches instrument names, scrapes data for those instruments using threading, processes the data, and saves it to the database.

        Args:
            interval (str): The interval at which to run the scraper, e.g., '1h', '1d'.

        Returns:
            None
        """
        aevo_assets = Aevo.fetch_aevo_instrument_names()
        aevo_assets = aevo_assets[:5]
        logger.info(f"[AEVO]Running scraper for {interval} interval with assets: {len(aevo_assets)}")

        # Start timing
        start_time = time.time()

        # Scrape data from AEVO
        aevo_data = Aevo.runWithThreading(Aevo.fetch_aevo_data, interval, aevo_assets)

        # Process data to match the expected format
        processed_aevo_data = Aevo.process_aevo_data(aevo_data)

        # End timing
        end_time = time.time()
        duration = end_time - start_time

        # Display duration
        logger.info(f"[AEVO]Data scraping completed in {duration:.2f} seconds.")

        save_status = save_to_database(processed_aevo_data, AevoDB)
        if save_status == True:
            logger.info(f"[AEVO]Data saved to the database successfully.")
        else:
            logger.error(f"[AEVO]{save_status}")

    def process_aevo_data(data):
        """
        Process raw AEVO data into a structured format.

        Args:
            data (list): A list of raw data entries fetched from AEVO.

        Returns:
            list: A list of processed data entries.
        """
        processed_data = []
        for entry in data:
            coin_symbol = entry[0].replace('-PERP', '')
            processed_entry = [
                coin_symbol,
                int(entry[1]),
                entry[2],
                entry[3]
            ]
            processed_data.append(processed_entry)
        return processed_data

    @staticmethod
    def delete_all_data():
        """
        Delete all data from the AEVO database.

        This method deletes all rows in the AevoDB table.

        Returns:
            None
        """
        delete_all_data(AevoDB)

    @staticmethod
    def count_rows():
        """
        Count the number of rows in the AEVO database.

        This method counts and logger.infos the number of rows in the AevoDB table.

        Returns:
            None
        """
        count = count_rows(AevoDB)
        logger.info(f"[AEVO]Number of rows in the database: {count}")

    def fetch_aevo_instrument_names():
        """
        Fetch instrument names from AEVO API.

        This method retrieves the instrument names available in AEVO by making an API call.

        Returns:
            list: A list of instrument names fetched from the AEVO API.
        """
        # url = "https://api.aevo.xyz/assets"
        # headers = {
        #     'accept': 'application/json'
        # }

        try:
            # response = requests.get(url, headers=headers)
            # response.raise_for_status()
            # instrument_names = response.json()

            with open("data_const/avail_aevo.json", 'r', encoding='utf-8') as f:
                instrument_names = json.load(f)
            return instrument_names

        except requests.RequestException as e:
            logger.info(f"[AEVO]An error occurred while fetching instrument names: {e}")
            return []

    
    def fetch_aevo_data(instrument_name, start_time, end_time, limit=50):
        """
        Fetch funding rate history data from AEVO for a given instrument with rotating User-Agent in every loop.

        This method fetches funding rate history for a given instrument by making an API call.
        It retries up to a set limit in case of 429 (Too Many Requests) or 503 (Service Unavailable) errors,
        and rotates the User-Agent for every request to mimic different devices.

        Args:
            instrument_name (str): The name of the instrument to fetch funding data for.
            start_time (int): The start timestamp for fetching data.
            end_time (int): The end timestamp for fetching data.
            limit (int, optional): The maximum number of data points to retrieve per request. Defaults to 50.

        Returns:
            list: A list of funding history data fetched from the AEVO API.
        """
        url = 'https://api.aevo.xyz/funding-history'
        
        # Create a session object to persist cookies and headers across requests
        session = requests.Session()
        
        # Initialize the fake UserAgent object for rotating User-Agents
        ua = UserAgent()
        
        all_data = []
        current_end_time = end_time

        while current_end_time > start_time:
            # Rotate the User-Agent for every request
            headers = {
                'accept': 'application/json',
                'User-Agent': ua.random  # New User-Agent in each loop iteration
            }

            params = {
                'instrument_name': f"{instrument_name.upper()}-PERP",
                'start_time': str(int(start_time)),
                'end_time': str(int(current_end_time)),
                'limit': limit
            }

            retries = 0
            max_retries = 5  # Increased retry attempts for 429/503 errors
            backoff_factor = 1.5  # Exponential backoff factor

            while retries < max_retries:
                try:
                    # Send a request using the session to maintain cookies and rotating User-Agent
                    response = session.get(url, params=params, headers=headers)
                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json()

                    # Handle rate limiting (429)
                    if response.status_code == 429:
                        retry_after = response.headers.get('Retry-After')
                        wait_time = int(retry_after) if retry_after else backoff_factor ** retries
                        # logger.error(f"Rate limit hit, retrying after {wait_time} seconds with new User-Agent...")
                        time.sleep(wait_time)
                        retries += 1
                        continue  # Retry the same request

                    # Handle server issues (503)
                    elif response.status_code == 503:
                        # logger.error(f"Service unavailable for {instrument_name}. Retrying...")
                        retries += 1
                        wait_time = backoff_factor ** retries
                        time.sleep(wait_time)
                        continue

                    # Successful data fetch
                    all_data.extend(data['funding_history'])
                    
                    # Stop if the number of entries is less than the limit (no more data)
                    if len(data['funding_history']) < limit:
                        return all_data

                    # Update the current_end_time to the timestamp of the earliest data point retrieved
                    current_end_time = min(int(item[1]) for item in data['funding_history'])
                    break  # Exit retry loop for successful request

                except requests.RequestException as e:
                    # Log the error (optionally)
                    # logger.error(f"Error fetching data for {instrument_name}: {e}")
                    
                    # Retry with exponential backoff for other connection issues
                    retries += 1
                    wait_time = backoff_factor ** retries
                    time.sleep(wait_time)

        return all_data


    def runWithThreading(fetch_data_function, interval, instrument_names):
        """
        Run data fetching for multiple instruments concurrently using threading.

        This method fetches data for multiple instruments in parallel using threads.

        Args:
            fetch_data_function (function): The function used to fetch data.
            interval (str): The interval for the data fetch operation.
            instrument_names (list): A list of instrument names to fetch data for.

        Returns:
            list: Combined results from all threads.
        """
        start_time, end_time = get_timestamp_for_interval(interval)

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(fetch_data_function, instrument_name, start_time, end_time)
                for instrument_name in instrument_names
            ]
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.extend(data)

        return results
