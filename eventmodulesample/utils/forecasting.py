"""
utils/forecasting.py
--------------------
ARIMA-based attendance forecasting for CHAMPS.

Groups historical attendance records by event_type, counts PRESENT + LATE
headcount per event occurrence (i.e. people who actually showed up), then
fits ARIMA(1,1,1) to forecast the *next* expected headcount for each type.

NOTE: Absent records are intentionally excluded from the forecast series.
      Absent records represent no-shows; including them would inflate the
      predicted headcount whenever absences are bulk-recorded.

Falls back gracefully when there is too little data (< 2 data points) or
when statsmodels is not installed.
"""

from __future__ import annotations
from collections import defaultdict
from datetime import date
from typing import Any


# ── helpers ──────────────────────────────────────────────────────────────────

def _headcounts_by_type(events_with_att: list[dict]) -> dict[str, list[dict]]:
    """
    events_with_att: list of dicts produced by the route, each has
        { 'event': Event, 'present': int, 'late': int, 'absent': int, 'total': int }

    Groups per event_type ordered by event_date (ascending).
    Returns a dict of { event_type: [ { 'date': date, 'showed_up': int, 'absent': int, 'total': int } ] }

    'showed_up' = present + late  ← this is what the ARIMA model trains on.
    """
    grouped: dict[str, list[tuple[date, int, int, int]]] = defaultdict(list)
    for es in events_with_att:
        ev = es["event"]
        showed_up = es["present"] + es["late"]
        grouped[ev.event_type].append((
            ev.event_date or date.min,
            showed_up,
            es["absent"],
            es["total"],
        ))

    result: dict[str, list[dict]] = {}
    for etype, rows in grouped.items():
        rows.sort(key=lambda x: x[0])
        result[etype] = [
            {"date": d, "showed_up": s, "absent": a, "total": t}
            for d, s, a, t in rows
        ]
    return result


def _arima_forecast(series: list[int]) -> int | None:
    """
    Fit ARIMA on *series* and return a 1-step-ahead forecast (int).
    Returns None if the series is too short or statsmodels is unavailable.
    """
    if len(series) < 2:
        return None

    try:
        from statsmodels.tsa.arima.model import ARIMA
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Use simpler order when series is very short to avoid over-fitting
            order = (1, 1, 1) if len(series) >= 4 else (1, 1, 0)
            model = ARIMA(series, order=order)
            fit   = model.fit()
            forecast = fit.forecast(steps=1)
            value = int(round(float(forecast.iloc[0])))
            return max(0, value)   # attendance can't be negative
    except Exception:
        # Graceful fallback: simple moving average of last 3
        window = series[-3:]
        return int(round(sum(window) / len(window)))


# ── public API ────────────────────────────────────────────────────────────────

def build_forecasts(event_stats: list[dict]) -> list[dict]:
    """
    Returns a list of forecast dicts, one per event_type:

        {
            "event_type":      str,
            "occurrences":     int,        # how many past events fed the model
            "history":         list[int],  # showed-up counts used (chronological)
            "avg_showed_up":   float,      # average of present+late per event
            "avg_absent":      float,      # average absences per event (info only)
            "predicted":       int | None, # ARIMA 1-step-ahead forecast
            "trend":           str,        # "up" | "down" | "stable" | "new"
            "confidence":      str,        # "High" | "Medium" | "Low"
        }
    """
    by_type = _headcounts_by_type(event_stats)
    results = []

    for etype, rows in sorted(by_type.items()):
        n = len(rows)

        # Series used for ARIMA = people who actually showed up
        history     = [r["showed_up"] for r in rows]
        absent_vals = [r["absent"]    for r in rows]

        avg_showed_up = round(sum(history)     / n, 1) if n else 0
        avg_absent    = round(sum(absent_vals) / n, 1) if n else 0

        predicted = _arima_forecast(history)

        # Trend: compare last two showed-up counts
        if n >= 2:
            delta = history[-1] - history[-2]
            if delta > 1:
                trend = "up"
            elif delta < -1:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "new"

        # Confidence based on data richness
        if n >= 5:
            confidence = "High"
        elif n >= 3:
            confidence = "Medium"
        else:
            confidence = "Low"

        results.append({
            "event_type":    etype,
            "occurrences":   n,
            "history":       history,
            "avg_attendance": avg_showed_up,   # kept same key so template doesn't break
            "avg_absent":    avg_absent,
            "predicted":     predicted,
            "trend":         trend,
            "confidence":    confidence,
        })

    return results