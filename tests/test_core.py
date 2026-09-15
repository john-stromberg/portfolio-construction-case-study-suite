from src.core import run_quant_placeholder

def test_quant_placeholder():
    out = run_quant_placeholder()
    assert out['status'] == 'ok'

