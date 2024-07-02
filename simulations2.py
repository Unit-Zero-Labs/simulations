import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Toplevel, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dataclasses import dataclass

@dataclass
class SimulationParams:
    alpha: float  # Mean reversion speed for interest rates
    gamma: float  # Long-term mean for interest rates
    beta: float   # Volatility of interest rates
    initial_rate: float  # Initial interest rate

def simulate_interest_rates(T, alpha, gamma, beta, initial_rate):
    """
    Generate interest rate data using an Ornstein-Uhlenbeck process.
    """
    dt = 1.0
    rates = np.zeros(T)
    rate = initial_rate
    for t in range(1, T):
        dW = np.random.normal(0, np.sqrt(dt))
        dR = alpha * (gamma - rate) * dt + beta * dW
        rate += dR
        rates[t] = rate
    return rates

def simulate_collateral_ratios(rates):
    """
    Generate collateral ratios based on interest rates.
    Suppose the collateral ratio decreases as the interest rate increases.
    """
    base_ratio = 150  # Example starting ratio, e.g., 150%
    ratios = base_ratio - 0.5 * (rates - rates.min())  # Simplistic dependency model
    return ratios

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compound Protocol Simulation")
        self.geometry("600x500")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Simulation Time Steps:").pack()
        self.t_entry = tk.Entry(self)
        self.t_entry.pack()
        # Entries for alpha, gamma, beta, initial_rate
        # As above, assuming these are already defined...
        tk.Button(self, text="Run Simulation", command=self.on_run_simulation).pack()

    def on_run_simulation(self):
        T = int(self.t_entry.get())
        # Assume alpha, gamma, beta, initial_rate are fetched from GUI entries...
        rates = simulate_interest_rates(T, alpha, gamma, beta, initial_rate)
        ratios = simulate_collateral_ratios(rates)
        self.show_results(rates, ratios)

    def show_results(self, rates, ratios):
        result_window = Toplevel(self)
        result_window.title("Interest Rate vs. Collateralization Ratio")
        result_window.geometry("650x450")
        fig, ax = plt.subplots()
        ax.plot(rates, ratios, 'o-')
        ax.set_title("Collateralization Ratio vs. Interest Rate")
        ax.set_xlabel("Interest Rate")
        ax.set_ylabel("Collateralization Ratio")
        canvas = FigureCanvasTkAgg(fig, master=result_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()
