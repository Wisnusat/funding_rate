from flask import Blueprint, request, jsonify
from app.middleware.auth_middleware import token_required
from app.services.fr_aevo import Aevo
from app.services.fr_hyperliquid import Hyperliquid
from app.services.fr_bybit import Bybit
from app.services.fr_gateio import Gateio
from app.services.fr_service import FrService
from app.services.scp import scrapper_with_pagination, get_coins

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