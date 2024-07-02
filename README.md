# UZ Simulation Lab
## Simulations using ornstein-uhlenbeck & GBM


Our Simulation Lab leverages multivariate geometric brownian motion process to produce correlated price paths for non-stable token pairs in a liquidity pool. For stable token pairs or simulations where averages tend toward an equilibrium, like utilization rates in lending protocols, we use Ornstein-Uhlenbeck process.

### Non-stable pairs: GBM

$$
dS_t = \mu S_t dt + \sigma S_t dW_t
$$

Where:
- $S_t$ is the asset price at time t
- $\mu$ is the drift (average rate of return)
- $\sigma$ is the volatility
- $W_t$ is a Wiener process (standard Brownian motion)

The solution gives the asset price at time t:

$$
S_t = S_0 \exp\left(\left(\mu - \frac{\sigma^2}{2}\right)t + \sigma W_t\right)
$$

### Stable pairs, lending: OU

$$
dX_t = \alpha (\gamma - X_t) dt + \beta dW_t 
$$

Initial parameters of the OU process:

- Initial value of the process X_0,
- Mean reversion rate α,
- Long-term mean γ,
- Volatility β.

At each timestep \(t\), update the rate \(X_t\) using the formula:

```{r, eval=FALSE}
X_t <- X_t_previous + alpha * (gamma - X_t_previous) * dt + beta * sqrt(dt) * rnorm(1)
```

#### Alpha (α): Mean Reversion Rate

the rate at which the process reverts to its long-term mean. Quantifies how quickly the process responds to deviations in time

A higher α indicates a faster adjustment back to the mean, leading to less volatile, more stable dynamics. In this mechanism, high α could suggest a token whose value is tightly controlled or regulated, quickly returning to a target or equilibrium value after fluctuations. A lower α might be something more speculative, like a meme token.

#### Gamma (γ): Long-term Mean

represents the equilibrium or mean level to which the process reverts over time

The value of 𝛾 sets the target or the expected average value of the process. It does not affect the volatility or speed of mean reversion but rather where the process settles in the long run. So this could reperesent a token price or value designed by the protocol. 

#### Beta (β): Volatility or Scale of the Brownian Motion

 measures the scale or intensity of the random fluctuations driven by the Brownian motion component of the process. 

A higher β increases the range and intensity of the fluctuations, leading to a more volatile and unpredictable process.



