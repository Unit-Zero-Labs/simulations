import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
import numpy as np
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta
import copy

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

class LendingSimulation:
    def __init__(self):
        self.asset_price = 1.0  # starting normalized price
        self.collateral_amount = 1000000  # init collateral in USD
        self.loan_amount = 0
        self.max_ltv = 0.8  # max LTV ratio
        self.liquidation_threshold = 0.9  # liq occurs at 90% of max LTV
        self.oracle_update_frequency = 60  # seconds

    def update_price(self, new_price):
        self.asset_price = new_price
        self.check_liquidation()

    def borrow(self, amount):
        max_borrow = self.collateral_amount * self.asset_price * self.max_ltv
        if self.loan_amount + amount <= max_borrow:
            self.loan_amount += amount
            return True
        return False

    def check_liquidation(self):
        current_ltv = self.loan_amount / (self.collateral_amount * self.asset_price)
        if current_ltv >= self.max_ltv * self.liquidation_threshold:
            return True
        return False

def run_boundary_analysis(simulation, price_scenarios):
    results = []
    for scenario in price_scenarios:
        sim = copy.deepcopy(simulation)
        max_borrowed = 0
        for price in scenario:
            sim.update_price(price)
            while sim.borrow(1000):  # sim small borrows
                max_borrowed = sim.loan_amount
        results.append({
            'scenario': scenario,
            'max_borrowed': max_borrowed,
            'final_price': scenario[-1],
            'liquidated': sim.check_liquidation()
        })
    return results

## LIQUIDITY POOL FORMULAE: GBM, CFMM 

def constant_product_formula(x, y, dx):
    k = x * y
    dy = y - k / (x + dx)
    return dy

def calculate_pool_metrics(self, prices, initial_x, initial_y):
    k = initial_x * initial_y
    y_values = [k / price for price in prices]
    x_values = [k / y for y in y_values]
    return x_values, y_values

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

############
############
## APP START
############
############
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
        self.stable_pool_frame = ttk.Frame(self.notebook)
        self.non_stable_pool_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.lending_frame, text="Lending Simulation")
        self.notebook.add(self.stable_pool_frame, text="Stable Pair Liquidity Pool")
        self.notebook.add(self.non_stable_pool_frame, text="Non-Stable Pair Liquidity Pool")

        self.create_lending_widgets()
        self.create_stable_pool_widgets()
        self.create_non_stable_pool_widgets()


## LENDING WIDGETS        

    def create_lending_widgets(self):
        input_frame = ttk.Frame(self.lending_frame)
        input_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(input_frame, text="Collateral Amount (USD):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.collateral_entry = ttk.Entry(input_frame, width=15)
        self.collateral_entry.grid(row=0, column=1, padx=5, pady=5)
        self.collateral_entry.insert(0, "1000000")

        ttk.Label(input_frame, text="Max LTV:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.max_ltv_entry = ttk.Entry(input_frame, width=15)
        self.max_ltv_entry.grid(row=1, column=1, padx=5, pady=5)
        self.max_ltv_entry.insert(0, "0.8")

        ttk.Label(input_frame, text="Liquidation Threshold:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.liquidation_threshold_entry = ttk.Entry(input_frame, width=15)
        self.liquidation_threshold_entry.grid(row=2, column=1, padx=5, pady=5)
        self.liquidation_threshold_entry.insert(0, "0.9")

        ttk.Label(input_frame, text="Oracle Update Frequency (s):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.oracle_frequency_entry = ttk.Entry(input_frame, width=15)
        self.oracle_frequency_entry.grid(row=3, column=1, padx=5, pady=5)
        self.oracle_frequency_entry.insert(0, "60")

        ttk.Button(input_frame, text="Run Boundary Analysis", command=self.run_lending_boundary_analysis).grid(row=4, column=0, columnspan=2, pady=10)

        self.lending_result_text = tk.Text(self.lending_frame, height=20, width=60)
        self.lending_result_text.pack(pady=10, padx=10, expand=True, fill='both')

## NONSTABLE PAIR WIDGETS        

    # A, B, price of A and B, balance of the pool 
    #
    def create_non_stable_pool_widgets(self):
        input_frame = ttk.Frame(self.non_stable_pool_frame)
        input_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(input_frame, text="Initial Price:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.non_stable_initial_price_entry = ttk.Entry(input_frame, width=10)
        self.non_stable_initial_price_entry.grid(row=0, column=1, padx=5, pady=5)
        self.non_stable_initial_price_entry.insert(0, "0.1")

        ttk.Label(input_frame, text="Drift (mu):").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.non_stable_mu_entry = ttk.Entry(input_frame, width=10)
        self.non_stable_mu_entry.grid(row=0, column=3, padx=5, pady=5)
        self.non_stable_mu_entry.insert(0, "0.1")

        ttk.Label(input_frame, text="Volatility (sigma):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.non_stable_sigma_entry = ttk.Entry(input_frame, width=10)
        self.non_stable_sigma_entry.grid(row=1, column=1, padx=5, pady=5)
        self.non_stable_sigma_entry.insert(0, "0.5")

        ttk.Label(input_frame, text="Number of Paths:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.non_stable_paths_entry = ttk.Entry(input_frame, width=10)
        self.non_stable_paths_entry.grid(row=1, column=3, padx=5, pady=5)
        self.non_stable_paths_entry.insert(0, "1000")

        ttk.Button(input_frame, text="Run Non-Stable Pool Simulation", command=self.run_non_stable_pool_simulation).grid(row=4, column=0, columnspan=4, pady=10)

        self.non_stable_plot_frame = ttk.Frame(self.non_stable_pool_frame)
        self.non_stable_plot_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.non_stable_figure, self.non_stable_ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.non_stable_canvas = FigureCanvasTkAgg(self.non_stable_figure, master=self.non_stable_plot_frame)
        self.non_stable_canvas_widget = self.non_stable_canvas.get_tk_widget()
        self.non_stable_canvas_widget.pack(expand=True, fill='both')

## STABLE PAIR WIDGETS

    def create_stable_pool_widgets(self):
        input_frame = ttk.Frame(self.stable_pool_frame)
        input_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(input_frame, text="Initial Price:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.stable_initial_price_entry = ttk.Entry(input_frame, width=10)
        self.stable_initial_price_entry.grid(row=0, column=1, padx=5, pady=5)
        self.stable_initial_price_entry.insert(0, "1.0")

        ttk.Label(input_frame, text="Mean Reversion Rate:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.stable_alpha_entry = ttk.Entry(input_frame, width=10)
        self.stable_alpha_entry.grid(row=0, column=3, padx=5, pady=5)
        self.stable_alpha_entry.insert(0, "0.1")

        ttk.Label(input_frame, text="Long-term Mean:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.stable_gamma_entry = ttk.Entry(input_frame, width=10)
        self.stable_gamma_entry.grid(row=1, column=1, padx=5, pady=5)
        self.stable_gamma_entry.insert(0, "1.0")

        ttk.Label(input_frame, text="Volatility:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.stable_beta_entry = ttk.Entry(input_frame, width=10)
        self.stable_beta_entry.grid(row=1, column=3, padx=5, pady=5)
        self.stable_beta_entry.insert(0, "0.01")

        ttk.Label(input_frame, text="Simulation Days:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.stable_days_entry = ttk.Entry(input_frame, width=10)
        self.stable_days_entry.grid(row=2, column=1, padx=5, pady=5)
        self.stable_days_entry.insert(0, "365")

        ttk.Button(input_frame, text="Run Stable Pool Simulation", command=self.run_stable_pool_simulation).grid(row=3, column=0, columnspan=4, pady=10)

        self.stable_plot_frame = ttk.Frame(self.stable_pool_frame)
        self.stable_plot_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.stable_figure, self.stable_ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.stable_canvas = FigureCanvasTkAgg(self.stable_figure, master=self.stable_plot_frame)
        self.stable_canvas_widget = self.stable_canvas.get_tk_widget()
        self.stable_canvas_widget.pack(expand=True, fill='both')



## LENDING SIM - BOUNDARY ANALYSIS

    def run_lending_boundary_analysis(self):
        try:
            simulation = LendingSimulation()
            simulation.collateral_amount = float(self.collateral_entry.get())
            simulation.max_ltv = float(self.max_ltv_entry.get())
            simulation.liquidation_threshold = float(self.liquidation_threshold_entry.get())
            simulation.oracle_update_frequency = float(self.oracle_frequency_entry.get())

            # boundary parameters
            normal_scenario = [1.0] * 10  # stable price
            spike_scenario = [1.0] * 5 + [10.0] + [1.0] * 4  #  price spike
            crash_scenario = [1.0] * 5 + [0.1] + [1.0] * 4  # price crash
            gradual_increase = [1.0 + 0.1*i for i in range(10)]  # grad increasing price
            gradual_decrease = [1.0 - 0.05*i for i in range(10)]  # grad decreasing price

            scenarios = [normal_scenario, spike_scenario, crash_scenario, gradual_increase, gradual_decrease]
            results = run_boundary_analysis(simulation, scenarios)

            self.lending_result_text.delete('1.0', tk.END)
            for result in results:
                self.lending_result_text.insert(tk.END, f"Scenario: {result['scenario']}\n")
                self.lending_result_text.insert(tk.END, f"Max Borrowed: ${result['max_borrowed']:,.2f}\n")
                self.lending_result_text.insert(tk.END, f"Final Price: ${result['final_price']:.2f}\n")
                self.lending_result_text.insert(tk.END, f"Liquidated: {result['liquidated']}\n\n")

            self.display_chart_in_new_window(results)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_chart_in_new_window(self, results):
        chart_window = tk.Toplevel(self)
        chart_window.title("Boundary Analysis Charts")
        chart_window.geometry("600x400")

        fig = self.create_boundary_analysis_chart(results)
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

   
        close_button = ttk.Button(chart_window, text="Close", command=chart_window.destroy)
        close_button.pack(pady=5)

    def create_boundary_analysis_chart(self, results):
        plt.rcParams.update({'font.size': 8})  
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), dpi=100)
        colors = plt.cm.rainbow(np.linspace(0, 1, len(results)))
        
        for result, color in zip(results, colors):
            scenario = result['scenario']
            max_borrowed = result['max_borrowed']
            time = range(len(scenario))
            
            # prices
            ax1.plot(time, scenario, label=f"Scenario {results.index(result)+1}", color=color)
            ax1.set_ylabel('Asset Price', fontsize=8)
            ax1.set_title('Asset Price Scenarios', fontsize=8)
            
            # borrowed amount 
            ax2.plot(time, [max_borrowed] * len(time), color=color)
            
        ax1.legend(fontsize=8)
        ax1.grid(True)
        ax1.tick_params(axis='both', which='major', labelsize=8)
        
        ax2.set_xlabel('Time', fontsize=8)
        ax2.set_ylabel('Max Borrowed Amount', fontsize=8)
        ax2.set_title('Maximum Borrowed Amount per Scenario', fontsize=8)
        ax2.grid(True)
        ax2.tick_params(axis='both', which='major', labelsize=8)
        
        #  liquidation threshold line
        max_y = max(result['max_borrowed'] for result in results)
        liquidation_line = max_y * float(self.liquidation_threshold_entry.get())
        ax2.axhline(y=liquidation_line, color='r', linestyle='--', label='Liquidation Threshold')
        ax2.legend(fontsize=7)

        plt.tight_layout()
        return fig
    

## STABLE SIM

    def run_stable_pool_simulation(self):
        try:
            initial_price = float(self.stable_initial_price_entry.get())
            alpha = float(self.stable_alpha_entry.get())
            gamma = float(self.stable_gamma_entry.get())
            beta = float(self.stable_beta_entry.get())
            days = int(self.stable_days_entry.get())

            ou_params = OUParams(alpha=alpha, gamma=gamma, beta=beta, X_0=initial_price)
            prices = simulate_OU_process(days, 1, ou_params)[0]

            start_date = datetime.now()
            date_range = [start_date + timedelta(days=i) for i in range(days)]

            self.stable_ax.clear()
            self.stable_ax.plot(date_range, prices, label='Token Price')
            self.stable_ax.axhline(y=gamma, color='r', linestyle='--', label='Long-term Mean')
            
            self.stable_ax.set_title('Stable Pair Liquidity Pool Simulation', fontsize=10)
            self.stable_ax.set_xlabel('Date', fontsize=8)
            self.stable_ax.set_ylabel('Price', fontsize=8)
            self.stable_ax.legend(fontsize=8)
            self.stable_ax.tick_params(axis='both', which='major', labelsize=8)
            self.stable_figure.tight_layout()
            self.stable_canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", str(e))

## NON STABLE LP SIM

    def run_non_stable_pool_simulation(self):
        try:
            S0 = float(self.non_stable_initial_price_entry.get())
            mu = float(self.non_stable_mu_entry.get())
            sigma = float(self.non_stable_sigma_entry.get())
            paths = int(self.non_stable_paths_entry.get())
            T = 1
            N = 365

            prices = geometric_brownian_motion(S0, mu, sigma, T, N, paths)
            start_date = datetime(2024, 1, 1)
            date_range = [start_date + timedelta(days=i) for i in range(N)]
            df = pd.DataFrame(prices.T, index=date_range, columns=[f'Path_{i}' for i in range(paths)])
            df['Median'] = df.median(axis=1)

            # calc liquidity pool metrics
            initial_x = 1000000  # example initial liquidity
            initial_y = initial_x * S0
            x_values, y_values = self.calculate_pool_metrics(df['Median'], initial_x, initial_y)

            self.non_stable_ax.clear()
            self.non_stable_ax.plot(df.index, df.iloc[:, :-1], color='cyan', alpha=0.1)
            self.non_stable_ax.plot(df.index, df['Median'], color='magenta', linewidth=2, label='Token Price (Median)')
            self.non_stable_ax.plot(date_range, x_values, label='Token X')
            self.non_stable_ax.plot(date_range, y_values, label='Token Y')

            # calc and plot price impact for a sample trade
            sample_dx = initial_x * 0.01  # 1% of initial liquidity
            price_impacts = [self.calculate_price_impact(x, y, sample_dx) for x, y in zip(x_values, y_values)]
            self.non_stable_ax.plot(date_range, price_impacts, label='Price Impact (1% trade)')

            self.non_stable_ax.set_title('Non-Stable Pair Liquidity Pool Simulation', fontsize=10)
            self.non_stable_ax.set_xlabel('Date', fontsize=8)
            self.non_stable_ax.set_ylabel('Value', fontsize=8)
            self.non_stable_ax.set_ylim(0, max(df.max().max(), 0.4))
            self.non_stable_ax.fill_between(df.index, df.min(axis=1), df.max(axis=1), color='cyan', alpha=0.3)
            self.non_stable_ax.legend(fontsize=8)
            self.non_stable_ax.tick_params(axis='both', which='major', labelsize=8)
            self.non_stable_figure.tight_layout()
            self.non_stable_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calculate_pool_metrics(self, prices, initial_x, initial_y):
        k = initial_x * initial_y
        y_values = [k / price for price in prices]
        x_values = [k / y for y in y_values]
        return x_values, y_values

    def calculate_price_impact(self, x, y, dx):
        dy = constant_product_formula(x, y, dx)
        initial_price = y / x
        final_price = (y - dy) / (x + dx)
        return (final_price - initial_price) / initial_price

if __name__ == "__main__":
    app = TokenSimulationApp()
    app.mainloop()