from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.stats import norm
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
        self.total_deposits = 10000000  # New: total deposits in the protocol
        self.interest_rate = 0.05  # New: annual interest rate
        self.liquidation_penalty = 0.1  # New: liquidation penalty

    def update_price(self, new_price):
        self.asset_price = max(new_price, 0.000001)  # Ensure price is never zero
        return self.check_liquidation()

    def borrow(self, amount):
        max_borrow = self.collateral_amount * self.asset_price * self.max_ltv
        if self.loan_amount + amount <= max_borrow:
            self.loan_amount += amount
            return True
        return False

    def check_liquidation(self):
        if self.collateral_amount * self.asset_price > 0:
            current_ltv = self.loan_amount / (self.collateral_amount * self.asset_price)
            return current_ltv >= self.liquidation_threshold
        return self.loan_amount > 0

    def calculate_utilization_ratio(self):
        return self.loan_amount / max(self.total_deposits, 0.000001)

    def calculate_interest(self, days):
        return self.loan_amount * (1 + self.interest_rate) ** (days / 365) - self.loan_amount

    def liquidate(self):
        liquidation_amount = self.loan_amount * (1 + self.liquidation_penalty)
        collateral_value = self.collateral_amount * self.asset_price
        if liquidation_amount > collateral_value:
            self.collateral_amount = 0
            self.loan_amount = max(0, self.loan_amount - collateral_value)
        else:
            self.collateral_amount = max(0, self.collateral_amount - liquidation_amount / self.asset_price)
            self.loan_amount = 0

################ OU ####################


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

################ GBM ####################

def geometric_brownian_motion(S0, mu, sigma, T, N, paths):
    dt = T/N
    t = np.linspace(0, T, N)
    W = np.random.normal(0, np.sqrt(dt), size=(paths, N))
    W = np.cumsum(W, axis=1)
    
    X = (mu - 0.5 * sigma**2) * t + sigma * W
    S = S0 * np.exp(X)
    return S

############## BOUNDARY ##################


def run_boundary_analysis(simulation, price_scenarios, borrow_scenarios):
    results = []
    for price_scenario, borrow_scenario in zip(price_scenarios, borrow_scenarios):
        sim = copy.deepcopy(simulation)
        ltv_ratios = []
        utilization_ratios = []
        liquidation_events = []
        for day, (price, borrow_amount) in enumerate(zip(price_scenario, borrow_scenario)):
            liquidated = sim.update_price(price)
            if not liquidated:
                sim.borrow(borrow_amount)
            else:
                sim.liquidate()
            
            sim.loan_amount += sim.calculate_interest(1)  # Add daily interest
            
            # Safeguard against division by zero
            if sim.collateral_amount * sim.asset_price > 0:
                ltv_ratio = sim.loan_amount / (sim.collateral_amount * sim.asset_price)
            else:
                ltv_ratio = float('inf') if sim.loan_amount > 0 else 0
            
            ltv_ratios.append(float(ltv_ratio))
            
            # Safeguard against division by zero for utilization ratio
            if sim.total_deposits > 0:
                utilization_ratio = sim.loan_amount / sim.total_deposits
            else:
                utilization_ratio = 1 if sim.loan_amount > 0 else 0
            
            utilization_ratios.append(float(utilization_ratio))
            liquidation_events.append(bool(liquidated))

        results.append({
            'price_scenario': [float(p) for p in price_scenario],
            'borrow_scenario': [float(b) for b in borrow_scenario],
            'final_price': float(price_scenario[-1]),
            'ltv_ratios': ltv_ratios,
            'utilization_ratios': utilization_ratios,
            'liquidation_events': liquidation_events
        })
    return results



############## APP ROUTES ##############

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
    simulation.total_deposits = float(data['total_deposits'])
    simulation.interest_rate = float(data['interest_rate'])
    simulation.liquidation_penalty = float(data['liquidation_penalty'])

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
        'days': list(range(days))
    })

@app.route('/run_non_stable_pool_simulation', methods=['POST'])
def run_non_stable_pool_simulation():
    data = request.json
    S0 = float(data['initial_price'])
    mu = float(data['mu'])
    sigma = float(data['sigma'])
    paths = int(data['paths'])
    T = 1  # 1 year simulation
    N = 365  # Daily price points

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

if __name__ == '__main__':
    app.run(debug=True)