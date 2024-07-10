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
        initial_tvl=float(data['initial_tvl']),
        initial_borrow=float(data['initial_borrow']),
        initial_token_circulating=float(data['initial_token_circulating']),
        initial_reserves=float(data['initial_reserves']),
        token_price=float(data['token_price']),
        protocol_revenue_share=float(data['protocol_revenue_share']),
        target_utilization=float(data['target_utilization']),
        base_monthly_emissions_rate=float(data['base_monthly_emissions_rate']),
        emissions_step_up=float(data['emissions_step_up']),
        mom_tvl_growth=float(data['mom_tvl_growth']),
        mom_borrow_growth=float(data['mom_borrow_growth']),
        total_team_allocation=float(data['total_team_allocation']),
        cliff=int(data['cliff']),
        vesting_months=int(data['vesting_months']),
        base_vesting_per_month=float(data['base_vesting_per_month']),
        vesting_step_up=float(data['vesting_step_up']),
        monthly_liquidations=float(data['monthly_liquidations']),
        monthly_sequencer_fees=float(data['monthly_sequencer_fees']),
        base_rate=float(data['base_rate']),
        multiplier=float(data['multiplier']),
        kink=float(data['kink']),
        jump_multiplier=float(data['jump_multiplier'])
    )

    num_simulations = int(data['num_simulations'])
    num_months = int(data['num_months'])

    results = simulation.run_simulations(num_simulations, num_months)

    return jsonify(results)