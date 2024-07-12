# app/routes/fund_raising.py

from flask import Blueprint, request, jsonify
from app.models.fund_raising import FundRaising

fund_raising_bp = Blueprint('fund_raising', __name__)

@fund_raising_bp.route('/generate_fund_raising_charts', methods=['POST'])
def generate_fund_raising_charts():
    data = request.json
    fund_raising = FundRaising(data['allocationData'], data['vestingData'], data['airdropModule'])
    
    pie_chart = fund_raising.generate_pie_chart()
    vesting_chart = fund_raising.generate_vesting_chart()
    
    return jsonify({
        'pie_chart': pie_chart.to_json(),
        'vesting_chart': vesting_chart.to_json()
    })