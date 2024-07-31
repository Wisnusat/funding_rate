from flask import Blueprint, request, jsonify
from app.middleware.auth_middleware import token_required
from app.services.fr_aevo import aevo

funding_rates_bp = Blueprint('funding-rates', __name__)

@funding_rates_bp.route('/aevo', methods=['GET'])
@token_required
def get_aevo_rates(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    try:
        rates = aevo.fetch_all_funding_history(page, limit, keywords)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500
    