"""Fail-closed publication gate for the three scoped REINFORCE claims."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_script(name: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "repro/src" / name)], cwd=ROOT, check=True)


def main() -> None:
    run_script("verify_reinforce_nsr.py")
    run_script("cumulative_science_gate.py")
    tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "repro/tests"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(tests.returncode == 0, tests.stdout + tests.stderr)
    run_script("cumulative_science_gate.py")
    run_script("build_evidence_bundle.py")

    cumulative = json.loads((OUT / "CUMULATIVE_SCIENCE_GATE.json").read_text())
    bundle_path = OUT / "evidence_bundle.jsonl"
    rows = [json.loads(line) for line in bundle_path.read_text().splitlines() if line]
    require(len(rows) > 15, "evidence bundle is unexpectedly small")
    for row in rows:
        artifact = ROOT / row["path"]
        require(artifact.is_file(), f"missing evidence artifact: {row['path']}")
        require(artifact.stat().st_size == row["bytes"], f"size mismatch: {row['path']}")
        require(digest(artifact) == row["sha256"], f"hash mismatch: {row['path']}")

    gate = {
        "paper": "Ol99zoW31J",
        "gate_version": "scoped-v2",
        "status": cumulative["status"],
        "strict_status": cumulative["strict_status"],
        "overall_status": cumulative["overall_status"],
        "tests_passed": True,
        "publication_gate_passed": cumulative["status"] == "SCOPED_PASS",
        "claims": cumulative["claims"],
        "controls": cumulative["controls"],
        "evidence_bundle_sha256": digest(bundle_path),
        "source_anchor_sha256": cumulative["source_anchor_sha256"],
        "score_forecast": None,
        "limitations": [
            "The verifier is clean-room; no author-code parity is claimed.",
            "Optimization trajectories, sampled RL rollouts, and broader polynomial/neural experiments are outside the current gate.",
            "The gate covers the three declared finite contracts, not every theorem or rendered figure.",
        ],
    }
    encoded = json.dumps(gate, indent=2) + "\n"
    (ROOT / "publication_gate.json").write_text(encoded)
    (OUT / "publication_gate.json").write_text(encoded)
    require((ROOT / "publication_gate.json").read_bytes() == (OUT / "publication_gate.json").read_bytes(), "gate copies differ")
    print(json.dumps(gate, indent=2))
    if not gate["publication_gate_passed"]:
        raise SystemExit("publication gate failed")


if __name__ == "__main__":
    main()
