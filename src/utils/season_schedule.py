"""Season and schedule times logic (summer/winter)."""

from datetime import date, time
from typing import Dict, Any

# Default: summer 1/1 - 30/6, rest is winter
DEFAULT_SUMMER_START_MONTH = 1
DEFAULT_SUMMER_START_DAY = 1
DEFAULT_SUMMER_END_MONTH = 6
DEFAULT_SUMMER_END_DAY = 30

# Schedule times by season (morning start, morning end, break start, break end, afternoon start, afternoon end)
# Summer: 6:30-12:00, break 12:00-14:00, afternoon 14:00-16:30 (5.5 + 2.5 = 8h)
# Winter: 7:00-11:30, break 11:30-13:30, afternoon 13:30-17:00 (4.5 + 3.5 = 8h)
SUMMER_SCHEDULE = {
    "morning_start": time(6, 30),
    "morning_end": time(12, 0),
    "break_start": time(12, 0),
    "break_end": time(14, 0),
    "afternoon_start": time(14, 0),
    "afternoon_end": time(16, 30),
    "daily_total_hours": 8.0,
}
WINTER_SCHEDULE = {
    "morning_start": time(7, 0),
    "morning_end": time(11, 30),
    "break_start": time(11, 30),
    "break_end": time(13, 30),
    "afternoon_start": time(13, 30),
    "afternoon_end": time(17, 0),
    "daily_total_hours": 8.0,
}


def _date_ordinal(d: date) -> int:
    """(month, day) as comparable ordinal (ignoring year)."""
    return d.month * 31 + d.day


def _in_range(month: int, day: int, start_m: int, start_d: int, end_m: int, end_d: int) -> bool:
    """True if (month, day) is in [start_m/start_d, end_m/end_d] inclusive."""
    o = month * 31 + day
    o_start = start_m * 31 + start_d
    o_end = end_m * 31 + end_d
    return o_start <= o <= o_end


def get_season_for_date(
    d: date,
    summer_start_month: int = DEFAULT_SUMMER_START_MONTH,
    summer_start_day: int = DEFAULT_SUMMER_START_DAY,
    summer_end_month: int = DEFAULT_SUMMER_END_MONTH,
    summer_end_day: int = DEFAULT_SUMMER_END_DAY,
) -> str:
    """Return 'summer' or 'winter' for the given date."""
    if _in_range(d.month, d.day, summer_start_month, summer_start_day, summer_end_month, summer_end_day):
        return "summer"
    return "winter"


def get_schedule_times_for_date(
    d: date,
    summer_start_month: int = DEFAULT_SUMMER_START_MONTH,
    summer_start_day: int = DEFAULT_SUMMER_START_DAY,
    summer_end_month: int = DEFAULT_SUMMER_END_MONTH,
    summer_end_day: int = DEFAULT_SUMMER_END_DAY,
) -> Dict[str, Any]:
    """Return schedule times dict for the given date (based on season)."""
    season = get_season_for_date(
        d, summer_start_month, summer_start_day, summer_end_month, summer_end_day
    )
    if season == "summer":
        return dict(SUMMER_SCHEDULE)
    return dict(WINTER_SCHEDULE)


def _parse_time_str(s: str) -> "time | None":
    """Parse 'HH:MM' or 'H:MM' to time."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    try:
        parts = s.split(":")
        if len(parts) >= 2:
            return time(int(parts[0]), int(parts[1]))
    except (ValueError, TypeError):
        pass
    return None


def _time_to_minutes(tm: time) -> int:
    """Convert time to minutes since midnight."""
    return tm.hour * 60 + tm.minute


def _compute_daily_total_hours(t: Dict[str, Any]) -> float:
    """Compute daily total work hours from morning and afternoon ranges (excluding break).
    Used so that when user changes the time frame in Settings, validation follows the configured total."""
    m_start = t.get("morning_start")
    m_end = t.get("morning_end")
    a_start = t.get("afternoon_start")
    a_end = t.get("afternoon_end")
    if not all([m_start, m_end, a_start, a_end]):
        return 8.0
    morning_mins = _time_to_minutes(m_end) - _time_to_minutes(m_start)
    afternoon_mins = _time_to_minutes(a_end) - _time_to_minutes(a_start)
    return (morning_mins + afternoon_mins) / 60.0


def _apply_time_overrides(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Apply time overrides (values as time or 'HH:MM' string) to base dict. Returns new dict."""
    result = dict(base)
    for key in ("morning_start", "morning_end", "break_start", "break_end", "afternoon_start", "afternoon_end"):
        val = overrides.get(key)
        if val is None:
            continue
        if isinstance(val, time):
            result[key] = val
        elif isinstance(val, str):
            t = _parse_time_str(val)
            if t is not None:
                result[key] = t
    return result


def get_schedule_times_from_settings(d: date, settings) -> Dict[str, Any]:
    """Return schedule times for date using season bounds and time overrides from Settings.
    daily_total_hours is computed from the configured morning/afternoon range so validation follows Settings."""
    start_m = int(settings.get("summer_start_month", DEFAULT_SUMMER_START_MONTH))
    start_d = int(settings.get("summer_start_day", DEFAULT_SUMMER_START_DAY))
    end_m = int(settings.get("summer_end_month", DEFAULT_SUMMER_END_MONTH))
    end_d = int(settings.get("summer_end_day", DEFAULT_SUMMER_END_DAY))
    base = get_schedule_times_for_date(d, start_m, start_d, end_m, end_d)
    season = get_season_for_date(d, start_m, start_d, end_m, end_d)
    overrides = settings.get_all_season_times(season)
    # Convert "HH:MM" overrides to time objects for _apply_time_overrides
    override_times = {}
    for k, v in overrides.items():
        if v:
            t = _parse_time_str(v)
            if t is not None:
                override_times[k] = t
    result = _apply_time_overrides(base, override_times)
    result["daily_total_hours"] = _compute_daily_total_hours(result)
    return result
