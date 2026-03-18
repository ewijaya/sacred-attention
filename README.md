# Toward a Mathematics of Sacred Attention

**Markov Absorption and Harmonic Resonance in the Rosary**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19078915.svg)](https://doi.org/10.5281/zenodo.19078915)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![arXiv](https://img.shields.io/badge/arXiv-pending-b31b1b.svg)]()
[![LaTeX](https://img.shields.io/badge/Built_with-LaTeX-008080.svg)](https://www.latex-project.org/)

## Overview

This paper develops two complementary mathematical models to explain why the Catholic Rosary's specific structure (10-bead decades with mystery meditations) proves effective for deepening contemplative attention.

### Model A: Markov Chain Absorption
- Models attentional states as a Markov chain: Distracted → Surface Prayer → Attentive Prayer → Deep Contemplation (absorbing)
- Decade structure provides periodic "attention resets" via mystery meditation
- Derives fundamental matrix N = (I−Q)⁻¹ and expected absorption times
- **Key result**: Rosary structure reduces absorption time by >54% vs. unstructured prayer

### Model B: Harmonic Resonance
- Models attentional dynamics as a damped harmonic oscillator with natural frequency ~0.1 Hz
- Rosary's Ave Maria rhythm naturally entrains respiration to 0.1 Hz (Bernardi et al. 2001)
- Derives resonance conditions and frequency response
- **Key result**: Rosary frequency lies within 6% of resonance peak, achieving 94% of maximum power gain

## Key Results

| Result | Value |
|--------|-------|
| Absorption time reduction (Rosary vs. unstructured) | >54% |
| Optimal decade length L* | 10 (proven near-optimal) |
| Rosary frequency vs. resonance peak | within 6% |
| Power gain at Rosary frequency | 94% of maximum |
| Empirical anchor | Bernardi et al. 2001 (BMJ) |

## Files

| File | Description |
|------|-------------|
| `manuscript.tex` | Full LaTeX source (IEEEtran format) |
| `manuscript.pdf` | Compiled PDF (7 pages, 4 figures) |
| `compute_data_v3.py` | Numerical computations and model validation |

## Compilation

```bash
pdflatex manuscript.tex
pdflatex manuscript.tex  # Run twice for cross-references
```

Requires: `amsmath`, `amsthm`, `tikz`, `pgfplots`, `booktabs` (standard TeX Live packages).

## Mathematical Content

- 8 Definitions (formal state space, absorbing chains, resonance conditions)
- 2 Theorems with complete proofs (absorption time reduction, optimal decade length)
- 2 Propositions with proofs (resonance condition, bandwidth analysis)
- 4 Worked numerical examples
- 4 TikZ/pgfplots figures (state diagram, absorption curve, frequency response, attention trajectories)

## Citation

```bibtex
@article{wijaya2026sacred,
  title   = {Toward a Mathematics of Sacred Attention: Markov Absorption and
             Harmonic Resonance in the Rosary},
  author  = {Wijaya, Edward},
  year    = {2026},
  doi     = {10.5281/zenodo.19078915},
  url     = {https://doi.org/10.5281/zenodo.19078915},
  publisher = {Zenodo},
  note    = {Preprint}
}
```

## References

1. Bernardi L, Sleight P, et al. "Effect of rosary prayer and yoga mantras on autonomic cardiovascular rhythms." *BMJ*. 2001;323:1446–9.
2. Kemeny JG, Snell JL. *Finite Markov Chains*. Springer, 1976.
3. Lutz A, Slagter HA, et al. "Attention regulation and monitoring in meditation." *Trends in Cognitive Sciences*. 2008;12(4):163–169.
4. Braboszcz C, Delorme A. "Lost in thoughts: neural markers of low alertness during mind wandering." *NeuroImage*. 2011;54(4):3040–7.
5. Smallwood J, Schooler JW. "The restless mind." *Psychological Bulletin*. 2006;132(6):946–958.
6. Klimesch W. "Alpha-band oscillations, attention, and controlled access to stored information." *Trends in Cognitive Sciences*. 2012;16(12):606–617.
7. Cahn BR, Polich J. "Meditation states and traits." *Psychological Bulletin*. 2006;132(2):180–211.
8. Strogatz SH. "From Kuramoto to Crawford." *Physica D*. 2000;143(1–4):1–20.

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt this material with appropriate attribution.

## Author

**Edward Wijaya**
Independent Researcher, Osaka, Japan
[ORCID: 0000-0002-1234-0761](https://orcid.org/0000-0002-1234-0761)
