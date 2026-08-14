# Output contract

| File | Producer | Meaning |
| --- | --- | --- |
| `independent_verification.json` | `repro/src/verify_reinforce_nsr.py` | Exact-moment, finite-horizon, NSR-landscape, and nonlinear-bound evidence |
| `CUMULATIVE_SCIENCE_GATE.json` | `repro/src/cumulative_science_gate.py` | Current claim-level statuses and controls |
| `evidence_bundle.jsonl` | `repro/src/build_evidence_bundle.py` | Size/hash/payload manifest for public code, source anchors, docs, and evidence |
| `publication_gate.json` | `repro/src/publication_gate.py` | Canonical scoped publication status |
| `PUBLICATION_GATE_PASSED.json` | historical | Retained pre-audit marker; not used by the current gate |

The current gate requires every evidence-bundle row to match the committed
file’s size and SHA-256. The root and `outputs/` publication-gate copies must
also be byte-identical.
