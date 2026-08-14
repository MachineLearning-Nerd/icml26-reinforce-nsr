"""Validate the committed evidence for the three scoped REINFORCE claims."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
PAPER = "Ol99zoW31J"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_tree_digest() -> tuple[int, str]:
    names = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "source/arxiv"], text=True).splitlines()
    encoded = "".join(f"{digest(ROOT / name)}  {name}\n" for name in sorted(names))
    return len(names), hashlib.sha256(encoded.encode()).hexdigest()


def main() -> None:
    manifest = json.loads((ROOT / "sources.json").read_text())
    report = json.loads((OUT / "independent_verification.json").read_text())
    require(manifest["paper"]["openreview_id"] == PAPER, "wrong source paper")
    require(report["paper"] == PAPER, "wrong verification paper")

    source_count, source_tree = source_tree_digest()
    require(source_count == manifest["paper"]["source_tree_file_count"], "source file count changed")
    require(source_tree == manifest["paper"]["source_tree_sha256"], "source tree hash changed")
    for relative, expected in manifest["anchors"].items():
        actual = digest(ROOT / "source/arxiv" / relative)
        require(actual == expected, f"source anchor changed: {relative}")

    claims = {item["id"]: item for item in report["claims"]}
    require(set(claims) == {"C1", "C2", "C3"}, "claim inventory changed")
    require(all(item["outcome"] == "verified" for item in claims.values()), "claim outcome changed")

    one = claims["C1"]["one_step"]
    finite = claims["C1"]["finite_horizon"]
    c1 = (
        one["cells"] == 12
        and one["max_mean_abs_error"] < 2e-12
        and one["max_second_relative_error"] < 2e-12
        and one["order4_controls_rejected"] > 0
        and finite["cells"] == 13
        and finite["max_gradient_relative_error"] < 1e-7
        and finite["minimum_variance"] >= -1e-10
    )

    landscape = claims["C2"]["landscape"]
    c2 = (
        landscape["cells"] == 3721
        and landscape["span_ratio"] > 1e6
        and landscape["small_sigma_slope_vs_std"] < -1.9
        and landscape["monotone_blowup_failures"] == 0
    )

    nonlinear = claims["C3"]["nonlinear_bound"]
    c3 = (
        nonlinear["cells"] == 48
        and nonlinear["theta_bound_failures"] == 0
        and nonlinear["logstd_bound_failures"] == 0
        and nonlinear["no_inverse_mutation_failures"] > 0
    )

    claims_out = {
        "C1": {
            "status": "VERIFIED_SCOPED" if c1 else "FAILED",
            "evidence": "12 one-step moment cells and 13 finite-horizon systems with independent checks",
        },
        "C2": {
            "status": "VERIFIED_SCOPED" if c2 else "FAILED",
            "evidence": "3,721-cell NSR landscape and an 80-point small-policy-noise blow-up sweep",
        },
        "C3": {
            "status": "VERIFIED_SCOPED_WITH_PROTOCOL_LIMITS" if c3 else "FAILED",
            "evidence": "48 cubic-dynamics/tanh-policy fourth-moment-bound cells with mutation control",
        },
    }
    passed = all(item["status"] != "FAILED" for item in claims_out.values())
    result = {
        "paper": PAPER,
        "gate_version": "scoped-v2",
        "status": "SCOPED_PASS" if passed else "FAILED",
        "strict_status": "NOT_READY",
        "overall_status": "VERIFIED_SCOPED_WITH_UNREPRODUCED_EXPERIMENTS" if passed else "FAILED",
        "claims": claims_out,
        "controls": {
            "source_anchor_checks": True,
            "source_tree_file_count": source_count,
            "source_tree_sha256": source_tree,
            "degree_four_control_rejected": one["order4_controls_rejected"] > 0,
            "inverse_covariance_mutation_detected": nonlinear["no_inverse_mutation_failures"] > 0,
        },
        "source_anchor_sha256": manifest["anchors"],
        "score_forecast": None,
    }
    (OUT / "CUMULATIVE_SCIENCE_GATE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit("cumulative science gate failed")


if __name__ == "__main__":
    main()
