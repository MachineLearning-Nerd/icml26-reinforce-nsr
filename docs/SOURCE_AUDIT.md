# Source audit — Ol99zoW31J

## Paper identity

- Title: *Non-Uniform Noise-to-Signal Ratio in the REINFORCE Policy-Gradient Estimator*
- Authors: Haoyu Han and Heng Yang
- arXiv: `2602.01460v3`
- OpenReview: `Ol99zoW31J`
- Recorded arXiv source archive SHA-256: `de620c3c2a99639010e9338e336ebe4ed79cbdf263761efb9eabc71322a9152d`
- Vendored source tree: `source/arxiv/`
- Canonical source-tree SHA-256: `f9cec0b849755711b619011ffd8638985638d89e5dc5fc3d4b8c116c030b2c6d`
- Vendored source files: 38

## Hash-pinned anchors

| Source file | SHA-256 | Role |
| --- | --- | --- |
| `source/arxiv/main.tex` | `e8ef3aebb0e9283c93aca97c350893f4cf5dffea8ce32baa0c0762e275c5f27c` | title, authors, paper structure, and claim inventory |
| `source/arxiv/sections/lqg.tex` | `424e862b4297defbfcacf75ffef81b0381ef5ee5b6bf4b86059edbef85c9c7fb` | one-step and finite-horizon LQG moments and NSR analysis |
| `source/arxiv/sections/nonlinear_new.tex` | `558392eb62a93ec68ecebf94db516ab2dffdc9310905c8a1724c5185b6edfb1b` | nonlinear-system variance-bound setup |
| `source/arxiv/sections/app-proof-nonlinear-upperbound.tex` | `11ece2dad7fac254e2aa0a2439caee4bc5d8e545cadb9b20f0eeb4b3c4ecbe83` | fourth-moment upper-bound proof |

The arXiv archive hash is retained as provenance from source collection. The
current public artifact is the 38-file vendored source tree, whose canonical
path/hash-list digest is checked by the cumulative gate.

## Implementation boundary

No author repository is identified in the primary source. The code under
`repro/src/` is clean-room and has two independent routes where the claim
requires them: Wick formulas versus Gaussian quadrature for C1, and covariance
recursion versus finite differences for finite-horizon gradients. The gate does
not read Trackio metadata, private Space identifiers, queue state, or absolute
local paths.
