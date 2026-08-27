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
            self.assertIn("ta.sma(close, 150)", source)

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
        self.assertIn("is_visible_rth_day_bar = timeframe.isintraday and is_rth_bar", desktop)
        self.assertIn("session_start_time >= chart.left_visible_bar_time", desktop)
        self.assertIn("use_latest_visible_rth_day = use_visible_replay and timeframe.isintraday and found_visible_rth_day", desktop)
        self.assertIn("latest_session_start_time > anchor_session_start_time", desktop)
        self.assertIn("use_complete_visible_rth_day = use_visible_replay and timeframe.isintraday and found_complete_visible_rth_day and not use_latest_visible_rth_day", desktop)
        self.assertIn("is_data_anchor_bar = use_visible_replay ? (timeframe.isintraday ? is_right_visible_bar : is_right_visible_bar) : barstate.islast", desktop)
        self.assertIn("active_session_start_bar = use_latest_visible_rth_day ? latest_session_start_bar : use_complete_visible_rth_day ? anchor_session_start_bar : session_start_bar", desktop)
        self.assertIn("target_index = target_base_index + offset", desktop)
        self.assertIn("should_create_levels = timeframe.isintraday and not na(active_session_start_bar) and is_data_anchor_bar", desktop)
        self.assertIn("if timeframe.isintraday and not na(active_session_start_bar) and is_data_anchor_bar", desktop)
        self.assertIn("if is_data_anchor_bar and show_info_table", desktop)

        self.assertNotIn("use_visible_replay", mobile)
        self.assertNotIn("chart.right_visible_bar_time", mobile)

    def test_ppd_low_line_is_desktop_only(self):
        desktop = read_desktop()
        mobile = read_mobile()

        self.assertIn("var float ppd_low", desktop)
        self.assertIn("ppd_low   := prev_low", desktop)
        self.assertIn("active_ppd_low = use_latest_visible_rth_day ? latest_ppd_low : use_complete_visible_rth_day ? anchor_ppd_low : ppd_low", desktop)
        self.assertIn("show_ppd_low_line = show_l and not na(active_ppd_low) and not na(active_prev_low) and active_ppd_low < active_prev_low and (active_prev_low - active_ppd_low) / active_prev_low < 0.01", desktop)
        self.assertIn("l_ppd_low   := line.new(active_session_start_bar, active_ppd_low, target_index, active_ppd_low", desktop)
        self.assertIn("lbl_ppd_low := label.new(target_label_index, active_ppd_low, get_text(\"PPD Low\", active_ppd_low)", desktop)
        self.assertIn("add_lbl(lns_arr, lbls_arr, prices_arr, l_ppd_low, lbl_ppd_low, active_ppd_low)", desktop)

        self.assertNotIn("PPD Low", mobile)

    def test_10d_sma_draws_above_20d_sma_on_desktop(self):
        desktop = read_desktop()
        self.assertLess(
            desktop.index("l_sma20   := line.new(active_session_start_bar, active_sma20_d"),
            desktop.index("l_sma10   := line.new(active_session_start_bar, active_sma10_d"),
        )

    def test_desktop_skips_lower_tf_scan_below_30m(self):
        desktop = read_desktop()

        self.assertIn("use_lower_tf_scan = not timeframe.isintraday or timeframe.multiplier >= 30", desktop)
        self.assertIn("array<float> lower_highs = use_lower_tf_scan ? request.security_lower_tf", desktop)
        self.assertIn("if timeframe.isintraday and timeframe.multiplier >= 30 and is_rth_bar and array.size(lower_highs) > 0", desktop)

    def test_desktop_daily_ma_security_requests_are_batched(self):
        desktop = read_desktop()

        self.assertIn("[sma5_d, sma10_d, sma20_d, sma50_d, sma150_d, sma200_d, ema10_d, ema20_d, ema50_d, atr_ma_d] = request.security", desktop)
        self.assertEqual(desktop.count("request.security(syminfo.tickerid, \"D\""), 2)

    def test_desktop_request_history_is_limited(self):
        desktop = read_desktop()

        self.assertIn("daily_calc_bars = 260", desktop)
        self.assertIn("lower_tf_calc_bars = 600", desktop)
        self.assertIn("calc_bars_count=daily_calc_bars", desktop)
        self.assertIn("calc_bars_count=lower_tf_calc_bars", desktop)

    def test_desktop_fast_load_mode_skips_intraday_rvol_history(self):
        desktop = read_desktop()

        self.assertIn("fast_load_mode = input.bool(true, \"Fast Load Mode\"", desktop)
        self.assertIn("rvol_slot_count = fast_load_mode ? 1 : rvol_session_minutes * (rvol_intraday_days + 1)", desktop)
        self.assertIn("if not fast_load_mode and is_new_day", desktop)
        self.assertIn("if not fast_load_mode and timeframe.isintraday and is_rth_bar", desktop)
        self.assertIn("calc_rvol = timeframe.isintraday and not fast_load_mode ? last_intraday_rvol * 100 : daily_rvol", desktop)

    def test_desktop_line_length_is_capped_to_rth_bars(self):
        desktop = read_desktop()

        self.assertIn("var int session_last_rth_bar", desktop)
        self.assertIn("session_last_rth_bar := bar_index", desktop)
        self.assertIn("active_rth_end_bar = use_latest_visible_rth_day ? latest_bar_index : use_complete_visible_rth_day ? anchor_bar_index : session_last_rth_bar", desktop)
        self.assertIn("target_base_index = timeframe.isintraday and not na(active_rth_end_bar) ? active_rth_end_bar : active_bar_index", desktop)
        self.assertIn("target_index = target_base_index + offset", desktop)


if __name__ == "__main__":
    unittest.main()
