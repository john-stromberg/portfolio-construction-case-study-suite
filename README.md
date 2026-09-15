# portfolio-construction-case-study-suite

Track: **SMA Quantitative Research**

## Research purpose

This project is designed to be run independently as a quantitative research module for portfolio construction and risk/exposure analysis across **equities, bonds, alternatives, ETFs, and mutual funds**.

## Local research workflow

1. Create environment and install dependencies
   - `python -m venv .venv`
   - `.venv\\Scripts\\Activate.ps1`
   - `pip install -e .`
2. Run tests
   - `pytest -q`
3. Run core module
   - `python src/core.py`
4. Open notebook workflow
   - Start Jupyter and run `notebooks/research.ipynb` for exploratory analysis
5. Generate/report findings
   - Update `reports/method_note.md` with assumptions and portfolio implications

## Repository structure

- `src/` quantitative methods and model logic
- `tests/` unit and methodological checks
- `notebooks/` exploratory and robustness notebooks
- `reports/` method notes and decision summaries
- `configs/` run parameters and defaults
- `data/` local data artifacts

## Expected outputs

- Reproducible model diagnostics and result tables
- Explainable interpretation of risk/exposure and optimization behavior
- Portfolio-construction implications documented for implementation decisions

## Research memo template

- **Hypothesis:** What quantitative relationship is being tested?
- **Specification:** Which model/constraints are used?
- **Robustness:** What alternate tests confirm stability?
- **Portfolio implication:** What action follows from the results?

## Notes

- Keep assumptions explicit and track known model limitations.
- Prefer interpretable outputs that can be communicated to PM and risk stakeholders.

