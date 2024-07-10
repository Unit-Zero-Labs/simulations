import numpy as np
from scipy.stats import norm

class TokenomicsSimulation:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.initial_reserves = kwargs.get('initial_reserves', 1000000)  
        self.monthly_expenses = kwargs.get('monthly_expenses', 100000)  

    def calculate_interest_rate(self, utilization):
        if utilization <= self.kink:
            return self.base_rate + (utilization / self.kink) * self.multiplier
        else:
            return self.base_rate + self.multiplier + ((utilization - self.kink) / (1 - self.kink)) * self.jump_multiplier

    def run_simulations(self, num_simulations, num_months):
        results = []

        for _ in range(num_simulations):
            tvl = self.initial_tvl
            borrow = self.initial_borrow
            token_circulating = self.initial_token_circulating
            team_tokens_vested = 0
            cumulative_revenue = 0
            reserves = self.initial_reserves
            runway = []
            monthly_data = []

            for month in range(num_months):
                # sim TVL and borrow growth, modeled as normal distributions
                tvl_growth = np.random.normal(self.mom_tvl_growth, self.mom_tvl_growth / 2)
                borrow_growth = np.random.normal(self.mom_borrow_growth, self.mom_borrow_growth / 2)

                tvl *= (1 + tvl_growth)
                borrow *= (1 + borrow_growth)
                # interest rate is a calc of utilization
                utilization = borrow / tvl
                interest_rate = self.calculate_interest_rate(utilization)

                # revenue from borrow interest, liqs, and sequencer fees
                borrow_revenue = borrow * interest_rate / 12
                liquidation_revenue = tvl * self.monthly_liquidations
                sequencer_revenue = tvl * self.monthly_sequencer_fees
                total_revenue = borrow_revenue + liquidation_revenue + sequencer_revenue

                # calc token emissions
                emissions_rate = self.base_monthly_emissions_rate * (1 + self.emissions_step_up * (borrow / self.initial_borrow - 1))
                token_emissions = self.total_token_emitted * emissions_rate

                # team vesting
                if month >= self.cliff:
                    vesting_rate = self.base_vesting_per_month * (1 + self.vesting_step_up * (borrow / self.initial_borrow - 1))
                    team_tokens_vested += self.total_team_allocation * vesting_rate
                
                token_circulating += token_emissions + (self.total_team_allocation * vesting_rate if month >= self.cliff else 0)

                # cumulative revenue
                cumulative_revenue += total_revenue
                net_income = total_revenue - self.monthly_expenses
                reserves += net_income

                # calc runway (in months)
                if net_income < 0:
                    runway_months = reserves / abs(net_income)
                else:
                    runway_months = 999  
                runway.append(runway_months)

                monthly_data.append({
                    'month': month + 1,
                    'tvl': tvl,
                    'borrow': borrow,
                    'utilization': utilization,
                    'interest_rate': interest_rate,
                    'total_revenue': total_revenue,
                    'net_income': net_income,
                    'reserves': reserves,
                    'runway': runway_months,
                    'token_emissions': token_emissions,
                    'token_circulating': token_circulating,
                    'team_tokens_vested': team_tokens_vested,
                    'cumulative_revenue': cumulative_revenue
                })

            results.append(monthly_data)

        # calc percentiles for key metrics
        percentiles = [5, 25, 50, 75, 95]
        final_month_data = [sim[-1] for sim in results]

        summary = {
            'tvl': {p: np.percentile([d['tvl'] for d in final_month_data], p) for p in percentiles},
            'borrow': {p: np.percentile([d['borrow'] for d in final_month_data], p) for p in percentiles},
            'utilization': {p: np.percentile([d['utilization'] for d in final_month_data], p) for p in percentiles},
            'total_revenue': {p: np.percentile([d['total_revenue'] for d in final_month_data], p) for p in percentiles},
            'token_circulating': {p: np.percentile([d['token_circulating'] for d in final_month_data], p) for p in percentiles},
            'cumulative_revenue': {p: np.percentile([d['cumulative_revenue'] for d in final_month_data], p) for p in percentiles},
            'runway': {p: np.percentile([d['runway'] for d in final_month_data], p) for p in percentiles},
            'net_income': {p: np.percentile([d['net_income'] for d in final_month_data], p) for p in percentiles}

        
        }

        return {
            'simulations': results,
            'summary': summary
        }