# portfolio-construction-case-study-suite

Track: **SMA Quantitative Research**

A research-grade portfolio construction case study suite that demonstrates a reproducible workflow for turning a constrained asset universe into an interpretable allocation memo.

## What this repo does

- Loads a baseline multi-asset universe
- Applies explicit portfolio constraints
- Produces a portfolio construction case study with weights, risk, and return diagnostics
- Exports markdown and JSON outputs for reporting
- Provides a notebook for exploratory analysis

## Local research workflow

1. Create environment and install dependencies
   - `python -m venv .venv`
   - `.venv\\Scripts\\Activate.ps1`
   - `pip install -e .`
2. Run tests
   - `pytest -q`
3. Run the case-study module
   - `python -c "from src.core import main; print(main())"`
4. Open notebook workflow
   - Start Jupyter and run `notebooks/research.ipynb`
5. Review outputs
   - `reports/portfolio_construction_case_study.md`
   - `reports/portfolio_construction_case_study.json`
   - `reports/method_note.md`

## Repository structure

- `src/` portfolio construction logic and report generation
- `tests/` unit and methodological checks
- `notebooks/` exploratory notebook workflow
- `reports/` method note and generated outputs
- `configs/` study metadata and allocation bounds
- `data/` optional local data artifacts

## Case study output

The core workflow returns:

- Title and hypothesis
- Expected return, volatility, and Sharpe ratio
- Asset-level weights
- Diagnostics and portfolio implications
- Risks and implementation notes

## Research memo template

- **Hypothesis:** What allocation question is being tested?
- **Specification:** Which constraints and assumptions are used?
- **Robustness:** What alternate checks confirm stability?
- **Portfolio implication:** What action follows from the results?

## Notes

- Keep assumptions explicit and track known model limitations.
- Use the notebook for exploration and the `main()` entry point for reproducible outputs.
- Prefer interpretable outputs that can be communicated to PM and risk stakeholders.

