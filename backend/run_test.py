import requests
from datetime import datetime, timedelta

def fetch_funding_history(ticker, start_time, end_time):
    url = "https://api.aevo.xyz/funding-history"
    params = {
        'instrument_name': ticker,
        'start_time': int(start_time.timestamp() * 1_000_000_000),
        'end_time': int(end_time.timestamp() * 1_000_000_000),
        'limit': 50
    }
    headers = {"accept": "application/json"}
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json().get('funding_history', [])
    else:
        print(f"Error: {response.status_code}")
        return []

def calculate_cumulative_rate(data):
    return sum(float(record[2]) for record in data if record[2] is not None)

def calculate_daily_average_rate(data):
    daily_rates = {}
    for record in data:
        if record[2] is not None:
            date = datetime.fromtimestamp(int(record[1]) / 1_000_000_000).date()
            if date not in daily_rates:
                daily_rates[date] = []
            daily_rates[date].append(float(record[2]))
    
    daily_averages = {date: sum(rates) / len(rates) for date, rates in daily_rates.items()}
    return daily_averages

def calculate_weekly_average_rate(data):
    weekly_rates = {}
    for record in data:
        if record[2] is not None:
            date = datetime.fromtimestamp(int(record[1]) / 1_000_000_000).date()
            week_start = date - timedelta(days=date.weekday())  # Monday as the start of the week
            if week_start not in weekly_rates:
                weekly_rates[week_start] = []
            weekly_rates[week_start].append(float(record[2]))
    
    weekly_averages = {week_start: sum(rates) / len(rates) for week_start, rates in weekly_rates.items()}
    return weekly_averages

# Example usage
ticker = "BTC-PERP"
current_time = datetime.now()
start_time = current_time - timedelta(days=30)
end_time = current_time

data = fetch_funding_history(ticker, start_time, end_time)

cumulative_rate = calculate_cumulative_rate(data)
daily_average_rates = calculate_daily_average_rate(data)
weekly_average_rates = calculate_weekly_average_rate(data)

print("Cumulative Funding Rate:", cumulative_rate)
print("Daily Average Funding Rates:", daily_average_rates)
print("Weekly Average Funding Rates:", weekly_average_rates)
