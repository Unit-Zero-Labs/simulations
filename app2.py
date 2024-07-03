from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from statsmodels.tsa.stattools import adfuller
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import json
from brownian_motion_generator import simulate_corr_OU_procs, estimate_OU_params, OUParams

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///defi_simulations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
celery = Celery(app.name, broker='redis://localhost:6379/0')
celery.conf.update(app.config)

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super(JSONEncoder, self).default(obj)

app.json_encoder = JSONEncoder

class SimulationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parameters = db.Column(db.JSON, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class HistoricalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

class SimulationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parameters = db.Column(db.JSON, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class HistoricalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

class SimulationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parameters = db.Column(db.JSON, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class HistoricalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())


class SimulationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parameters = db.Column(db.JSON, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class HistoricalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

## SIMULATION APP

@celery.task
def run_defi_simulation(data: Dict[str, Any]) -> Dict[str, Any]:
    T = data['time_steps']
    RUNS = data['num_simulations']
    processes = data['processes']

    ou_params = []
    for process in processes:
        if process.get('use_historical', False):
            params = estimate_params_from_historical(process['asset_name'])
        else:
            params = OUParams(
                alpha=process['alpha'],
                gamma=process['gamma'],
                beta=process['beta'],
                X_0=process.get('X_0'),
                distribution_type=process.get('distribution_type', 'normal')
            )
        ou_params.append(params)

    correlations = data.get('correlations')
    results = simulate_corr_OU_procs(T, tuple(ou_params), RUNS, rho=correlations)


    if data.get('calculate_impermanent_loss', False) and len(processes) >= 2:
        price_ratios = results[:, :, 0] / results[:, :, 1]
        impermanent_loss = calculate_impermanent_loss(price_ratios)
    else:
        impermanent_loss = None

    sim_result = SimulationResult(
        name=data['name'],
        parameters=data,
        results={
            'simulations': results,
            'risk_metrics': risk_metrics,
            'statistical_tests': statistical_tests,
            'impermanent_loss': impermanent_loss
        }
    )
    db.session.add(sim_result)
    db.session.commit()

    return {"simulation_id": sim_result.id}


### FLASK APP

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    task = run_defi_simulation.delay(data)
    return jsonify({"task_id": task.id}), 202

@app.route('/simulation_result/<task_id>')
def simulation_result(task_id):
    task = run_defi_simulation.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

@app.route('/upload_historical_data', methods=['POST'])
def upload_historical_data():
    data = request.json
    historical_data = HistoricalData(
        asset_name=data['asset_name'],
        data=json.dumps(data['data'])
    )
    db.session.add(historical_data)
    db.session.commit()
    return jsonify({"message": "Historical data uploaded successfully"}), 201

@app.route('/get_simulations', methods=['GET'])
def get_simulations():
    simulations = SimulationResult.query.all()
    return jsonify([{
        'id': sim.id,
        'name': sim.name,
        'created_at': sim.created_at.isoformat()
    } for sim in simulations])

@app.route('/get_simulation/<int:sim_id>', methods=['GET'])
def get_simulation(sim_id):
    simulation = SimulationResult.query.get_or_404(sim_id)
    return jsonify({
        'id': simulation.id,
        'name': simulation.name,
        'parameters': simulation.parameters,
        'results': simulation.results,
        'created_at': simulation.created_at.isoformat()
    })


### ERROR HANDLING

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)