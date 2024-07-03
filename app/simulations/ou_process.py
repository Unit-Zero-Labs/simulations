import numpy as np

class OUParams:
    def __init__(self, alpha, gamma, beta, X_0=None):
        self.alpha = alpha
        self.gamma = gamma
        self.beta = beta
        self.X_0 = X_0

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