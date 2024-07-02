import tkinter as tk
from tkinter import Toplevel, messagebox
import numpy as np
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tqdm

@dataclass
class OUParams:
    alpha: float  # mean reversion parameter
    gamma: float  # asymptotic mean
    beta: float  # Brownian motion scale (standard deviation)
    X_0: float = None  # initial starting value (otherwise gamma is used)

def simulate_OU_process(T, runs, ou_params):
    """
    Simulates multiple independent Ornstein-Uhlenbeck processes.
    """
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

def plot_results(data):
    fig, ax = plt.subplots()
    for i in range(data.shape[0]):
        ax.plot(data[i], label=f'Run {i+1}')
    ax.set_title("Token Simulation Results")
    ax.set_xlabel("Time Steps")
    ax.set_ylabel("Token Value")
    ax.legend()
    return fig

class TokenSimulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unit Zero OU Simulation")
        self.geometry("500x400")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Number of Time Steps (T):").pack()
        self.t_entry = tk.Entry(self)
        self.t_entry.pack()

        tk.Label(self, text="Number of Simulations (Runs):").pack()
        self.runs_entry = tk.Entry(self)
        self.runs_entry.pack()

        tk.Label(self, text="Alpha (mean reversion rate):").pack()
        self.alpha_entry = tk.Entry(self)
        self.alpha_entry.pack()

        tk.Label(self, text="Gamma (long-term mean):").pack()
        self.gamma_entry = tk.Entry(self)
        self.gamma_entry.pack()

        tk.Label(self, text="Beta (volatility):").pack()
        self.beta_entry = tk.Entry(self)
        self.beta_entry.pack()

        tk.Label(self, text="Initial Token Value:").pack()
        self.initial_value_entry = tk.Entry(self)
        self.initial_value_entry.pack()

        tk.Button(self, text="Run Simulation", command=self.on_run_simulation).pack()

    def on_run_simulation(self):
        try:
            T = int(self.t_entry.get())
            runs = int(self.runs_entry.get())
            alpha = float(self.alpha_entry.get())
            gamma = float(self.gamma_entry.get())
            beta = float(self.beta_entry.get())
            initial_value = float(self.initial_value_entry.get())
            ou_params = OUParams(alpha=alpha, gamma=gamma, beta=beta, X_0=initial_value)
            data = simulate_OU_process(T, runs, ou_params)
            self.show_results(data)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_results(self, data):
        result_window = Toplevel(self)
        result_window.title("Simulation Results")
        result_window.geometry("600x500")
        fig = plot_results(data)
        canvas = FigureCanvasTkAgg(fig, master=result_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = TokenSimulationApp()
    app.mainloop()