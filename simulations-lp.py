import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta

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


class LiquidityPoolSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unit Zero LP Simulation Lab")
        self.geometry("600x500")
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.Frame(self)
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

        ttk.Button(input_frame, text="Run Simulation", command=self.run_simulation).grid(row=2, column=0, columnspan=4, pady=10)

        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.figure, self.ax = plt.subplots(figsize=(4, 2.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(expand=True, fill='both')

    def run_simulation(self):
        S0 = float(self.initial_price_entry.get())
        mu = float(self.mu_entry.get())
        sigma = float(self.sigma_entry.get())
        paths = int(self.paths_entry.get())
        T = 1
        N = 365

        prices = geometric_brownian_motion(S0, mu, sigma, T, N, paths)
        start_date = datetime(2023, 1, 1)
        date_range = [start_date + timedelta(days=i) for i in range(N)]
        df = pd.DataFrame(prices.T, index=date_range, columns=[f'Path_{i}' for i in range(paths)])
        df['Median'] = df.median(axis=1)

        self.ax.clear()
        self.ax.plot(df.index, df.iloc[:, :-1], color='cyan', alpha=0.1)
        self.ax.plot(df.index, df['Median'], color='magenta', linewidth=2)
        self.ax.set_title('GBM Simulated prices (USD)', fontsize=10)
        self.ax.set_xlabel('Date', fontsize=8)
        self.ax.set_ylabel('USD ($)', fontsize=8)
        self.ax.set_ylim(0, max(df.max().max(), 0.4))
        self.ax.fill_between(df.index, df.min(axis=1), df.max(axis=1), color='cyan', alpha=0.3)
        self.ax.legend(['SYSUSD'], fontsize=8)
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = LiquidityPoolSimulator()
    app.mainloop()