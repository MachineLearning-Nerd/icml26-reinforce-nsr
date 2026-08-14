# Status — Ol99zoW31J

## Identity

- Paper: *Non-Uniform Noise-to-Signal Ratio in the REINFORCE Policy-Gradient Estimator*
- Authors: Haoyu Han and Heng Yang
- arXiv: `2602.01460v3`
- OpenReview: `Ol99zoW31J`
- Repository: `https://github.com/MachineLearning-Nerd/icml26-reinforce-nsr`

## Gate state

`SCOPED_PASS` / `VERIFIED_SCOPED_WITH_UNREPRODUCED_EXPERIMENTS`

The exact-moment, finite-horizon, NSR-landscape, and nonlinear-bound checks
pass. The strict paper-level status is `NOT_READY` because optimization
trajectory figures, sampled RL rollouts, and the broader polynomial/neural
experimental scope are not reproduced here. No score forecast is made.

## Evidence

- C1: 12 one-step cells and 13 finite-horizon systems, checked by independent
  Wick moments, degree-8 quadrature, covariance recursion, and finite differences.
- C2: 3,721 NSR landscape cells and an 80-point small-policy-noise sweep.
- C3: 48 nonlinear cubic/tanh cells with a retained inverse-covariance mutation
  control.
- Focused tests: `repro/tests/test_verifier.py`.
- Canonical gate: `publication_gate.json` and `outputs/publication_gate.json`.

## Provenance

The arXiv v3 source is vendored under `source/arxiv/` and its anchor hashes are
recorded in `sources.json`. The verifier is clean-room and does not rely on
private Trackio metadata, a queue handoff, or absolute local paths.
