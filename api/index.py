from flask import Flask, request, jsonify, send_from_directory
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.simulations.ou_process import OUParams, simulate_OU_process
from app.simulations.gbm import geometric_brownian_motion
from app.models.lending import LendingSimulation
from app.utils import run_boundary_analysis

app = Flask(__name__)

@app.route('/')
def serve():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

@app.route('/run_lending_simulation', methods=['POST'])
def run_lending_simulation():
    data = request.json
    simulation = LendingSimulation(
        collateral_amount=float(data['collateral_amount']),
        max_ltv=float(data['max_ltv']),
        liquidation_threshold=float(data['liquidation_threshold']),
        total_deposits=float(data['total_deposits']),
        interest_rate=float(data['interest_rate']),
        liquidation_penalty=float(data['liquidation_penalty'])
    )
    price_scenarios = [
        [1.0] * 365,  # stable price
        [1.0 + 0.001*i for i in range(365)],  # gradual increase
        [1.0 - 0.0005*i for i in range(365)],  # gradual decrease
        [1.0 + 0.1*np.sin(2*np.pi*i/30) for i in range(365)],  # sinusoidal
        [1.0] * 182 + [0.5] * 183,  # sudden crash
    ]

    borrow_scenarios = [
        [1000] * 365,  # constant borrowing
        [1000 + 10*i for i in range(365)],  # increasing borrowing
        [5000 - 10*i for i in range(365)],  # decreasing borrowing
        [5000 if i % 30 == 0 else 0 for i in range(365)],  # periodic large borrows
        [0] * 365,  # no additional borrowing
    ]

    results = run_boundary_analysis(simulation, price_scenarios, borrow_scenarios)
    return jsonify(results)

@app.route('/run_stable_pool_simulation', methods=['POST'])
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

@app.route('/run_non_stable_pool_simulation', methods=['POST'])
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

# This is for Vercel
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Hello, World!'.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Received POST data'.encode('utf-8'))

if __name__ == '__main__':
    app.run(debug=True)