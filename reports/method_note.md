# Method Note

## Study Title
Portfolio Construction Case Study

## Hypothesis
A diversified multi-asset portfolio can improve risk-adjusted returns while respecting practical allocation bounds.

## Specification
- Assets: US equities, international equities, bonds, real estate, gold
- Constraints: asset-level lower and upper bounds, full-investment budget constraint
- Method: normalized constrained baseline allocation for research walkthrough
- Benchmark: equal-weight starting point

## Robustness
- Check allocation stability under modest changes to return and volatility assumptions.
- Confirm that portfolio statistics remain sensible under alternative correlation regimes.
- Compare outputs to equal-weight and concentrated allocations.

## Portfolio Implication
Use the case study as a baseline strategic allocation and replace the heuristic with a solver-backed optimization when productionizing.

