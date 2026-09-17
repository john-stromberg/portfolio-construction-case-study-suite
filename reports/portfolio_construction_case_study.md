# Portfolio Construction Case Study

**Hypothesis**: A balanced multi-asset portfolio can improve risk-adjusted returns while respecting implementation constraints.

## Summary
The case study constructs a diversified core portfolio that balances growth, income, and diversifiers under explicit bounds.

## Portfolio Construction Result
- Expected return: 6.26%
- Expected volatility: 9.48%
- Sharpe ratio: 0.4496

## Weights
- BND: 21.05%
- VGSLX: 21.05%
- VTIAX: 21.05%
- VTSAX: 21.05%
- GLD: 15.79%

## Recommendation
Use the resulting allocation as the baseline strategic mix, then refine with manager views, liquidity constraints, and implementation cost analysis.

## Risks
- Weights are derived from a normalized constrained heuristic and should be replaced with a solver for production use.
- Expected return and risk are based on forward estimates rather than realized data.
- Correlations may shift in stress regimes and reduce diversification benefits.

## Diagnostics
{
  "asset_count": 5,
  "budget_constraint": 1.0,
  "max_weight_bounds": {
    "BND": 0.5,
    "GLD": 0.15,
    "VGSLX": 0.2,
    "VTIAX": 0.35,
    "VTSAX": 0.45
  },
  "min_weight_bounds": {
    "BND": 0.1,
    "GLD": 0.0,
    "VGSLX": 0.0,
    "VTIAX": 0.1,
    "VTSAX": 0.1
  }
}