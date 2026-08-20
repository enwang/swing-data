import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESKTOP = ROOT / "SwingData_desktop.pine"
MOBILE = ROOT / "SwingData_mobile.pine"


def read_desktop() -> str:
    return DESKTOP.read_text()


def read_mobile() -> str:
    return MOBILE.read_text()


class SwingDataStaticTests(unittest.TestCase):
    def test_no_vertical_label_price_offset(self):
        source = read_desktop() + "\n" + read_mobile()

        self.assertNotIn("vertical_stagger_labels", source)
        self.assertNotIn("or_label_gap", source)
        self.assertNotIn("label_y =", source)

    def test_opening_range_labels_stay_on_true_prices(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn("line.new(session_start_bar, or5_high, target_index, or5_high", source)
            self.assertIn("label.new(target_label_index, or5_high, \"5m\"", source)
            self.assertIn("tooltip=get_text(\"5m OR High\", or5_high)", source)
            self.assertIn("label.set_xy(lbl_or5h, target_label_index, or5_high)", source)

            self.assertIn("line.new(session_start_bar, or30_high, target_index, or30_high", source)
            self.assertIn("label.new(target_label_index, or30_high, \"30m\"", source)
            self.assertIn("tooltip=get_text(\"30m OR High\", or30_high)", source)
            self.assertIn("label.set_xy(lbl_or30h, target_label_index, or30_high)", source)

    def test_opening_range_overlap_uses_horizontal_offset_only(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn("or30_x = target_label_index + lbl_step_bars", source)
            self.assertIn("label.set_x(lbl_or5h, or5_x)", source)
            self.assertIn("label.set_x(lbl_or30h, or30_x)", source)
            self.assertNotIn("label.set_y(lbl_or5h", source)
            self.assertNotIn("label.set_y(lbl_or30h", source)


if __name__ == "__main__":
    unittest.main()
