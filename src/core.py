"""Portfolio construction case-study utilities.

This module provides a small but complete research workflow for constructing
portfolio case studies from a constrained asset universe.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json

import numpy as np

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    yaml = None

try:
    from sma_quant_core.models import Asset, PortfolioConstraint, PortfolioConstraints
    from sma_quant_core.metrics import Metrics
except ModuleNotFoundError:  # pragma: no cover - notebook/script fallback
    import sys

    CURRENT_FILE = Path(__file__).resolve()
    REPO_ROOT = CURRENT_FILE.parents[1]
    CORE_ROOT = REPO_ROOT.parent / "sma-quant-core"
    for path in (CORE_ROOT, REPO_ROOT, REPO_ROOT / "src"):
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    from sma_quant_core.models import Asset, PortfolioConstraint, PortfolioConstraints
    from sma_quant_core.metrics import Metrics

try:
    from scenarios import Scenario, apply_scenario
except ModuleNotFoundError:  # pragma: no cover - late import fallback
    import sys
    CURRENT_FILE = Path(__file__).resolve()
    REPO_ROOT = CURRENT_FILE.parents[1]
    SRC_PATH = REPO_ROOT / "src"
    if SRC_PATH.exists() and str(SRC_PATH) not in sys.path:
        sys.path.insert(0, str(SRC_PATH))
    from scenarios import Scenario, apply_scenario


@dataclass
class CaseStudyResult:
    """Container for portfolio construction outputs."""

    title: str
    hypothesis: str
    summary: str
    weights: dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    portfolio_metrics: dict[str, Any]
    recommendation: str
    risks: list[str]
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            f"**Hypothesis**: {self.hypothesis}",
            "",
            "## Summary",
            self.summary,
            "",
            "## Portfolio Construction Result",
            f"- Expected return: {self.expected_return:.2%}",
            f"- Expected volatility: {self.expected_volatility:.2%}",
            f"- Sharpe ratio: {self.sharpe_ratio:.4f}",
            "",
            "## Weights",
        ]
        for asset_id, weight in sorted(self.weights.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- {asset_id}: {weight:.2%}")
        lines.extend([
            "",
            "## Recommendation",
            self.recommendation,
            "",
            "## Risks",
        ])
        lines.extend(f"- {risk}" for risk in self.risks)
        lines.extend([
            "",
            "## Diagnostics",
            json.dumps(self.diagnostics, indent=2, sort_keys=True),
        ])
        return "\n".join(lines)


@dataclass
class StrategyComparison:
    """Container for comparing multiple portfolio construction strategies."""

    title: str
    strategies: dict[str, CaseStudyResult]  # strategy_name -> CaseStudyResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "strategies": {name: result.to_dict() for name, result in self.strategies.items()},
        }

    def comparison_table(self) -> str:
        """Generate a markdown table comparing key metrics across strategies."""
        lines = [
            f"# {self.title}",
            "",
            "## Strategy Comparison",
            "",
            "| Strategy | Expected Return | Volatility | Sharpe Ratio | Max Weight | Weight Concentration |",
            "|----------|-----------------|------------|--------------|-----------|-----------------------|",
        ]

        for strategy_name, result in sorted(self.strategies.items()):
            # Calculate weight concentration (Herfindahl index: sum of squared weights)
            concentration = sum(w**2 for w in result.weights.values())
            max_weight = max(result.weights.values())

            lines.append(
                f"| {strategy_name} | {result.expected_return:.2%} | {result.expected_volatility:.2%} "
                f"| {result.sharpe_ratio:.4f} | {max_weight:.2%} | {concentration:.4f} |"
            )

        lines.extend(
            [
                "",
                "## Strategy Details",
                "",
            ]
        )

        for strategy_name, result in sorted(self.strategies.items()):
            lines.extend(
                [
                    f"### {strategy_name}",
                    "",
                    f"**Weights distribution:**",
                    "",
                ]
            )
            for asset_id, weight in sorted(result.weights.items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"- {asset_id}: {weight:.2%}")
            lines.append("")

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Generate full comparison markdown report."""
        return self.comparison_table()


DEFAULT_SAMPLE_ASSETS = [
    Asset("VTSAX", "US Stock Market", "equity", 0.08, 0.15),
    Asset("VTIAX", "International Stock Market", "equity", 0.07, 0.18),
    Asset("BND", "US Aggregate Bonds", "fixed_income", 0.04, 0.05),
    Asset("VGSLX", "REITs", "alternative", 0.07, 0.18),
    Asset("GLD", "Gold", "alternative", 0.05, 0.15),
]

DEFAULT_CORRELATION = np.array([
    [1.00, 0.82, -0.18, 0.60, -0.08],
    [0.82, 1.00, -0.10, 0.58, -0.02],
    [-0.18, -0.10, 1.00, -0.15, 0.15],
    [0.60, 0.58, -0.15, 1.00, -0.12],
    [-0.08, -0.02, 0.15, -0.12, 1.00],
])


def load_config(config_path: str | Path = "configs/default.yml") -> dict[str, Any]:
    """Load configuration for the case-study suite."""

    path = Path(config_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    text = path.read_text(encoding="utf-8")

    if yaml is not None:
        return yaml.safe_load(text) or {}

    config: dict[str, Any] = {}
    current_section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            current_section = key
            config[current_section] = {}
            continue
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip('"\'') for item in value[1:-1].split(",") if item.strip()]
            config[key] = items
        else:
            normalized = value.strip('"\'')
            if normalized.replace(".", "", 1).isdigit():
                config[key] = float(normalized) if "." in normalized else int(normalized)
            else:
                config[key] = normalized
    return config


def build_default_constraints() -> PortfolioConstraints:
    """Construct the baseline portfolio constraint set."""

    constraints = PortfolioConstraints(budget_constraint=1.0)
    constraints.add_weight_constraint("VTSAX", 0.10, 0.45)
    constraints.add_weight_constraint("VTIAX", 0.10, 0.35)
    constraints.add_weight_constraint("BND", 0.10, 0.50)
    constraints.add_weight_constraint("VGSLX", 0.00, 0.20)
    constraints.add_weight_constraint("GLD", 0.00, 0.15)
    return constraints


def _as_asset_map(assets: list[Asset]) -> dict[str, Asset]:
    return {asset.id: asset for asset in assets}


def construct_equal_weight_portfolio(assets: list[Asset] | None = None) -> dict[str, float]:
    """Construct an equal-weight portfolio (1/N)."""
    assets = assets or list(DEFAULT_SAMPLE_ASSETS)
    weight = 1.0 / len(assets)
    return {asset.id: float(weight) for asset in assets}


def construct_risk_parity_portfolio(
    assets: list[Asset] | None = None,
    correlation_matrix: np.ndarray | None = None,
) -> dict[str, float]:
    """Construct a risk-parity portfolio (inverse-volatility weighted)."""
    assets = assets or list(DEFAULT_SAMPLE_ASSETS)
    correlation_matrix = correlation_matrix if correlation_matrix is not None else DEFAULT_CORRELATION

    # Risk parity: weight each asset inversely to its volatility
    volatilities = np.array([asset.volatility for asset in assets], dtype=float)
    inverse_vols = 1.0 / (volatilities + 1e-8)  # Add small epsilon to avoid division by zero
    weights = inverse_vols / inverse_vols.sum()

    return {asset.id: float(weight) for asset, weight in zip(assets, weights, strict=False)}


def _portfolio_statistics(weights: dict[str, float], assets: list[Asset], correlation_matrix: np.ndarray) -> tuple[float, float, float, dict[str, Any]]:
    asset_map = _as_asset_map(assets)
    ordered_assets = list(weights)
    vector = np.array([weights[a] for a in ordered_assets], dtype=float)
    returns = np.array([asset_map[a].expected_return for a in ordered_assets], dtype=float)
    volatilities = np.array([asset_map[a].volatility for a in ordered_assets], dtype=float)
    covariance = np.outer(volatilities, volatilities) * correlation_matrix[: len(ordered_assets), : len(ordered_assets)]
    expected_return = float(vector @ returns)
    expected_volatility = float(np.sqrt(vector.T @ covariance @ vector))
    sharpe_ratio = float((expected_return - 0.02) / expected_volatility) if expected_volatility > 0 else 0.0
    diagnostics = Metrics.portfolio_metrics(vector, [asset_map[a] for a in ordered_assets], correlation_matrix)
    return expected_return, expected_volatility, sharpe_ratio, diagnostics


def compare_strategies(
    title: str = "Portfolio Strategy Comparison",
    assets: list[Asset] | None = None,
    constraints: PortfolioConstraints | None = None,
    correlation_matrix: np.ndarray | None = None,
    scenario: Scenario | None = None,
) -> StrategyComparison:
    """Compare multiple portfolio construction strategies side by side.

    Runs three canonical methods:
      1. Curriculum: constrained mean-variance (baseline case study)
      2. RiskParity: inverse-volatility weights
      3. EqualWeight: 1/N naive diversification

    Args:
        title: Comparison title
        assets: Asset universe
        constraints: Portfolio constraints
        correlation_matrix: Asset correlation matrix
        scenario: Optional market scenario for stress testing

    Returns:
        A StrategyComparison containing all results.
    """
    assets = assets or list(DEFAULT_SAMPLE_ASSETS)
    correlation_matrix = correlation_matrix if correlation_matrix is not None else DEFAULT_CORRELATION

    strategies = {}

    # Curriculum method: constrained case study
    curriculum = construct_case_study(
        title="Curriculum (Constrained Mean-Variance)",
        hypothesis="A balanced portfolio respects explicit weight constraints and risk bounds.",
        assets=assets,
        constraints=constraints,
        correlation_matrix=correlation_matrix,
        scenario=scenario,
    )
    strategies["Curriculum"] = curriculum

    # Risk Parity method
    rp_assets = assets if not scenario or scenario == Scenario.BASELINE else apply_scenario(assets, scenario)
    rp_weights = construct_risk_parity_portfolio(assets=rp_assets, correlation_matrix=correlation_matrix)
    rp_return, rp_vol, rp_sharpe, rp_diag = _portfolio_statistics(rp_weights, rp_assets, correlation_matrix)
    risk_parity = CaseStudyResult(
        title="Risk Parity (Inverse-Volatility Weighted)",
        hypothesis="Equal risk contribution from each asset improves robustness and reduces concentration.",
        summary="Risk parity weights each asset inversely to its volatility, resulting in equal marginal risk contribution.",
        weights=rp_weights,
        expected_return=rp_return,
        expected_volatility=rp_vol,
        sharpe_ratio=rp_sharpe,
        portfolio_metrics=rp_diag,
        recommendation="Risk parity is useful for diversification when constraints are relaxed.",
        risks=[
            "Relies on volatility estimates that may shift in stress regimes.",
            "May concentrate in lower-volatility assets during normal markets.",
        ],
        diagnostics={"method": "inverse-volatility-weighted", "asset_count": len(rp_assets)},
    )
    strategies["RiskParity"] = risk_parity

    # Equal Weight method
    ew_assets = assets if not scenario or scenario == Scenario.BASELINE else apply_scenario(assets, scenario)
    ew_weights = construct_equal_weight_portfolio(assets=ew_assets)
    ew_return, ew_vol, ew_sharpe, ew_diag = _portfolio_statistics(ew_weights, ew_assets, correlation_matrix)
    equal_weight = CaseStudyResult(
        title="Equal Weight (1/N Naive)",
        hypothesis="A simple 1/N allocation provides a competitive baseline and is robust to estimation error.",
        summary="Equal weight allocates 1/N to each asset, providing a naive but surprisingly competitive diversification.",
        weights=ew_weights,
        expected_return=ew_return,
        expected_volatility=ew_vol,
        sharpe_ratio=ew_sharpe,
        portfolio_metrics=ew_diag,
        recommendation="Equal weight is a robust, zero-alpha benchmark and useful for backtesting optimization quality.",
        risks=[
            "Ignores asset characteristics and correlations.",
            "No response to changing market conditions or volatility.",
        ],
        diagnostics={"method": "equal-weight", "asset_count": len(ew_assets)},
    )
    strategies["EqualWeight"] = equal_weight

    return StrategyComparison(title=title, strategies=strategies)


def construct_case_study(
    title: str = "Portfolio Construction Case Study",
    hypothesis: str = "A balanced multi-asset portfolio can improve risk-adjusted returns while respecting implementation constraints.",
    assets: list[Asset] | None = None,
    constraints: PortfolioConstraints | None = None,
    correlation_matrix: np.ndarray | None = None,
    scenario: Scenario | None = None,
) -> CaseStudyResult:
    """Build a simple research case study with normalized constrained weights.

    Args:
        title: Case study title
        hypothesis: Research hypothesis
        assets: List of assets to include (defaults to DEFAULT_SAMPLE_ASSETS)
        constraints: Portfolio constraints (defaults to build_default_constraints())
        correlation_matrix: Asset correlation matrix (defaults to DEFAULT_CORRELATION)
        scenario: Optional market scenario to stress-test (defaults to Scenario.BASELINE)

    Returns:
        CaseStudyResult containing portfolio weights, returns, and diagnostics
    """

    assets = assets or list(DEFAULT_SAMPLE_ASSETS)
    if scenario and scenario != Scenario.BASELINE:
        assets = apply_scenario(assets, scenario)
        title = f"{title} ({scenario.value})"
    constraints = constraints or build_default_constraints()
    correlation_matrix = correlation_matrix if correlation_matrix is not None else DEFAULT_CORRELATION

    min_weights = {c.asset_id: c.lower_bound for c in constraints.constraints if c.asset_id and c.lower_bound is not None}
    max_weights = {c.asset_id: c.upper_bound for c in constraints.constraints if c.asset_id and c.upper_bound is not None}

    raw = np.array([1.0 / len(assets)] * len(assets), dtype=float)
    for idx, asset in enumerate(assets):
        lower = min_weights.get(asset.id, 0.0)
        upper = max_weights.get(asset.id, 1.0)
        raw[idx] = float(np.clip(raw[idx], lower, upper))

    if raw.sum() <= 0:
        raw = np.array([1.0 / len(assets)] * len(assets), dtype=float)
    weights = raw / raw.sum()
    weight_map = {asset.id: float(weight) for asset, weight in zip(assets, weights, strict=False)}

    expected_return, expected_volatility, sharpe_ratio, diagnostics = _portfolio_statistics(
        weight_map,
        assets,
        correlation_matrix,
    )

    summary = (
        "The case study constructs a diversified core portfolio that balances growth, income, "
        "and diversifiers under explicit bounds."
    )
    recommendation = (
        "Use the resulting allocation as the baseline strategic mix, then refine with manager "
        "views, liquidity constraints, and implementation cost analysis."
    )
    risks = [
        "Weights are derived from a normalized constrained heuristic and should be replaced with a solver for production use.",
        "Expected return and risk are based on forward estimates rather than realized data.",
        "Correlations may shift in stress regimes and reduce diversification benefits.",
    ]

    return CaseStudyResult(
        title=title,
        hypothesis=hypothesis,
        summary=summary,
        weights=weight_map,
        expected_return=expected_return,
        expected_volatility=expected_volatility,
        sharpe_ratio=sharpe_ratio,
        portfolio_metrics=diagnostics,
        recommendation=recommendation,
        risks=risks,
        diagnostics={
            "budget_constraint": constraints.budget_constraint,
            "asset_count": len(assets),
            "min_weight_bounds": {k: v for k, v in min_weights.items()},
            "max_weight_bounds": {k: v for k, v in max_weights.items()},
        },
    )


def export_case_study(result: CaseStudyResult, output_dir: str | Path = "reports") -> dict[str, str]:
    """Write markdown and JSON summaries to the reports directory."""

    out_dir = Path(output_dir)
    if not out_dir.is_absolute():
        out_dir = Path(__file__).resolve().parents[1] / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = result.title.lower().replace(" ", "_")
    markdown_path = out_dir / f"{slug}.md"
    json_path = out_dir / f"{slug}.json"
    markdown_path.write_text(result.to_markdown(), encoding="utf-8")
    json_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return {"markdown": str(markdown_path), "json": str(json_path)}


def run_quant_placeholder() -> dict:
    """Backward-compatible entry point for older tests."""

    result = construct_case_study()
    return {
        "status": "ok",
        "track": "SMA Quantitative Research",
        "title": result.title,
        "expected_return": result.expected_return,
        "expected_volatility": result.expected_volatility,
        "sharpe_ratio": result.sharpe_ratio,
        "weights": result.weights,
    }


def main() -> dict[str, Any]:
    """Run the case-study suite and export outputs."""

    config = load_config()
    result = construct_case_study(title=config.get("study_title", "Portfolio Construction Case Study"))
    paths = export_case_study(result, config.get("output_dir", "reports"))
    return {"result": result.to_dict(), "paths": paths}

