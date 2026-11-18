"""Numpy checks of the two exact statements in the theory section.
(1) With g_t independent of the past and stationary momentum m_t = mu*m_{t-1} + g_t, cos(m_t, m_{t-1}) -> mu.
(2) d L(W_{t-1} - lr*s*O)/d s = -lr * g_t . O, checked by finite differences on a random quadratic."""
import warnings; warnings.filterwarnings("ignore")  # spurious matmul warnings from macOS Accelerate
import numpy as np
rng = np.random.default_rng(0)
for mu in (0.9, 0.95, 0.99):
    m = np.zeros(4096); cs = []
    for t in range(3000):
        g = rng.standard_normal(4096); mn = mu * m + g
        if t > 1000: cs.append(mn @ m / (np.linalg.norm(mn) * np.linalg.norm(m)))
        m = mn
    print(f"mu {mu}: mean cos(m_t, m_t-1) = {np.mean(cs):.4f}")
A = rng.standard_normal((50, 50)); H = A @ A.T / 50; W = rng.standard_normal(50); O = rng.standard_normal(50); lr, s = 0.1, 0.7
L = lambda w: 0.5 * w @ H @ w
Wt = W - lr * s * O; g = H @ Wt; eps = 1e-6
fd = (L(W - lr * (s + eps) * O) - L(W - lr * (s - eps) * O)) / (2 * eps)
print(f"finite difference dL/ds = {fd:.6f}, -lr * g_t.O = {-lr * g @ O:.6f}")
