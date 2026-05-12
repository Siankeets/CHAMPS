"""
utils/forecasting.py
--------------------
ARIMA-based attendance forecasting for CHAMPS.

Groups historical attendance records by event_type, counts headcount per
event occurrence, then fits ARIMA(1,1,1) to forecast the *next* expected
headcount for each event type.

Falls back gracefully when there is too little data (< 2 data points) or
when statsmodels is not installed.
"""

from __future__ import annotations
from collections import defaultdict
from datetime import date
from typing import Any


# ── helpers ──────────────────────────────────────────────────────────────────

def _headcounts_by_type(events_with_att: list[dict]) -> dict[str, list[int]]:
    """
    events_with_att: list of dicts produced by the route, each has
        { 'event': Event, 'present': int, 'late': int, 'absent': int, 'total': int }
    Groups total headcount per event_type ordered by event_date (ascending).
    """
    grouped: dict[str, list[tuple[date, int]]] = defaultdict(list)
    for es in events_with_att:
        ev = es["event"]
        grouped[ev.event_type].append((ev.event_date or date.min, es["total"]))

    # Sort each group chronologically and extract just the counts
    result: dict[str, list[int]] = {}
    for etype, pairs in grouped.items():
        pairs.sort(key=lambda x: x[0])
        result[etype] = [count for _, count in pairs]
    return result


def _arima_forecast(series: list[int]) -> int | None:
    """
    Fit ARIMA(1,1,1) on *series* and return a 1-step-ahead forecast (int).
    Returns None if the series is too short or statsmodels is unavailable.
    """
    if len(series) < 2:
        return None
    try:
        from statsmodels.tsa.arima.model import ARIMA
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Use simpler order when series is very short
            order = (1, 1, 1) if len(series) >= 4 else (1, 1, 0)
            model = ARIMA(series, order=order)
            fit = model.fit()
            forecast = fit.forecast(steps=1)
            value = int(round(float(forecast.iloc[0])))
            return max(0, value)          # attendance can't be negative
    except Exception:
        # Graceful fallback: simple moving average of last 3
        window = series[-3:]
        return int(round(sum(window) / len(window)))


# ── public API ────────────────────────────────────────────────────────────────

def build_forecasts(event_stats: list[dict]) -> list[dict]:
    """
    Returns a list of forecast dicts, one per event_type:

        {
            "event_type": str,
            "occurrences": int,          # how many past events fed the model
            "history": list[int],        # headcounts used (chronological)
            "avg_attendance": float,
            "predicted": int | None,     # ARIMA 1-step-ahead forecast
            "trend": str,                # "up" | "down" | "stable" | "new"
            "confidence": str,           # "High" | "Medium" | "Low"
        }
    """
    by_type = _headcounts_by_type(event_stats)
    results = []

    for etype, history in sorted(by_type.items()):
        n = len(history)
        avg = sum(history) / n if n else 0
        predicted = _arima_forecast(history)

        # Trend: compare last two data points (or predicted vs avg)
        if n >= 2:
            delta = history[-1] - history[-2]
            if delta > 1:
                trend = "up"
            elif delta < -1:
                trend = "down"
            else:
                trend = "stable"
        elif predicted is not None:
            trend = "new"
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
            "event_type":      etype,
            "occurrences":     n,
            "history":         history,
            "avg_attendance":  round(avg, 1),
            "predicted":       predicted,
            "trend":           trend,
            "confidence":      confidence,
        })

    return results