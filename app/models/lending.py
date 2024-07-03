import numpy as np

class LendingSimulation:
    def __init__(self, collateral_amount, max_ltv, liquidation_threshold, total_deposits, interest_rate, liquidation_penalty):
        self.asset_price = 1.0  
        self.collateral_amount = collateral_amount
        self.loan_amount = 0
        self.max_ltv = max_ltv
        self.liquidation_threshold = liquidation_threshold
        self.oracle_update_frequency = 60  
        self.total_deposits = total_deposits
        self.interest_rate = interest_rate
        self.liquidation_penalty = liquidation_penalty

    def update_price(self, new_price):
        self.asset_price = max(new_price, 0.000001) 
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