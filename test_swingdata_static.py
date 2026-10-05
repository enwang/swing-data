import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESKTOP = ROOT / "SwingData_desktop.pine"
MOBILE = ROOT / "SwingData_mobile.pine"
INTRADAY_DIVIDER = ROOT / "intraday_divider.pine"
ATR_RVOL = ROOT / "atr_rvol.pine"
ATR_RVOL_MOBILE = ROOT / "atr_rvol_mobile.pine"
DOLLAR_VOLUME = ROOT / "dollar_volume.pine"
REPLAY = ROOT / "SwingData_replay.pine"


def read_desktop() -> str:
    return DESKTOP.read_text()


def read_mobile() -> str:
    return MOBILE.read_text()


def read_intraday_divider() -> str:
    return INTRADAY_DIVIDER.read_text()


def read_data_table() -> str:
    return ATR_RVOL.read_text()


def read_mobile_data_table() -> str:
    return ATR_RVOL_MOBILE.read_text()


def read_dollar_volume() -> str:
    return DOLLAR_VOLUME.read_text()


def read_replay() -> str:
    return REPLAY.read_text()


def assignment(source: str, name: str) -> str:
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith(name) and "=" in stripped:
            return stripped
    raise AssertionError(f"missing assignment for {name}")


class SwingDataStaticTests(unittest.TestCase):
    def test_replay_uses_partial_rightmost_day_only_on_one_minute(self):
        replay = read_replay()

        self.assertIn("use_partial_visible_rth_day = timeframe.isminutes and timeframe.multiplier == 1", replay)
        self.assertIn("use_latest_visible_rth_day = use_visible_replay and use_partial_visible_rth_day and found_visible_rth_day and not latest_visible_is_live_day", replay)
        self.assertIn("not use_partial_visible_rth_day and found_complete_visible_rth_day", replay)
        self.assertIn("has_replay_anchor = use_latest_visible_rth_day or use_complete_visible_rth_day", replay)

    def test_replay_does_not_duplicate_latest_day_and_matches_ma_algorithm(self):
        replay = read_replay()

        self.assertIn("latest_visible_is_live_day = latest_visible_day == latest_loaded_day", replay)
        self.assertIn("complete_visible_is_live_day = complete_visible_day == latest_loaded_day", replay)
        for expression in (
            "ta.sma(close, 5)[1]",
            "ta.sma(close, 10)[1]",
            "ta.sma(close, 20)[1]",
            "ta.sma(close, 50)[1]",
            "ta.sma(close, 150)[1]",
            "ta.sma(close, 200)[1]",
            "ta.ema(close, 10)[1]",
            "ta.ema(close, 20)[1]",
            "ta.ema(close, 50)[1]",
        ):
            self.assertIn(expression, replay)

    def test_daily_ma_levels_use_only_completed_daily_bars(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn("ta.sma(close, 5)[1]", source)
            self.assertIn("ta.sma(close, 10)[1]", source)
            self.assertIn("ta.sma(close, 20)[1]", source)
            self.assertIn("ta.sma(close, 50)[1]", source)
            self.assertIn("ta.sma(close, 150)[1]", source)
            self.assertIn("ta.sma(close, 200)[1]", source)
            self.assertIn("ta.ema(close, 10)[1]", source)
            self.assertIn("ta.ema(close, 20)[1]", source)
            self.assertIn("ta.ema(close, 50)[1]", source)

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
        self.assertIn("line.new(active_session_start_bar, active_or5_high, target_index, active_or5_high", mobile)
        self.assertIn("label.new(target_label_index, active_or5_high, \"5m\"", mobile)
        self.assertIn("tooltip=get_text(\"5m OR High\", active_or5_high)", mobile)
        self.assertIn("label.set_xy(lbl_or5h, target_label_index, active_or5_high)", mobile)

        self.assertIn("line.new(active_session_start_bar, active_or30_high, target_index, active_or30_high", mobile)
        self.assertIn("label.new(target_label_index, active_or30_high, \"30m\"", mobile)
        self.assertIn("tooltip=get_text(\"30m OR High\", active_or30_high)", mobile)
        self.assertIn("label.set_xy(lbl_or30h, target_label_index, active_or30_high)", mobile)

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

        for source in (read_desktop(), read_mobile()):
            self.assertIn("l_sma150  := line.new(active_session_start_bar, active_sma150_d", source)
            self.assertIn("lbl_sma150:= label.new(target_label_index, active_sma150_d, get_name(\"150D SMA\")", source)

    def test_visible_right_edge_replay_is_split_from_fast_desktop(self):
        desktop = read_desktop()
        replay = read_replay()
        mobile = read_mobile()

        self.assertIn('indicator("Swing Data Replay", overlay=true)', replay)
        self.assertIn("use_visible_replay = input.bool(true, \"Use Last Complete Visible RTH Day\"", replay)
        self.assertIn("is_right_visible_bar = time == chart.right_visible_bar_time", replay)
        self.assertIn("session_start_time >= chart.left_visible_bar_time", replay)
        self.assertIn("time >= chart.left_visible_bar_time", replay)
        self.assertIn("use_latest_visible_rth_day = use_visible_replay and use_partial_visible_rth_day and found_visible_rth_day and not latest_visible_is_live_day", replay)
        self.assertIn("use_complete_visible_rth_day = use_visible_replay and timeframe.isintraday and not use_partial_visible_rth_day and found_complete_visible_rth_day and not complete_visible_is_live_day", replay)
        self.assertNotIn("replay_is_historical_view", replay)
        self.assertIn('current_rth_start = timestamp("America/New_York", year(timenow, "America/New_York")', replay)
        self.assertIn('current_rth_end = timestamp("America/New_York", year(timenow, "America/New_York")', replay)
        self.assertIn("market_is_active = timenow >= current_rth_start and timenow < current_rth_end and last_bar_time >= current_rth_start", replay)
        self.assertIn("should_create_levels = timeframe.isintraday and not market_is_active", replay)
        self.assertIn("if timeframe.isintraday and not market_is_active", replay)

        self.assertNotIn("use_visible_replay", desktop)
        self.assertNotIn("chart.right_visible_bar_time", desktop)
        self.assertNotIn("chart.left_visible_bar_time", desktop)
        self.assertIn("use_latest_visible_rth_day = false", desktop)
        self.assertIn("use_complete_visible_rth_day = false", desktop)
        self.assertIn("is_data_anchor_bar = barstate.islast", desktop)
        self.assertIn("target_index = target_base_index + offset", desktop)
        self.assertIn("should_create_levels = timeframe.isintraday and not na(active_session_start_bar) and is_data_anchor_bar", desktop)
        self.assertIn("if timeframe.isintraday and not na(active_session_start_bar) and is_data_anchor_bar", desktop)

        self.assertNotIn("use_visible_replay", mobile)
        self.assertNotIn("chart.right_visible_bar_time", mobile)

    def test_ppd_low_line_is_enabled_in_both_fast_versions(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn("var float ppd_low", source)
            self.assertIn("ppd_low   := prev_low", source)
            self.assertIn("show_ppd_low_line = show_l and not na(active_ppd_low)", source)
            self.assertIn("l_ppd_low   := line.new(active_session_start_bar, active_ppd_low", source)
            self.assertIn('get_text("PPD Low", active_ppd_low)', source)

    def test_10d_sma_draws_above_20d_sma_on_desktop(self):
        desktop = read_desktop()
        self.assertLess(
            desktop.index("l_sma20   := line.new(active_session_start_bar, active_sma20_d"),
            desktop.index("l_sma10   := line.new(active_session_start_bar, active_sma10_d"),
        )

    def test_desktop_uses_native_intraday_bars_without_lower_tf_scan(self):
        desktop = read_desktop()

        self.assertNotIn("request.security_lower_tf", desktop)
        self.assertNotIn("lower_highs", desktop)
        self.assertNotIn("lower_lows", desktop)
        self.assertNotIn("lower_times", desktop)
        self.assertIn("session_lod := math.min(session_lod, low)", desktop)
        self.assertIn("running_today_low  := math.min(running_today_low, low)", desktop)

    def test_desktop_daily_ma_security_requests_are_batched(self):
        desktop = read_desktop()

        self.assertIn("[sma5_d, sma10_d, sma20_d, sma50_d, sma150_d, sma200_d, ema10_d, ema20_d, ema50_d] = request.security", desktop)
        self.assertEqual(desktop.count("request.security(syminfo.tickerid, \"D\""), 1)

    def test_20d_sma_is_light_orange_in_both_fast_versions(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn("col_20    = input.color(color.rgb(255, 183, 77)", source)

    def test_both_fast_versions_draw_active_session_today_low(self):
        for source in (read_desktop(), read_mobile()):
            self.assertIn('show_today_low = input.bool(true, "Show Today Low"', source)
            self.assertIn("col_today_low = input.color(color.rgb(0, 137, 123)", source)
            self.assertIn('line.new(active_session_start_bar, active_session_lod, target_index, active_session_lod', source)
            self.assertIn('get_text("Today Low", active_session_lod)', source)
            self.assertIn("line.set_xy2(l_today_low, target_index, active_session_lod)", source)

    def test_mobile_uses_lightweight_requests_and_external_dashboard(self):
        mobile = read_mobile()

        self.assertEqual(mobile.count('request.security(syminfo.tickerid, "D"'), 1)
        self.assertNotIn("request.security_lower_tf", mobile)
        self.assertNotIn("table.new", mobile)
        self.assertNotIn("rvol_cum_by_minute", mobile)
        self.assertNotIn("calc_rvol", mobile)
        self.assertIn('offset    = input.int(3, "Line Extension (Bars Ahead)"', mobile)
        self.assertIn('label_offset = input.int(0, "Label Gap From Line End"', mobile)

    def test_mobile_enables_all_moving_average_labels_by_default(self):
        mobile = read_mobile()

        self.assertIn('show_near_intraday_levels = input.bool(false, "Intraday: Only Show Nearby/Overlapped Levels"', mobile)
        self.assertIn('show_5    = input.bool(true,  "Show 5D SMA"', mobile)
        self.assertNotIn("ema_skip_gap", mobile)
        self.assertIn("if show_ema10 and level_is_relevant_at(active_ema10_d, active_close, active_session_lod, active_session_hod)", mobile)
        self.assertIn("if show_ema20 and level_is_relevant_at(active_ema20_d, active_close, active_session_lod, active_session_hod)", mobile)
        self.assertIn("if show_ema50 and level_is_relevant_at(active_ema50_d, active_close, active_session_lod, active_session_hod)", mobile)

    def test_desktop_core_data_requests_are_not_history_limited(self):
        source = read_desktop() + "\n" + read_data_table()

        self.assertNotIn("daily_calc_bars", source)
        self.assertNotIn("lower_tf_calc_bars", source)
        self.assertNotIn("calc_bars_count=", source)

    def test_desktop_table_logic_is_split_out(self):
        desktop = read_desktop()

        self.assertNotIn("tbl_size", desktop)
        self.assertNotIn("top_tbl", desktop)
        self.assertNotIn("bottom_tbl", desktop)
        self.assertNotIn("calc_rvol", desktop)
        self.assertNotIn("rvol_cum_by_minute", desktop)
        self.assertNotIn("chart_lod", desktop)
        self.assertNotIn("ATR Multiple Dot", desktop)

    def test_data_table_intraday_rvol_uses_same_time_history(self):
        table = read_data_table()

        self.assertNotIn("fast_load_mode", table)
        self.assertIn("rvol_slot_count = rvol_session_minutes * (rvol_intraday_days + 1)", table)
        self.assertIn("if is_new_day", table)
        self.assertIn("if timeframe.isintraday and is_rth_bar", table)
        self.assertIn("calc_rvol = timeframe.isintraday ? last_intraday_rvol * 100 : daily_rvol", table)

    def test_mobile_data_table_restores_compact_atr_lod_rvol_dashboard(self):
        table = read_mobile_data_table()

        self.assertIn('indicator("ATR RVOL Mobile", overlay=true)', table)
        self.assertIn("tbl_size  = input.string('Tiny'", table)
        self.assertIn("var table mobile_tbl = table.new(position.bottom_right, 3, 5", table)
        self.assertIn('table.cell(mobile_tbl, 1, 0, "rVOL"', table)
        self.assertIn('table.cell(mobile_tbl, 1, 1, "LoD%"', table)
        self.assertIn('table.cell(mobile_tbl, 1, 2, "Multiple"', table)
        self.assertIn('table.cell(mobile_tbl, 1, 3, "Gain%"', table)
        self.assertIn('table.cell(mobile_tbl, 1, 4, "ATR%"', table)
        self.assertIn("calc_rvol = timeframe.isintraday ? last_intraday_rvol * 100 : daily_rvol", table)

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

    def test_dollar_volume_indicator_uses_price_times_volume(self):
        dollar_volume = read_dollar_volume()

        self.assertIn('indicator("Dollar Volume", shorttitle="Dollar Vol", format=format.volume)', dollar_volume)
        self.assertIn("dollar_volume = volume * close", dollar_volume)
        self.assertIn("dollar_volume_ma = ta.sma(dollar_volume, ma_len)", dollar_volume)
        self.assertIn('plot(dollar_volume, title="Dollar Volume", style=plot.style_columns', dollar_volume)

    def test_data_table_intraday_lod_display_uses_live_session_lod(self):
        table = read_data_table()

        self.assertIn("var bool session_lod_ready = false", table)
        self.assertIn("if is_new_exchange_day and not is_rth_bar", table)
        self.assertIn("session_lod_ready := false", table)
        self.assertIn("session_lod := low", table)
        self.assertIn("session_lod_ready := true", table)
        self.assertIn("chart_lod    = timeframe.isintraday ? session_lod : na(daily_rth_low) ? low : daily_rth_low", table)
        self.assertIn("lodd_close = timeframe.isintraday ? close : chart_close", table)
        self.assertIn("calc_lodd = chart_atr > 0 ? ((lodd_close - chart_lod) / chart_atr) * 100 : na", table)
        self.assertIn("has_lod = (not timeframe.isintraday or session_lod_ready) and not na(chart_lod) and not na(calc_lodd)", table)
        self.assertIn("color_lodd = has_lod and calc_lodd > 50.0 ? tbl_extended_col : tbl_text_col", table)
        self.assertIn('str_lodd = has_lod ? str.tostring(calc_lodd, "0") + "%" : ""', table)
        self.assertIn('str_lodp = has_lod ? str.tostring(chart_lod, "#.##") : ""', table)

    def test_data_table_lod_has_no_stale_intraday_fallbacks(self):
        table = read_data_table()

        self.assertNotIn("confirmed_session_lod", table)
        self.assertNotIn("confirmed_daily_rth_low", table)
        chart_lod = assignment(table, "chart_lod")
        lodd_close = assignment(table, "lodd_close")
        calc_lodd = assignment(table, "calc_lodd")
        has_lod = assignment(table, "has_lod")

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

        self.assertIn("session_lod_ready", has_lod)
        self.assertNotIn("active_", has_lod)


if __name__ == "__main__":
    unittest.main()
