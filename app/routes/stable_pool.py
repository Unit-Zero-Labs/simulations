from flask import Blueprint, request, jsonify
from app.simulations.ou_process import OUParams, simulate_OU_process
import pandas as pd
from datetime import datetime, timedelta

stable_pool_bp = Blueprint('stable_pool', __name__)

@stable_pool_bp.route('/run_stable_pool_simulation', methods=['POST'])
def run_stable_pool_simulation():
    data = request.json
    initial_price = float(data['initial_price'])
    alpha = float(data['alpha'])
    gamma = float(data['gamma'])
    beta = float(data['beta'])
    days = int(data['days'])

    ou_params = OUParams(alpha=alpha, gamma=gamma, beta=beta, X_0=initial_price)
    prices = simulate_OU_process(days, 1, ou_params)[0]

    return jsonify({
        'prices': prices.tolist(),
        'days': list(range(days)),
        'gamma': gamma 
    })