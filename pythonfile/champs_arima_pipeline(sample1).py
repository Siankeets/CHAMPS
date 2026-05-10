# =============================================================================
# CHAMPS - Event Attendance Forecasting Pipeline
# Model: ARIMA (AutoRegressive Integrated Moving Average)
# Description: Generates dummy weekly attendance data, trains an ARIMA model,
#              forecasts the next 6 events, and outputs recommendations.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings("ignore")

# =============================================================================
# STEP 1: GENERATE DUMMY ATTENDANCE DATA
# Simulates 2 years (104 weeks) of weekly BCBP Lipa event attendance.
# Attendance is based on a realistic range with seasonal variation and noise.
# =============================================================================

def generate_dummy_data(n_weeks=104, seed=42):
    """
    Generates synthetic weekly attendance data for BCBP Lipa Chapter events.

    Parameters:
        n_weeks (int): Number of weeks to simulate.
        seed (int): Random seed for reproducibility.

    Returns:
        pd.Series: Time-indexed attendance series.
    """
    np.random.seed(seed)

    # Date range: weekly events starting Jan 2023
    dates = pd.date_range(start="2023-01-07", periods=n_weeks, freq="W")

    # Base attendance around 120 members (realistic for BCBP chapter)
    base = 120

    # Seasonal component: higher attendance mid-year and year-end (retreats, AGMs)
    seasonal = 20 * np.sin(np.linspace(0, 4 * np.pi, n_weeks))

    # Slight upward trend over time (growing membership)
    trend = np.linspace(0, 15, n_weeks)

    # Random noise to simulate real-world variation
    noise = np.random.normal(0, 10, n_weeks)

    # Combine all components, floor at 50 (minimum realistic attendance)
    attendance = (base + seasonal + trend + noise).astype(int)
    attendance = np.clip(attendance, 50, 300)

    series = pd.Series(attendance, index=dates, name="attendance")
    return series


# =============================================================================
# STEP 2: STATIONARITY CHECK (ADF Test)
# ARIMA requires the series to be stationary. We check and difference if needed.
# =============================================================================

def check_stationarity(series):
    """
    Runs the Augmented Dickey-Fuller test to check if the series is stationary.

    Parameters:
        series (pd.Series): The time series to test.

    Returns:
        bool: True if stationary, False otherwise.
    """
    result = adfuller(series.dropna())
    p_value = result[1]
    print(f"\n[Stationarity Check]")
    print(f"  ADF Statistic : {result[0]:.4f}")
    print(f"  p-value       : {p_value:.4f}")

    if p_value <= 0.05:
        print("  Result        : Series is STATIONARY (p <= 0.05) ✓")
        return True
    else:
        print("  Result        : Series is NOT stationary (p > 0.05), differencing needed.")
        return False


# =============================================================================
# STEP 3: TRAIN ARIMA MODEL
# ARIMA(p, d, q) parameters:
#   p = autoregressive order (how many past values to use)
#   d = differencing order (how many times to difference for stationarity)
#   q = moving average order (how many past errors to use)
#
# We use ARIMA(2, 1, 2) as a solid general-purpose starting point for
# weekly attendance data. This can be tuned later with auto_arima if needed.
# =============================================================================

def train_arima(series, order=(2, 1, 2)):
    """
    Trains an ARIMA model on the attendance time series.

    Parameters:
        series (pd.Series): The attendance time series.
        order (tuple): The (p, d, q) order for ARIMA.

    Returns:
        Fitted ARIMA model result object.
    """
    print(f"\n[Model Training]")
    print(f"  Training ARIMA{order} on {len(series)} weeks of data...")

    model = ARIMA(series, order=order, freq="W")
    result = model.fit()

    print(f"  AIC  : {result.aic:.2f}")
    print(f"  BIC  : {result.bic:.2f}")
    print("  Model trained successfully ✓")
    return result


# =============================================================================
# STEP 4: FORECAST NEXT 6 EVENTS
# =============================================================================

def forecast_attendance(model_result, steps=6):
    """
    Forecasts attendance for the next N events using the trained ARIMA model.

    Parameters:
        model_result: Fitted ARIMA model result.
        steps (int): Number of future events to forecast.

    Returns:
        pd.DataFrame: Forecast table with dates, predicted attendance,
                      and confidence intervals.
    """
    print(f"\n[Forecasting]")
    print(f"  Generating forecast for next {steps} events...")

    forecast = model_result.get_forecast(steps=steps)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()

    forecast_df = pd.DataFrame({
        "event_date"        : forecast_mean.index.strftime("%Y-%m-%d"),
        "predicted_attendance": forecast_mean.values.astype(int),
        "lower_bound"       : conf_int.iloc[:, 0].values.astype(int),
        "upper_bound"       : conf_int.iloc[:, 1].values.astype(int),
    })

    # Floor values at 0 (attendance can't be negative)
    forecast_df["predicted_attendance"] = forecast_df["predicted_attendance"].clip(lower=0)
    forecast_df["lower_bound"] = forecast_df["lower_bound"].clip(lower=0)
    forecast_df["upper_bound"] = forecast_df["upper_bound"].clip(lower=0)

    return forecast_df, forecast_mean, conf_int


# =============================================================================
# STEP 5: GENERATE RECOMMENDATIONS
# Based on forecasted attendance, output actionable planning recommendations.
# =============================================================================

def generate_recommendations(forecast_df):
    """
    Generates event planning recommendations based on forecasted attendance.

    Thresholds (calibrated for ~120 member BCBP chapter):
        < 80   : Low attendance — minimal setup needed
        80-119 : Moderate — standard setup
        120-159: Good — prepare full setup
        >= 160 : High — scale up resources significantly

    Parameters:
        forecast_df (pd.DataFrame): Output of forecast_attendance().

    Returns:
        pd.DataFrame: Forecast table with added recommendation column.
    """
    def recommend(count):
        if count < 80:
            return (
                "LOW attendance expected. "
                "Minimal food/chairs needed. "
                "Consider boosting member engagement before this event."
            )
        elif count < 120:
            return (
                "MODERATE attendance expected. "
                "Prepare standard setup (food for ~100, standard AV). "
                "Send reminders to increase turnout."
            )
        elif count < 160:
            return (
                "GOOD attendance expected. "
                "Prepare full chapter setup (food for ~130, full AV). "
                "Confirm venue capacity and logistics."
            )
        else:
            return (
                "HIGH attendance expected. "
                "Scale up food, seating, and AV equipment. "
                "Consider overflow arrangements and extra volunteers."
            )

    forecast_df["recommendation"] = forecast_df["predicted_attendance"].apply(recommend)
    return forecast_df


# =============================================================================
# STEP 6: VISUALIZE RESULTS
# Plots historical attendance + 6-week forecast with confidence interval.
# =============================================================================

def plot_forecast(series, forecast_mean, conf_int, steps=6):
    """
    Plots the historical attendance data alongside the ARIMA forecast.

    Parameters:
        series (pd.Series): Historical attendance data.
        forecast_mean (pd.Series): Forecasted attendance values.
        conf_int (pd.DataFrame): Confidence intervals for the forecast.
        steps (int): Number of forecasted steps.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    # Plot last 30 weeks of history for clarity
    history_window = series[-30:]
    ax.plot(history_window.index, history_window.values,
            label="Historical Attendance", color="#2c7bb6", linewidth=2)

    # Plot forecast
    ax.plot(forecast_mean.index, forecast_mean.values,
            label="Forecasted Attendance", color="#d7191c",
            linewidth=2, linestyle="--", marker="o", markersize=6)

    # Confidence interval shading
    ax.fill_between(
        conf_int.index,
        conf_int.iloc[:, 0],
        conf_int.iloc[:, 1],
        color="#d7191c", alpha=0.15,
        label="95% Confidence Interval"
    )

    # Vertical line separating history from forecast
    ax.axvline(x=series.index[-1], color="gray", linestyle=":", linewidth=1.5,
               label="Forecast Start")

    ax.set_title("CHAMPS — BCBP Lipa Event Attendance Forecast (Next 6 Weeks)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Event Date", fontsize=11)
    ax.set_ylabel("Attendance Count", fontsize=11)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("champs_attendance_forecast.png", dpi=150)
    print("\n  Chart saved as: champs_attendance_forecast.png ✓")
    plt.show()


# =============================================================================
# MAIN — RUN THE FULL PIPELINE
# =============================================================================

def main():
    print("=" * 60)
    print("  CHAMPS — Attendance Forecasting Pipeline (ARIMA)")
    print("  BCBP Lipa Chapter | Weekly Events")
    print("=" * 60)

    # --- Step 1: Generate Data ---
    print("\n[Data Generation]")
    attendance_series = generate_dummy_data(n_weeks=104)
    print(f"  Generated {len(attendance_series)} weeks of dummy attendance data.")
    print(f"  Date range  : {attendance_series.index[0].date()} → {attendance_series.index[-1].date()}")
    print(f"  Avg. attendance : {attendance_series.mean():.1f}")
    print(f"  Min / Max       : {attendance_series.min()} / {attendance_series.max()}")

    # --- Step 2: Stationarity Check ---
    check_stationarity(attendance_series)

    # --- Step 3: Train ARIMA ---
    model_result = train_arima(attendance_series, order=(2, 1, 2))

    # --- Step 4: Forecast ---
    forecast_df, forecast_mean, conf_int = forecast_attendance(model_result, steps=6)

    # --- Step 5: Recommendations ---
    forecast_df = generate_recommendations(forecast_df)

    # --- Step 6: Print Results ---
    print("\n" + "=" * 60)
    print("  FORECAST RESULTS — Next 6 Events")
    print("=" * 60)
    for _, row in forecast_df.iterrows():
        print(f"\n  📅 Event Date : {row['event_date']}")
        print(f"     Predicted  : {row['predicted_attendance']} attendees")
        print(f"     Range      : {row['lower_bound']} – {row['upper_bound']}")
        print(f"     Advice     : {row['recommendation']}")

    # --- Step 7: Save to CSV ---
    forecast_df.to_csv("champs_forecast_output.csv", index=False)
    print(f"\n  Forecast saved to: champs_forecast_output.csv ✓")

    # --- Step 8: Plot ---
    plot_forecast(attendance_series, forecast_mean, conf_int, steps=6)

    print("\n" + "=" * 60)
    print("  Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
