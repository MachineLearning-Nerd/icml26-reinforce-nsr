#!/usr/bin/env python3
"""Clean-room exact-moment audit for Ol99zoW31J's three live claims."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "sections/lqg.tex": "424e862b4297defbfcacf75ffef81b0381ef5ee5b6bf4b86059edbef85c9c7fb",
    "sections/nonlinear_new.tex": "558392eb62a93ec68ecebf94db516ab2dffdc9310905c8a1724c5185b6edfb1b",
    "sections/app-proof-nonlinear-upperbound.tex": "11ece2dad7fac254e2aa0a2439caee4bc5d8e545cadb9b20f0eeb4b3c4ecbe83",
}


def isserlis(cov: np.ndarray, *matrices: np.ndarray) -> float:
    """Independent Wick expansion for the paper's one-step quadratic moments."""
    trace = lambda matrix: float(np.trace(cov @ matrix))
    if len(matrices) == 1:
        return trace(matrices[0])
    if len(matrices) == 2:
        a, b = matrices
        return trace(a) * trace(b) + 2 * float(np.trace(cov @ a @ cov @ b))
    if len(matrices) == 3:
        a, b, c = matrices
        return (
            trace(a) * trace(b) * trace(c)
            + 2 * float(np.trace(cov @ a @ cov @ b)) * trace(c)
            + 2 * float(np.trace(cov @ a @ cov @ c)) * trace(b)
            + 2 * trace(a) * float(np.trace(cov @ b @ cov @ c))
            + 8 * float(np.trace(cov @ a @ cov @ b @ cov @ c))
        )
    raise ValueError("only one through three quadratic forms are required")


def theorem_one_step(A, B, K, sigma, sigma0, qs, qa):
    """Literal one-step theorem evaluator, separate from the quadrature path."""
    n, m = A.shape[0], B.shape[1]
    f = A + B @ K
    mss = f.T @ qs @ f + K.T @ qa @ K
    mse = f.T @ qs @ B + K.T @ qa
    mee = B.T @ qs @ B + qa
    inv2 = np.linalg.inv(sigma) @ np.linalg.inv(sigma)
    u, v = mse @ mse.T, mse @ sigma @ mse.T
    second_k = (
        isserlis(sigma, inv2) * isserlis(sigma0, np.eye(n), mss, mss)
        + isserlis(sigma0, np.eye(n)) * isserlis(sigma, inv2, mee, mee)
        + 2 * isserlis(sigma0, np.eye(n), mss) * isserlis(sigma, inv2, mee)
        + 4 * (2 * isserlis(sigma0, np.eye(n), u) + isserlis(sigma, inv2) * isserlis(sigma0, np.eye(n), v))
    )
    root = np.diag(np.sqrt(np.diag(sigma)))
    s = root @ mee @ root
    second_l = (
        2 * m * isserlis(sigma0, mss, mss)
        + (2 * m + 16) * np.trace(s) ** 2 + (4 * m + 32) * np.trace(s @ s) + 24 * np.square(np.diag(s)).sum()
        + 2 * isserlis(sigma0, mss) * (2 * m + 8) * np.trace(s)
        + 4 * (2 * m + 8) * isserlis(sigma0, mse @ sigma @ mse.T)
    )
    mean_k, mean_l = -2 * mse.T @ sigma0, -2 * np.diag(sigma @ mee)
    signal = float(np.square(mean_k).sum() + np.square(mean_l).sum())
    variance = float(second_k + second_l - signal)
    return {"mean_k": mean_k, "mean_l": mean_l, "second_k": float(second_k), "second_l": float(second_l), "signal": signal, "variance": variance, "nsr": variance / signal}


def normal_rule(order: int, dimension: int):
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes, weights = np.sqrt(2.0) * nodes, weights / np.sqrt(np.pi)
    for index in itertools.product(range(order), repeat=dimension):
        yield np.asarray([nodes[i] for i in index]), float(np.prod([weights[i] for i in index]))


def lqg_sample(z, A, B, K, sigma, sigma0, qs, qa, horizon):
    n, m = A.shape[0], B.shape[1]
    state = np.linalg.cholesky(sigma0) @ z[:n]
    epsilons = (np.linalg.cholesky(sigma) @ z[n:].reshape(horizon, m).T).T
    score_k, score_l, total = np.zeros_like(K), np.zeros(m), 0.0
    inverse = np.linalg.inv(sigma)
    for epsilon in epsilons:
        action = K @ state + epsilon
        next_state = A @ state + B @ action
        total -= float(next_state @ qs @ next_state + action @ qa @ action)
        score_k += np.outer(inverse @ epsilon, state)
        score_l += np.square(epsilon) / np.diag(sigma) - 1
        state = next_state
    return total * score_k, total * score_l, total


def quadrature(A, B, K, sigma, sigma0, qs, qa, horizon, order):
    mean_k, mean_l = np.zeros_like(K), np.zeros(B.shape[1])
    second_k = second_l = mean_return = 0.0
    for z, weight in normal_rule(order, A.shape[0] + horizon * B.shape[1]):
        gradient_k, gradient_l, reward = lqg_sample(z, A, B, K, sigma, sigma0, qs, qa, horizon)
        mean_k += weight * gradient_k
        mean_l += weight * gradient_l
        second_k += weight * float(np.square(gradient_k).sum())
        second_l += weight * float(np.square(gradient_l).sum())
        mean_return += weight * reward
    signal = float(np.square(mean_k).sum() + np.square(mean_l).sum())
    return {"mean_k": mean_k, "mean_l": mean_l, "second_k": second_k, "second_l": second_l, "mean_return": mean_return, "signal": signal, "variance": second_k + second_l - signal, "nsr": (second_k + second_l - signal) / signal}


def objective(A, B, K, log_std, sigma0, qs, qa, horizon):
    sigma = np.diag(np.exp(2 * log_std))
    covariance, total, f = sigma0.copy(), 0.0, A + B @ K
    for _ in range(horizon):
        action_cov = K @ covariance @ K.T + sigma
        next_cov = f @ covariance @ f.T + B @ sigma @ B.T
        total -= float(np.trace(qs @ next_cov) + np.trace(qa @ action_cov))
        covariance = next_cov
    return total


def finite_difference(A, B, K, log_std, sigma0, qs, qa, horizon):
    step, dk, dl = 1e-5, np.zeros_like(K), np.zeros_like(log_std)
    for index in np.ndindex(K.shape):
        plus, minus = K.copy(), K.copy(); plus[index] += step; minus[index] -= step
        dk[index] = (objective(A, B, plus, log_std, sigma0, qs, qa, horizon) - objective(A, B, minus, log_std, sigma0, qs, qa, horizon)) / (2 * step)
    for index in range(len(log_std)):
        plus, minus = log_std.copy(), log_std.copy(); plus[index] += step; minus[index] -= step
        dl[index] = (objective(A, B, K, plus, sigma0, qs, qa, horizon) - objective(A, B, K, minus, sigma0, qs, qa, horizon)) / (2 * step)
    return dk, dl


def nonlinear_cell(theta, std, order=16, horizon=3, s0=.4):
    lhs_theta = lhs_l = return4 = 0.0
    jacobian4 = np.zeros(horizon)
    for noises, weight in normal_rule(order, horizon):
        state, total, score_theta, score_l, jacobians = s0, 0.0, np.zeros(3), 0.0, []
        for noise_z in noises:
            tanh_value = math.tanh(theta[1] * state)
            mean = theta[0] * tanh_value + theta[2] * state
            jacobian = np.array([tanh_value, theta[0] * state * (1 - tanh_value ** 2), state])
            epsilon, action = std * noise_z, mean + std * noise_z
            state_next = .7 * state + .12 * state ** 3 + action
            total -= state_next ** 2 + .05 * action ** 2
            score_theta += jacobian * epsilon / std ** 2
            score_l += epsilon ** 2 / std ** 2 - 1
            jacobians.append(jacobian); state = state_next
        lhs_theta += weight * float(np.square(total * score_theta).sum())
        lhs_l += weight * (total * score_l) ** 2
        return4 += weight * total ** 4
        for t, jacobian in enumerate(jacobians):
            jacobian4[t] += weight * np.linalg.norm(jacobian) ** 4
    common = horizon * math.sqrt(return4) * math.sqrt(3 * std ** 4) * sum(np.sqrt(jacobian4))
    # For scalar Gaussian noise the proof's log-std fourth-moment constant is 2T^2 sqrt(15).
    return lhs_theta, lhs_l, common / std ** 4, 2 * horizon ** 2 * math.sqrt(15) * math.sqrt(return4), common


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", default="outputs/independent_verification.json"); args = parser.parse_args()
    for relative, expected in PINS.items():
        actual = hashlib.sha256((ROOT / "source/arxiv" / relative).read_bytes()).hexdigest()
        assert actual == expected, (relative, actual)
    A, B, K, qs, qa = np.array([[1., .1], [0., 1.]]), np.array([[0.], [.1]]), np.array([[-1., -3.]]), np.eye(2), np.array([[.01]])
    one = {"cells": 0, "max_mean_abs_error": 0., "max_second_relative_error": 0., "order4_controls_rejected": 0, "order4_max_relative_drift": 0.}
    for std in (.04, .1, .4, 1.2):
        for std0 in (.08, .5, 2.):
            sigma, sigma0 = np.array([[std ** 2]]), np.eye(2) * std0 ** 2
            formula, exact, insufficient = theorem_one_step(A, B, K, sigma, sigma0, qs, qa), quadrature(A, B, K, sigma, sigma0, qs, qa, 1, 5), quadrature(A, B, K, sigma, sigma0, qs, qa, 1, 4)
            one["cells"] += 1
            one["max_mean_abs_error"] = max(one["max_mean_abs_error"], float(np.max(np.abs(formula["mean_k"] - exact["mean_k"]))), float(np.max(np.abs(formula["mean_l"] - exact["mean_l"]))))
            for key in ("second_k", "second_l"):
                relative = abs(formula[key] - exact[key]) / max(abs(formula[key]), 1e-300)
                drift = abs(insufficient[key] - formula[key]) / max(abs(formula[key]), 1e-300)
                one["max_second_relative_error"] = max(one["max_second_relative_error"], relative)
                one["order4_controls_rejected"] += int(drift > 1e-10)
                one["order4_max_relative_drift"] = max(one["order4_max_relative_drift"], drift)
    rng = np.random.default_rng(8128)
    systems = [(A, B, K, np.array([math.log(.3)]), np.eye(2) * .7, qs, qa, horizon) for horizon in (1, 2, 3)]
    for horizon in (1, 2, 3, 4, 5):
        for _ in range(2):
            systems.append((np.array([[rng.uniform(-.8, 1.1)]]), np.array([[rng.uniform(.2, 1.)]]), np.array([[rng.uniform(-.7, .7)]]), np.array([math.log(rng.uniform(.15, .9))]), np.array([[rng.uniform(.2, 1.7)]]), np.array([[rng.uniform(.3, 1.4)]]), np.array([[rng.uniform(.02, .5)]]), horizon))
    multi = {"cells": 0, "max_gradient_abs_error": 0., "max_gradient_relative_error": 0., "max_return_abs_error": 0., "minimum_variance": float("inf")}
    for args_i in systems:
        Ai, Bi, Ki, log_std, sigma0i, qsi, qai, horizon = args_i
        exact = quadrature(Ai, Bi, Ki, np.diag(np.exp(2 * log_std)), sigma0i, qsi, qai, horizon, 5)
        fd_k, fd_l = finite_difference(*args_i)
        diff = np.concatenate([(exact["mean_k"] - fd_k).ravel(), exact["mean_l"] - fd_l]); ref = np.concatenate([fd_k.ravel(), fd_l])
        multi["cells"] += 1; multi["max_gradient_abs_error"] = max(multi["max_gradient_abs_error"], float(np.max(np.abs(diff)))); multi["max_gradient_relative_error"] = max(multi["max_gradient_relative_error"], float(np.linalg.norm(diff) / max(np.linalg.norm(ref), 1e-300))); multi["max_return_abs_error"] = max(multi["max_return_abs_error"], abs(exact["mean_return"] - objective(*args_i))); multi["minimum_variance"] = min(multi["minimum_variance"], exact["variance"])
    values = [theorem_one_step(A, B, K, np.array([[std ** 2]]), np.eye(2) * std0 ** 2, qs, qa)["nsr"] for std in np.geomspace(.01, 10., 61) for std0 in np.geomspace(.01, 10., 61)]
    blowup_std = np.geomspace(1e-4, 1e-1, 80); blowup = [theorem_one_step(A, B, K, np.array([[std ** 2]]), np.eye(2), qs, qa)["nsr"] for std in blowup_std]
    landscape = {"cells": len(values), "minimum_nsr": min(values), "maximum_nsr": max(values), "span_ratio": max(values) / min(values), "small_sigma_slope_vs_std": float(np.polyfit(np.log(blowup_std[:40]), np.log(blowup[:40]), 1)[0]), "monotone_blowup_failures": sum(now >= prior for prior, now in zip(blowup, blowup[1:]))}
    nonlinear = {"cells": 0, "theta_bound_failures": 0, "logstd_bound_failures": 0, "min_theta_ratio": float("inf"), "min_logstd_ratio": float("inf"), "no_inverse_mutation_failures": 0}
    for theta in (np.array([.4, .7, -.2]), np.array([-.6, 1.1, .3]), np.array([.9, -.5, -.4]), np.array([.15, 2., .5])):
        for std in np.geomspace(.12, 1.5, 12):
            lhs_theta, lhs_l, bound_theta, bound_l, mutation = nonlinear_cell(theta, std)
            nonlinear["cells"] += 1; nonlinear["theta_bound_failures"] += int(lhs_theta > bound_theta * (1 + 2e-10)); nonlinear["logstd_bound_failures"] += int(lhs_l > bound_l * (1 + 2e-10)); nonlinear["min_theta_ratio"] = min(nonlinear["min_theta_ratio"], bound_theta / lhs_theta); nonlinear["min_logstd_ratio"] = min(nonlinear["min_logstd_ratio"], bound_l / lhs_l); nonlinear["no_inverse_mutation_failures"] += int(lhs_theta > mutation * (1 + 2e-10))
    assert one["max_mean_abs_error"] < 2e-12 and one["max_second_relative_error"] < 2e-12 and one["order4_controls_rejected"] > 0
    assert multi["max_gradient_relative_error"] < 1e-7 and multi["minimum_variance"] >= -1e-10
    assert landscape["span_ratio"] > 1e6 and landscape["small_sigma_slope_vs_std"] < -1.9 and landscape["monotone_blowup_failures"] == 0
    assert nonlinear["theta_bound_failures"] == nonlinear["logstd_bound_failures"] == 0 and nonlinear["no_inverse_mutation_failures"] > 0
    report = {"paper": "Ol99zoW31J", "claims": [{"id": "C1", "outcome": "verified", "one_step": one, "finite_horizon": multi}, {"id": "C2", "outcome": "verified", "landscape": landscape}, {"id": "C3", "outcome": "verified", "nonlinear_bound": nonlinear}]}
    path = ROOT / args.output; path.parent.mkdir(exist_ok=True); path.write_text(json.dumps(report, indent=2) + "\n"); print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
