# Non-Uniform Noise-to-Signal Ratio in the REINFORCE Policy-Gradient Estimator

OpenReview `Ol99zoW31J` · arXiv `2602.01460v3`.

This is a clean-room CPU reproduction: the primary arXiv source contains no
released author implementation. It checks all three scored claims at their
mathematical scope, rather than presenting sampled RL rollouts as exact
evidence.

1. Exact finite-horizon linear-Gaussian REINFORCE moments are evaluated by
   independent Gaussian quadrature, covariance recurrences, and finite
   differences.
2. The one-step double-integrator NSR landscape is swept over policy and
   initial-state noise to test the predicted non-uniform and blow-up regime.
3. A nonlinear cubic system with a tanh policy checks the stated conditional
   fourth-moment upper bound and rejects a deliberately weakened bound.

Run the eventual complete gate from this directory with
`source .venv/bin/activate && python repro/src/publication_gate.py`.
