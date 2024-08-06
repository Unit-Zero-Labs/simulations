import numpy as np
from app.simulations.gbm import geometric_brownian_motion

def calculate_il(price_ratio):
    return 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1

class LPSimulation:
    def __init__(self, token_launch_price, lp_pool_allocation, initial_total_supply, simulation_days, mu, sigma, paths,
                 token_adoption_velocity, avg_token_utility_allocation, avg_token_holding, avg_token_sell):
        self.token_launch_price = token_launch_price
        self.lp_pool_allocation = lp_pool_allocation
        self.initial_total_supply = initial_total_supply
        self.simulation_days = simulation_days
        self.mu = mu
        self.sigma = sigma
        self.paths = paths
        
        # ETH parameters
        self.token_lp_weighting = 0.50
        self.lp_pairing_token2_ticker = "ETH"
        self.lp_pairing_token2_price = 3750
        self.initial_lp_pairing_token2_amount = self.lp_pairing_token2_price * self.lp_pool_allocation
        
        # token holder Assumptions
        self.token_adoption_velocity = token_adoption_velocity
        self.avg_token_utility_allocation = avg_token_utility_allocation / 100
        self.avg_token_holding = avg_token_holding / 100
        self.avg_token_sell = avg_token_sell / 100

    def simulate(self):
        initial_market_cap = self.initial_total_supply * self.token_launch_price
        initial_liquidity = self.lp_pool_allocation * 2  # Assuming equal value of both tokens in the pool

        prices = geometric_brownian_motion(self.token_launch_price, self.mu, self.sigma, self.simulation_days/365, self.simulation_days, self.paths)
        
        initial_token_amount = self.lp_pool_allocation / self.token_launch_price
        initial_eth_amount = self.initial_lp_pairing_token2_amount / self.lp_pairing_token2_price
        
        tvl = prices * initial_token_amount + initial_eth_amount * self.lp_pairing_token2_price
        il = calculate_il(prices / self.token_launch_price)
        
        # apply token holder assumptions to adjust prices
        # TO DO: apply LP pool token ratio toggle
        # what other charts do we need here?
        adoption_factor = 1 + (self.token_adoption_velocity * self.simulation_days / 365)
        utility_factor = 1 + self.avg_token_utility_allocation
        holding_factor = 1 + self.avg_token_holding
        sell_factor = 1 - self.avg_token_sell
        
        adjusted_prices = prices * adoption_factor * utility_factor * holding_factor * sell_factor
        
        percentiles = [5, 25, 50, 75, 95]
        price_percentiles = np.percentile(adjusted_prices, percentiles, axis=0)
        tvl_percentiles = np.percentile(tvl, percentiles, axis=0)
        il_percentiles = np.percentile(il, percentiles, axis=0)
        
        return {
            'price_percentiles': price_percentiles,
            'tvl_percentiles': tvl_percentiles,
            'il_percentiles': il_percentiles,
            'median_prices': price_percentiles[2],
            'median_tvl': tvl_percentiles[2],
            'median_il': il_percentiles[2],
            'initial_market_cap': initial_market_cap,
            'initial_liquidity': initial_liquidity
        }