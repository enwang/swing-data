import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESKTOP = ROOT / "SwingData_desktop.pine"
MOBILE = ROOT / "SwingData_mobile.pine"
INTRADAY_DIVIDER = ROOT / "intraday_divider.pine"


def read_desktop() -> str:
    return DESKTOP.read_text()


def read_mobile() -> str:
    return MOBILE.read_text()


def read_intraday_divider() -> str:
    return INTRADAY_DIVIDER.read_text()


def assignment(source: str, name: str) -> str:
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith(name) and "=" in stripped:
            return stripped
    raise AssertionError(f"missing assignment for {name}")


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

    def test_desktop_label_stagger_stays_near_lines(self):
        desktop = read_desktop()

        self.assertIn('lbl_step_bars   = input.int(3, "Label Stagger (bars)"', desktop)
        self.assertIn('lbl_max_slots   = input.int(2, "Max Label Stagger Slots"', desktop)
        self.assertIn("stagger_labels(array<line> lns, array<label> lbls, array<float> prices, float min_gap, int base_x, int step_bars, int max_slots, int line_gap)", desktop)
        self.assertIn("slot := math.min(slot + 1, max_slots)", desktop)
        self.assertIn("stagger_labels(lns_arr, lbls_arr, prices_arr, min_gap, target_label_index, lbl_step_bars, lbl_max_slots, label_offset)", desktop)

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
        self.assertIn("time >= chart.left_visible_bar_time", desktop)
        self.assertIn("use_latest_visible_rth_day = use_visible_replay and timeframe.isintraday and barstate.islast and is_rth_bar and found_visible_rth_day", desktop)
        self.assertNotIn("latest_session_start_time > anchor_session_start_time", desktop)
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
        self.assertIn("show_ppd_low_line = show_l and not na(active_ppd_low) and not na(active_prev_low) and active_ppd_low < active_prev_low and (active_prev_low - active_ppd_low) / active_prev_low < 0.03", desktop)
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

    def test_desktop_preserves_lod_lower_tf_scan_from_5m(self):
        desktop = read_desktop()

        self.assertIn('lower_tf = timeframe.isintraday and timeframe.multiplier >= 30 ? "1" : timeframe.isintraday ? str.tostring(timeframe.multiplier) : "1"', desktop)
        self.assertIn("lower_lows   = request.security_lower_tf(syminfo.tickerid, lower_tf, low)", desktop)
        self.assertIn("if timeframe.isintraday and timeframe.multiplier >= 5 and is_rth_bar and array.size(lower_highs) > 0", desktop)
        self.assertIn("session_lod := na(session_lod) ? bar_low  : math.min(session_lod, bar_low)", desktop)

    def test_desktop_daily_ma_security_requests_are_batched(self):
        desktop = read_desktop()

        self.assertIn("[sma5_d, sma10_d, sma20_d, sma50_d, sma150_d, sma200_d, ema10_d, ema20_d, ema50_d, atr_ma_d] = request.security", desktop)
        self.assertEqual(desktop.count("request.security(syminfo.tickerid, \"D\""), 2)

    def test_desktop_core_data_requests_are_not_history_limited(self):
        desktop = read_desktop()

        self.assertNotIn("daily_calc_bars", desktop)
        self.assertNotIn("lower_tf_calc_bars", desktop)
        self.assertNotIn("calc_bars_count=", desktop)

    def test_desktop_intraday_rvol_uses_same_time_history(self):
        desktop = read_desktop()

        self.assertNotIn("fast_load_mode", desktop)
        self.assertIn("rvol_slot_count = rvol_session_minutes * (rvol_intraday_days + 1)", desktop)
        self.assertIn("if is_new_day", desktop)
        self.assertIn("if timeframe.isintraday and is_rth_bar", desktop)
        self.assertIn("calc_rvol = timeframe.isintraday ? last_intraday_rvol * 100 : daily_rvol", desktop)

    def test_desktop_line_length_is_capped_to_rth_bars(self):
        desktop = read_desktop()

        self.assertIn("var int session_last_rth_bar", desktop)
        self.assertIn("session_last_rth_bar := bar_index", desktop)
        self.assertIn("active_rth_end_bar = use_latest_visible_rth_day ? latest_bar_index : use_complete_visible_rth_day ? anchor_bar_index : session_last_rth_bar", desktop)
        self.assertIn("target_base_index = timeframe.isintraday and not na(active_rth_end_bar) ? active_rth_end_bar : active_bar_index", desktop)
        self.assertIn("target_index = target_base_index + offset", desktop)

    def test_desktop_nearby_filter_keeps_overhead_levels_near_hod(self):
        desktop = read_desktop()

        self.assertIn("near_day_high = not na(p) and not na(anchor_hod) and math.abs(p - anchor_hod) <= near_band", desktop)
        self.assertIn("not show_near_intraday_levels or not timeframe.isintraday or overlaps_today or near_close or near_day_low or near_day_high", desktop)

    def test_desktop_has_no_today_divider_logic(self):
        desktop = read_desktop()

        self.assertNotIn("show_today_divider", desktop)
        self.assertNotIn("today_divider_col", desktop)
        self.assertNotIn("l_today_divider", desktop)
        self.assertNotIn("fast_should_draw_today_divider", desktop)
        self.assertNotIn("fast_divider_session_start_bar", desktop)
        self.assertNotIn("fast_found_visible_eth_bar", desktop)

    def test_standalone_intraday_divider_is_lightweight(self):
        divider = read_intraday_divider()

        self.assertIn('indicator("Intraday Divider", overlay=true, max_lines_count=500)', divider)
        self.assertIn('show_today_divider = input.bool(true, "Show RTH Start Divider"', divider)
        self.assertIn("is_rth_start_bar = timeframe.isintraday and is_rth_bar and (not is_rth_bar_prev or is_new_exchange_day)", divider)
        self.assertIn("is_rth_only_start_bar = is_rth_start_bar and (is_rth_bar_prev or is_new_exchange_day)", divider)
        self.assertIn("if show_today_divider and is_rth_only_start_bar", divider)
        self.assertIn("line.new(bar_index, low, bar_index, high", divider)
        self.assertIn("style=line.style_dashed, extend=extend.both", divider)
        self.assertNotIn("request.security", divider)
        self.assertNotIn("request.security_lower_tf", divider)
        self.assertNotIn("ta.sma", divider)
        self.assertNotIn("ta.ema", divider)
        self.assertNotIn("bgcolor", divider)
        self.assertNotIn("chart.left_visible_bar_time", divider)
        self.assertNotIn("chart.right_visible_bar_time", divider)

    def test_desktop_intraday_lod_display_uses_live_session_lod(self):
        desktop = read_desktop()

        self.assertIn("var bool session_lod_ready = false", desktop)
        self.assertIn("if is_new_exchange_day and not is_rth_bar", desktop)
        self.assertIn("session_lod_ready := false", desktop)
        self.assertIn("session_hod := high", desktop)
        self.assertIn("session_lod := low", desktop)
        self.assertIn("session_lod_ready := true", desktop)
        self.assertIn("chart_lod     = timeframe.isintraday ? session_lod : na(daily_rth_low) ? low : daily_rth_low", desktop)
        self.assertIn("lodd_close = timeframe.isintraday ? close : chart_close", desktop)
        self.assertIn("calc_lodd = (chart_atr > 0)    ? ((lodd_close - chart_lod) / chart_atr) * 100 : na", desktop)
        self.assertIn("display_chart_lod = timeframe.isintraday ? chart_lod : na(active_chart_lod) ? low : active_chart_lod", desktop)
        self.assertIn("display_calc_lodd = timeframe.isintraday ? calc_lodd : chart_atr > 0 ? ((chart_close - display_chart_lod) / chart_atr) * 100 : na", desktop)
        self.assertIn("has_lod = (not timeframe.isintraday or (barstate.islast and session_lod_ready)) and not na(display_chart_lod) and not na(display_calc_lodd)", desktop)
        self.assertIn("color_lodd = has_lod and display_calc_lodd > 50.0 ? tbl_extended_col : tbl_text_col", desktop)
        self.assertIn('str_lodd = has_lod ? str.tostring(display_calc_lodd, "0") + "%" : ""', desktop)
        self.assertIn('str_lodp = has_lod ? str.tostring(display_chart_lod, "#.##") : ""', desktop)

    def test_desktop_lod_has_no_stale_intraday_fallbacks(self):
        desktop = read_desktop()

        self.assertNotIn("confirmed_session_lod", desktop)
        self.assertNotIn("confirmed_daily_rth_low", desktop)
        chart_lod = assignment(desktop, "chart_lod")
        lodd_close = assignment(desktop, "lodd_close")
        calc_lodd = assignment(desktop, "calc_lodd")
        display_chart_lod = assignment(desktop, "display_chart_lod")
        display_calc_lodd = assignment(desktop, "display_calc_lodd")
        has_lod = assignment(desktop, "has_lod")

        self.assertIn("timeframe.isintraday ? session_lod", chart_lod)
        self.assertIn("na(daily_rth_low) ? low : daily_rth_low", chart_lod)
        self.assertNotIn("[1]", chart_lod)

        self.assertIn("timeframe.isintraday ? close : chart_close", lodd_close)
        self.assertNotIn("? d_close", lodd_close)
        self.assertNotIn("- d_close", lodd_close)
        self.assertNotIn("active_", lodd_close)
        self.assertNotIn("[1]", lodd_close)

        self.assertIn("lodd_close - chart_lod", calc_lodd)
        self.assertNotIn("chart_close - chart_lod", calc_lodd)
        self.assertNotIn("? d_close", calc_lodd)
        self.assertNotIn("- d_close", calc_lodd)
        self.assertNotIn("active_", calc_lodd)
        self.assertNotIn("[1]", calc_lodd)

        intraday_display_branch = display_chart_lod.split(":", 1)[0]
        self.assertIn("timeframe.isintraday ? chart_lod", intraday_display_branch)
        self.assertNotIn("active_", intraday_display_branch)
        self.assertNotIn("[1]", display_chart_lod)

        intraday_lodd_branch = display_calc_lodd.split(":", 1)[0]
        self.assertIn("timeframe.isintraday ? calc_lodd", intraday_lodd_branch)
        self.assertNotIn("active_", intraday_lodd_branch)
        self.assertNotIn("[1]", display_calc_lodd)

        self.assertIn("session_lod_ready", has_lod)
        self.assertIn("barstate.islast", has_lod)
        self.assertNotIn("active_", has_lod)


if __name__ == "__main__":
    unittest.main()
