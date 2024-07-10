# app/routes/tokenomics.py

from flask import Blueprint, request, jsonify
from app.models.tokenomics import TokenomicsSimulation
import numpy as np

tokenomics_bp = Blueprint('tokenomics', __name__)

@tokenomics_bp.route('/run_tokenomics_simulation', methods=['POST'])
def run_tokenomics_simulation():
    data = request.json
    simulation = TokenomicsSimulation(
        total_token_emitted=float(data['total_token_emitted']),
        base_monthly_emissions_rate=float(data['base_monthly_emissions_rate']),
        emissions_step_up=float(data['emissions_step_up']),
        mom_tvl_growth=float(data['mom_tvl_growth']),
        mom_borrow_growth=float(data['mom_borrow_growth']),
        token_price=float(data['token_price']),
        total_team_allocation=float(data['total_team_allocation']),
        cliff=int(data['cliff']),
        vesting_months=int(data['vesting_months']),
        base_vesting_per_month=float(data['base_vesting_per_month']),
        vesting_step_up=float(data['vesting_step_up']),
        initial_tvl=float(data['tvl']),
        initial_borrow=float(data['borrow']),
        initial_token_circulating=float(data['token_circulating']),
        monthly_liquidations=float(data['monthly_liquidations']),
        monthly_sequencer_fees=float(data['monthly_sequencer_fees']),
        revenue_distribution_percentage=float(data['revenue_distribution_percentage']),
        lender_percentage=float(data['lender_percentage']),
        reserve_fee=float(data['reserve_fee']),
        admin_fee=float(data['admin_fee']),
        protocol_fee=float(data['protocol_fee']),
        liquidation_fee=float(data['liquidation_fee']),
        base_rate=float(data['base_rate']),
        multiplier=float(data['multiplier']),
        kink=float(data['kink']),
        jump_multiplier=float(data['jump_multiplier']),
        initial_reserves=float(data['initial_reserves']),
        protocol_revenue_share=float(data['protocol_revenue_share']),
        target_utilization=float(data['target_utilization'])
    )

    num_simulations = int(data['num_simulations'])
    num_months = int(data['num_months'])

    results = simulation.run_simulations(num_simulations, num_months)

    return jsonify(results)