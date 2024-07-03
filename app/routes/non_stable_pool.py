from flask import Blueprint, request, jsonify
from app.simulations.gbm import geometric_brownian_motion
from datetime import datetime, timedelta
import pandas as pd
import numpy as np 

non_stable_pool_bp = Blueprint('non_stable_pool', __name__)

@non_stable_pool_bp.route('/run_non_stable_pool_simulation', methods=['POST'])
def run_non_stable_pool_simulation():
    data = request.json
    S0 = float(data['initial_price'])
    mu = float(data['mu'])
    sigma = float(data['sigma'])
    paths = int(data['paths'])
    T = 1  # 1 year simulation
    N = 365  # daily price points

    prices = geometric_brownian_motion(S0, mu, sigma, T, N, paths)
    
    df = pd.DataFrame(prices.T)
    percentiles = [5, 25, 50, 75, 95]
    percentile_df = df.quantile(q=[p/100 for p in percentiles], axis=1).T

    start_date = datetime(2023, 1, 1)
    date_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(N)]

    return jsonify({
        'dates': date_range,
        'percentile_prices': percentile_df.values.T.tolist(),
        'median_prices': percentile_df[0.5].tolist()
    })