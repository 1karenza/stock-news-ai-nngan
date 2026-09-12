"""Regression checks for restoring V5 alongside the current news application."""
import unittest
import ast
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parent / "app.py"


class BondV5Tests(unittest.TestCase):
    def test_assessment_percentage_and_missing_yield(self):
        # Load the calculation independently from Streamlit's page execution.
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == "bond_investment_assessment")
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(APP_PATH), "exec"), namespace)
        assess = namespace["bond_investment_assessment"]
        inputs = dict(fair_price=100, market_price=80, ytm=0.12, required_yield=0.08,
                      mod_duration=2, credit_rating="AAA", liquidity="Cao")
        result = assess(**inputs)
        self.assertAlmostEqual(result["valuation_gap"], 0.20)
        self.assertTrue(any("20.00%" in reason for reason in result["reasons"]))
        for missing in ("ytm", "mod_duration"):
            incomplete = assess(**{**inputs, missing: None})
            self.assertEqual(incomplete["verdict"], "CẦN THÊM DỮ LIỆU")

    def test_presets_keep_price_duration_and_cashflow_results(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs), 2)
        metrics = {item.label: item.value for item in app.metric}
        self.assertEqual(metrics["Giá lý thuyết"], "96.044")
        self.assertEqual(metrics["YTM từ giá thị trường"], "8,88%")
        self.assertEqual(metrics["Modified Duration"], "4.02")
        self.assertEqual(len(app.dataframe[0].value), 10)
        self.assertTrue(any("CẦN THÊM DỮ LIỆU" in item.value for item in app.markdown))

        for preset, price, periods in [
            ("Ví dụ B – Coupon 10%, 3 năm", "105.154", 3),
            ("Ví dụ C – Zero-coupon 4 năm", "73.503", 4),
        ]:
            app.selectbox(key="bond_preset").select(preset).run()
            self.assertFalse(app.exception)
            metrics = {item.label: item.value for item in app.metric}
            self.assertEqual(metrics["Giá lý thuyết"], price)
            self.assertEqual(len(app.dataframe[0].value), periods)

    def test_form_submission_updates_risk_verdict_and_ytm_mode(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        next(item for item in app.selectbox if item.label == "Xếp hạng tín nhiệm").select("AAA")
        next(item for item in app.selectbox if item.label == "Thanh khoản thứ cấp").select("Cao")
        next(item for item in app.selectbox if item.label == "Tài sản bảo đảm").select("Có tài sản bảo đảm")
        next(item for item in app.number_input if item.label == "Giá thị trường").set_value(90000.0)
        next(item for item in app.button if "Tính định giá" in item.label).click().run()
        self.assertFalse(app.exception)
        panel = next(item.value for item in app.markdown if 'class="assessment-panel"' in item.value)
        self.assertIn('data-level="success"', panel)
        self.assertIn("CÓ THỂ CÂN NHẮC", panel)

        next(item for item in app.selectbox if item.label == "Xếp hạng tín nhiệm").select("B hoặc thấp hơn")
        next(item for item in app.selectbox if item.label == "Thanh khoản thứ cấp").select("Thấp")
        next(item for item in app.number_input if item.label == "Giá thị trường").set_value(110000.0)
        next(item for item in app.radio if item.label == "Mục tiêu").set_value("Tính YTM từ giá thị trường")
        next(item for item in app.button if "Tính định giá" in item.label).click().run()
        self.assertFalse(app.exception)
        panel = next(item.value for item in app.markdown if 'class="assessment-panel"' in item.value)
        self.assertIn('data-level="error"', panel)
        self.assertIn("CHƯA HẤP DẪN", panel)
        metrics = {item.label: item.value for item in app.metric}
        self.assertIn("YTM", metrics)
        self.assertNotEqual(metrics["YTM"], "N/A")


if __name__ == "__main__":
    unittest.main()
