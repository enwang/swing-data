# Swing Data

TradingView Pine Script indicators for intraday swing-trading levels and quick dashboard stats.

## Files

- `SwingData_desktop.pine` - desktop version with top-right and bottom-right data tables.
- `SwingData_mobile.pine` - mobile version without the top-right table, with compact bottom-right stats.
- `test_swingdata_static.py` - static regression tests for label behavior.

## Current Label Rule

Opening range labels stay on their true price level. If `5m` and `30m` opening range highs overlap, the script only moves the `30m` label horizontally; it does not move either label vertically.

## Test

```bash
python3 test_swingdata_static.py
```
