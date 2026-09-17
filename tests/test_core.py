from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from core import (  # noqa: E402
    CaseStudyResult,
    build_default_constraints,
    construct_case_study,
    export_case_study,
    load_config,
    main,
    run_quant_placeholder,
)


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

