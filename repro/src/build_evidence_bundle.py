"""Build a hash-addressed manifest for the public reproduction evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "README.md",
    "STATUS.md",
    "sources.json",
    "repro/requirements.txt",
    "repro/src/verify_reinforce_nsr.py",
    "repro/src/cumulative_science_gate.py",
    "repro/src/build_evidence_bundle.py",
    "repro/src/publication_gate.py",
    "repro/tests/test_verifier.py",
    "docs/CLAIM_AUDIT.md",
    "docs/SOURCE_AUDIT.md",
    "docs/BRANCH_AUDIT.md",
    "docs/PUBLICATION_GATE.md",
    "source/arxiv/main.tex",
    "source/arxiv/sections/lqg.tex",
    "source/arxiv/sections/nonlinear_new.tex",
    "source/arxiv/sections/app-proof-nonlinear-upperbound.tex",
    "outputs/independent_verification.json",
    "outputs/CUMULATIVE_SCIENCE_GATE.json",
    "outputs/PUBLICATION_GATE_PASSED.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cumulative = json.loads((ROOT / "outputs/CUMULATIVE_SCIENCE_GATE.json").read_text())
    if cumulative["status"] != "SCOPED_PASS":
        raise SystemExit("cannot build a publication bundle before the cumulative gate passes")
    missing = [relative for relative in FILES if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit(f"missing gate artifacts: {missing}")
    rows = []
    for relative in FILES:
        path = ROOT / relative
        row = {"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)}
        if path.suffix == ".json":
            row["payload"] = json.loads(path.read_text())
        rows.append(row)
    output = ROOT / "outputs/evidence_bundle.jsonl"
    output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    print(json.dumps({"records": len(rows), "bytes": output.stat().st_size, "sha256": digest(output)}, indent=2))


if __name__ == "__main__":
    main()
