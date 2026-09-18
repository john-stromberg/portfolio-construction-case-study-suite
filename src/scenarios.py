"""Scenario and stress-test definitions for portfolio robustness analysis."""

from enum import Enum
from dataclasses import dataclass

import numpy as np

from sma_quant_core.models import Asset


class Scenario(Enum):
    """Market scenarios for stress-testing portfolio robustness."""

    BASELINE = "baseline"  # No adjustments
    RISK_OFF = "risk_off"  # Risk-averse flight to safety
    RATES_UP = "rates_up"  # Rising interest rate environment
    EQUITY_SHOCK = "equity_shock"  # Significant equity drawdown


@dataclass
class ScenarioAdjustment:
    """Adjustment factors applied to assets for a given scenario."""

    scenario: Scenario
    return_multiplier: dict[str, float]  # asset_id -> multiplier (0.9 = -10%)
    volatility_multiplier: dict[str, float]  # asset_id -> multiplier (1.2 = +20%)


def get_scenario_adjustment(scenario: Scenario) -> ScenarioAdjustment:
    """Retrieve adjustment factors for a given scenario.

    Scenarios encode realistic stress events:
    - BASELINE: no adjustment (benchmark)
    - RISK_OFF: equity down, bonds up (flight to safety)
    - RATES_UP: bonds down significantly (duration risk), equity mixed
    - EQUITY_SHOCK: severe equity drawdown, alternatives suffer, bonds rally

    These are pedagogical adjustments that demonstrate tail risk and diversification.
    """

    if scenario == Scenario.BASELINE:
        # No adjustments
        return ScenarioAdjustment(
            scenario=Scenario.BASELINE,
            return_multiplier={},
            volatility_multiplier={},
        )

    elif scenario == Scenario.RISK_OFF:
        # Flight to safety: equities down, bonds up, treasures rally, alternatives down
        return ScenarioAdjustment(
            scenario=Scenario.RISK_OFF,
            return_multiplier={
                "VTSAX": 0.75,  # US equities -25%
                "VTIAX": 0.70,  # Intl equities -30% (more exposed)
                "BND": 1.05,  # Bonds +5% (gains from flight to safety)
                "VGSLX": 0.65,  # REITs down -35% (real assets suffer)
                "GLD": 1.10,  # Gold +10% (safe haven)
            },
            volatility_multiplier={
                "VTSAX": 1.5,  # Equity volatility spikes
                "VTIAX": 1.6,  # Intl equity volatility spikes more
                "BND": 0.8,  # Bond volatility drops in safe-haven flight
                "VGSLX": 1.8,  # REIT volatility spikes
                "GLD": 1.2,  # Gold volatility increases slightly
            },
        )

    elif scenario == Scenario.RATES_UP:
        # Rising rates: bonds hurt, floating rate assets hurt, equities hit but less
        return ScenarioAdjustment(
            scenario=Scenario.RATES_UP,
            return_multiplier={
                "VTSAX": 0.90,  # US equities -10% (earnings pressure)
                "VTIAX": 0.88,  # Intl equities -12% (currency + rates)
                "BND": 0.75,  # Bonds -25% (duration risk)
                "VGSLX": 0.70,  # REITs -30% (refinancing pressure)
                "GLD": 1.00,  # Gold flat (neutral to rates)
            },
            volatility_multiplier={
                "VTSAX": 1.3,
                "VTIAX": 1.35,
                "BND": 1.4,  # Bond volatility spikes with rate uncertainty
                "VGSLX": 1.5,  # REIT volatility spikes
                "GLD": 1.1,
            },
        )

    elif scenario == Scenario.EQUITY_SHOCK:
        # Severe equity drawdown: equities crater, bonds rally sharply, gold spikes
        return ScenarioAdjustment(
            scenario=Scenario.EQUITY_SHOCK,
            return_multiplier={
                "VTSAX": 0.60,  # US equities -40%
                "VTIAX": 0.55,  # Intl equities -45%
                "BND": 1.15,  # Bonds +15% (flight to quality, duration gains)
                "VGSLX": 0.40,  # REITs -60% (correlation breakdown, liquidity)
                "GLD": 1.25,  # Gold +25% (extreme safe haven)
            },
            volatility_multiplier={
                "VTSAX": 2.0,  # Extreme equity volatility
                "VTIAX": 2.1,
                "BND": 0.9,  # Bond volatility drops as quality deepens
                "VGSLX": 2.3,  # Extreme REIT volatility
                "GLD": 1.4,  # Higher gold volatility
            },
        )

    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def apply_scenario(
    assets: list[Asset],
    scenario: Scenario,
) -> list[Asset]:
    """Apply scenario adjustments to asset return and volatility expectations.

    Args:
        assets: List of Asset objects to adjust
        scenario: Scenario enum value

    Returns:
        New list of Asset objects with adjusted return and volatility expectations
    """

    adjustment = get_scenario_adjustment(scenario)

    adjusted = []
    for asset in assets:
        # Get adjustment multipliers, defaulting to 1.0 (no change) if not specified
        ret_mult = adjustment.return_multiplier.get(asset.id, 1.0)
        vol_mult = adjustment.volatility_multiplier.get(asset.id, 1.0)

        adjusted_asset = Asset(
            id=asset.id,
            name=asset.name,
            asset_class=asset.asset_class,
            expected_return=asset.expected_return * ret_mult,
            volatility=asset.volatility * vol_mult,
        )
        adjusted.append(adjusted_asset)

    return adjusted
