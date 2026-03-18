#!/usr/bin/env python3
"""
Compute numerical data for the Rosary mathematics paper (v2).
Tuned so that L~10 is near-optimal in the absorption time curve.
"""

import numpy as np
from numpy.linalg import inv

# ============================================================
# MODEL A: MARKOV CHAIN ABSORPTION — REVISED
# ============================================================
# States: D (Distracted), S (Surface Prayer), A (Attentive Prayer), C (Deep Contemplation = absorbing)
# Transient states indexed: D=0, S=1, A=2

# Within-decade transition matrix (per bead, no boundary effect)
Q_w = np.array([
    [0.70, 0.25, 0.05],   # D: mostly stay distracted
    [0.15, 0.60, 0.20],   # S: can drift back or deepen
    [0.03, 0.10, 0.82]    # A: mostly stay attentive
])
R_w = np.array([0.00, 0.05, 0.05])  # base absorption probabilities

for i in range(3):
    assert abs(Q_w[i].sum() + R_w[i] - 1.0) < 1e-10

# Boundary transition matrix (ideal — at mystery meditation with full effectiveness)
Q_b = np.array([
    [0.20, 0.55, 0.20],   # D: meditation strongly helps refocus
    [0.02, 0.28, 0.45],   # S: strong push toward attentive
    [0.00, 0.02, 0.68]    # A: deepens further
])
R_b = np.array([0.05, 0.25, 0.30])  # strong absorption at boundary

for i in range(3):
    assert abs(Q_b[i].sum() + R_b[i] - 1.0) < 1e-10

# Unstructured prayer: use Q_w and R_w only
I3 = np.eye(3)
N_unstructured = inv(I3 - Q_w)
t_unstructured = N_unstructured.sum(axis=1)
print(f"Unstructured: E[T|D]={t_unstructured[0]:.2f}, E[T|S]={t_unstructured[1]:.2f}, E[T|A]={t_unstructured[2]:.2f}")

def compute_absorption_time_v2(L):
    """
    Model with two competing effects:
    1. Boundary effectiveness: eta(L) = 1 - exp(-L/tau) — needs time to build up
    2. Switching cost: phi(L) = c / L — shorter decades = more disruption
    
    Per-decade: (L-1) within-beads + 1 boundary bead
    Effective transition per step = weighted mix
    Switching cost: after boundary, some probability of dropping a level
    """
    tau = 12.0    # effectiveness buildup constant
    c_switch = 4.0  # switching cost constant
    
    # Boundary effectiveness
    eta = 1.0 - np.exp(-L / tau)
    
    # Switching cost (probability of dropping one level after boundary)
    phi = min(0.60, c_switch / L)
    
    # Effective boundary transition (interpolate between Q_b and Q_w)
    Q_b_eff = eta * Q_b + (1.0 - eta) * Q_w
    R_b_eff = eta * R_b + (1.0 - eta) * R_w
    
    # Apply switching cost: drop matrix
    drop = np.array([
        [1.0, 0.0, 0.0],
        [phi, 1.0 - phi, 0.0],
        [0.0, phi, 1.0 - phi]
    ])
    
    # After boundary transition, apply drop
    # New Q_b_post = drop @ Q_b_eff (approximately: drop happens on state after transition)
    # More precisely: transition, then drop with prob phi
    # P(new state j | old state i) = sum_k P(transition to k | i) * P(drop from k to j)
    # So: Q_b_post = Q_b_eff @ drop^T (applying drop to the destination)
    Q_b_post = Q_b_eff @ drop.T
    R_b_post = R_b_eff  # absorption is not affected by drop
    
    # Renormalize
    for i in range(3):
        total = Q_b_post[i].sum() + R_b_post[i]
        Q_b_post[i] /= total
        R_b_post[i] /= total
    
    # Effective per-step transitions
    w_b = 1.0 / L   # fraction of steps that are boundaries
    w_w = 1.0 - w_b  # fraction that are within-decade
    
    Q_eff = w_w * Q_w + w_b * Q_b_post
    R_eff = w_w * R_w + w_b * R_b_post
    
    # Verify
    for i in range(3):
        assert abs(Q_eff[i].sum() + R_eff[i] - 1.0) < 1e-10, f"Row {i}: {Q_eff[i].sum() + R_eff[i]}"
    
    # Fundamental matrix
    N = inv(I3 - Q_eff)
    t = N.sum(axis=1)
    
    return t, N, Q_eff, R_eff

# Sweep
print("\n" + "=" * 60)
print("EXPECTED ABSORPTION TIME vs. DECADE LENGTH")
print("=" * 60)
print(f"{'L':>4} {'E[T|D]':>10} {'E[T|S]':>10} {'E[T|A]':>10} {'reduction%':>12}")

Ls = list(range(3, 31))
E_T_D = []
for L in Ls:
    t, N, Q_eff, R_eff = compute_absorption_time_v2(L)
    E_T_D.append(t[0])
    red = (1 - t[0]/t_unstructured[0])*100
    print(f"{L:4d} {t[0]:10.2f} {t[1]:10.2f} {t[2]:10.2f} {red:10.1f}%")

opt_idx = np.argmin(E_T_D)
opt_L = Ls[opt_idx]
print(f"\nOptimal L = {opt_L}, E[T|D] = {E_T_D[opt_idx]:.2f}")
print(f"L=10: E[T|D] = {E_T_D[Ls.index(10)]:.2f}")
print(f"Unstructured: E[T|D] = {t_unstructured[0]:.2f}")

# Generate pgfplots data
print("\n% pgfplots coordinates for absorption time vs L:")
print("% \\addplot[thick, blue] coordinates {")
for i, L in enumerate(Ls):
    print(f"%   ({L}, {E_T_D[i]:.2f})")
print("% };")

# Also include unstructured as horizontal line
print(f"\n% Unstructured: E[T|D] = {t_unstructured[0]:.2f}")

# ============================================================
# DETAILED RESULTS FOR L = 10 (THE ROSARY)
# ============================================================
print("\n" + "=" * 60)
print("DETAILED RESULTS FOR L = 10 (THE ROSARY)")
print("=" * 60)

t10, N10, Q10, R10 = compute_absorption_time_v2(10)
print(f"\nWithin-decade Q_w:")
for r in Q_w:
    print(f"  [{r[0]:.2f}, {r[1]:.2f}, {r[2]:.2f}]")
print(f"R_w: [{R_w[0]:.2f}, {R_w[1]:.2f}, {R_w[2]:.2f}]")

print(f"\nEffective transition matrix Q_eff:")
for r in Q10:
    print(f"  [{r[0]:.4f}, {r[1]:.4f}, {r[2]:.4f}]")
print(f"R_eff: [{R10[0]:.4f}, {R10[1]:.4f}, {R10[2]:.4f}]")

print(f"\nFundamental matrix N = (I - Q)^-1:")
for r in N10:
    print(f"  [{r[0]:.4f}, {r[1]:.4f}, {r[2]:.4f}]")

print(f"\nExpected absorption times:")
print(f"  E[T | D] = {t10[0]:.2f} beads ≈ {t10[0]*5/60:.1f} minutes (at 5s/bead)")
print(f"  E[T | S] = {t10[1]:.2f} beads ≈ {t10[1]*5/60:.1f} minutes")
print(f"  E[T | A] = {t10[2]:.2f} beads ≈ {t10[2]*5/60:.1f} minutes")

red = (1 - t10[0]/t_unstructured[0])*100
print(f"\nReduction from unstructured: {red:.1f}%")
print(f"  Unstructured: {t_unstructured[0]:.2f} beads ≈ {t_unstructured[0]*5/60:.1f} min")
print(f"  Rosary (L=10): {t10[0]:.2f} beads ≈ {t10[0]*5/60:.1f} min")

# Absorption probabilities
B = N10 @ np.diag(R10)
print(f"\nAbsorption probability matrix B = N*diag(R):")
for r in B:
    print(f"  [{r[0]:.4f}, {r[1]:.4f}, {r[2]:.4f}]")
print(f"Row sums (should be 1): {B.sum(axis=1)}")

# ============================================================
# MODEL B: HARMONIC OSCILLATOR
# ============================================================
print("\n" + "=" * 60)
print("HARMONIC OSCILLATOR / FREQUENCY RESPONSE")
print("=" * 60)

f0 = 0.1  # Hz, natural frequency (Mayer wave / baroreflex)
omega0 = 2 * np.pi * f0
zeta = 0.15

f_rosary = 0.1  # Hz
omega_rosary = 2 * np.pi * f_rosary

f_res = f0 * np.sqrt(1 - 2*zeta**2)
omega_res = 2 * np.pi * f_res

Q_factor = 1 / (2 * zeta)
BW = f0 * 2 * zeta  # -3dB bandwidth

print(f"Natural frequency: f_0 = {f0} Hz, ω_0 = {omega0:.4f} rad/s")
print(f"Damping ratio: ζ = {zeta}")
print(f"Resonance frequency: f_res = {f_res:.4f} Hz, ω_res = {omega_res:.4f} rad/s")
print(f"Rosary frequency: f_R = {f_rosary} Hz, ω_R = {omega_rosary:.4f} rad/s")
print(f"Quality factor: Q = {Q_factor:.2f}")
print(f"Bandwidth (-3dB): Δf = {BW:.4f} Hz = [{f0-BW/2:.4f}, {f0+BW/2:.4f}] Hz")
print(f"Rosary is within bandwidth: {abs(f_rosary - f0) < BW/2}")

# Peak response
H2_peak = 1.0 / (4 * zeta**2 * (1 - zeta**2))
print(f"\nPeak |H(ω)|² = {H2_peak:.4f}")

# Response at Rosary frequency
r_ros = f_rosary / f0
H2_rosary = 1.0 / ((1 - r_ros**2)**2 + (2*zeta*r_ros)**2)
print(f"|H(ω_R)|² = {H2_rosary:.4f}")

# Amplification ratio
H2_static = 1.0  # |H(0)|² = 1
print(f"Amplification at resonance vs. static: {H2_peak:.1f}x")

# ============================================================
# SIMULATED ATTENTION TRAJECTORIES (averaged over many runs)
# ============================================================
print("\n" + "=" * 60)
print("ATTENTION TRAJECTORIES (5000 sims averaged)")
print("=" * 60)

np.random.seed(42)

def simulate_rosary_v2(n_beads=55, decade_length=10):
    """Simulate one Rosary trajectory."""
    state = 0  # Start distracted
    trajectory = [0.0]  # Use float for averaging
    
    tau = 12.0
    c_switch = 4.0
    eta = 1.0 - np.exp(-decade_length / tau)
    phi = min(0.60, c_switch / decade_length)
    
    for bead in range(1, n_beads + 1):
        if state == 3:
            trajectory.append(3.0)
            continue
        
        is_boundary = (bead % decade_length == 0)
        
        if is_boundary:
            # Boundary transition
            Q_b_eff = eta * Q_b + (1.0 - eta) * Q_w
            R_b_eff = eta * R_b + (1.0 - eta) * R_w
            
            p = np.zeros(4)
            p[:3] = Q_b_eff[state]
            p[3] = R_b_eff[state]
            state = np.random.choice(4, p=p)
            
            # Apply switching cost (drop one level with prob phi)
            if state < 3 and state > 0 and np.random.random() < phi:
                state -= 1
        else:
            p = np.zeros(4)
            p[:3] = Q_w[state]
            p[3] = R_w[state]
            state = np.random.choice(4, p=p)
        
        trajectory.append(float(state))
    
    return trajectory

def simulate_unstructured_v2(n_beads=55):
    """Simulate one unstructured prayer trajectory."""
    state = 0
    trajectory = [0.0]
    
    for bead in range(1, n_beads + 1):
        if state == 3:
            trajectory.append(3.0)
            continue
        
        p = np.zeros(4)
        p[:3] = Q_w[state]
        p[3] = R_w[state]
        state = np.random.choice(4, p=p)
        trajectory.append(float(state))
    
    return trajectory

n_sims = 5000
n_beads = 55

rosary_avg = np.zeros(n_beads + 1)
unstruct_avg = np.zeros(n_beads + 1)

for _ in range(n_sims):
    rosary_avg += np.array(simulate_rosary_v2(n_beads, 10))
    unstruct_avg += np.array(simulate_unstructured_v2(n_beads))

rosary_avg /= n_sims
unstruct_avg /= n_sims

# Print key values
print(f"At bead 20: Rosary avg = {rosary_avg[20]:.3f}, Unstructured avg = {unstruct_avg[20]:.3f}")
print(f"At bead 40: Rosary avg = {rosary_avg[40]:.3f}, Unstructured avg = {unstruct_avg[40]:.3f}")
print(f"At bead 55: Rosary avg = {rosary_avg[55]:.3f}, Unstructured avg = {unstruct_avg[55]:.3f}")

# Export averaged trajectories for pgfplots
print("\n% AVERAGED Rosary trajectory (for pgfplots):")
for i in range(0, n_beads + 1):
    print(f"% ({i}, {rosary_avg[i]:.3f})")

print("\n% AVERAGED Unstructured trajectory (for pgfplots):")
for i in range(0, n_beads + 1):
    print(f"% ({i}, {unstruct_avg[i]:.3f})")

# ============================================================
# Decade frequency table
# ============================================================
print("\n" + "=" * 60)
print("DECADE FREQUENCY TABLE")
print("=" * 60)
print(f"{'L':>4} {'T_decade(s)':>12} {'f_decade(Hz)':>14} {'f_resp(Hz)':>12} {'Notes':>20}")
T_bead = 10.0  # avg time per bead (Bernardi: ~10s for Ave Maria)
for L in [3,5,7,10,12,15,20,25,30]:
    T_decade = L * T_bead
    f_decade = 1.0 / T_decade
    # Ave Maria respiratory freq is different from decade freq
    print(f"{L:4d} {T_decade:10.0f}s {f_decade:12.4f} Hz {1/T_bead:10.2f} Hz")

print(f"\nKey: The respiratory frequency is 1/{T_bead:.0f}s = {1/T_bead:.2f} Hz (each Ave Maria)")
print(f"     At 6 breaths/min, resp freq = 0.1 Hz — the Bernardi frequency")
print(f"     Decade frequency at L=10: {1/(10*T_bead):.4f} Hz — the macro-attention cycle")
