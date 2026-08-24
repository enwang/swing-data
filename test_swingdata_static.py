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
        desktop = read_desktop()
        self.assertIn("line.new(active_session_start_bar, active_or5_high, target_index, active_or5_high", desktop)
        self.assertIn("label.new(target_label_index, active_or5_high, \"5m\"", desktop)
        self.assertIn("tooltip=get_text(\"5m OR High\", active_or5_high)", desktop)
        self.assertIn("label.set_xy(lbl_or5h, target_label_index, active_or5_high)", desktop)

        self.assertIn("line.new(active_session_start_bar, active_or30_high, target_index, active_or30_high", desktop)
        self.assertIn("label.new(target_label_index, active_or30_high, \"30m\"", desktop)
        self.assertIn("tooltip=get_text(\"30m OR High\", active_or30_high)", desktop)
        self.assertIn("label.set_xy(lbl_or30h, target_label_index, active_or30_high)", desktop)

        mobile = read_mobile()
        self.assertIn("line.new(session_start_bar, or5_high, target_index, or5_high", mobile)
        self.assertIn("label.new(target_label_index, or5_high, \"5m\"", mobile)
        self.assertIn("tooltip=get_text(\"5m OR High\", or5_high)", mobile)
        self.assertIn("label.set_xy(lbl_or5h, target_label_index, or5_high)", mobile)

        self.assertIn("line.new(session_start_bar, or30_high, target_index, or30_high", mobile)
        self.assertIn("label.new(target_label_index, or30_high, \"30m\"", mobile)
        self.assertIn("tooltip=get_text(\"30m OR High\", or30_high)", mobile)
        self.assertIn("label.set_xy(lbl_or30h, target_label_index, or30_high)", mobile)

    def test_opening_range_overlap_uses_horizontal_offset_only(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn("or30_x = target_label_index + lbl_step_bars", source)
            self.assertIn("label.set_x(lbl_or5h, or5_x)", source)
            self.assertIn("label.set_x(lbl_or30h, or30_x)", source)
            self.assertNotIn("label.set_y(lbl_or5h", source)
            self.assertNotIn("label.set_y(lbl_or30h", source)

    def test_150d_sma_is_enabled_in_both_versions(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn("show_150  = input.bool(true,  \"Show 150D SMA\"", source)
            self.assertIn("col_150   = color.rgb(190, 150, 255)", source)
            self.assertIn("sma150_d  = request.security(syminfo.tickerid, \"D\", ta.sma(close, 150)", source)

        self.assertIn("l_sma150  := line.new(active_session_start_bar, active_sma150_d", read_desktop())
        self.assertIn("lbl_sma150:= label.new(target_label_index, active_sma150_d, get_name(\"150D SMA\")", read_desktop())
        self.assertIn("l_sma150  := line.new(session_start_bar, sma150_d", read_mobile())
        self.assertIn("lbl_sma150:= label.new(target_label_index, sma150_d, get_name(\"150D SMA\")", read_mobile())

    def test_visible_right_edge_replay_anchor_is_desktop_only(self):
        desktop = read_desktop()
        mobile = read_mobile()

        self.assertIn("use_visible_replay = input.bool(true, \"Use Last Complete Visible RTH Day\"", desktop)
        self.assertIn("is_right_visible_bar = time == chart.right_visible_bar_time", desktop)
        self.assertIn("is_complete_visible_rth_day = timeframe.isintraday and is_rth_close_bar", desktop)
        self.assertIn("session_start_time >= chart.left_visible_bar_time", desktop)
        self.assertIn("use_complete_visible_rth_day = use_visible_replay and timeframe.isintraday and found_complete_visible_rth_day", desktop)
        self.assertIn("is_data_anchor_bar = use_visible_replay ? (timeframe.isintraday ? is_right_visible_bar : is_right_visible_bar) : barstate.islast", desktop)
        self.assertIn("active_session_start_bar = use_complete_visible_rth_day ? anchor_session_start_bar : session_start_bar", desktop)
        self.assertIn("target_index = active_bar_index + offset", desktop)
        self.assertIn("should_create_levels = timeframe.isintraday and not na(active_session_start_bar) and is_data_anchor_bar", desktop)
        self.assertIn("if timeframe.isintraday and not na(active_session_start_bar) and is_data_anchor_bar", desktop)
        self.assertIn("if is_data_anchor_bar and show_info_table", desktop)

        self.assertNotIn("use_visible_replay", mobile)
        self.assertNotIn("chart.right_visible_bar_time", mobile)


if __name__ == "__main__":
    unittest.main()
