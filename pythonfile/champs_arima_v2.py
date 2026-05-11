# =============================================================================
# CHAMPS - Event Attendance Forecasting Pipeline v2
# Model: ARIMA (AutoRegressive Integrated Moving Average)
#
# What changed from v1:
#   - 2 events per week: Saturday Breakfast + Sunday Mass
#   - Smoother dummy data (less wild spikes/dips)
#   - Combined model treating both events as one unified time series
#   - Fully explained inline so you understand what every part does
#   - Database-ready: shows exactly where you'd swap dummy data for real DB data
#
# Author note:
#   The values in generate_dummy_data() are interchangeable — meaning once
#   your Flask + MySQL database is set up, you replace that entire function
#   with a database query. Everything else (model, forecast, chart) stays
#   exactly the same. We marked that swap point clearly below.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings("ignore")


# =============================================================================
# STEP 1: DATA SOURCE
# -----------------------------------------------------------------------------
# RIGHT NOW: We generate dummy data that mimics real BCBP attendance patterns.
#
# IN THE FUTURE (when your DB is ready): Replace this entire function with
# a database query like:
#
#   import mysql.connector
#   def load_from_database():
#       conn = mysql.connector.connect(host="localhost", user="root",
#                                      password="", database="champs_db")
#       query = """
#           SELECT program_date, COUNT(*) as attendance
#           FROM attendance
#           WHERE attendance_status = 'Attended'
#           GROUP BY program_date
#           ORDER BY program_date ASC
#       """
#       df = pd.read_sql(query, conn)
#       df['program_date'] = pd.to_datetime(df['program_date'])
#       df = df.set_index('program_date')
#       return df['attendance']
#
# The model, forecast, and chart code below will work with EITHER version —
# dummy data or real database data — without any other changes needed.
# =============================================================================

def generate_dummy_data(n_weeks=104, seed=42):
    """
    Generates 2 years of smooth, realistic attendance data for BCBP Lipa.
    Two events per week: Saturday Breakfast and Sunday Mass.

    HOW THE SMOOTHNESS WORKS:
    - We use a rolling average (window=4) to smooth out random noise.
      This means each data point is averaged with its 3 neighbors,
      which removes sudden extreme spikes and makes the trend gradual.
    - Noise is kept small (std=6 instead of 10) so swings are gentle.
    - Seasonal variation uses a slow sine wave so highs/lows build
      gradually over months, not jump week to week.

    WHY 2 EVENTS PER WEEK:
    - Saturday Breakfast typically has slightly lower attendance (~100)
      since it's early morning on a weekend.
    - Sunday Mass typically has higher attendance (~130) as it follows
      the regular worship schedule.
    - We generate both and combine them into one time series so the
      model sees the full picture of weekly chapter activity.

    Parameters:
        n_weeks (int): Number of weeks to simulate (104 = 2 years).
        seed (int): Random seed so results are reproducible.

    Returns:
        pd.Series: Time-indexed attendance series with 2 entries per week.
    """
    np.random.seed(seed)

    # --- Saturday Breakfast Gatherings ---
    sat_dates = pd.date_range(start="2023-01-07", periods=n_weeks, freq="W-SAT")
    sat_base = 100
    sat_seasonal = 15 * np.sin(np.linspace(0, 4 * np.pi, n_weeks))  # slow wave
    sat_trend = np.linspace(0, 12, n_weeks)                          # gentle growth
    sat_noise = np.random.normal(0, 6, n_weeks)                      # small noise
    sat_attendance = sat_base + sat_seasonal + sat_trend + sat_noise
    sat_attendance = pd.Series(sat_attendance, index=sat_dates)

    # --- Sunday Masses ---
    sun_dates = pd.date_range(start="2023-01-08", periods=n_weeks, freq="W-SUN")
    sun_base = 130
    sun_seasonal = 18 * np.sin(np.linspace(0, 4 * np.pi, n_weeks))
    sun_trend = np.linspace(0, 15, n_weeks)
    sun_noise = np.random.normal(0, 6, n_weeks)
    sun_attendance = sun_base + sun_seasonal + sun_trend + sun_noise
    sun_attendance = pd.Series(sun_attendance, index=sun_dates)

    # --- Combine both into one time series, sorted by date ---
    combined = pd.concat([sat_attendance, sun_attendance]).sort_index()

    # --- Smooth using rolling average (window=4) ---
    # This is the key fix for the spiky problem your friend noticed.
    # Each point becomes the average of itself and 3 neighbors,
    # so the line flows smoothly instead of jumping around.
    combined = combined.rolling(window=4, min_periods=1).mean()

    # Floor at 50 (minimum realistic attendance), cap at 300
    combined = combined.clip(lower=50, upper=300).round().astype(int)
    combined.index.name = "event_date"
    combined.name = "attendance"

    return combined


# =============================================================================
# STEP 2: STATIONARITY CHECK
# -----------------------------------------------------------------------------
# WHAT IS STATIONARITY?
#   A time series is "stationary" when its statistical properties (mean,
#   variance) don't change over time. ARIMA needs this to work properly.
#
# HOW WE CHECK IT:
#   We use the Augmented Dickey-Fuller (ADF) test. It gives us a p-value:
#   - p <= 0.05 → stationary → ARIMA can use it as-is (d=0 or d=1)
#   - p > 0.05  → NOT stationary → we need to "difference" the data first
#
# WHAT IS DIFFERENCING?
#   Instead of using the raw attendance values, we use the CHANGE between
#   consecutive values (e.g., week2 - week1). This removes trends and
#   makes the series stationary. The "d" in ARIMA(p,d,q) controls this.
# =============================================================================

def check_stationarity(series):
    """
    Runs the ADF test and reports whether the series is stationary.

    Parameters:
        series (pd.Series): Attendance time series.

    Returns:
        bool: True if stationary, False if not.
    """
    result = adfuller(series.dropna())
    p_value = result[1]

    print(f"\n[STEP 2: Stationarity Check]")
    print(f"  ADF Statistic : {result[0]:.4f}")
    print(f"  p-value       : {p_value:.4f}")

    if p_value <= 0.05:
        print("  Result        : STATIONARY ✓ (p <= 0.05)")
        print("  Meaning       : The data has stable patterns — ARIMA can model it directly.")
    else:
        print("  Result        : NOT stationary (p > 0.05)")
        print("  Meaning       : Differencing needed — ARIMA will handle this via d parameter.")

    return p_value <= 0.05


# =============================================================================
# STEP 3: TRAIN THE ARIMA MODEL
# -----------------------------------------------------------------------------
# WHAT IS ARIMA?
#   ARIMA stands for AutoRegressive Integrated Moving Average.
#   It has 3 parameters written as ARIMA(p, d, q):
#
#   p = AutoRegressive order
#       How many PAST ATTENDANCE VALUES the model looks back at to predict
#       the next one. p=3 means: "use the last 3 events to predict the next."
#
#   d = Differencing order
#       How many times we subtract consecutive values to make data stationary.
#       d=1 means: use (this week - last week) instead of raw values.
#       This removes long-term upward/downward drift from the data.
#
#   q = Moving Average order
#       How many PAST FORECAST ERRORS the model uses to self-correct.
#       q=2 means: "look at the last 2 prediction mistakes and adjust."
#
# WHY ARIMA(3, 1, 2)?
#   - p=3: Good for weekly data where the last few events strongly predict
#          the next one (e.g., if last 3 Saturdays were well-attended,
#          next Saturday likely will be too).
#   - d=1: One round of differencing removes the gentle upward trend
#          in the data so ARIMA sees stable patterns.
#   - q=2: Two error terms help the model recover quickly from
#          unexpected dips or spikes (like a rainy Sunday with low turnout).
#
# ARE THESE VALUES FIXED?
#   No — p, d, q are tunable. If your adviser wants, we can add auto_arima
#   later to automatically find the best values from the data itself.
#   For now, (3,1,2) is a solid, well-justified choice for this use case.
# =============================================================================

def train_arima(series, order=(3, 1, 2)):
    """
    Trains an ARIMA model on the combined attendance time series.

    Parameters:
        series (pd.Series): The attendance time series.
        order (tuple): ARIMA (p, d, q) parameters.

    Returns:
        Fitted ARIMA model result object.
    """
    print(f"\n[STEP 3: Model Training]")
    print(f"  ARIMA Order   : p={order[0]}, d={order[1]}, q={order[2]}")
    print(f"  Training on   : {len(series)} data points ({len(series)//2} weeks)")
    print(f"  Training...")

    model = ARIMA(series, order=order)
    result = model.fit()

    # AIC and BIC are model quality scores — lower is better.
    # They penalize complexity so we don't overfit.
    print(f"  AIC  : {result.aic:.2f}  (lower = better fit)")
    print(f"  BIC  : {result.bic:.2f}  (lower = better fit)")
    print(f"  Model trained successfully ✓")

    return result


# =============================================================================
# STEP 4: FORECAST NEXT 12 DATA POINTS (6 WEEKS = 12 EVENTS)
# -----------------------------------------------------------------------------
# Since we have 2 events per week (Saturday + Sunday), forecasting
# "6 weeks ahead" means forecasting 12 data points.
#
# WHAT IS A CONFIDENCE INTERVAL?
#   The model gives us a predicted value AND a range it's confident in.
#   - Lower bound: attendance probably won't go below this
#   - Upper bound: attendance probably won't go above this
#   - The wider the range, the more uncertain the model is
#     (normal for forecasts further into the future)
# =============================================================================

def forecast_attendance(model_result, steps=12):
    """
    Forecasts attendance for the next N events (12 = 6 weeks x 2 events).

    Parameters:
        model_result: Fitted ARIMA model result.
        steps (int): Number of future events to forecast.

    Returns:
        tuple: (forecast_df, forecast_mean, conf_int)
    """
    print(f"\n[STEP 4: Forecasting]")
    print(f"  Forecasting next {steps} events ({steps//2} weeks)...")

    forecast = model_result.get_forecast(steps=steps)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()

    # Label each event as Saturday Breakfast or Sunday Mass
    event_labels = []
    for i in range(steps):
        event_labels.append("Saturday Breakfast" if i % 2 == 0 else "Sunday Mass")

    # Generate forecast dates continuing from the last event date
    last_date = model_result.model.endog  # used to derive last index
    # Build future dates: alternate Saturday then Sunday, 2 per week
    future_dates = []
    # Find the last date in the training series
    last_train_date = model_result.data.dates[-1] if model_result.data.dates is not None else pd.Timestamp("2024-12-29")
    current = pd.Timestamp(last_train_date)
    for i in range(steps):
        current += pd.Timedelta(days=1)
        while current.weekday() not in (5, 6):  # 5=Saturday, 6=Sunday
            current += pd.Timedelta(days=1)
        future_dates.append(current)

    forecast_df = pd.DataFrame({
        "event_date"           : [d.strftime("%Y-%m-%d") for d in future_dates],
        "event_type"           : event_labels,
        "predicted_attendance" : forecast_mean.values.astype(int),
        "lower_bound"          : conf_int.iloc[:, 0].values.astype(int),
        "upper_bound"          : conf_int.iloc[:, 1].values.astype(int),
    })

    forecast_df["predicted_attendance"] = forecast_df["predicted_attendance"].clip(lower=0)
    forecast_df["lower_bound"] = forecast_df["lower_bound"].clip(lower=0)
    forecast_df["upper_bound"] = forecast_df["upper_bound"].clip(lower=0)

    return forecast_df, forecast_mean, conf_int


# =============================================================================
# STEP 5: GENERATE RECOMMENDATIONS
# -----------------------------------------------------------------------------
# Thresholds are split by event type since Saturday Breakfast naturally
# has lower attendance than Sunday Mass. This makes recommendations
# more accurate and fair for each event type.
# =============================================================================

def generate_recommendations(forecast_df):
    """
    Generates planning recommendations per event based on predicted attendance.

    Parameters:
        forecast_df (pd.DataFrame): Forecast table from forecast_attendance().

    Returns:
        pd.DataFrame: Forecast table with recommendation column added.
    """

    def recommend(row):
        count = row["predicted_attendance"]
        etype = row["event_type"]

        # Saturday Breakfast thresholds (lower base attendance)
        if etype == "Saturday Breakfast":
            if count < 70:
                return "LOW — Minimal setup. Prepare food for ~60. Send reminders to boost turnout."
            elif count < 100:
                return "MODERATE — Standard setup. Prepare food for ~90, basic AV."
            elif count < 130:
                return "GOOD — Full setup. Food for ~110, full AV, confirm venue."
            else:
                return "HIGH — Scale up. Extra food, seating, and volunteers needed."

        # Sunday Mass thresholds (higher base attendance)
        else:
            if count < 90:
                return "LOW — Minimal setup. Prepare food for ~80. Investigate low turnout."
            elif count < 120:
                return "MODERATE — Standard setup. Food for ~110, standard AV."
            elif count < 160:
                return "GOOD — Full setup. Food for ~140, full AV, confirm venue layout."
            else:
                return "HIGH — Scale up significantly. Extra food, seating, overflow area needed."

    forecast_df["recommendation"] = forecast_df.apply(recommend, axis=1)
    return forecast_df


# =============================================================================
# STEP 6: VISUALIZE
# -----------------------------------------------------------------------------
# We plot the last 8 weeks of history (16 data points) alongside the
# 6-week forecast so the chart stays clean and readable.
# The shaded area shows the confidence interval — how wide the model's
# uncertainty is. Wider = less certain (normal for further-out forecasts).
# =============================================================================

def plot_forecast(series, forecast_mean, conf_int):
    """
    Plots historical attendance and the ARIMA forecast with confidence interval.

    Parameters:
        series (pd.Series): Full historical attendance series.
        forecast_mean (pd.Series): Forecasted values.
        conf_int (pd.DataFrame): Confidence intervals.
    """
    # Build future dates for plotting
    future_dates = []
    last_train_date = series.index[-1]
    current = pd.Timestamp(last_train_date)
    for i in range(12):
        current += pd.Timedelta(days=1)
        while current.weekday() not in (5, 6):
            current += pd.Timedelta(days=1)
        future_dates.append(current)
    future_dates = pd.DatetimeIndex(future_dates)

    fig, ax = plt.subplots(figsize=(15, 6))

    history_window = series[-16:]
    ax.plot(history_window.index, history_window.values,
            label="Historical Attendance", color="#2c7bb6",
            linewidth=2, marker="o", markersize=4)

    ax.plot(future_dates, forecast_mean.values,
            label="Forecasted Attendance", color="#d7191c",
            linewidth=2, linestyle="--", marker="o", markersize=6)

    ax.fill_between(
        future_dates,
        conf_int.iloc[:, 0].values,
        conf_int.iloc[:, 1].values,
        color="#d7191c", alpha=0.15,
        label="95% Confidence Interval"
    )

    ax.axvline(x=series.index[-1], color="gray",
               linestyle=":", linewidth=1.5, label="Forecast Start")

    ax.set_title(
        "CHAMPS — BCBP Lipa Attendance Forecast\n"
        "Saturday Breakfast + Sunday Mass | Next 6 Weeks",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Event Date", fontsize=11)
    ax.set_ylabel("Attendance Count", fontsize=11)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("champs_forecast_v2.png", dpi=150)
    print("\n  Chart saved as: champs_forecast_v2.png ✓")
    plt.show()


# =============================================================================
# MAIN — RUN FULL PIPELINE
# =============================================================================

def main():
    print("=" * 65)
    print("  CHAMPS — Attendance Forecasting Pipeline v2")
    print("  BCBP Lipa Chapter | Saturday + Sunday | 2-Year Training Data")
    print("=" * 65)

    # --- Step 1: Load Data ---
    # ---------------------------------------------------------------
    # DATABASE SWAP POINT:
    # Replace generate_dummy_data() with load_from_database() here
    # once your MySQL/Flask setup is ready. Nothing else changes.
    # ---------------------------------------------------------------
    print("\n[STEP 1: Data Loading]")
    series = generate_dummy_data(n_weeks=104)
    sat_count = len([d for d in series.index if d.weekday() == 5])
    sun_count = len([d for d in series.index if d.weekday() == 6])
    print(f"  Total events    : {len(series)} ({sat_count} Saturdays, {sun_count} Sundays)")
    print(f"  Date range      : {series.index[0].date()} → {series.index[-1].date()}")
    print(f"  Avg attendance  : {series.mean():.1f}")
    print(f"  Min / Max       : {series.min()} / {series.max()}")

    # --- Step 2: Stationarity ---
    check_stationarity(series)

    # --- Step 3: Train ---
    model_result = train_arima(series, order=(3, 1, 2))

    # --- Step 4: Forecast (12 points = 6 weeks x 2 events) ---
    forecast_df, forecast_mean, conf_int = forecast_attendance(model_result, steps=12)

    # --- Step 5: Recommendations ---
    forecast_df = generate_recommendations(forecast_df)

    # --- Step 6: Print Results ---
    print("\n" + "=" * 65)
    print("  FORECAST RESULTS — Next 6 Weeks (Saturday + Sunday)")
    print("=" * 65)

    current_week = None
    week_num = 0
    for _, row in forecast_df.iterrows():
        # Group output by week
        week_label = row["event_date"][:8]  # year-month
        if week_label != current_week:
            week_num += 1
            current_week = week_label
            print(f"\n  ── Week {week_num} ──────────────────────────────────────")

        icon = "🍳" if row["event_type"] == "Saturday Breakfast" else "⛪"
        print(f"\n  {icon} {row['event_type']} | {row['event_date']}")
        print(f"     Predicted  : {row['predicted_attendance']} attendees")
        print(f"     Range      : {row['lower_bound']} – {row['upper_bound']}")
        print(f"     Advice     : {row['recommendation']}")

    # --- Step 7: Save CSV ---
    forecast_df.to_csv("champs_forecast_v2.csv", index=False)
    print(f"\n  Forecast saved to: champs_forecast_v2.csv ✓")

    # --- Step 8: Plot ---
    plot_forecast(series, forecast_mean, conf_int)

    print("\n" + "=" * 65)
    print("  Pipeline complete.")
    print("=" * 65)


if __name__ == "__main__":
    main()
