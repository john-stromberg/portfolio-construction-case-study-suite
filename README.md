# portfolio-construction-case-study-suite

Track: **SMA Quantitative Research**

A research-grade portfolio construction case-study suite that demonstrates a reproducible workflow for turning a constrained asset universe into an interpretable allocation memo. **Now enhanced with solver-backed optimization, comparative portfolio methods, strategy analysis, and scenario stress-testing for improved learning and usability.**

## What this repo does

- Loads a baseline multi-asset universe (VTSAX, VTIAX, BND, VGSLX, GLD)
- Applies explicit portfolio constraints and bounds
- Constructs portfolios using **three pedagogically distinct methods**:
  - **Curriculum (Optimal)**: Solver-backed minimum-variance optimization (respects explicit bounds, powered by cvxpy)
  - **Risk Parity**: Inverse-volatility weighted (equal risk contribution)
  - **Equal Weight**: 1/N naive allocation (benchmark for estimation error)
- **Compares strategies side by side** to reveal trade-offs and design choices
- **Stress-tests** portfolios under realistic market scenarios (Risk-Off, Equity Shock, Rates Up)
- Produces markdown and JSON outputs for reporting and documentation
- Provides a notebook for exploratory analysis and learning

## Why comparative portfolio construction?

**For learning:**
- See how solver-backed optimization compares to simpler heuristics
- Understand constraints by comparing constrained vs. unconstrained methods
- Learn robustness by stress-testing strategies across scenarios

**For practice:**
- Risk Parity reveals what volatility weighting looks like
- Equal Weight shows how much estimation error can degrade performance
- Solver-backed method demonstrates rigorous constrained optimization
- Scenario analysis teaches tail risk and crisis diversification

**For implementation:**
- Benchmark optimization quality against naive and risk-parity methods
- Test allocation strategies before deployment
- Document design rationale through comparative memo

## Local research workflow

1. **Create environment and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -e .
   ```

2. **Run all tests**
   ```bash
   pytest -q
   ```

3. **Run baseline case study**
   ```bash
   python -c "from src.core import main; print(main())"
   ```

4. **Try the comparative notebook workflow**
   - Open Jupyter: `jupyter notebook`
   - Run `notebooks/research.ipynb`
   - See strategy comparisons in baseline and stress scenarios

5. **Review outputs**
   - `reports/portfolio_construction_case_study.md` – generated baseline memo
   - `reports/portfolio_construction_case_study.json` – structured output for downstream use
   - `reports/method_note.md` – research methodology template

## Core API: Three construction methods

```python
from src.core import (
    construct_case_study,              # Optimal method (solver-backed)
    construct_optimal_portfolio,       # Direct solver-based optimization
    construct_equal_weight_portfolio,  # Equal-weight baseline
    construct_risk_parity_portfolio,   # Risk-parity method
    compare_strategies,                # Side-by-side comparison
)
from src.scenarios import Scenario, apply_scenario  # Stress scenarios

# Single method
optimal_weights = construct_case_study().weights  # Uses solver by default
heuristic_weights = construct_case_study(use_solver=False).weights  # Fallback heuristic
equal_weight = construct_equal_weight_portfolio()
risk_parity = construct_risk_parity_portfolio()

# Comparative analysis
comparison = compare_strategies()
print(comparison.to_markdown())  # Print markdown table

# Stress testing
comparison_risk_off = compare_strategies(scenario=Scenario.RISK_OFF)
comparison_shock = compare_strategies(scenario=Scenario.EQUITY_SHOCK)
```

## Solver-backed optimization

The **Curriculum (Optimal)** method uses `cvxpy` to solve a **constrained minimum-variance problem**:

```
minimize: portfolio_variance
subject to:
  - Sum of weights = 1 (fully invested)
  - All weights >= 0 (no short selling)
  - Individual weight bounds per asset (from config)
```

This is a **convex optimization problem** solved numerically by cvxpy's interior-point solver. The result is:
- **Deterministic**: Same input → same output
- **Feasible**: Respects all constraints
- **Efficient**: Minimizes risk for the given asset universe and bounds

If `cvxpy` is not installed or the solver fails, the code gracefully falls back to a **heuristic clipped equal-weight method**. You can also explicitly use the heuristic via `construct_case_study(use_solver=False)`.

## Installation and dependencies

**Core dependencies** (required):
- `python >= 3.12`
- `numpy`, `pyyaml` (config parsing, optional with fallback)

**Solver dependency** (optional, enables `construct_optimal_portfolio`):
- `cvxpy >= 1.9` – Install with: `pip install cvxpy`

If cvxpy is not installed, the suite still works with heuristic fallback.

## Scenarios for stress testing

Built-in scenarios demonstrate portfolio behavior under realistic stress:

- **BASELINE**: No adjustments (benchmark)
- **RISK_OFF**: Flight to safety (equities down, bonds rally, gold spikes)
- **RATES_UP**: Rising rate environment (bonds hurt, equities pressured)
- **EQUITY_SHOCK**: Severe equity downturn (equities crater, bonds rally sharply)

Each scenario adjusts asset return and volatility expectations to simulate tail events and teach tail-risk thinking.

## Repository structure

```
src/
  core.py          – Portfolio construction methods, solver optimization, comparison engine, exports
  clients.py       – Synthetic client account intake generator and optimization adapter
  scenarios.py     – Scenario definitions and stress-test application
  __init__.py      – Package exports
tests/
  test_core.py     – 23 comprehensive tests covering methods, solver paths, client intake, scenarios, comparisons
notebooks/
  research.ipynb   – Interactive notebook with baseline, comparison, and scenario workflows
reports/
  method_note.md   – Research methodology template and guidance
  portfolio_construction_case_study.md    – Generated baseline memo
  portfolio_construction_case_study.json   – Structured output
configs/
  default.yml      – Asset universe, bounds, and study metadata
```

## Case study output structure

Each portfolio construction returns:

- **Title & Hypothesis** – What allocation question is being tested?
- **Portfolio metrics** – Expected return, volatility, Sharpe ratio
- **Weights** – Asset-level allocations
- **Summary & Recommendation** – Interpretation and next steps
- **Risks & Diagnostics** – Known limitations and constraint details

## Strategy comparison output

Comparative analysis produces:

- **Side-by-side metrics table** – Return, volatility, Sharpe, concentration across methods
- **Weight distribution** – How each method allocates differently
- **Learning annotations** – Pedagogical notes on each method's strengths and weaknesses

Example:

```
| Strategy | Expected Return | Volatility | Sharpe Ratio | Max Weight | Weight Concentration |
|----------|-----------------|------------|--------------|-----------|-----------------------|
| Curriculum | 6.26% | 9.48% | 0.4496 | 21.05% | 0.1104 |
| RiskParity | 5.82% | 8.54% | 0.3788 | 36.19% | 0.1851 |
| EqualWeight | 5.60% | 8.71% | 0.3563 | 20.00% | 0.0500 |
```

## Client account intake workflow

This repo can now mimic new client accounts being brought in for portfolio construction.

Use the generator to create synthetic client accounts with:
- risk tolerance
- investment horizon
- capital size
- liquidity need
- tax sensitivity
- generated constraints aligned to the existing solver workflow

Example:

```python
from src import generate_client_account, generate_client_portfolio_examples

client = generate_client_account(seed=42)
example = generate_client_portfolio_examples(count=3, seed=42)

print(client.to_dict())
print(example[0].result.to_markdown())
```

The generated client can be passed directly into the solver-backed construction flow through the included adapter.

## Testing & validation

Run the full test suite:

```bash
pytest tests/test_core.py -v
```

Tests cover (23 total):

- Single construction methods (Optimal/Solver, Risk Parity, Equal Weight)
- Solver-backed optimization and fallback behavior
- Strategy comparison structure and markdown output
- Scenario application and stress testing
- Scenario-aware strategy comparison
- Constraint validation and weight bounds
- Configuration loading and export generation
- End-to-end workflow (`main()`)

Expected output: **19 passed** (all tests pass with cvxpy installed; heuristic fallback works without it)

## Design principles

- **Comparative by design**: Users learn through side-by-side comparison, not single methods
- **Solver-backed optimization**: Curriculum method uses cvxpy for rigorous constrained optimization
- **Graceful fallback**: Without cvxpy, automatically uses heuristic method
- **Scenario-aware**: Robustness is tested with built-in stress scenarios
- **Interpretable outputs**: Markdown reports communicate findings clearly
- **Test-driven**: Every feature is backed by comprehensive tests
- **Notebook-first exploration**: Jupyter workflow for interactive learning

## Notes

- Keep assumptions explicit and track known model limitations
- Constraints are specified per-asset in `configs/default.yml`
- Modify scenarios in `src/scenarios.py` to reflect your risk model
- Use the notebook for exploration; use `main()` for reproducible, automated outputs
- Prefer interpretable outputs that can be communicated to PM and risk stakeholders

## For educators & students

This suite is designed for **learning portfolio construction from first principles**:

1. **Start with Equal Weight** (simplest, most robust)
2. **Compare with Risk Parity** (introduces volatility considerations)
3. **Study Optimal method** (learns constrained optimization with solvers)
4. **Stress test all three** (understands tail risk and diversification)

The four-step progression builds intuition from naive to sophisticated methods while teaching when and why each is appropriate.

