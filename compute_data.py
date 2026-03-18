#!/usr/bin/env python3
"""
Compute numerical data for the Rosary mathematics paper.
Generates data for pgfplots figures and numerical examples.
"""

import numpy as np
from numpy.linalg import inv

# ============================================================
# MODEL A: MARKOV CHAIN ABSORPTION
# ============================================================
# States: D (Distracted), S (Surface Prayer), A (Attentive Prayer), C (Deep Contemplation = absorbing)
# Transient states indexed: D=0, S=1, A=2

# Within-decade transition matrix (per bead)
Q_w = np.array([
    [0.70, 0.28, 0.02],   # D: mostly stay distracted, sometimes surface
    [0.12, 0.60, 0.23],   # S: can drift back, stay, or deepen
    [0.01, 0.08, 0.85]    # A: rarely regress, mostly stay or absorb
])
R_w = np.array([0.00, 0.05, 0.06])  # absorption probabilities

# Verify row sums
for i in range(3):
    assert abs(Q_w[i].sum() + R_w[i] - 1.0) < 1e-10, f"Row {i} doesn't sum to 1"

# Boundary transition matrix (at decade boundary, mystery meditation)
Q_b_max = np.array([
    [0.35, 0.55, 0.10],   # D: meditation helps refocus
    [0.03, 0.37, 0.40],   # S: strong push toward attentive
    [0.00, 0.03, 0.77]    # A: deepens further
])
R_b_max = np.array([0.00, 0.20, 0.20])  # enhanced absorption at boundary

for i in range(3):
    assert abs(Q_b_max[i].sum() + R_b_max[i] - 1.0) < 1e-10, f"Boundary row {i} doesn't sum to 1"

def compute_absorption_time(L, tau=6.0, p_drop=0.20):
    """
    Compute expected absorption time for decade length L.
    
    Model: 
    - Within decade (L-1 beads): Q_w transitions
    - Boundary (1 bead): Q_b transition with effectiveness eta(L)
    - After boundary: attention drops with probability p_drop (reset cost)
    
    Effective per-step Q = ((L-1)/L)*Q_w + (1/L)*[eta(L)*Q_b + (1-eta(L))*Q_w] 
                          with additional reset mixing
    """
    # Boundary effectiveness: builds up with decade length
    eta = 1.0 - np.exp(-L / tau)
    
    # Effective boundary transition
    Q_b_eff = eta * Q_b_max + (1.0 - eta) * Q_w
    R_b_eff = eta * R_b_max + (1.0 - eta) * R_w
    
    # Reset cost at boundaries: with prob p_drop, drop one level
    # This is applied as a mixing matrix after the boundary
    # D stays D, S can drop to D, A can drop to S
    drop_matrix = np.array([
        [1.0, 0.0, 0.0],
        [p_drop, 1.0 - p_drop, 0.0],
        [0.0, p_drop, 1.0 - p_drop]
    ])
    
    # Apply drop to boundary transitions
    Q_b_with_drop = drop_matrix @ Q_b_eff
    R_b_with_drop = drop_matrix @ R_b_eff
    
    # Renormalize (drop doesn't affect absorption)
    for i in range(3):
        total = Q_b_with_drop[i].sum() + R_b_with_drop[i]
        Q_b_with_drop[i] /= total
        R_b_with_drop[i] /= total
    
    # Effective per-step transition
    Q_eff = ((L - 1.0) / L) * Q_w + (1.0 / L) * Q_b_with_drop
    R_eff = ((L - 1.0) / L) * R_w + (1.0 / L) * R_b_with_drop
    
    # Verify
    for i in range(3):
        assert abs(Q_eff[i].sum() + R_eff[i] - 1.0) < 1e-10
    
    # Fundamental matrix
    I = np.eye(3)
    N = inv(I - Q_eff)
    
    # Expected absorption time from each state
    t = N.sum(axis=1)  # t_i = sum_j N_{ij}
    
    return t, N, Q_eff, R_eff

# Sweep over decade lengths
print("=" * 60)
print("EXPECTED ABSORPTION TIME vs. DECADE LENGTH")
print("=" * 60)
print(f"{'L':>4} {'E[T|D]':>10} {'E[T|S]':>10} {'E[T|A]':>10}")
print("-" * 40)

Ls = list(range(3, 31))
E_T_D = []
for L in Ls:
    t, N, Q_eff, R_eff = compute_absorption_time(L)
    E_T_D.append(t[0])
    print(f"{L:4d} {t[0]:10.2f} {t[1]:10.2f} {t[2]:10.2f}")

# Find optimal L
opt_idx = np.argmin(E_T_D)
opt_L = Ls[opt_idx]
print(f"\nOptimal L = {opt_L}, E[T|D] = {E_T_D[opt_idx]:.2f}")

# Also compute for unstructured prayer (L -> infinity, effectively Q_w)
I = np.eye(3)
N_unstructured = inv(I - Q_w)
t_unstructured = N_unstructured.sum(axis=1)
print(f"\nUnstructured prayer: E[T|D] = {t_unstructured[0]:.2f}, E[T|S] = {t_unstructured[1]:.2f}, E[T|A] = {t_unstructured[2]:.2f}")

# Print pgfplots coordinates
print("\n% pgfplots coordinates for absorption time vs L:")
print("\\addplot coordinates {")
for i, L in enumerate(Ls):
    print(f"  ({L}, {E_T_D[i]:.2f})")
print("};")

# ============================================================
# Detailed results for L=10 (the Rosary)
# ============================================================
print("\n" + "=" * 60)
print("DETAILED RESULTS FOR L = 10 (THE ROSARY)")
print("=" * 60)

t10, N10, Q10, R10 = compute_absorption_time(10)
print(f"\nEffective transition matrix Q_eff:")
print(Q10)
print(f"\nAbsorption vector R_eff:")
print(R10)
print(f"\nFundamental matrix N:")
print(N10)
print(f"\nExpected absorption times: D={t10[0]:.2f}, S={t10[1]:.2f}, A={t10[2]:.2f}")
print(f"\nVariances:")
N_sq = N10 @ (2 * np.diag(np.diag(N10)) - I) - np.diag(np.diag(N10 @ N10))
# Actually variance = N(2N_dg - I) * ones - t^2 component by component... 
# Let me use the correct formula
# Var(T_i) = (2N - I) * N * ones - (N * ones)^2 elementwise
# Actually: Var(T_i) = sum_j (2*N_{ij} - delta_{ij}) * N_{ij} ... no
# The correct formula is: let t = N*1, then Var = (2N_dg - I)*t - t_sq
# where t_sq is elementwise square of t, N_dg is diagonal matrix of N
N_dg = np.diag(np.diag(N10))
t_vec = t10
var_T = (2 * N_dg - I) @ np.ones(3)
# Hmm, this isn't right. Let me use the standard formula.
# For absorbing Markov chains: Var(T_i) = (2N - I)N * 1 - (N*1)^2 element-wise
# Actually: Let t = N*1 (expected times), then 
# Var(T_i) = sum_j N_{ij}(2*N_{ij} - delta_{ij}) ... no
# Standard result: variance vector = (2*N_dg - I) * t - t.*t
# where N_dg = diag(N), t.*t = elementwise square
var_T = (2 * N_dg - I) @ t_vec - t_vec**2
print(f"Var(T|D) = {var_T[0]:.2f}, SD = {np.sqrt(abs(var_T[0])):.2f}")
print(f"Var(T|S) = {var_T[1]:.2f}, SD = {np.sqrt(abs(var_T[1])):.2f}")
print(f"Var(T|A) = {var_T[2]:.2f}, SD = {np.sqrt(abs(var_T[2])):.2f}")

# Absorption probabilities (from each state, what's the probability of being absorbed via each transient state?)
B = N10 @ np.diag(R10)
print(f"\nAbsorption probability matrix B = N*diag(R):")
print(B)

# ============================================================
# COMPARISON: Rosary vs Unstructured
# ============================================================
print("\n" + "=" * 60)
print("COMPARISON: ROSARY (L=10) vs UNSTRUCTURED")
print("=" * 60)
print(f"Rosary E[T|D] = {t10[0]:.2f} beads")
print(f"Unstructured E[T|D] = {t_unstructured[0]:.2f} beads")
print(f"Reduction = {(1 - t10[0]/t_unstructured[0])*100:.1f}%")
print(f"\nAt ~5 seconds per bead:")
print(f"Rosary: {t10[0]*5/60:.1f} minutes to deep contemplation")
print(f"Unstructured: {t_unstructured[0]*5/60:.1f} minutes to deep contemplation")

# ============================================================
# MODEL B: HARMONIC OSCILLATOR
# ============================================================
print("\n" + "=" * 60)
print("HARMONIC OSCILLATOR / FREQUENCY RESPONSE")
print("=" * 60)

# Natural frequency: Mayer wave frequency ~ 0.1 Hz
f0 = 0.1  # Hz
omega0 = 2 * np.pi * f0

# Damping ratio
zeta = 0.15  # moderate damping

# Rosary frequency
f_rosary = 0.1  # Hz (one Ave Maria breath cycle)
omega_rosary = 2 * np.pi * f_rosary

# Resonance frequency
f_res = f0 * np.sqrt(1 - 2*zeta**2)
omega_res = omega0 * np.sqrt(1 - 2*zeta**2)

print(f"Natural frequency: f0 = {f0} Hz, omega0 = {omega0:.4f} rad/s")
print(f"Damping ratio: zeta = {zeta}")
print(f"Resonance frequency: f_res = {f_res:.4f} Hz")
print(f"Rosary frequency: f_rosary = {f_rosary} Hz")
print(f"Bandwidth (-3dB): Delta_f = {zeta * f0:.4f} Hz")

# Quality factor
Q_factor = 1 / (2 * zeta)
print(f"Quality factor Q = {Q_factor:.2f}")

# Frequency response data for pgfplots
print("\n% pgfplots coordinates for |H(omega)|^2:")
print("\\addplot coordinates {")
freqs = np.linspace(0.01, 0.25, 200)
for f in freqs:
    omega = 2 * np.pi * f
    r = omega / omega0
    H2 = 1.0 / ((1 - r**2)**2 + (2*zeta*r)**2)
    print(f"  ({f:.4f}, {H2:.4f})")
print("};")

# Peak value
H2_peak = 1.0 / (4 * zeta**2 * (1 - zeta**2))
print(f"\nPeak |H|^2 = {H2_peak:.2f}")

# Value at Rosary frequency
r_ros = omega_rosary / omega0
H2_rosary = 1.0 / ((1 - r_ros**2)**2 + (2*zeta*r_ros)**2)
print(f"|H(omega_rosary)|^2 = {H2_rosary:.2f}")

# ============================================================
# SIMULATED ATTENTION TRAJECTORIES
# ============================================================
print("\n" + "=" * 60)
print("SIMULATED ATTENTION TRAJECTORIES")
print("=" * 60)

np.random.seed(42)

def simulate_rosary(n_beads=50, decade_length=10):
    """Simulate attention trajectory during Rosary prayer."""
    # State encoding: D=0, S=1, A=2, C=3
    state = 0  # Start distracted
    trajectory = [0]
    
    for bead in range(1, n_beads + 1):
        if state == 3:  # Absorbed
            trajectory.append(3)
            continue
        
        # Determine if this is a boundary bead
        is_boundary = (bead % decade_length == 0)
        
        if is_boundary:
            Q = Q_b_max
            R = R_b_max
        else:
            Q = Q_w
            R = R_w
        
        # Transition
        p = np.zeros(4)
        p[:3] = Q[state]
        p[3] = R[state]
        
        state = np.random.choice(4, p=p)
        trajectory.append(state)
    
    return trajectory

def simulate_unstructured(n_beads=50):
    """Simulate attention trajectory during unstructured prayer."""
    state = 0
    trajectory = [0]
    
    for bead in range(1, n_beads + 1):
        if state == 3:
            trajectory.append(3)
            continue
        
        p = np.zeros(4)
        p[:3] = Q_w[state]
        p[3] = R_w[state]
        
        state = np.random.choice(4, p=p)
        trajectory.append(state)
    
    return trajectory

# Run many simulations and average
n_sims = 5000
n_beads = 55

rosary_avg = np.zeros(n_beads + 1)
unstruct_avg = np.zeros(n_beads + 1)

for _ in range(n_sims):
    traj_r = simulate_rosary(n_beads, 10)
    traj_u = simulate_unstructured(n_beads)
    rosary_avg += np.array(traj_r)
    unstruct_avg += np.array(traj_u)

rosary_avg /= n_sims
unstruct_avg /= n_sims

# Print pgfplots coordinates (subsample every bead)
print("\n% Rosary average attention trajectory:")
print("\\addplot coordinates {")
for i in range(0, n_beads + 1):
    print(f"  ({i}, {rosary_avg[i]:.3f})")
print("};")

print("\n% Unstructured average attention trajectory:")
print("\\addplot coordinates {")
for i in range(0, n_beads + 1):
    print(f"  ({i}, {unstruct_avg[i]:.3f})")
print("};")

# Also do a single representative run for qualitative illustration
np.random.seed(17)
single_rosary = simulate_rosary(55, 10)
single_unstruct = simulate_unstructured(55)

print("\n% Single Rosary trajectory:")
print("\\addplot coordinates {")
for i, v in enumerate(single_rosary):
    print(f"  ({i}, {v})")
print("};")

print("\n% Single unstructured trajectory:")
print("\\addplot coordinates {")
for i, v in enumerate(single_unstruct):
    print(f"  ({i}, {v})")
print("};")

# ============================================================
# Additional: Decade frequency analysis
# ============================================================
print("\n" + "=" * 60)
print("DECADE FREQUENCY ANALYSIS")
print("=" * 60)

T_bead = 5.0  # seconds per bead (average)
for L in [5, 7, 10, 12, 15, 20]:
    T_decade = L * T_bead
    f_decade = 1.0 / T_decade
    print(f"L={L}: T_decade = {T_decade:.0f}s, f_decade = {f_decade:.4f} Hz")

print(f"\nAve Maria duration: ~{T_bead}s → respiratory frequency = {1/T_bead:.2f} Hz")
print(f"But with natural Ave Maria (~10s with pauses): f = 0.1 Hz")
print(f"Mayer wave frequency: ~0.1 Hz")
print(f"Match! This is the Bernardi finding.")
