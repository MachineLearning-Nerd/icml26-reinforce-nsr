import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = "Ol99zoW31J"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    independent = json.loads((ROOT / "outputs/independent_verification.json").read_text())
    assert len(independent["claims"]) == 3 and all(row["outcome"] == "verified" for row in independent["claims"])
    c1, c2, c3 = independent["claims"]
    assert c1["one_step"]["order4_controls_rejected"] > 0 and c1["finite_horizon"]["minimum_variance"] >= 0
    assert c2["landscape"]["span_ratio"] > 1e6 and c2["landscape"]["small_sigma_slope_vs_std"] < -1.9
    assert c3["nonlinear_bound"]["no_inverse_mutation_failures"] > 0
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "repro/tests"], cwd=ROOT, capture_output=True, text=True)
    assert tests.returncode == 0, tests.stdout + tests.stderr
    bundle = ROOT / "outputs/evidence_bundle.jsonl"
    rows = [json.loads(line) for line in bundle.read_text().splitlines() if line]
    assert len(rows) == 12
    for row in rows:
        path = ROOT / row["path"]
        assert path.is_file() and path.stat().st_size == row["bytes"] and digest(path) == row["sha256"]
    metadata = json.loads((ROOT / ".trackio/metadata.json").read_text())
    assert metadata["space_id"] == f"DineshAI/{PAPER}" and metadata["openreview_id"] == PAPER and metadata["arxiv_id"] == "2602.01460"
    assert {"icml2026-repro", f"paper-{PAPER}"}.issubset(metadata["tags"])
    artifact = next(item for item in metadata["local_path_artifacts"] if item["path"] == "outputs/evidence_bundle.jsonl")
    assert artifact["size"] == bundle.stat().st_size
    pages = ROOT / ".trackio/logbook/pages"
    names = ("overview", "claim-1", "claim-2", "claim-3", "methods", "negative-controls", "conclusion")
    assert all((pages / name / "page.md").is_file() for name in names)
    conclusion = (pages / "conclusion/page.md").read_text()
    assert f"FULL_GATE_READY: {PAPER}" in conclusion and "pinned" in conclusion
    out = {"paper": PAPER, "official_claim_count": 3, "maximum_points": 6, "tests_passed": True, "publication_gate_passed": True, "tests": tests.stdout.strip(), "bundle": {"records": len(rows), "bytes": bundle.stat().st_size, "sha256": digest(bundle)}, "trackio_space": metadata["space_id"]}
    (ROOT / "outputs/PUBLICATION_GATE_PASSED.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
