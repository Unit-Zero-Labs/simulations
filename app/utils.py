import copy

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