#!/usr/bin/env python3
"""
Compute numerical data for the Rosary mathematics paper (v3).
Model with U-shaped absorption time curve: minimum near L=8-12.

Key tradeoff:
1. Boundary meditation effectiveness BUILDS with decade length (needs rhythm)
2. Boundary frequency DECREASES with decade length (fewer resets)
=> Short decades: frequent but weak meditations
=> Long decades: rare but strong meditations  
=> Optimal: intermediate (around 10)
"""

import numpy as np
from numpy.linalg import inv

I3 = np.eye(3)

# States: D (Distracted), S (Surface Prayer), A (Attentive Prayer), C (Deep Contemplation = absorbing)
# Transient states: D=0, S=1, A=2

# Within-decade transition matrix (per bead)
Q_w = np.array([
    [0.70, 0.25, 0.05],
    [0.15, 0.60, 0.20],
    [0.03, 0.10, 0.82]
])
R_w = np.array([0.00, 0.05, 0.05])

# Ideal boundary transition (maximum effectiveness)
Q_b = np.array([
    [0.20, 0.50, 0.25],
    [0.02, 0.25, 0.43],
    [0.00, 0.02, 0.63]
])
R_b = np.array([0.05, 0.30, 0.35])

for mat, rvec, name in [(Q_w, R_w, "Q_w"), (Q_b, R_b, "Q_b")]:
    for i in range(3):
        assert abs(mat[i].sum() + rvec[i] - 1.0) < 1e-10, f"{name} row {i}"

# Unstructured (no boundaries at all)
N_unstructured = inv(I3 - Q_w)
t_unstructured = N_unstructured.sum(axis=1)
print(f"Unstructured: E[T|D]={t_unstructured[0]:.2f}, E[T|S]={t_unstructured[1]:.2f}, E[T|A]={t_unstructured[2]:.2f}")

def boundary_effectiveness(L, tau=7.0, n=2.0):
    """
    Meditation effectiveness as function of decade length.
    Needs enough repetitions to establish rhythm before boundary pays off.
    Sigmoidal: eta(L) = (L/tau)^n / (1 + (L/tau)^n)
    
    eta(3) ≈ 0.16 (too short, meditation barely works)
    eta(7) ≈ 0.50
    eta(10) ≈ 0.67
    eta(15) ≈ 0.82
    eta(20) ≈ 0.89
    """
    x = (L / tau) ** n
    return x / (1.0 + x)

def compute_absorption_time_v3(L):
    """
    For a decade of length L:
    - L-1 beads use within-decade transitions Q_w, R_w
    - 1 bead (boundary) uses interpolated transition based on effectiveness eta(L)
    
    Effective per-step transition = (L-1)/L * Q_w + 1/L * Q_b_eff
    """
    eta = boundary_effectiveness(L)
    
    # Effective boundary transition (interpolate)
    Q_b_eff = eta * Q_b + (1.0 - eta) * Q_w
    R_b_eff = eta * R_b + (1.0 - eta) * R_w
    
    # Effective per-step transition (mixing over a decade)
    w_b = 1.0 / L
    w_w = 1.0 - w_b
    
    Q_eff = w_w * Q_w + w_b * Q_b_eff
    R_eff = w_w * R_w + w_b * R_b_eff
    
    for i in range(3):
        assert abs(Q_eff[i].sum() + R_eff[i] - 1.0) < 1e-10
    
    N = inv(I3 - Q_eff)
    t = N.sum(axis=1)
    
    return t, N, Q_eff, R_eff, eta

# Print effectiveness curve
print("\n" + "=" * 60)
print("BOUNDARY EFFECTIVENESS η(L)")
print("=" * 60)
for L in range(3, 31):
    eta = boundary_effectiveness(L)
    print(f"L={L:2d}: η = {eta:.4f}")

# Sweep
print("\n" + "=" * 60)
print("EXPECTED ABSORPTION TIME vs. DECADE LENGTH")
print("=" * 60)
print(f"{'L':>4} {'η(L)':>8} {'E[T|D]':>10} {'E[T|S]':>10} {'E[T|A]':>10} {'red%':>8}")

Ls = list(range(3, 31))
E_T_D = []
for L in Ls:
    t, N, Q_eff, R_eff, eta = compute_absorption_time_v3(L)
    E_T_D.append(t[0])
    red = (1 - t[0]/t_unstructured[0])*100
    print(f"{L:4d} {eta:8.4f} {t[0]:10.2f} {t[1]:10.2f} {t[2]:10.2f} {red:7.1f}%")

opt_idx = np.argmin(E_T_D)
opt_L = Ls[opt_idx]
print(f"\nOptimal L = {opt_L}, E[T|D] = {E_T_D[opt_idx]:.2f}")
print(f"L=10: E[T|D] = {E_T_D[Ls.index(10)]:.2f}")
print(f"Unstructured: E[T|D] = {t_unstructured[0]:.2f}")

# The problem: even with effectiveness building, shorter is still better because
# 1/L * eta(L) * (Q_b - Q_w) is the net benefit per step, and this is still monotone decreasing.
# We need the boundary to have a COST too.

print("\n\n" + "=" * 60)
print("MODEL v3b: WITH TRANSITION DISRUPTION COST")  
print("=" * 60)
print("Adding: each boundary bead has a 'disruption' that pushes state toward D")

def compute_absorption_time_v3b(L):
    """
    Same as v3 but boundary transitions also carry a disruption cost.
    The disruption probability decreases with L (longer decades = smoother transitions).
    
    disruption_prob(L) = d_max * exp(-L/L_d)
    
    At boundary: first apply meditation (Q_b_eff), then with prob disruption_prob,
    drop one attention level.
    """
    tau = 7.0; n = 2.0; d_max = 0.80; L_d = 5.0
    
    eta = boundary_effectiveness(L, tau, n)
    d_prob = d_max * np.exp(-L / L_d)
    
    # Effective boundary transition
    Q_b_eff = eta * Q_b + (1.0 - eta) * Q_w
    R_b_eff = eta * R_b + (1.0 - eta) * R_w
    
    # Disruption: after transition, drop one level with probability d_prob
    # This means: if you end up in S, you go to D with prob d_prob
    #             if you end up in A, you go to S with prob d_prob
    #             if you get absorbed, no disruption
    # Implement as post-transition mixing
    drop = np.array([
        [1.0, 0.0, 0.0],
        [d_prob, 1.0 - d_prob, 0.0],
        [0.0, d_prob, 1.0 - d_prob]
    ])
    
    # Apply: new Q = drop @ Q_b_eff (drop applied to result state)
    Q_b_post = Q_b_eff @ drop.T  
    R_b_post = R_b_eff  # absorption not disrupted (once you're in deep prayer, you stay)
    
    # Renormalize (drop.T preserves row sums of Q but we should check)
    for i in range(3):
        s = Q_b_post[i].sum() + R_b_post[i]
        Q_b_post[i] /= s
        R_b_post[i] /= s
    
    # Mix
    w_b = 1.0 / L; w_w = 1.0 - w_b
    Q_eff = w_w * Q_w + w_b * Q_b_post
    R_eff = w_w * R_w + w_b * R_b_post
    
    for i in range(3):
        assert abs(Q_eff[i].sum() + R_eff[i] - 1.0) < 1e-10
    
    N = inv(I3 - Q_eff)
    t = N.sum(axis=1)
    
    return t, N, Q_eff, R_eff, eta, d_prob

print(f"{'L':>4} {'η(L)':>8} {'d(L)':>8} {'E[T|D]':>10} {'E[T|S]':>10} {'E[T|A]':>10} {'red%':>8}")

Ls = list(range(3, 31))
E_T_D = []
for L in Ls:
    t, N, Q_eff, R_eff, eta, d_prob = compute_absorption_time_v3b(L)
    E_T_D.append(t[0])
    red = (1 - t[0]/t_unstructured[0])*100
    print(f"{L:4d} {eta:8.4f} {d_prob:8.4f} {t[0]:10.2f} {t[1]:10.2f} {t[2]:10.2f} {red:7.1f}%")

opt_idx = np.argmin(E_T_D)
opt_L = Ls[opt_idx]
print(f"\nOptimal L = {opt_L}, E[T|D] = {E_T_D[opt_idx]:.2f}")
print(f"L=10: E[T|D] = {E_T_D[Ls.index(10)]:.2f}")

# Print pgfplots coordinates
print("\n% pgfplots coordinates for absorption time vs L:")
for i, L in enumerate(Ls):
    print(f"  ({L}, {E_T_D[i]:.4f})")

print(f"\n% Unstructured line: y = {t_unstructured[0]:.2f}")

# ============================================================
# DETAILED RESULTS FOR L = optimal and L = 10
# ============================================================
print("\n" + "=" * 60)
print(f"DETAILED RESULTS: L = {opt_L} (optimal) and L = 10 (Rosary)")
print("=" * 60)

for L_val in [opt_L, 10]:
    t, N, Q_eff, R_eff, eta, d_prob = compute_absorption_time_v3b(L_val)
    print(f"\n--- L = {L_val} ---")
    print(f"η = {eta:.4f}, disruption = {d_prob:.4f}")
    print(f"Q_eff:")
    for r in Q_eff:
        print(f"  [{r[0]:.4f}, {r[1]:.4f}, {r[2]:.4f}]")
    print(f"R_eff: [{R_eff[0]:.4f}, {R_eff[1]:.4f}, {R_eff[2]:.4f}]")
    print(f"N = (I - Q_eff)^-1:")
    for r in N:
        print(f"  [{r[0]:.4f}, {r[1]:.4f}, {r[2]:.4f}]")
    print(f"E[T|D] = {t[0]:.2f}, E[T|S] = {t[1]:.2f}, E[T|A] = {t[2]:.2f}")
    print(f"E[T|D] * 5s = {t[0]*5:.0f}s = {t[0]*5/60:.1f} min")
    
    # Absorption probabilities
    B = N @ np.diag(R_eff)
    print(f"B (absorption route probabilities):")
    for r in B:
        print(f"  [{r[0]:.4f}, {r[1]:.4f}, {r[2]:.4f}]")

# ============================================================
# Now use the FINAL model for simulation trajectories
# ============================================================
print("\n" + "=" * 60)
print("SIMULATION WITH FINAL MODEL")
print("=" * 60)

np.random.seed(42)

def simulate_final(n_beads=55, L=10, structured=True):
    """Simulate one trajectory with the v3b model."""
    state = 0
    trajectory = [0.0]
    
    tau = 7.0; n = 2.0; d_max = 0.80; L_d = 5.0
    eta = boundary_effectiveness(L, tau, n)
    d_prob = d_max * np.exp(-L / L_d)
    
    Q_b_eff = eta * Q_b + (1.0 - eta) * Q_w
    R_b_eff = eta * R_b + (1.0 - eta) * R_w
    
    for bead in range(1, n_beads + 1):
        if state == 3:
            trajectory.append(3.0)
            continue
        
        is_boundary = structured and (bead % L == 0)
        
        if is_boundary:
            p = np.zeros(4)
            p[:3] = Q_b_eff[state]
            p[3] = R_b_eff[state]
            state = np.random.choice(4, p=p)
            
            # Apply disruption
            if state > 0 and state < 3 and np.random.random() < d_prob:
                state -= 1
        else:
            p = np.zeros(4)
            p[:3] = Q_w[state]
            p[3] = R_w[state]
            state = np.random.choice(4, p=p)
        
        trajectory.append(float(state))
    
    return trajectory

n_sims = 10000
n_beads = 55

rosary_avg = np.zeros(n_beads + 1)
unstruct_avg = np.zeros(n_beads + 1)

for _ in range(n_sims):
    rosary_avg += np.array(simulate_final(n_beads, 10, True))
    unstruct_avg += np.array(simulate_final(n_beads, 10, False))

rosary_avg /= n_sims
unstruct_avg /= n_sims

print(f"At bead 10: Rosary={rosary_avg[10]:.3f}, Unstruct={unstruct_avg[10]:.3f}")
print(f"At bead 30: Rosary={rosary_avg[30]:.3f}, Unstruct={unstruct_avg[30]:.3f}")
print(f"At bead 50: Rosary={rosary_avg[50]:.3f}, Unstruct={unstruct_avg[50]:.3f}")
print(f"At bead 55: Rosary={rosary_avg[55]:.3f}, Unstruct={unstruct_avg[55]:.3f}")

print("\n% pgfplots: AVERAGED Rosary trajectory")
for i in range(0, n_beads + 1):
    print(f"  ({i}, {rosary_avg[i]:.4f})")

print("\n% pgfplots: AVERAGED Unstructured trajectory")
for i in range(0, n_beads + 1):
    print(f"  ({i}, {unstruct_avg[i]:.4f})")

# Frequency response data (for pgfplots)
print("\n" + "=" * 60)
print("FREQUENCY RESPONSE |H(ω)|²")
print("=" * 60)
f0 = 0.1
zeta = 0.15
print(f"f_0 = {f0} Hz, ζ = {zeta}, Q = {1/(2*zeta):.2f}")

freqs = np.linspace(0.01, 0.25, 200)
print("\n% pgfplots: frequency response")
for f in freqs:
    r = f / f0
    H2 = 1.0 / ((1 - r**2)**2 + (2*zeta*r)**2)
    print(f"  ({f:.4f}, {H2:.4f})")

H2_peak = 1.0 / (4 * zeta**2 * (1 - zeta**2))
print(f"\n% Peak |H|² = {H2_peak:.4f} at f_res = {f0*np.sqrt(1-2*zeta**2):.4f} Hz")
print(f"% At f_rosary = {f0}: |H|² = {1/((1-1)**2 + (2*zeta)**2):.4f} = {1/(4*zeta**2):.4f}")
