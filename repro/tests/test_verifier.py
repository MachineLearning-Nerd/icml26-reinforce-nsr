from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from verify_reinforce_nsr import lqg_sample, nonlinear_cell, theorem_one_step


def double_integrator():
    return (
        np.array([[1.0, .1], [0.0, 1.0]]), np.array([[0.0], [.1]]),
        np.array([[-1.0, -3.0]]), np.eye(2), np.array([[.01]]),
    )


def test_one_step_formula_has_positive_variance():
    a, b, k, qs, qa = double_integrator()
    result = theorem_one_step(a, b, k, np.array([[.1 ** 2]]), np.eye(2), qs, qa)
    assert result["variance"] > 0 and result["nsr"] > 0


def test_smaller_policy_noise_increases_nsr_in_blowup_regime():
    a, b, k, qs, qa = double_integrator()
    high = theorem_one_step(a, b, k, np.array([[.1 ** 2]]), np.eye(2), qs, qa)["nsr"]
    low = theorem_one_step(a, b, k, np.array([[.01 ** 2]]), np.eye(2), qs, qa)["nsr"]
    assert low > 50 * high


def test_quadrature_sample_has_correct_gradient_shapes():
    a, b, k, qs, qa = double_integrator()
    gk, gl, reward = lqg_sample(np.zeros(3), a, b, k, np.array([[.1 ** 2]]), np.eye(2), qs, qa, 1)
    assert gk.shape == k.shape and gl.shape == (1,) and reward <= 0


def test_non_linear_bound_rejects_missing_inverse_factor():
    lhs_theta, lhs_l, bound_theta, bound_l, mutation = nonlinear_cell(np.array([.4, .7, -.2]), .12)
    assert lhs_theta <= bound_theta and lhs_l <= bound_l
    assert lhs_theta > mutation
