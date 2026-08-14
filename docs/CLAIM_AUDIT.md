# Claim audit — Ol99zoW31J

The current gate evaluates the three live contracts represented by the
committed verifier. The result is exact or independently checked within these
finite contracts; it does not relabel every paper theorem or experiment as
reproduced.

## C1 — exact finite-horizon linear-Gaussian REINFORCE moments

Source anchors: `source/arxiv/sections/lqg.tex` for the one-step theorem and
finite-horizon LQG construction, plus `main.tex` for the paper identity.

Producer path:

1. `theorem_one_step` implements the paper’s Wick/Isserlis moment formulas for
   the gain and log-standard-deviation gradient components.
2. `normal_rule` and `quadrature` provide an independent degree-8 Gaussian
   quadrature route.
3. `finite_difference` differentiates the covariance-recursion objective for
   one- through five-step systems.
4. `main()` evaluates four policy standard deviations × three initial-state
   standard deviations (12 cells), then 13 finite-horizon systems.

Checker path:

- `repro/src/cumulative_science_gate.py` checks the recorded cell counts,
  moment/gradient tolerances, nonnegative variance, and retained degree-4
  control failures.
- `repro/tests/test_verifier.py` independently checks positive variance and
  gradient shapes.

Recorded result: maximum one-step mean error `9.714e-15`, maximum second-moment
relative error `1.095e-15`, 12 degree-4 controls rejected, and maximum
finite-horizon gradient relative error `1.699e-10`. Status:
`VERIFIED_SCOPED`.

## C2 — non-uniform NSR and small-policy-noise blow-up

Source anchor: the NSR scaling analysis and double-integrator example in
`source/arxiv/sections/lqg.tex`.

Producer path:

- `theorem_one_step` evaluates the fixed double-integrator setting over a
  61×61 grid of policy standard deviation and initial-state standard
  deviation.
- It then evaluates 80 policy standard deviations from `10^-4` through
  `10^-1` at fixed initial-state covariance to fit the small-policy-noise
  slope.

Checker path: `cumulative_science_gate.py` requires 3,721 landscape cells, a
span ratio above `1e6`, a fitted slope below `-1.9`, and zero monotonicity
failures. The tests also require the low-noise NSR to exceed the higher-noise
value by a factor of 50.

Recorded result: NSR ranges from `18.5004600` to `4.037626453e9`, with span
ratio `2.182446518e8`, fitted slope `-1.9999993696`, and zero monotonicity
failures. Status: `VERIFIED_SCOPED`.

## C3 — nonlinear fourth-moment variance upper bound

Source anchors: `source/arxiv/sections/nonlinear_new.tex` and
`source/arxiv/sections/app-proof-nonlinear-upperbound.tex`.

Producer path:

- `nonlinear_cell` evaluates a cubic scalar dynamics with a tanh policy over
  four parameter vectors × 12 policy standard deviations.
- It computes the mean-policy and log-standard-deviation fourth-moment
  quantities, the paper’s bounds, and a deliberately weakened mutation that
  omits the required inverse-covariance factor.

Checker path: `cumulative_science_gate.py` requires 48 cells, zero bound
violations, and at least one failed weakened-bound cell. The focused test
repeats a representative cell.

Recorded result: zero theta-bound failures, zero log-std-bound failures, and
26/48 failures for the weakened inverse-covariance control. Minimum retained
bound ratios are `3.1577` and `4.8720`. Status:
`VERIFIED_SCOPED_WITH_PROTOCOL_LIMITS`.

The limitation is material: this verifies the declared cubic/tanh finite
contract, not every polynomial system, neural policy, or optimization result in
the paper.

## Non-claims

- No author implementation or author-code parity is claimed.
- No sampled RL rollout, MuJoCo/GPOMDP experiment, or optimization-trajectory
  figure is counted as reproduced by the current gate.
- No score forecast is made.
