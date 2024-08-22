import numpy as np
from datetime import datetime, timedelta

def nanoseconds_to_datetime(nanoseconds):
    # Convert nanoseconds to seconds (1 second = 1e9 nanoseconds)
    seconds = nanoseconds / 1e9

    # Create a datetime object from the seconds
    timestamp = datetime.utcfromtimestamp(seconds)

    return timestamp

def get_timestamp_for_interval(interval):
    current_time = datetime.utcnow()
    end_time = int(current_time.timestamp() * 1e9)  # API might need seconds; adjust accordingly

    intervals = {
        '1h': 3600,
        '1d': 86400,
        '7d': 7 * 86400,
        '1M': 30 * 86400,
        '1y': 365 * 86400
    }

    if interval not in intervals:
        raise ValueError("Invalid interval")

    start_time = end_time - int(intervals[interval] * 1e9)
    return int(start_time), int(end_time)

def get_timeframe(timeframe: str):
    now = datetime.now()
    if timeframe == '1h':
        since = now - timedelta(hours=1)
    elif timeframe == '1d':
        since = now - timedelta(days=1)
    elif timeframe == '7d':
        since = now - timedelta(days=7)
    elif timeframe == '1M':
        since = now - timedelta(days=30)  # Approximation for 1 month
    elif timeframe == '1y':
        since = now - timedelta(days=365)
    else:
        raise ValueError("Unsupported timeframe. Use '1h', '1d', '7d', '1M', or '1y'.")

    since_timestamp = int(since.timestamp() * 1000)
    until_timestamp = int(now.timestamp() * 1000)
    return since_timestamp, until_timestamp

def accumulate_funding_rates(data):
    if not data:
        return "0.000000"

    np_data = np.array(data)
    funding_rates = np_data[:, 2].astype(float)
    total_funding_rate = np.sum(funding_rates)
    return f"{total_funding_rate:.6f}"
