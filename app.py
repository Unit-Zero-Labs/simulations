from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import copy

app = Flask(__name__, static_folder='static')

class OUParams:
    def __init__(self, alpha, gamma, beta, X_0=None):
        self.alpha = alpha
        self.gamma = gamma
        self.beta = beta
        self.X_0 = X_0

class LendingSimulation:
    def __init__(self):
        self.asset_price = 1.0
        self.collateral_amount = 1000000
        self.loan_amount = 0
        self.max_ltv = 0.8
        self.liquidation_threshold = 0.9
        self.oracle_update_frequency = 60

    def update_price(self, new_price):
        self.asset_price = new_price
        return self.check_liquidation()

    def borrow(self, amount):
        max_borrow = self.collateral_amount * self.asset_price * self.max_ltv
        if self.loan_amount + amount <= max_borrow:
            self.loan_amount += amount
            return True
        return False

    def check_liquidation(self):
        current_ltv = self.loan_amount / (self.collateral_amount * self.asset_price)
        return current_ltv >= self.max_ltv * self.liquidation_threshold

def simulate_OU_process(T, runs, ou_params):
    dt = 1.0
    data = np.zeros((runs, T))
    for run in range(runs):
        X_t = ou_params.X_0 if ou_params.X_0 is not None else ou_params.gamma
        data[run, 0] = X_t
        for t in range(1, T):
            dW = np.random.normal(0, np.sqrt(dt))
            dX = ou_params.alpha * (ou_params.gamma - X_t) * dt + ou_params.beta * dW
            X_t += dX
            data[run, t] = X_t
    return data

def geometric_brownian_motion(S0, mu, sigma, T, N, paths):
    dt = T/N
    t = np.linspace(0, T, N)
    W = np.random.normal(0, np.sqrt(dt), size=(paths, N-1))
    W = np.concatenate((np.zeros((paths, 1)), W), axis=1)
    W = np.cumsum(W, axis=1)
    
    X = (mu - 0.5 * sigma**2) * t + sigma * W
    S = S0 * np.exp(X)
    return S

def run_boundary_analysis(simulation, price_scenarios):
    results = []
    for scenario in price_scenarios:
        sim = copy.deepcopy(simulation)
        max_borrowed = 0
        ltv_ratios = []
        liquidation_events = []
        for price in scenario:
            liquidated = sim.update_price(price)
            while sim.borrow(1000):
                max_borrowed = sim.loan_amount
            ltv_ratios.append(sim.loan_amount / (sim.collateral_amount * sim.asset_price))
            liquidation_events.append(liquidated)
        results.append({
            'scenario': scenario,
            'max_borrowed': max_borrowed,
            'final_price': scenario[-1],
            'ltv_ratios': ltv_ratios,
            'liquidation_events': liquidation_events
        })
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_lending_simulation', methods=['POST'])
def run_lending_simulation():
    data = request.json
    simulation = LendingSimulation()
    simulation.collateral_amount = float(data['collateral_amount'])
    simulation.max_ltv = float(data['max_ltv'])
    simulation.liquidation_threshold = float(data['liquidation_threshold'])

    scenarios = [
        [1.0] * 10,  # stable price
        [1.0] * 5 + [10.0] + [1.0] * 4,  # price spike
        [1.0] * 5 + [0.1] + [1.0] * 4,  # price crash
        [1.0 + 0.1*i for i in range(10)],  # gradual increase
        [1.0 - 0.05*i for i in range(10)]  # gradual decrease
    ]

    results = run_boundary_analysis(simulation, scenarios)
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
        'days': list(range(days))
    })

@app.route('/run_non_stable_pool_simulation', methods=['POST'])
def run_non_stable_pool_simulation():
    data = request.json
    S0 = float(data['initial_price'])
    mu = float(data['mu'])
    sigma = float(data['sigma'])
    paths = int(data['paths'])
    T = 1
    N = 365

    prices = geometric_brownian_motion(S0, mu, sigma, T, N, paths)
    df = pd.DataFrame(prices.T)
    median_prices = df.median(axis=1).tolist()
    min_prices = df.min(axis=1).tolist()
    max_prices = df.max(axis=1).tolist()

    return jsonify({
        'median_prices': median_prices,
        'min_prices': min_prices,
        'max_prices': max_prices,
        'days': list(range(N))
    })

if __name__ == '__main__':
    app.run(debug=True)