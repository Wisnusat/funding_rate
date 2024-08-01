from flask import Blueprint, request, jsonify
from app.middleware.auth_middleware import token_required
from app.services.fr_aevo import aevo
from app.services.fr_service import FrService

funding_rates_bp = Blueprint('funding-rates', __name__)

@funding_rates_bp.route('/aevo', methods=['GET'])
@token_required
def get_aevo_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    time = request.args.get('time', default='1h', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        rates = aevo.fetch_all_funding_history(page, limit, time, sort_order, keyword)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/hyperliquid', methods=['GET'])
@token_required
def get_hyperliquid_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    try:
        # rates = aevo.fetch_all_funding_history(page, limit)
        rates = {
            'code': 200,
            'message': 'HyperLiquid funding rates coming soon!'
        }
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/bybit', methods=['GET'])
@token_required
def get_bybit_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    try:
        # rates = aevo.fetch_all_funding_history(page, limit)
        rates = {
            'code': 200,
            'message': 'Bybit funding rates coming soon!'
        }
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@funding_rates_bp.route('/gateio', methods=['GET'])
@token_required
def get_gateio_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    try:
        # rates = aevo.fetch_all_funding_history(page, limit)
        rates = {
            'code': 200,
            'message': 'Gateio funding rates coming soon!'
        }
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500