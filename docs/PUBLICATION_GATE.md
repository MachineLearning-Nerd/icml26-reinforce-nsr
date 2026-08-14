# Publication gate

The current gate is a self-contained `SCOPED_PASS` for the three declared
clean-room contracts. It is an evidence-release gate, not a prediction of an
external evaluator score.

## Gate sequence

[`repro/src/publication_gate.py`](../repro/src/publication_gate.py):

1. regenerates `outputs/independent_verification.json` with the source anchors;
2. runs the cumulative claim checks;
3. runs `pytest -q repro/tests`;
4. rebuilds and validates `outputs/evidence_bundle.jsonl`; and
5. writes identical JSON summaries to `publication_gate.json` and
   `outputs/publication_gate.json`.

The gate has no dependency on hidden Trackio metadata, private Space state,
queue handoffs, or absolute paths. The historical
`outputs/PUBLICATION_GATE_PASSED.json` file is retained only as a labeled
pre-audit artifact.

## Status semantics

- `SCOPED_PASS` means the declared finite contracts, source pins, independent
  routes, negative controls, and focused tests passed.
- `VERIFIED_SCOPED` means a claim passed its declared numerical contract.
- `VERIFIED_SCOPED_WITH_PROTOCOL_LIMITS` records the finite cubic/tanh scope
  for the general nonlinear bound.
- `VERIFIED_SCOPED_WITH_UNREPRODUCED_EXPERIMENTS` records that the current gate
  does not reproduce the paper’s optimization-trajectory or rollout figures.
- `NOT_READY` is the strict paper-level status for that remaining coverage.
- `score_forecast: null` is intentional.

## Fail-closed conditions

The gate fails if an anchor changes, the source-tree digest changes, any
claim-level tolerance fails, a negative control stops detecting its mutation,
the evidence manifest is stale, or the root/output gate copies differ.
