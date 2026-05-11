# =============================================================================
# CHAMPS - Event Attendance Forecasting Pipeline v5
# Model: ARIMA (AutoRegressive Integrated Moving Average)
#
# How it works:
#   - User is shown a numbered menu of available event types
#   - User picks one event
#   - ONLY that event's data, model, validation, and report runs
#   - Outputs: terminal report + individual CSV + chart
#
# This mirrors how it will work in Flask later:
#   Instead of a terminal menu, the user clicks an event on the web UI,
#   which sends the event name to a Flask route, which calls run_forecast().
#   Everything below run_forecast() stays exactly the same.
#
# Flask integration point (future):
#   @app.route('/forecast', methods=['POST'])
#   def forecast_route():
#       event_name = request.form.get('event_name')
#       result = run_forecast(event_name)
#       return jsonify(result)
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
# EVENT REGISTRY
# -----------------------------------------------------------------------------
# Add new event types here as BCBP Lipa grows.
# Each entry defines the attendance profile for that event.
# When connected to the database, these become query filters.
#
# DATABASE SWAP POINT (per event):
#   Replace generate_event_data() with:
#
#   def load_from_database(event_name):
#       import mysql.connector
#       conn = mysql.connector.connect(
#           host="localhost", user="root",
#           password="", database="champs_db"
#       )
#       query = """
#           SELECT p.program_date,
#                  COUNT(a.member_id) AS attendance
#           FROM programs p
#           LEFT JOIN attendance a
#               ON p.program_id = a.program_id
#               AND a.attendance_status = 'Attended'
#           WHERE p.program_type = %s
#           GROUP BY p.program_date
#           ORDER BY p.program_date ASC
#       """
#       df = pd.read_sql(query, conn, params=(event_name,))
#       df['program_date'] = pd.to_datetime(df['program_date'])
#       series = df.set_index('program_date')['attendance']
#       conn.close()
#       return series
# =============================================================================

EVENT_REGISTRY = {
    "Saturday Breakfast": {
        "description" : "Weekly breakfast gathering open to all members",
        "base"        : 120,
        "seasonal"    : 18,
        "trend"       : 12,
        "noise"       : 12,
        "spike_boost" : (25, 55),
        "dip_drop"    : (15, 40),
        "n_spikes"    : 10,
        "n_dips"      : 8,
        "weekday"     : "W-SAT",
        "start_date"  : "2023-01-07",
        "icon"        : "🍳",
        # Recommendation thresholds
        "thresholds"  : {
            "low"     : (0,   80,  "LOW — Minimal setup. Food for ~70. Send member reminders."),
            "moderate": (80,  120, "MODERATE — Standard setup. Food for ~100, basic AV."),
            "good"    : (120, 150, "GOOD — Full setup. Food for ~130, full AV, confirm venue."),
            "high"    : (150, 999, "HIGH — Scale up. Extra food, seating, and volunteers needed."),
        },
    },
    "Friday Action Group": {
        "description" : "Weekly leader/action group meetings (core members only)",
        "base"        : 45,
        "seasonal"    : 6,
        "trend"       : 5,
        "noise"       : 7,
        "spike_boost" : (8, 20),
        "dip_drop"    : (5, 15),
        "n_spikes"    : 8,
        "n_dips"      : 6,
        "weekday"     : "W-FRI",
        "start_date"  : "2023-01-06",
        "icon"        : "👥",
        "thresholds"  : {
            "low"     : (0,  30, "LOW — Minimal setup. Check leader availability and send reminders."),
            "moderate": (30, 45, "MODERATE — Standard setup. Prepare materials for ~40 leaders."),
            "good"    : (45, 60, "GOOD — Full setup. Materials and snacks for ~50 leaders."),
            "high"    : (60, 999,"HIGH — Larger than usual. Scale up room and materials."),
        },
    },
}


# =============================================================================
# TERMINAL MENU
# =============================================================================

def show_menu():
    """
    Displays a numbered list of available events and returns the user's choice.

    Returns:
        str: The selected event name (key from EVENT_REGISTRY).
    """
    event_list = list(EVENT_REGISTRY.keys())

    print("\n" + "=" * 65)
    print("  CHAMPS — Attendance Forecasting System")
    print("  BCBP Lipa Chapter")
    print("=" * 65)
    print("\n  Select an event to generate a forecast report:\n")

    for i, event_name in enumerate(event_list, 1):
        cfg = EVENT_REGISTRY[event_name]
        print(f"  [{i}] {cfg['icon']}  {event_name}")
        print(f"       {cfg['description']}\n")

    print("  [0]  ❌  Exit\n")
    print("-" * 65)

    while True:
        try:
            choice = int(input("  Enter number: ").strip())
            if choice == 0:
                print("\n  Exiting CHAMPS Forecasting System. Goodbye!")
                exit()
            elif 1 <= choice <= len(event_list):
                selected = event_list[choice - 1]
                print(f"\n  Selected: {EVENT_REGISTRY[selected]['icon']}  {selected}")
                return selected
            else:
                print(f"  ⚠  Please enter a number between 0 and {len(event_list)}.")
        except ValueError:
            print("  ⚠  Invalid input. Please enter a number.")


# =============================================================================
# DATA GENERATION
# =============================================================================

def generate_event_data(event_name, n_weeks=104, seed=42):
    """
    Generates realistic dummy attendance data for the selected event type.
    Replace this with load_from_database(event_name) when DB is ready.

    Parameters:
        event_name (str): Must match a key in EVENT_REGISTRY.
        n_weeks (int)   : Weeks to simulate (104 = 2 years).
        seed (int)      : Random seed for reproducibility.

    Returns:
        pd.Series: Weekly attendance series.
    """
    cfg = EVENT_REGISTRY[event_name]
    np.random.seed(seed)

    dates = pd.date_range(
        start=cfg["start_date"],
        periods=n_weeks,
        freq=cfg["weekday"]
    )

    base     = cfg["base"]
    seasonal = cfg["seasonal"] * np.sin(np.linspace(0, 4 * np.pi, n_weeks))
    trend    = np.linspace(0, cfg["trend"], n_weeks)
    noise    = np.random.normal(0, cfg["noise"], n_weeks)
    attendance = base + seasonal + trend + noise

    # Inject spikes (holidays, special events)
    spike_weeks = np.random.choice(n_weeks, size=cfg["n_spikes"], replace=False)
    for w in spike_weeks:
        attendance[w] += np.random.randint(*cfg["spike_boost"])

    # Inject dips (conflicts, bad weather)
    available = [w for w in range(n_weeks) if w not in spike_weeks]
    dip_weeks = np.random.choice(available, size=cfg["n_dips"], replace=False)
    for w in dip_weeks:
        attendance[w] -= np.random.randint(*cfg["dip_drop"])

    series = pd.Series(attendance, index=dates)
    series = series.rolling(window=2, min_periods=1).mean()
    series = series.clip(lower=10, upper=300).round().astype(int)
    series.index.name = "event_date"
    series.name = "attendance"

    return series


# =============================================================================
# STATIONARITY CHECK
# =============================================================================

def check_stationarity(series):
    """
    Runs the ADF test to check if the series is stationary.
    ARIMA needs stationarity — d=1 handles it if not.
    """
    result  = adfuller(series.dropna())
    p_value = result[1]
    stationary = p_value <= 0.05
    status = "STATIONARY ✓" if stationary else "NOT stationary — d=1 will handle this"
    print(f"  ADF p-value : {p_value:.4f} → {status}")
    return stationary


# =============================================================================
# TRAIN / TEST / VALIDATE
# =============================================================================

def train_test_validate(series, test_weeks=21, order=(3, 1, 2)):
    """
    Splits data into train/test, trains ARIMA on train set,
    validates on test set, reports MAE and RMSE.

    Parameters:
        series (pd.Series): Full attendance series.
        test_weeks (int)  : Weeks reserved for testing (~20%).
        order (tuple)     : ARIMA (p, d, q).

    Returns:
        tuple: (mae, rmse, test_series, test_forecast)
    """
    train = series[:-test_weeks]
    test  = series[-test_weeks:]

    print(f"  Training set : {len(train)} weeks")
    print(f"  Testing set  : {len(test)} weeks")

    train_model   = ARIMA(train, order=order).fit()
    test_forecast = train_model.forecast(steps=len(test))

    mae  = mean_absolute_error(test.values, test_forecast.values)
    rmse = np.sqrt(mean_squared_error(test.values, test_forecast.values))

    print(f"  MAE          : {mae:.2f} attendees avg error")
    print(f"  RMSE         : {rmse:.2f}")
    print(f"  MAE Rating   : {'GOOD ✓' if mae < 10 else 'ACCEPTABLE ✓' if mae < 15 else 'NEEDS IMPROVEMENT'}")
    print(f"  RMSE Rating  : {'GOOD ✓' if rmse < 15 else 'ACCEPTABLE ✓' if rmse < 20 else 'NEEDS IMPROVEMENT'}")

    return mae, rmse, test, test_forecast


# =============================================================================
# FORECAST
# =============================================================================

def forecast_event(full_model, event_name, last_date, steps=6):
    """
    Forecasts the next N weeks for the selected event type.

    Parameters:
        full_model  : ARIMA model trained on full dataset.
        event_name  : Selected event name.
        last_date   : Last date in the training series.
        steps (int) : Weeks ahead to forecast.

    Returns:
        tuple: (forecast_df, forecast_mean, conf_int, future_dates)
    """
    cfg      = EVENT_REGISTRY[event_name]
    forecast = full_model.get_forecast(steps=steps)
    forecast_mean = forecast.predicted_mean
    conf_int      = forecast.conf_int()

    # Determine target weekday from config
    weekday_map    = {"W-SAT": 5, "W-FRI": 4, "W-SUN": 6}
    target_weekday = weekday_map[cfg["weekday"]]

    # Generate future dates on the correct weekday
    future_dates = []
    current = pd.Timestamp(last_date)
    for _ in range(steps):
        current += pd.Timedelta(days=1)
        while current.weekday() != target_weekday:
            current += pd.Timedelta(days=1)
        future_dates.append(current)

    forecast_df = pd.DataFrame({
        "event_type"           : event_name,
        "event_date"           : [d.strftime("%Y-%m-%d") for d in future_dates],
        "predicted_attendance" : forecast_mean.values.astype(int),
        "lower_bound"          : conf_int.iloc[:, 0].values.astype(int),
        "upper_bound"          : conf_int.iloc[:, 1].values.astype(int),
    })

    forecast_df["predicted_attendance"] = forecast_df["predicted_attendance"].clip(lower=0)
    forecast_df["lower_bound"]          = forecast_df["lower_bound"].clip(lower=0)
    forecast_df["upper_bound"]          = forecast_df["upper_bound"].clip(lower=0)

    return forecast_df, forecast_mean, conf_int, future_dates


# =============================================================================
# RECOMMENDATIONS
# =============================================================================

def generate_recommendations(forecast_df, event_name):
    """
    Generates planning recommendations using the event's own thresholds.
    Each event type has its own calibrated ranges defined in EVENT_REGISTRY.
    """
    thresholds = EVENT_REGISTRY[event_name]["thresholds"]

    def recommend(count):
        for level, (low, high, advice) in thresholds.items():
            if low <= count < high:
                return advice
        return "No recommendation available."

    forecast_df["recommendation"] = forecast_df["predicted_attendance"].apply(recommend)
    return forecast_df


# =============================================================================
# PRINT REPORT
# =============================================================================

def print_report(forecast_df, event_name, mae, rmse):
    """
    Prints a clean forecast report for the selected event type.
    """
    cfg  = EVENT_REGISTRY[event_name]
    icon = cfg["icon"]

    print("\n" + "=" * 65)
    print(f"  {icon}  FORECAST REPORT — {event_name.upper()}")
    print("=" * 65)
    print(f"  {cfg['description']}")
    print(f"  Model Accuracy : MAE = {mae:.2f} | RMSE = {rmse:.2f}")
    print(f"  Forecast Period: Next 6 Weeks")
    print("-" * 65)

    for i, (_, row) in enumerate(forecast_df.iterrows(), 1):
        print(f"\n  Week {i}  |  {row['event_date']}")
        print(f"  Predicted    : {row['predicted_attendance']} attendees")
        print(f"  Range        : {row['lower_bound']} – {row['upper_bound']}")
        print(f"  Advice       : {row['recommendation']}")

    print("\n" + "=" * 65)


# =============================================================================
# VISUALIZATION
# =============================================================================

def plot_forecast(series, test_series, test_forecast,
                  forecast_mean, conf_int, future_dates, event_name):
    """
    Plots historical data, validation window, and 6-week forecast
    specifically for the selected event type.
    """
    cfg   = EVENT_REGISTRY[event_name]
    icon  = cfg["icon"]
    color = "#2c7bb6" if "SAT" in cfg["weekday"] else "#1a9641"
    fcast_color = "#d7191c" if "SAT" in cfg["weekday"] else "#ff7f00"

    fig, ax = plt.subplots(figsize=(14, 5))

    # Last 12 weeks of history before test period
    history = series[:-len(test_series)][-12:]
    ax.plot(history.index, history.values,
            color=color, linewidth=2,
            marker="o", markersize=4, label="Historical Attendance")

    # Actual test values
    ax.plot(test_series.index, test_series.values,
            color="#555555", linewidth=2,
            marker="o", markersize=4, label="Actual (Test Period)")

    # Model predictions on test (validation)
    ax.plot(test_series.index, test_forecast.values,
            color="#f4a582", linewidth=2, linestyle="--",
            marker="x", markersize=5, label="Model Predictions (Validation)")

    # Future forecast
    future_idx = pd.DatetimeIndex(future_dates)
    ax.plot(future_idx, forecast_mean.values,
            color=fcast_color, linewidth=2, linestyle="--",
            marker="o", markersize=6, label="Forecast (Next 6 Weeks)")

    # Confidence interval
    ax.fill_between(
        future_idx,
        conf_int.iloc[:, 0].values,
        conf_int.iloc[:, 1].values,
        color=fcast_color, alpha=0.15,
        label="95% Confidence Interval"
    )

    # Dividers
    ax.axvline(x=test_series.index[0], color="orange",
               linestyle=":", linewidth=1.5, label="Test Period Start")
    ax.axvline(x=series.index[-1], color="gray",
               linestyle=":", linewidth=1.5, label="Forecast Start")

    ax.set_title(
        f"CHAMPS — BCBP Lipa Chapter\n"
        f"{icon}  {event_name} — Attendance Forecast (Next 6 Weeks)",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.set_xlabel("Event Date", fontsize=11)
    ax.set_ylabel("Attendance Count", fontsize=11)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()

    safe_name  = event_name.lower().replace(" ", "_")
    chart_file = f"champs_forecast_{safe_name}.png"
    plt.savefig(chart_file, dpi=150)
    print(f"  Chart saved  : {chart_file} ✓")
    plt.show()


# =============================================================================
# CORE FUNCTION — run_forecast()
# -----------------------------------------------------------------------------
# This is the main function that runs the full pipeline for ONE event.
#
# THIS IS YOUR FLASK INTEGRATION POINT:
#   When Flask is set up, your route just calls run_forecast(event_name)
#   and returns the result as JSON. Nothing else in this file changes.
#
#   @app.route('/forecast', methods=['POST'])
#   def forecast_route():
#       event_name = request.form.get('event_name')
#       result = run_forecast(event_name)
#       return jsonify(result)
# =============================================================================

def run_forecast(event_name, order=(3, 1, 2), forecast_weeks=6, n_weeks=104):
    """
    Runs the full forecasting pipeline for a single event type.

    Parameters:
        event_name (str)    : Must match a key in EVENT_REGISTRY.
        order (tuple)       : ARIMA (p, d, q) — default (3, 1, 2).
        forecast_weeks (int): Weeks ahead to forecast — default 6.
        n_weeks (int)       : Weeks of history to use — default 104 (2 years).

    Returns:
        dict: Forecast results (usable by Flask/JSON later).
    """
    cfg  = EVENT_REGISTRY[event_name]
    icon = cfg["icon"]

    print("\n" + "=" * 65)
    print(f"  {icon}  Running Forecast: {event_name}")
    print("=" * 65)

    # ── Step 1: Load Data ──────────────────────────────────────────────
    # SWAP: replace generate_event_data() with load_from_database(event_name)
    print("\n[Step 1: Loading Data]")
    series = generate_event_data(event_name, n_weeks=n_weeks)
    print(f"  Weeks loaded : {len(series)}")
    print(f"  Date range   : {series.index[0].date()} → {series.index[-1].date()}")
    print(f"  Avg          : {series.mean():.1f} | Min: {series.min()} | Max: {series.max()}")

    # ── Step 2: Stationarity ───────────────────────────────────────────
    print("\n[Step 2: Stationarity Check]")
    check_stationarity(series)

    # ── Step 3: Train / Test / Validate ───────────────────────────────
    print("\n[Step 3: Train / Test / Validate]")
    mae, rmse, test_series, test_forecast = train_test_validate(
        series, test_weeks=21, order=order
    )

    # ── Step 4: Retrain on Full Dataset ───────────────────────────────
    print("\n[Step 4: Retraining on Full Dataset]")
    full_model = ARIMA(series, order=order).fit()
    print(f"  AIC : {full_model.aic:.2f} | BIC : {full_model.bic:.2f} ✓")

    # ── Step 5: Forecast ──────────────────────────────────────────────
    print(f"\n[Step 5: Forecasting Next {forecast_weeks} Weeks]")
    forecast_df, forecast_mean, conf_int, future_dates = forecast_event(
        full_model, event_name,
        last_date=series.index[-1],
        steps=forecast_weeks
    )

    # ── Step 6: Recommendations ───────────────────────────────────────
    forecast_df = generate_recommendations(forecast_df, event_name)

    # ── Step 7: Print Report ──────────────────────────────────────────
    print_report(forecast_df, event_name, mae, rmse)

    # ── Step 8: Save CSV ──────────────────────────────────────────────
    safe_name = event_name.lower().replace(" ", "_")
    csv_file  = f"champs_forecast_{safe_name}.csv"
    forecast_df.to_csv(csv_file, index=False)
    print(f"  CSV saved    : {csv_file} ✓")

    # ── Step 9: Plot ──────────────────────────────────────────────────
    print("\n[Step 6: Generating Chart]")
    plot_forecast(series, test_series, test_forecast,
                  forecast_mean, conf_int, future_dates, event_name)

    # ── Return results (ready for Flask/JSON) ─────────────────────────
    return {
        "event_name"  : event_name,
        "mae"         : round(mae, 2),
        "rmse"        : round(rmse, 2),
        "forecast"    : forecast_df.to_dict(orient="records"),
        "csv_file"    : csv_file,
    }


# =============================================================================
# MAIN — MENU LOOP
# Keeps showing the menu after each forecast so the user can
# generate reports for multiple events in one session.
# =============================================================================

def main():
    while True:
        # Show menu and get user's event choice
        selected_event = show_menu()

        # Run the full pipeline for the selected event only
        run_forecast(selected_event)

        # After report is done, ask if they want to generate another
        print("\n" + "-" * 65)
        again = input("  Generate another forecast? (y/n): ").strip().lower()
        if again != "y":
            print("\n  Exiting CHAMPS Forecasting System. Goodbye!\n")
            break


if __name__ == "__main__":
    main()
