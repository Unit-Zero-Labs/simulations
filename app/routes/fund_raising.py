# app/routes/fund_raising.py

from flask import Blueprint, request, jsonify
from app.models.fund_raising import FundRaising

fund_raising_bp = Blueprint('fund_raising', __name__)

@fund_raising_bp.route('/generate_fund_raising_charts', methods=['POST'])
def generate_fund_raising_charts():
    data = request.json
    fund_raising = FundRaising(
        data['allocationData'],
        data['vestingData'],
        data['airdropModule'],
        float(data['initialTotalSupply']),
        float(data['publicSaleValuation'])
    )
    
    return jsonify(fund_raising.generate_charts())