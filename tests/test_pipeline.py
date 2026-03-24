from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import build_municipal_profile, build_summary_dict, build_synthetic_cadunico_sample


class PipelineTest(unittest.TestCase):
    def test_profile_outputs_expected_summary(self) -> None:
        sample_df = build_synthetic_cadunico_sample()
        profile_df = build_municipal_profile(sample_df)
        summary = build_summary_dict(sample_df, profile_df)

        self.assertEqual(summary["ano_referencia"], 2018)
        self.assertEqual(summary["municipios_cobertos"], 102)
        self.assertGreater(summary["familias_amostra"], 20000)
        self.assertGreater(summary["pct_extrema_pobreza"], 20.0)
        self.assertIn("municipio_maior_priorizacao", summary)


if __name__ == "__main__":
    unittest.main()
