from flask import Blueprint, request, jsonify
from app.models.lending import LendingSimulation
from app.utils import run_boundary_analysis
import numpy as np

lending_bp = Blueprint('lending', __name__)

@lending_bp.route('/run_lending_simulation', methods=['POST'])
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