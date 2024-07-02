import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
import numpy as np
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta


@dataclass
class OUParams:
    alpha: float
    gamma: float
    beta: float
    X_0: float = None

@dataclass
class LendingBorrowingParams:
    collateralization_ratio: float
    interest_rate: float
    liquidation_threshold: float
    utilization_rate: float

@dataclass
class LiquidityPoolParams:
    initial_x: float  # Initial amount of token X
    initial_y: float  # Initial amount of token Y
    fee_percent: float  # Fee percentage for swaps

## LENDING FORMULAE: OU

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

## LIQUIDITY POOL FORMULAE: GBM, CFMM 

def constant_product_formula(x, y, dx):
    k = x * y
    dy = y - k / (x + dx)
    return dy

def calculate_price_impact(x, y, dx):
    dy = constant_product_formula(x, y, dx)
    initial_price = y / x
    final_price = (y - dy) / (x + dx)
    return (final_price - initial_price) / initial_price



def geometric_brownian_motion(S0, mu, sigma, T, N, paths):
    """
    Generates paths of geometric Brownian motion.
    
    :param S0: Initial stock price
    :param mu: Drift coefficient
    :param sigma: Volatility
    :param T: Total time
    :param N: Number of time steps
    :param paths: Number of paths to generate
    :return: Array of simulated prices
    """
    dt = T/N
    t = np.linspace(0, T, N)
    W = np.random.normal(0, np.sqrt(dt), size=(paths, N-1))
    W = np.concatenate((np.zeros((paths, 1)), W), axis=1)
    W = np.cumsum(W, axis=1)
    
    X = (mu - 0.5 * sigma**2) * t + sigma * W
    S = S0 * np.exp(X)
    return S

def plot_results(data, title):
    fig, ax = plt.subplots()
    for i in range(data.shape[0]):
        ax.plot(data[i], label=f'Run {i+1}')
    ax.set_title(title)
    ax.set_xlabel("Time Steps")
    ax.set_ylabel("Token Value")
    ax.legend()
    return fig

## APP START

class TokenSimulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unit Zero Simulation Lab")
        self.geometry("600x600")
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.lending_frame = ttk.Frame(self.notebook)
        self.liquidity_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.lending_frame, text="Lending/Stable-Pair Pool Simulation")
        self.notebook.add(self.liquidity_frame, text="Non-Stable Pool Simulation")

        self.create_lending_widgets()
        self.create_liquidity_widgets()

## LENDING WIDGETS        


    def create_lending_widgets(self):
        input_frame = ttk.Frame(self.lending_frame)
        input_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(input_frame, text="Initial Asset Price:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.initial_price_entry = ttk.Entry(input_frame, width=10)
        self.initial_price_entry.grid(row=0, column=1, padx=5, pady=5)
        self.initial_price_entry.insert(0, "100")

        ttk.Label(input_frame, text="Collateralization Ratio:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.collateralization_ratio_entry = ttk.Entry(input_frame, width=10)
        self.collateralization_ratio_entry.grid(row=0, column=3, padx=5, pady=5)
        self.collateralization_ratio_entry.insert(0, "1.5")

        ttk.Label(input_frame, text="Interest Rate (annual):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.interest_rate_entry = ttk.Entry(input_frame, width=10)
        self.interest_rate_entry.grid(row=1, column=1, padx=5, pady=5)
        self.interest_rate_entry.insert(0, "0.05")

        ttk.Label(input_frame, text="Liquidation Threshold:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.liquidation_threshold_entry = ttk.Entry(input_frame, width=10)
        self.liquidation_threshold_entry.grid(row=1, column=3, padx=5, pady=5)
        self.liquidation_threshold_entry.insert(0, "1.2")

        ttk.Label(input_frame, text="Loan Duration (days):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.loan_duration_entry = ttk.Entry(input_frame, width=10)
        self.loan_duration_entry.grid(row=2, column=1, padx=5, pady=5)
        self.loan_duration_entry.insert(0, "365")

        ttk.Label(input_frame, text="Loan Amount:").grid(row=2, column=2, padx=5, pady=5, sticky='e')
        self.loan_amount_entry = ttk.Entry(input_frame, width=10)
        self.loan_amount_entry.grid(row=2, column=3, padx=5, pady=5)
        self.loan_amount_entry.insert(0, "1000")

        ttk.Label(input_frame, text="Mean Reversion Rate:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.alpha_entry = ttk.Entry(input_frame, width=10)
        self.alpha_entry.grid(row=3, column=1, padx=5, pady=5)
        self.alpha_entry.insert(0, "0.1")

        ttk.Label(input_frame, text="Long-term Mean:").grid(row=3, column=2, padx=5, pady=5, sticky='e')
        self.gamma_entry = ttk.Entry(input_frame, width=10)
        self.gamma_entry.grid(row=3, column=3, padx=5, pady=5)
        self.gamma_entry.insert(0, "100")

        ttk.Label(input_frame, text="Volatility:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.beta_entry = ttk.Entry(input_frame, width=10)
        self.beta_entry.grid(row=4, column=1, padx=5, pady=5)
        self.beta_entry.insert(0, "0.2")

        ttk.Button(input_frame, text="Run Lending Simulation", command=self.run_lending_simulation).grid(row=5, column=0, columnspan=4, pady=10)

        self.lending_plot_frame = ttk.Frame(self.lending_frame)
        self.lending_plot_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.lending_figure, self.lending_ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.lending_canvas = FigureCanvasTkAgg(self.lending_figure, master=self.lending_plot_frame)
        self.lending_canvas_widget = self.lending_canvas.get_tk_widget()
        self.lending_canvas_widget.pack(expand=True, fill='both')

## LIQUIDITY WIDGETS        

    # A, B, price of A and B, balance of the pool 
    #
    def create_liquidity_widgets(self):
        input_frame = ttk.Frame(self.liquidity_frame)
        input_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(input_frame, text="Initial Price:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.initial_price_entry = ttk.Entry(input_frame, width=10)
        self.initial_price_entry.grid(row=0, column=1, padx=5, pady=5)
        self.initial_price_entry.insert(0, "0.1")

        ttk.Label(input_frame, text="Drift (mu):").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.mu_entry = ttk.Entry(input_frame, width=10)
        self.mu_entry.grid(row=0, column=3, padx=5, pady=5)
        self.mu_entry.insert(0, "0.1")

        ttk.Label(input_frame, text="Volatility (sigma):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.sigma_entry = ttk.Entry(input_frame, width=10)
        self.sigma_entry.grid(row=1, column=1, padx=5, pady=5)
        self.sigma_entry.insert(0, "0.5")

        ttk.Label(input_frame, text="Number of Paths:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.paths_entry = ttk.Entry(input_frame, width=10)
        self.paths_entry.grid(row=1, column=3, padx=5, pady=5)
        self.paths_entry.insert(0, "1000")

        ttk.Button(input_frame, text="Run Liquidity Simulation", command=self.run_liquidity_simulation).grid(row=4, column=0, columnspan=4, pady=10)

        self.liquidity_plot_frame = ttk.Frame(self.liquidity_frame)
        self.liquidity_plot_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.liquidity_figure, self.liquidity_ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.liquidity_canvas = FigureCanvasTkAgg(self.liquidity_figure, master=self.liquidity_plot_frame)
        self.liquidity_canvas_widget = self.liquidity_canvas.get_tk_widget()
        self.liquidity_canvas_widget.pack(expand=True, fill='both')

## LENDING SIM

    def run_lending_simulation(self):
        try:
            initial_price = float(self.initial_price_entry.get())
            collateralization_ratio = float(self.collateralization_ratio_entry.get())
            interest_rate = float(self.interest_rate_entry.get())
            liquidation_threshold = float(self.liquidation_threshold_entry.get())
            loan_duration = int(self.loan_duration_entry.get())
            loan_amount = float(self.loan_amount_entry.get())
            alpha = float(self.alpha_entry.get())
            gamma = float(self.gamma_entry.get())
            beta = float(self.beta_entry.get())

            ou_params = OUParams(alpha=alpha, gamma=gamma, beta=beta, X_0=initial_price)
            lending_params = LendingBorrowingParams(
                collateralization_ratio=collateralization_ratio,
                interest_rate=interest_rate,
                liquidation_threshold=liquidation_threshold,
                utilization_rate=loan_amount / (initial_price * collateralization_ratio)
            )

            asset_prices = simulate_OU_process(loan_duration, 1, ou_params)[0]
            
            collateral_value = asset_prices * (loan_amount / initial_price) * collateralization_ratio
            loan_value = loan_amount * (1 + interest_rate) ** (np.arange(loan_duration) / 365)
            
            health_factor = collateral_value / loan_value
            liquidation_events = health_factor < liquidation_threshold

            start_date = datetime.now()
            date_range = [start_date + timedelta(days=i) for i in range(loan_duration)]

            self.lending_ax.clear()
            self.lending_ax.plot(date_range, asset_prices, label='Asset Price')
            self.lending_ax.plot(date_range, collateral_value, label='Collateral Value')
            self.lending_ax.plot(date_range, loan_value, label='Loan Value')
            self.lending_ax.plot(date_range, health_factor, label='Health Factor')
            self.lending_ax.axhline(y=liquidation_threshold, color='r', linestyle='--', label='Liquidation Threshold')
            
            for i, liquidation in enumerate(liquidation_events):
                if liquidation:
                    self.lending_ax.axvline(x=date_range[i], color='r', alpha=0.3)

            self.lending_ax.set_title('Lending Simulation Results', fontsize=10)
            self.lending_ax.set_xlabel('Date', fontsize=8)
            self.lending_ax.set_ylabel('Value', fontsize=8)
            self.lending_ax.legend(fontsize=8)
            self.lending_ax.tick_params(axis='both', which='major', labelsize=8)
            self.lending_figure.tight_layout()
            self.lending_canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", str(e))

## LIQUIDITY SIM

    def run_liquidity_simulation(self):
        try:
            S0 = float(self.initial_price_entry.get())
            mu = float(self.mu_entry.get())
            sigma = float(self.sigma_entry.get())
            paths = int(self.paths_entry.get())
            T = 1
            N = 365

            prices = geometric_brownian_motion(S0, mu, sigma, T, N, paths)
            start_date = datetime(2024, 1, 1)
            date_range = [start_date + timedelta(days=i) for i in range(N)]
            df = pd.DataFrame(prices.T, index=date_range, columns=[f'Path_{i}' for i in range(paths)])
            df['Median'] = df.median(axis=1)

            self.liquidity_ax.clear()
            self.liquidity_ax.plot(df.index, df.iloc[:, :-1], color='cyan', alpha=0.1)
            self.liquidity_ax.plot(df.index, df['Median'], color='magenta', linewidth=2)
            self.liquidity_ax.set_title('GBM Simulated prices (USD)', fontsize=10)
            self.liquidity_ax.set_xlabel('Date', fontsize=8)
            self.liquidity_ax.set_ylabel('USD ($)', fontsize=8)
            self.liquidity_ax.set_ylim(0, max(df.max().max(), 0.4))
            self.liquidity_ax.fill_between(df.index, df.min(axis=1), df.max(axis=1), color='cyan', alpha=0.3)
            self.liquidity_ax.legend(['Token-ETH'], fontsize=8)
            self.liquidity_ax.tick_params(axis='both', which='major', labelsize=8)
            self.liquidity_figure.tight_layout()
            self.liquidity_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = TokenSimulationApp()
    app.mainloop()
