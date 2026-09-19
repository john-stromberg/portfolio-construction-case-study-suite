"""Light synthetic example workflow utilities.

This module creates small illustrative client-like examples that can be fed into
portfolio construction workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from random import Random
from typing import Any

import numpy as np

from core import (
    DEFAULT_CORRELATION,
    DEFAULT_SAMPLE_ASSETS,
    build_default_constraints,
    construct_case_study,
)
from sma_quant_core.models import PortfolioConstraints


class ClientRiskTolerance(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    BALANCED = "balanced"
    GROWTH = "growth"
    AGGRESSIVE = "aggressive"


class ClientGoal(str, Enum):
    BALANCED_GROWTH = "balanced_growth"
    LONG_TERM_GROWTH = "long_term_growth"


@dataclass
class ClientAccount:
    client_id: str
    name: str
    risk_tolerance: ClientRiskTolerance
    goal: ClientGoal
    horizon_years: int
    constraints: PortfolioConstraints
    notes: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["risk_tolerance"] = self.risk_tolerance.value
        data["goal"] = self.goal.value
        return data


@dataclass
class ClientPortfolioExample:
    client: ClientAccount
    result: Any
    weights: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "client": self.client.to_dict(),
            "result": self.result.to_dict() if hasattr(self.result, "to_dict") else self.result,
            "weights": self.weights,
        }


_RISK_PROFILE_MAP: dict[ClientRiskTolerance, dict[str, float]] = {
    ClientRiskTolerance.CONSERVATIVE: {"equity_cap": 0.45, "bond_min": 0.30, "gld_min": 0.03},
    ClientRiskTolerance.MODERATE: {"equity_cap": 0.60, "bond_min": 0.20, "gld_min": 0.02},
    ClientRiskTolerance.BALANCED: {"equity_cap": 0.70, "bond_min": 0.15, "gld_min": 0.02},
    ClientRiskTolerance.GROWTH: {"equity_cap": 0.80, "bond_min": 0.10, "gld_min": 0.00},
    ClientRiskTolerance.AGGRESSIVE: {"equity_cap": 0.90, "bond_min": 0.05, "gld_min": 0.00},
}


def _bounded(value: float, lower: float, upper: float) -> float:
    return float(max(lower, min(upper, value)))


def _choose(enum_type: type[Enum], rng: Random):
    return list(enum_type)[rng.randrange(len(list(enum_type)))]


def _make_client_constraints(risk_tolerance: ClientRiskTolerance, rng: Random) -> PortfolioConstraints:
    profile = _RISK_PROFILE_MAP[risk_tolerance]
    base = build_default_constraints()

    constraints = PortfolioConstraints(budget_constraint=1.0)
    for constraint in base.constraints:
        lower = constraint.lower_bound if constraint.lower_bound is not None else 0.0
        upper = constraint.upper_bound if constraint.upper_bound is not None else 1.0

        if constraint.asset_id in {"VTSAX", "VTIAX", "VGSLX"}:
            upper = min(upper, profile["equity_cap"])
        if constraint.asset_id == "BND":
            lower = max(lower, profile["bond_min"])
        if constraint.asset_id == "GLD":
            lower = max(lower, profile["gld_min"])
            upper = max(upper, 0.15 if risk_tolerance in {ClientRiskTolerance.CONSERVATIVE, ClientRiskTolerance.MODERATE, ClientRiskTolerance.BALANCED} else 0.10)

        # Slight randomized tightening/loosening so clients differ while remaining feasible
        jitter = rng.uniform(-0.03, 0.03)
        lower = _bounded(lower + jitter, 0.0, upper)
        upper = _bounded(upper + rng.uniform(-0.02, 0.04), lower, 1.0)
        if lower > upper:
            lower = upper

        constraints.add_weight_constraint(constraint.asset_id, lower, upper)

    return constraints


def generate_client_account(seed: int | None = None) -> ClientAccount:
    rng = Random(seed)
    risk_tolerance = _choose(ClientRiskTolerance, rng)
    goal = _choose(ClientGoal, rng)
    horizon_years = rng.randint(3, 25)

    name = f"Client {rng.randint(1000, 9999)}"
    client_id = f"acct-{rng.randint(100000, 999999)}"
    constraints = _make_client_constraints(risk_tolerance, rng)
    notes = (
        f"Illustrative synthetic example for a {risk_tolerance.value} investor with a {horizon_years}-year horizon. "
        f"Goal: {goal.value.replace('_', ' ')}."
    )

    return ClientAccount(
        client_id=client_id,
        name=name,
        risk_tolerance=risk_tolerance,
        goal=goal,
        horizon_years=horizon_years,
        constraints=constraints,
        notes=notes,
    )


def generate_client_examples(count: int = 3, seed: int | None = None) -> list[ClientAccount]:
    rng = Random(seed)
    return [generate_client_account(seed=rng.randint(0, 10**9)) for _ in range(count)]



def construct_portfolio_for_client(client: ClientAccount, use_solver: bool = True) -> ClientPortfolioExample:
    result = construct_case_study(
        title=f"{client.name} - {client.goal.value.replace('_', ' ').title()}",
        hypothesis=f"Client {client.client_id} profile: {client.risk_tolerance.value} risk tolerance, {client.horizon_years}-year horizon.",
        assets=list(DEFAULT_SAMPLE_ASSETS),
        constraints=client.constraints,
        correlation_matrix=DEFAULT_CORRELATION,
        use_solver=use_solver,
    )
    return ClientPortfolioExample(client=client, result=result, weights=result.weights)


def generate_client_portfolio_examples(count: int = 3, seed: int | None = None, use_solver: bool = True) -> list[ClientPortfolioExample]:
    clients = generate_client_examples(count=count, seed=seed)
    return [construct_portfolio_for_client(client, use_solver=use_solver) for client in clients]
