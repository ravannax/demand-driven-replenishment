"""Smoke test del pipeline sobre datos sintéticos (si existen) o regenerados."""

from pathlib import Path

from src.generate_synthetic import generate_all
from src.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"


def test_pipeline_end_to_end(tmp_path):
    out = tmp_path / "out"
    data = tmp_path / "data"
    generate_all(seed=42, out_dir=data)
    df = run_pipeline(data_dir=data, output_dir=out, buffer_months=3.0, cutoff_day=21)

    assert len(df) == 100
    assert (df["cantidad_a_comprar"] >= 0).all()
    # Ningún descontinuado debería pedir compra
    if "descontinuado" in df.columns:
        disc = df["descontinuado"].fillna(False).astype(bool)
        assert (df.loc[disc, "cantidad_a_comprar"] == 0).all()
    assert (out / "sugerido_compras.csv").exists()
    assert (out / "resumen.csv").exists()
