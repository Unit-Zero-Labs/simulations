from flask import Blueprint, request, jsonify
from app.models.lp_sim import LPSimulation
from datetime import datetime, timedelta

lp_sim_bp = Blueprint('lp_sim', __name__)

@lp_sim_bp.route('/run_lp_simulation', methods=['POST'])
def run_lp_simulation():
    data = request.json
    token_launch_price = float(data['tokenLaunchPrice'])
    lp_pool_allocation = float(data['lpPoolAllocation'])
    initial_total_supply = float(data['initialTotalSupply'])
    simulation_days = int(data['simulationDays'])
    mu = float(data['mu'])
    sigma = float(data['sigma'])
    paths = int(data['paths'])
    
    token_adoption_velocity = float(data['tokenAdoptionVelocity'])
    avg_token_utility_allocation = float(data['avgTokenUtilityAllocation'])
    avg_token_holding = float(data['avgTokenHolding'])
    avg_token_sell = float(data['avgTokenSell'])

    lp_sim = LPSimulation(
        token_launch_price, lp_pool_allocation, initial_total_supply, simulation_days, mu, sigma, paths,
        token_adoption_velocity, avg_token_utility_allocation, avg_token_holding, avg_token_sell
    )
    results = lp_sim.simulate()
    
    start_date = datetime.now()
    date_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(simulation_days)]

    return jsonify({
        'dates': date_range,
        'price_percentiles': results['price_percentiles'].tolist(),
        'tvl_percentiles': results['tvl_percentiles'].tolist(),
        'il_percentiles': results['il_percentiles'].tolist(),
        'median_prices': results['median_prices'].tolist(),
        'median_tvl': results['median_tvl'].tolist(),
        'median_il': results['median_il'].tolist(),
        'initial_market_cap': results['initial_market_cap'],
        'initial_liquidity': results['initial_liquidity']
    })