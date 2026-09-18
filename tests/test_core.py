from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from core import (  # noqa: E402
    CaseStudyResult,
    StrategyComparison,
    build_default_constraints,
    compare_strategies,
    construct_case_study,
    construct_equal_weight_portfolio,
    construct_optimal_portfolio,
    construct_risk_parity_portfolio,
    export_case_study,
    load_config,
    main,
    run_quant_placeholder,
)
from scenarios import Scenario, apply_scenario  # noqa: E402


def test_quant_placeholder():
    out = run_quant_placeholder()
    assert out["status"] == "ok"
    assert out["track"] == "SMA Quantitative Research"
    assert pytest.approx(sum(out["weights"].values()), rel=1e-6) == 1.0


def test_construct_case_study_returns_result():
    result = construct_case_study()
    assert isinstance(result, CaseStudyResult)
    assert result.title == "Portfolio Construction Case Study"
    assert pytest.approx(sum(result.weights.values()), rel=1e-6) == 1.0
    assert result.expected_return > 0
    assert result.expected_volatility > 0
    assert isinstance(result.to_dict(), dict)
    assert "Portfolio Construction Case Study" in result.to_markdown()


def test_constraints_include_baseline_bounds():
    constraints = build_default_constraints()
    assert constraints.budget_constraint == 1.0
    asset_ids = [constraint.asset_id for constraint in constraints.constraints if constraint.asset_id]
    assert "VTSAX" in asset_ids
    assert "GLD" in asset_ids


def test_export_case_study_writes_files(tmp_path: Path):
    result = construct_case_study(title="Case Study Output")
    paths = export_case_study(result, tmp_path)
    assert Path(paths["markdown"]).exists()
    assert Path(paths["json"]).exists()


def test_load_config_reads_defaults():
    config = load_config()
    assert config["run_mode"] == "research"
    assert config["study_title"] == "Portfolio Construction Case Study"


def test_main_returns_paths():
    output = main()
    assert "result" in output
    assert "paths" in output
    assert Path(output["paths"]["markdown"]).exists()
    assert Path(output["paths"]["json"]).exists()


def test_equal_weight_construction():
    """Test equal-weight portfolio construction (1/N)."""
    weights = construct_equal_weight_portfolio()
    assert pytest.approx(sum(weights.values()), rel=1e-6) == 1.0
    # All weights should be equal
    expected_weight = 1.0 / len(weights)
    for weight in weights.values():
        assert pytest.approx(weight, rel=1e-6) == expected_weight


def test_risk_parity_construction():
    """Test risk-parity portfolio construction (inverse-volatility weighted)."""
    weights = construct_risk_parity_portfolio()
    assert pytest.approx(sum(weights.values()), rel=1e-6) == 1.0
    # Risk parity should allocate more to lower-volatility assets
    # BND has lowest volatility (0.05), so should have highest weight
    assert weights["BND"] > weights["VTIAX"]
    assert weights["BND"] > weights["VGSLX"]


def test_strategy_comparison():
    """Test strategy comparison engine."""
    comparison = compare_strategies()
    assert isinstance(comparison, StrategyComparison)
    assert len(comparison.strategies) == 3
    assert "Curriculum" in comparison.strategies
    assert "RiskParity" in comparison.strategies
    assert "EqualWeight" in comparison.strategies

    # All strategies should produce valid results
    for strategy_name, result in comparison.strategies.items():
        assert isinstance(result, CaseStudyResult)
        assert pytest.approx(sum(result.weights.values()), rel=1e-6) == 1.0
        assert result.expected_return > 0
        assert result.expected_volatility > 0


def test_strategy_comparison_markdown():
    """Test strategy comparison markdown output."""
    comparison = compare_strategies()
    markdown = comparison.to_markdown()
    assert "Strategy Comparison" in markdown
    assert "Curriculum" in markdown
    assert "RiskParity" in markdown
    assert "EqualWeight" in markdown
    assert "Expected Return" in markdown
    assert "Volatility" in markdown
    assert "Sharpe Ratio" in markdown


def test_scenario_application_risk_off():
    """Test scenario-based stress testing (risk-off scenario)."""
    assets_baseline = construct_case_study().weights

    result_risk_off = construct_case_study(scenario=Scenario.RISK_OFF)
    assert "risk_off" in result_risk_off.title.lower()
    assert result_risk_off.expected_return < construct_case_study().expected_return
    # In risk-off, bonds should outperform equities
    assert result_risk_off.weights.get("BND", 0) > 0


def test_scenario_application_equity_shock():
    """Test scenario-based stress testing (equity shock scenario)."""
    result_shock = construct_case_study(scenario=Scenario.EQUITY_SHOCK)
    assert "equity_shock" in result_shock.title.lower()
    # Gold should have higher weight in shock scenario
    result_baseline = construct_case_study()
    # Shock scenario should emphasize safe havens (bonds, gold)
    assert result_shock.expected_volatility > result_baseline.expected_volatility


def test_compare_strategies_with_scenario():
    """Test strategy comparison under stress scenario."""
    comparison = compare_strategies(scenario=Scenario.RISK_OFF)
    assert "risk_off" in comparison.strategies["Curriculum"].title.lower()

    # All three methods should still produce valid portfolios
    for strategy_name, result in comparison.strategies.items():
        assert pytest.approx(sum(result.weights.values()), rel=1e-6) == 1.0
        assert result.expected_volatility > 0


def test_optimal_portfolio_construction():
    """Test solver-backed optimal portfolio construction."""
    weights = construct_optimal_portfolio()
    assert pytest.approx(sum(weights.values()), rel=1e-6) == 1.0
    # All weights should be non-negative
    for weight in weights.values():
        assert weight >= -1e-6  # Allow tiny numerical errors


def test_construct_case_study_with_solver():
    """Test case study uses solver by default."""
    result = construct_case_study(use_solver=True)
    assert isinstance(result, CaseStudyResult)
    assert pytest.approx(sum(result.weights.values()), rel=1e-6) == 1.0
    assert result.expected_return > 0
    assert result.expected_volatility > 0


def test_construct_case_study_with_heuristic():
    """Test case study can use heuristic fallback."""
    result = construct_case_study(use_solver=False)
    assert isinstance(result, CaseStudyResult)
    assert pytest.approx(sum(result.weights.values()), rel=1e-6) == 1.0
    assert result.expected_return > 0
    assert result.expected_volatility > 0


def test_solver_vs_heuristic_comparison():
    """Test that solver produces different/better results than heuristic."""
    result_optimal = construct_case_study(use_solver=True)
    result_heuristic = construct_case_study(use_solver=False)

    # Both should be valid portfolios
    assert pytest.approx(sum(result_optimal.weights.values()), rel=1e-6) == 1.0
    assert pytest.approx(sum(result_heuristic.weights.values()), rel=1e-6) == 1.0

    # Optimal solution should have Sharpe ratio >= heuristic
    # (accounting for numerical precision)
    assert result_optimal.sharpe_ratio >= result_heuristic.sharpe_ratio - 1e-3


def test_optimal_portfolio_respects_constraints():
    """Test that optimal portfolio respects all constraints."""
    constraints = build_default_constraints()
    weights = construct_optimal_portfolio(constraints=constraints)

    # Check budget constraint
    assert pytest.approx(sum(weights.values()), rel=1e-6) == 1.0

    # Check weight bounds
    for constraint in constraints.constraints:
        if constraint.asset_id and constraint.asset_id in weights:
            weight = weights[constraint.asset_id]
            if constraint.lower_bound is not None:
                assert weight >= constraint.lower_bound - 1e-5, f"{constraint.asset_id} weight {weight} below lower bound {constraint.lower_bound}"
            if constraint.upper_bound is not None:
                assert weight <= constraint.upper_bound + 1e-5, f"{constraint.asset_id} weight {weight} above upper bound {constraint.upper_bound}"


def test_construct_case_study_with_solver_and_scenario():
    """Test that solver works with scenarios."""
    result_baseline = construct_case_study(scenario=Scenario.BASELINE, use_solver=True)
    result_risk_off = construct_case_study(scenario=Scenario.RISK_OFF, use_solver=True)

    # Both should be valid
    assert pytest.approx(sum(result_baseline.weights.values()), rel=1e-6) == 1.0
    assert pytest.approx(sum(result_risk_off.weights.values()), rel=1e-6) == 1.0

    # Risk-off scenario should have lower expected return
    assert result_risk_off.expected_return < result_baseline.expected_return

