# =============================================================================
# CHAMPS - Event Attendance Forecasting Pipeline v3
# Model: ARIMA (AutoRegressive Integrated Moving Average)
#
# What changed from v2:
#   - More realistic dummy data (random event cancellations, holiday spikes,
#     rainy day dips, special events — things that actually happen in BCBP)
#   - Train/Test Split: model is validated before being trusted to forecast
#   - MAE and RMSE metrics so you can report model accuracy to your adviser
#   - Model retrains on full dataset after validation for best forecast
#   - Database swap point preserved from v2
#
# WHY REALISTIC DATA MATTERS:
#   If the training data is too smooth/perfect, the model learns a pattern
#   that doesn't exist in real life. When real messy data comes in later
#   (from your actual DB), the model performs poorly because it was never
#   trained to handle variation. More realistic dummy data = more honest
#   model performance = more trustworthy results.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")


# =============================================================================
# STEP 1: GENERATE REALISTIC DUMMY DATA
# -----------------------------------------------------------------------------
# What makes this more realistic than v2:
#
#   1. HIGHER NOISE (std=12)
#      Real attendance doesn't move in smooth waves. People get sick,
#      traffic is bad, it rains — noise of 12 captures that day-to-day
#      unpredictability better than std=6.
#
#   2. HOLIDAY / SPECIAL EVENT SPIKES
#      Christmas season, Holy Week, and BCBP anniversaries bring unusually
#      high attendance. We randomly inject these a few times per year.
#
#   3. LOW TURNOUT EVENTS (random cancellations/conflicts)
#      Some events clash with local fiestas, school events, or bad weather.
#      We randomly drop attendance significantly a few times per year.
#
#   4. LIGHTER SMOOTHING (window=2 instead of 4)
#      We still smooth slightly to avoid pure noise, but use a smaller
#      window so natural variation is preserved in the data.
#
#   5. SATURDAY vs SUNDAY DIFFERENCE PRESERVED
#      Saturday Breakfast still runs lower than Sunday Mass, consistent
#      with real BCBP chapter patterns.
#
# DATABASE SWAP POINT:
#   Replace this entire function with a DB query when ready:
#
#   def load_from_database():
#       import mysql.connector
#       conn = mysql.connector.connect(
#           host="localhost", user="root",
#           password="", database="champs_db"
#       )
#       query = """
#           SELECT p.program_date,
#                  p.program_type,
#                  COUNT(a.member_id) as attendance
#           FROM programs p
#           LEFT JOIN attendance a
#               ON p.program_id = a.program_id
#               AND a.attendance_status = 'Attended'
#           GROUP BY p.program_date, p.program_type
#           ORDER BY p.program_date ASC
#       """
#       df = pd.read_sql(query, conn)
#       df['program_date'] = pd.to_datetime(df['program_date'])
#       df = df.set_index('program_date')['attendance']
#       conn.close()
#       return df
# =============================================================================

def generate_dummy_data(n_weeks=104, seed=42):
    """
    Generates 2 years of realistic attendance data for BCBP Lipa.
    Two events per week: Saturday Breakfast + Sunday Mass.
    Includes natural variation, holiday spikes, and low-turnout events.

    Parameters:
        n_weeks (int): Weeks to simulate (104 = 2 years).
        seed (int): Random seed for reproducibility.

    Returns:
        pd.Series: Time-indexed attendance series (208 data points).
    """
    np.random.seed(seed)

    # -------------------------------------------------------------------------
    # Saturday Breakfast (base ~100 attendees)
    # -------------------------------------------------------------------------
    sat_dates = pd.date_range(start="2023-01-07", periods=n_weeks, freq="W-SAT")
    sat_base = 100
    sat_seasonal = 15 * np.sin(np.linspace(0, 4 * np.pi, n_weeks))
    sat_trend = np.linspace(0, 12, n_weeks)
    sat_noise = np.random.normal(0, 12, n_weeks)   # higher noise = more realistic
    sat_attendance = sat_base + sat_seasonal + sat_trend + sat_noise

    # -------------------------------------------------------------------------
    # Sunday Mass (base ~130 attendees)
    # -------------------------------------------------------------------------
    sun_dates = pd.date_range(start="2023-01-08", periods=n_weeks, freq="W-SUN")
    sun_base = 130
    sun_seasonal = 18 * np.sin(np.linspace(0, 4 * np.pi, n_weeks))
    sun_trend = np.linspace(0, 15, n_weeks)
    sun_noise = np.random.normal(0, 12, n_weeks)
    sun_attendance = sun_base + sun_seasonal + sun_trend + sun_noise

    # -------------------------------------------------------------------------
    # Inject Holiday / Special Event Spikes
    # These simulate Christmas gatherings, Holy Week retreats, BCBP
    # anniversaries, and regional assemblies where attendance surges.
    # We pick ~6 random weeks per year and add a +30 to +60 attendance boost.
    # -------------------------------------------------------------------------
    spike_weeks = np.random.choice(n_weeks, size=12, replace=False)
    for w in spike_weeks:
        boost = np.random.randint(30, 60)
        sat_attendance[w] += boost
        sun_attendance[w] += boost

    # -------------------------------------------------------------------------
    # Inject Low Turnout Events
    # These simulate bad weather, local fiesta conflicts, or schedule clashes.
    # We pick ~4 random weeks per year and subtract -20 to -45 from attendance.
    # -------------------------------------------------------------------------
    dip_weeks = np.random.choice(
        [w for w in range(n_weeks) if w not in spike_weeks],
        size=8, replace=False
    )
    for w in dip_weeks:
        drop = np.random.randint(20, 45)
        sat_attendance[w] -= drop
        sun_attendance[w] -= drop

    # -------------------------------------------------------------------------
    # Combine into one time series
    # -------------------------------------------------------------------------
    sat_series = pd.Series(sat_attendance, index=sat_dates)
    sun_series = pd.Series(sun_attendance, index=sun_dates)
    combined = pd.concat([sat_series, sun_series]).sort_index()

    # Light smoothing (window=2) — preserves variation but removes extreme
    # single-day outliers that would confuse the model
    combined = combined.rolling(window=2, min_periods=1).mean()

    # Clip to realistic bounds and round to whole numbers
    combined = combined.clip(lower=50, upper=300).round().astype(int)
    combined.index.name = "event_date"
    combined.name = "attendance"

    return combined


# =============================================================================
# STEP 2: STATIONARITY CHECK (ADF Test)
# -----------------------------------------------------------------------------
# Same as v2 — checks if the series is ready for ARIMA.
# p <= 0.05 = stationary = good to go.
# p > 0.05  = needs differencing (handled by d parameter in ARIMA).
# =============================================================================

def check_stationarity(series):
    """
    Runs the Augmented Dickey-Fuller test for stationarity.

    Parameters:
        series (pd.Series): Attendance time series.

    Returns:
        bool: True if stationary.
    """
    result = adfuller(series.dropna())
    p_value = result[1]

    print(f"\n[STEP 2: Stationarity Check]")
    print(f"  ADF Statistic : {result[0]:.4f}")
    print(f"  p-value       : {p_value:.4f}")

    if p_value <= 0.05:
        print("  Result        : STATIONARY ✓ (p <= 0.05)")
        print("  Meaning       : Stable patterns detected — ARIMA can model directly.")
    else:
        print("  Result        : NOT stationary — differencing will be applied (d=1).")

    return p_value <= 0.05


# =============================================================================
# STEP 3: TRAIN ARIMA MODEL
# -----------------------------------------------------------------------------
# ARIMA(p, d, q) — same logic as v2, using (3, 1, 2):
#   p=3 : Use last 3 events to predict next
#   d=1 : Difference once to remove trend
#   q=2 : Self-correct using last 2 forecast errors
# =============================================================================

def train_arima(series, order=(3, 1, 2)):
    """
    Trains an ARIMA model on the given attendance series.

    Parameters:
        series (pd.Series): Attendance series (can be train split or full).
        order (tuple): ARIMA (p, d, q) parameters.

    Returns:
        Fitted ARIMA model result object.
    """
    model = ARIMA(series, order=order)
    result = model.fit()
    return result


# =============================================================================
# STEP 4: TRAIN/TEST SPLIT + VALIDATION
# -----------------------------------------------------------------------------
# WHY DO WE SPLIT THE DATA?
#   We can't just train the model on everything and call it accurate —
#   that's like studying the answer key before an exam. The model would
#   look great on data it already saw, but fail on new data.
#
#   Instead, we:
#   1. Train on 80% of data (first ~166 events / ~83 weeks)
#   2. Test on the remaining 20% (last ~42 events / ~21 weeks)
#   3. Compare what the model predicted vs what actually happened
#
# WHY 21 WEEKS FOR TESTING?
#   We use the last 42 data points (21 weeks x 2 events) as the test set.
#   This is ~20% of 208 total events, which is a standard split ratio.
#
# WHAT ARE MAE AND RMSE?
#   These measure how wrong the model's predictions are on average:
#
#   MAE (Mean Absolute Error):
#     Average of absolute differences between predicted and actual values.
#     Example: MAE=8 means predictions are off by ~8 attendees on average.
#     Easy to explain to non-technical people (your panel).
#
#   RMSE (Root Mean Squared Error):
#     Similar to MAE but penalizes large errors more heavily.
#     Example: RMSE=12 means large prediction errors exist occasionally.
#     Lower RMSE = model handles outliers (spikes/dips) better.
#
#   GOOD VALUES FOR YOUR DATA (~100-145 avg attendance):
#     MAE  < 15  = acceptable
#     MAE  < 10  = good
#     RMSE < 20  = acceptable
#     RMSE < 15  = good
# =============================================================================

def train_test_validate(series, test_weeks=21, order=(3, 1, 2)):
    """
    Splits data into train/test, trains ARIMA on train set,
    forecasts test period, and computes MAE and RMSE.

    Parameters:
        series (pd.Series): Full attendance time series.
        test_weeks (int): Number of weeks to reserve for testing.
        order (tuple): ARIMA (p, d, q) parameters.

    Returns:
        tuple: (mae, rmse, test_series, test_forecast_values)
    """
    test_points = test_weeks * 2          # 2 events per week
    train_series = series[:-test_points]
    test_series = series[-test_points:]

    print(f"\n[STEP 3: Train/Test Split]")
    print(f"  Total events   : {len(series)}")
    print(f"  Training set   : {len(train_series)} events ({len(train_series)//2} weeks)")
    print(f"  Testing set    : {len(test_series)} events ({len(test_series)//2} weeks)")

    # Train on training set only
    print(f"\n[STEP 4: Training ARIMA{order} on training set...]")
    train_model = train_arima(train_series, order=order)
    print(f"  AIC : {train_model.aic:.2f}")
    print(f"  BIC : {train_model.bic:.2f}")

    # Forecast the test period
    test_forecast = train_model.forecast(steps=len(test_series))

    # Compute error metrics
    mae  = mean_absolute_error(test_series.values, test_forecast.values)
    rmse = np.sqrt(mean_squared_error(test_series.values, test_forecast.values))

    print(f"\n[STEP 5: Model Validation on Test Set]")
    print(f"  MAE  : {mae:.2f}  (avg prediction error in attendees)")
    print(f"  RMSE : {rmse:.2f}  (penalizes larger errors more)")

    if mae < 10:
        print(f"  MAE Rating  : GOOD ✓")
    elif mae < 15:
        print(f"  MAE Rating  : ACCEPTABLE ✓")
    else:
        print(f"  MAE Rating  : NEEDS IMPROVEMENT — consider tuning p/d/q")

    if rmse < 15:
        print(f"  RMSE Rating : GOOD ✓")
    elif rmse < 20:
        print(f"  RMSE Rating : ACCEPTABLE ✓")
    else:
        print(f"  RMSE Rating : NEEDS IMPROVEMENT")

    return mae, rmse, test_series, test_forecast


# =============================================================================
# STEP 5: FORECAST NEXT 12 DATA POINTS (6 WEEKS = 12 EVENTS)
# -----------------------------------------------------------------------------
# After validation, we retrain the model on the FULL dataset (all 208 events)
# before forecasting future events. This gives the model as much historical
# context as possible for the most accurate forecast.
# =============================================================================

def forecast_attendance(model_result, last_date, steps=12):
    """
    Forecasts attendance for the next N events using the trained ARIMA model.

    Parameters:
        model_result : Fitted ARIMA model result (trained on full dataset).
        last_date    : Last date in the training series (for date generation).
        steps (int)  : Number of future events to forecast (12 = 6 weeks).

    Returns:
        tuple: (forecast_df, forecast_mean, conf_int)
    """
    forecast = model_result.get_forecast(steps=steps)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()

    # Generate future Saturday/Sunday dates
    future_dates = []
    current = pd.Timestamp(last_date)
    for i in range(steps):
        current += pd.Timedelta(days=1)
        while current.weekday() not in (5, 6):  # 5=Sat, 6=Sun
            current += pd.Timedelta(days=1)
        future_dates.append(current)

    # Label alternating Saturday/Sunday
    event_labels = [
        "Saturday Breakfast" if d.weekday() == 5 else "Sunday Mass"
        for d in future_dates
    ]

    forecast_df = pd.DataFrame({
        "event_date"            : [d.strftime("%Y-%m-%d") for d in future_dates],
        "event_type"            : event_labels,
        "predicted_attendance"  : forecast_mean.values.astype(int),
        "lower_bound"           : conf_int.iloc[:, 0].values.astype(int),
        "upper_bound"           : conf_int.iloc[:, 1].values.astype(int),
    })

    forecast_df["predicted_attendance"] = forecast_df["predicted_attendance"].clip(lower=0)
    forecast_df["lower_bound"]          = forecast_df["lower_bound"].clip(lower=0)
    forecast_df["upper_bound"]          = forecast_df["upper_bound"].clip(lower=0)

    return forecast_df, forecast_mean, conf_int, future_dates


# =============================================================================
# STEP 6: RECOMMENDATIONS
# =============================================================================

def generate_recommendations(forecast_df):
    """
    Generates planning recommendations per event based on predicted attendance.
    Thresholds are split by event type (Saturday vs Sunday).
    """
    def recommend(row):
        count = row["predicted_attendance"]
        etype = row["event_type"]

        if etype == "Saturday Breakfast":
            if count < 70:
                return "LOW — Minimal setup. Food for ~60. Send reminders to boost turnout."
            elif count < 100:
                return "MODERATE — Standard setup. Food for ~90, basic AV."
            elif count < 130:
                return "GOOD — Full setup. Food for ~110, full AV, confirm venue."
            else:
                return "HIGH — Scale up. Extra food, seating, and volunteers needed."
        else:
            if count < 90:
                return "LOW — Minimal setup. Food for ~80. Investigate low turnout."
            elif count < 120:
                return "MODERATE — Standard setup. Food for ~110, standard AV."
            elif count < 160:
                return "GOOD — Full setup. Food for ~140, full AV, confirm venue layout."
            else:
                return "HIGH — Scale up significantly. Extra food, seating, overflow needed."

    forecast_df["recommendation"] = forecast_df.apply(recommend, axis=1)
    return forecast_df


# =============================================================================
# STEP 7: VISUALIZATION
# Plots 3 things:
#   1. Historical attendance (last 8 weeks shown for clarity)
#   2. Actual test values vs model predictions (validation window)
#   3. Future 6-week forecast with confidence interval
# =============================================================================

def plot_results(series, test_series, test_forecast,
                 forecast_mean, conf_int, future_dates):
    """
    Plots historical data, validation comparison, and future forecast.
    """
    fig, ax = plt.subplots(figsize=(16, 6))

    # Historical (last 16 points = 8 weeks)
    history = series[:-len(test_series)][-16:]
    ax.plot(history.index, history.values,
            color="#2c7bb6", linewidth=2,
            marker="o", markersize=4, label="Historical Attendance")

    # Test set: actual values
    ax.plot(test_series.index, test_series.values,
            color="#1a9641", linewidth=2,
            marker="o", markersize=4, label="Actual (Test Period)")

    # Test set: model predictions
    ax.plot(test_series.index, test_forecast.values,
            color="#f4a582", linewidth=2, linestyle="--",
            marker="x", markersize=5, label="Model Predictions (Validation)")

    # Future forecast
    future_dates_idx = pd.DatetimeIndex(future_dates)
    ax.plot(future_dates_idx, forecast_mean.values,
            color="#d7191c", linewidth=2, linestyle="--",
            marker="o", markersize=6, label="Forecast (Next 6 Weeks)")

    # Confidence interval
    ax.fill_between(
        future_dates_idx,
        conf_int.iloc[:, 0].values,
        conf_int.iloc[:, 1].values,
        color="#d7191c", alpha=0.15,
        label="95% Confidence Interval"
    )

    # Dividers
    ax.axvline(x=test_series.index[0], color="orange",
               linestyle=":", linewidth=1.5, label="Test Period Start")
    ax.axvline(x=series.index[-1], color="gray",
               linestyle=":", linewidth=1.5, label="Forecast Start")

    ax.set_title(
        "CHAMPS — BCBP Lipa Attendance Forecast v3\n"
        "Saturday Breakfast + Sunday Mass | Validation + 6-Week Forecast",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Event Date", fontsize=11)
    ax.set_ylabel("Attendance Count", fontsize=11)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("champs_forecast_v3.png", dpi=150)
    print("  Chart saved as: champs_forecast_v3.png ✓")
    plt.show()


# =============================================================================
# MAIN — FULL PIPELINE
# =============================================================================

def main():
    print("=" * 65)
    print("  CHAMPS — Attendance Forecasting Pipeline v3")
    print("  BCBP Lipa | Saturday + Sunday | Realistic Data + Validation")
    print("=" * 65)

    # ------------------------------------------------------------------
    # STEP 1: Load Data
    # DATABASE SWAP: replace generate_dummy_data() with load_from_database()
    # ------------------------------------------------------------------
    print("\n[STEP 1: Data Loading]")
    series = generate_dummy_data(n_weeks=104)
    sat_count = sum(1 for d in series.index if d.weekday() == 5)
    sun_count = sum(1 for d in series.index if d.weekday() == 6)
    print(f"  Total events    : {len(series)} ({sat_count} Saturdays, {sun_count} Sundays)")
    print(f"  Date range      : {series.index[0].date()} → {series.index[-1].date()}")
    print(f"  Avg attendance  : {series.mean():.1f}")
    print(f"  Min / Max       : {series.min()} / {series.max()}")

    # ------------------------------------------------------------------
    # STEP 2: Stationarity Check
    # ------------------------------------------------------------------
    check_stationarity(series)

    # ------------------------------------------------------------------
    # STEPS 3-5: Train/Test Split + Validation
    # ------------------------------------------------------------------
    mae, rmse, test_series, test_forecast = train_test_validate(
        series, test_weeks=21, order=(3, 1, 2)
    )

    # ------------------------------------------------------------------
    # STEP 6: Retrain on FULL dataset for best forecast
    # We validated the model above. Now we give it ALL the data so it
    # has maximum context when predicting future events.
    # ------------------------------------------------------------------
    print(f"\n[STEP 6: Retraining on Full Dataset for Forecast]")
    full_model = train_arima(series, order=(3, 1, 2))
    print(f"  AIC : {full_model.aic:.2f}")
    print(f"  BIC : {full_model.bic:.2f}")
    print(f"  Full model ready ✓")

    # ------------------------------------------------------------------
    # STEP 7: Forecast next 6 weeks (12 events)
    # ------------------------------------------------------------------
    print(f"\n[STEP 7: Forecasting Next 6 Weeks]")
    forecast_df, forecast_mean, conf_int, future_dates = forecast_attendance(
        full_model, last_date=series.index[-1], steps=12
    )

    # ------------------------------------------------------------------
    # STEP 8: Recommendations
    # ------------------------------------------------------------------
    forecast_df = generate_recommendations(forecast_df)

    # ------------------------------------------------------------------
    # STEP 9: Print Results
    # ------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("  FORECAST RESULTS — Next 6 Weeks (Saturday + Sunday)")
    print("=" * 65)

    seen_weeks = set()
    week_num = 0
    for _, row in forecast_df.iterrows():
        week_key = row["event_date"][:8]
        if week_key not in seen_weeks:
            week_num += 1
            seen_weeks.add(week_key)
            print(f"\n  ── Week {week_num} ──────────────────────────────────────")

        icon = "🍳" if row["event_type"] == "Saturday Breakfast" else "⛪"
        print(f"\n  {icon}  {row['event_type']} | {row['event_date']}")
        print(f"      Predicted  : {row['predicted_attendance']} attendees")
        print(f"      Range      : {row['lower_bound']} – {row['upper_bound']}")
        print(f"      Advice     : {row['recommendation']}")

    # ------------------------------------------------------------------
    # STEP 10: Save CSV + Plot
    # ------------------------------------------------------------------
    forecast_df.to_csv("champs_forecast_v3.csv", index=False)
    print(f"\n  Forecast saved to: champs_forecast_v3.csv ✓")

    print(f"\n[STEP 8: Generating Chart]")
    plot_results(series, test_series, test_forecast,
                 forecast_mean, conf_int, future_dates)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("  PIPELINE SUMMARY")
    print("=" * 65)
    print(f"  Training data   : {len(series)} events over 104 weeks")
    print(f"  ARIMA order     : (3, 1, 2)")
    print(f"  Validation MAE  : {mae:.2f} attendees avg error")
    print(f"  Validation RMSE : {rmse:.2f}")
    print(f"  Forecast period : Next 6 weeks (12 events)")
    print(f"  Output files    : champs_forecast_v3.csv, champs_forecast_v3.png")
    print("=" * 65)
    print("  Pipeline complete.")
    print("=" * 65)


if __name__ == "__main__":
    main()
