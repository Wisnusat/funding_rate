import os
from flask import Blueprint, request, jsonify
from app.middleware.auth_middleware import token_required
from app.services.fr_aevo import Aevo
from app.services.fr_hyperliquid import Hyperliquid
from app.services.fr_bybit import Bybit
from app.services.fr_gateio import Gateio
from app.services.fr_service import FrService
from app.services.scp import scrapper_with_pagination, get_coins
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

funding_rates_bp = Blueprint('funding-rates', __name__)

# NEW
@funding_rates_bp.route('/aggregated-funding', methods=['GET'])
@token_required
def get_aggregated_funding(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    time = request.args.get('time', default='1h', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        aggregated_data = scrapper_with_pagination(page, limit, time, sort_order, keyword)
        return jsonify(aggregated_data)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/coins', methods=['GET'])
@token_required
def get_available_coins(current_user):
    keyword = request.args.get('keyword', default=None, type=str)
    try:
        coins = get_coins(keyword)
        return jsonify(coins)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

# detail coin by coinmarketcap
@funding_rates_bp.route('/coin-details-cmc', methods=['GET'])
@token_required
def get_detail_coin(current_user):
    # Fetch API Key from environment variables
    COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')

    if not COINMARKETCAP_API_KEY:
        return jsonify({"error": "CoinMarketCap API key is missing"}), 500

    # Prepare headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
    }

    # Get the coin symbol from the request query parameters
    coin = request.args.get('coin', None)

    if not coin:
        return jsonify({"error": "Please provide a coin symbol"}), 400

    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?symbol={coin.upper()}"

    try:
        # Make the request to CoinMarketCap API
        response = requests.get(url, headers=headers)

        # Check for successful response
        if response.status_code == 200:
            data = response.json()

            # Ensure response has the correct structure
            if 'data' in data and coin.upper() in data['data']:
                return jsonify(data), 200
            else:
                return jsonify({"error": "Invalid response structure from CoinMarketCap"}), 502
        elif response.status_code == 401:
            return jsonify({"error": "Invalid API Key"}), 401
        else:
            return jsonify({"error": "Unable to fetch data from CoinMarketCap"}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

# OLD
@funding_rates_bp.route('/tickers', methods=['GET'])
@token_required
def get_tickers(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    time = request.args.get('time', default='1h', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        tickers = FrService.tickers(page, limit, time, sort_order, keyword)
        return jsonify(tickers)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/hyperliquid', methods=['GET'])
@token_required
def get_hyperliquid_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    time = request.args.get('time', default='1h', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        rates = Hyperliquid.fetch_funding_rate_history(page, limit, time, sort_order, keyword)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/aevo', methods=['GET'])
@token_required
def get_aevo_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    time = request.args.get('time', default='1h', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        rates = Aevo.fetch_all_funding_history(page, limit, time, sort_order, keyword)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/bybit', methods=['GET'])
@token_required
def get_bybit_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    time = request.args.get('time', default='1h', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        rates = Bybit.fetch_funding_rate_history(page, limit, time, sort_order, keyword)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/gateio', methods=['GET'])
@token_required
def get_gateio_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    time = request.args.get('time', default='1h', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        rates = Gateio.fetch_funding_rate_history(page, limit, time, sort_order, keyword)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500