# Portfolio Construction Case Study

**Hypothesis**: A balanced multi-asset portfolio can improve risk-adjusted returns while respecting implementation constraints.

## Summary
The case study constructs a diversified core portfolio that balances growth, income, and diversifiers under explicit bounds using optimization.

## Portfolio Construction Result
- Expected return: 5.36%
- Expected volatility: 5.79%
- Sharpe ratio: 0.5791

## Weights
- BND: 50.00%
- VTSAX: 15.55%
- GLD: 15.00%
- VTIAX: 10.00%
- VGSLX: 9.45%

## Recommendation
Use the resulting allocation as the baseline strategic mix, then refine with manager views, liquidity constraints, and implementation cost analysis.

## Risks
- Expected return and risk are based on forward estimates rather than realized data.
- Correlations may shift in stress regimes and reduce diversification benefits.
- Optimization assumes known risk/return parameters that may be unstable.

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