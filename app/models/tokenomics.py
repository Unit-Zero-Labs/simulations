import numpy as np
from scipy.stats import norm

class TokenomicsSimulation:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        required_params = ['initial_reserves', 'token_price', 'protocol_revenue_share', 'target_utilization', 'total_token_emitted']
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"'{param}' is a required parameter")
        
        self.initial_reserves = kwargs['initial_reserves']
        self.token_price = kwargs['token_price']
        self.protocol_revenue_share = kwargs['protocol_revenue_share']
        self.target_utilization = kwargs['target_utilization']
        self.total_token_emitted = kwargs['total_token_emitted']

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
            token_reserves = self.initial_reserves / (2 * self.token_price)  
            stable_reserves = self.initial_reserves / 2 
            monthly_data = []

            for month in range(num_months):
                # sim TVL and borrow growth
                tvl_growth = np.random.normal(self.mom_tvl_growth, self.mom_tvl_growth / 2)
                borrow_growth = np.random.normal(self.mom_borrow_growth, self.mom_borrow_growth / 2)

                tvl *= (1 + tvl_growth)
                borrow *= (1 + borrow_growth)

                utilization = borrow / tvl
                interest_rate = self.calculate_interest_rate(utilization)

                # calc revenue
                borrow_revenue = borrow * interest_rate / 12
                liquidation_revenue = tvl * self.monthly_liquidations
                sequencer_revenue = tvl * self.monthly_sequencer_fees
                total_revenue = borrow_revenue + liquidation_revenue + sequencer_revenue

                # rev distribution
                protocol_revenue = total_revenue * self.protocol_revenue_share
                token_holder_revenue = total_revenue - protocol_revenue

                # calc token emissions
                emissions_rate = self.base_monthly_emissions_rate * (1 + self.emissions_step_up * (utilization - self.target_utilization))
                token_emissions = self.total_token_emitted * emissions_rate

                # Team vesting
                if month >= self.cliff:
                    vesting_rate = self.base_vesting_per_month * (1 + self.vesting_step_up * (utilization - self.target_utilization))
                    team_tokens_vested += self.total_team_allocation * vesting_rate
                
                token_circulating += token_emissions + (team_tokens_vested if month >= self.cliff else 0)

                # calc expenses and net income
                expenses = (token_emissions + team_tokens_vested) * self.token_price
                net_income = protocol_revenue - expenses

                # update reserves
                token_reserves += net_income / self.token_price
                stable_reserves += net_income

                # update token price 
                self.token_price *= (1 + (net_income / (token_circulating * self.token_price)) * 0.1)

                # calc runway
                if net_income > 0:
                    token_reserves += (net_income / 2) / self.token_price
                    stable_reserves += net_income / 2
                else:
                    # if net income is negative, draw from both reserves proportionally
                    total_reserves_value = (token_reserves * self.token_price) + stable_reserves
                    token_draw_ratio = (token_reserves * self.token_price) / total_reserves_value
                    token_reserves += (net_income * token_draw_ratio) / self.token_price
                    stable_reserves += net_income * (1 - token_draw_ratio)
                token_reserves = max(0, token_reserves)
                stable_reserves = max(0, stable_reserves)

                # now get runway based on total reserves
                total_reserves_value = (token_reserves * self.token_price) + stable_reserves
                if net_income < 0:
                    monthly_burn_rate = abs(net_income)
                    runway_months = total_reserves_value / monthly_burn_rate if monthly_burn_rate > 0 else float('inf')
                else:
                    runway_months = net_income + 10000


                cumulative_revenue += total_revenue

                monthly_data.append({
                    'month': month + 1,
                    'tvl': tvl,
                    'borrow': borrow,
                    'utilization': utilization,
                    'interest_rate': interest_rate,
                    'total_revenue': total_revenue,
                    'protocol_revenue': protocol_revenue,
                    'token_holder_revenue': token_holder_revenue,
                    'net_income': net_income,
                    'token_reserves': token_reserves,
                    'stable_reserves': stable_reserves,
                    'runway': runway_months,
                    'token_emissions': token_emissions,
                    'token_circulating': token_circulating,
                    'team_tokens_vested': team_tokens_vested,
                    'cumulative_revenue': cumulative_revenue,
                    'token_price': self.token_price,
                    'expenses': expenses
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
            'protocol_revenue': {p: np.percentile([d['protocol_revenue'] for d in final_month_data], p) for p in percentiles},
            'token_holder_revenue': {p: np.percentile([d['token_holder_revenue'] for d in final_month_data], p) for p in percentiles},
            'net_income': {p: np.percentile([d['net_income'] for d in final_month_data], p) for p in percentiles},
            'token_reserves': {p: np.percentile([d['token_reserves'] for d in final_month_data], p) for p in percentiles},
            'stable_reserves': {p: np.percentile([d['stable_reserves'] for d in final_month_data], p) for p in percentiles},
            'runway': {p: np.percentile([d['runway'] for d in final_month_data], p) for p in percentiles},
            'token_circulating': {p: np.percentile([d['token_circulating'] for d in final_month_data], p) for p in percentiles},
            'cumulative_revenue': {p: np.percentile([d['cumulative_revenue'] for d in final_month_data], p) for p in percentiles},
            'token_price': {p: np.percentile([d['token_price'] for d in final_month_data], p) for p in percentiles},
            'expenses': {p: np.percentile([d['expenses'] for d in final_month_data], p) for p in percentiles}
        }

        return {
            'simulations': results,
            'summary': summary
        }