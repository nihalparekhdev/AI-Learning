"""
ml_engine.py - AI / ML layer (no Streamlit code here, so it is easy to test).

1. Forecasting      : lag-feature regression with recursive multi-step prediction,
                      back-tested against two naive baselines.
2. Anomaly detection: Isolation Forest (unsupervised).
3. Regime discovery : K-Means clustering + PCA projection.
4. Auto-insights    : plain-English findings generated from the results.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import (GradientBoostingRegressor, IsolationForest,
                              RandomForestRegressor)
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

LAGS = [1, 2, 3, 6, 12, 24]
FEATURES = [f"lag_{k}" for k in LAGS] + ["roll_6", "roll_24", "hour_sin", "hour_cos", "dow"]

MODELS = {
    "Gradient Boosting": lambda: GradientBoostingRegressor(
        n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42),
    "Random Forest": lambda: RandomForestRegressor(
        n_estimators=150, min_samples_leaf=2, random_state=42, n_jobs=1),
    "Ridge Regression": lambda: make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
}


# --------------------------------------------------------------------------
# 1. FORECASTING
# --------------------------------------------------------------------------
def prepare_series(df: pd.DataFrame, col: str) -> pd.Series:
    s = df[col].astype(float).asfreq("h").interpolate(limit=3).dropna()
    if len(s) < 72:
        raise ValueError("Need at least 72 hourly points to train a forecast model.")
    return s


def make_training_frame(s: pd.Series):
    X = pd.DataFrame(index=s.index)
    for k in LAGS:
        X[f"lag_{k}"] = s.shift(k)
    prev = s.shift(1)
    X["roll_6"] = prev.rolling(6).mean()
    X["roll_24"] = prev.rolling(24).mean()
    X["hour_sin"] = np.sin(2 * np.pi * s.index.hour / 24)
    X["hour_cos"] = np.cos(2 * np.pi * s.index.hour / 24)
    X["dow"] = s.index.dayofweek
    data = X[FEATURES].join(s.rename("y")).dropna()
    return data[FEATURES], data["y"]


def recursive_forecast(model, history: pd.Series, horizon: int) -> pd.Series:
    """Predict one hour, feed it back in as history, repeat."""
    vals = list(history.values)
    last = history.index[-1]
    idx, preds = [], []
    for step in range(1, horizon + 1):
        ts = last + pd.Timedelta(hours=step)
        row = {f"lag_{k}": vals[-k] for k in LAGS}
        row["roll_6"] = float(np.mean(vals[-6:]))
        row["roll_24"] = float(np.mean(vals[-24:]))
        row["hour_sin"] = np.sin(2 * np.pi * ts.hour / 24)
        row["hour_cos"] = np.cos(2 * np.pi * ts.hour / 24)
        row["dow"] = ts.dayofweek
        p = float(model.predict(pd.DataFrame([row])[FEATURES])[0])
        vals.append(p)
        preds.append(p)
        idx.append(ts)
    return pd.Series(preds, index=pd.DatetimeIndex(idx, freq="h"))


def _scores(actual, pred):
    return {"MAE": mean_absolute_error(actual, pred),
            "RMSE": float(np.sqrt(mean_squared_error(actual, pred)))}


def backtest(s: pd.Series, model_name: str, horizon: int):
    """Hide the last `horizon` hours, forecast them, compare with reality."""
    train, test = s.iloc[:-horizon], s.iloc[-horizon:]
    X, y = make_training_frame(train)
    model = MODELS[model_name]().fit(X, y)
    pred = recursive_forecast(model, train, horizon)

    persistence = pd.Series(train.iloc[-1], index=test.index)
    seasonal = pd.Series(np.resize(train.iloc[-24:].values, horizon), index=test.index)

    metrics = pd.DataFrame({
        model_name: _scores(test, pred.values),
        "Persistence (last value)": _scores(test, persistence),
        "Seasonal naive (same hour yesterday)": _scores(test, seasonal),
    }).T.round(3)
    frame = pd.DataFrame({"actual": test, "predicted": pred.values}, index=test.index)
    return metrics, frame


def forecast(s: pd.Series, model_name: str, horizon: int) -> dict:
    metrics, bt_frame = backtest(s, model_name, horizon)
    X, y = make_training_frame(s)
    model = MODELS[model_name]().fit(X, y)
    fc = recursive_forecast(model, s, horizon)

    rmse = metrics.loc[model_name, "RMSE"]
    fc_df = pd.DataFrame({"forecast": fc,
                          "lower": fc - 1.96 * rmse,
                          "upper": fc + 1.96 * rmse})

    est = model[-1] if hasattr(model, "steps") else model
    imp = getattr(est, "feature_importances_", None)
    if imp is None:
        imp = np.abs(est.coef_)
        imp = imp / imp.sum()
    importance = pd.Series(imp, index=FEATURES).sort_values()

    baselines = metrics.drop(index=model_name)["RMSE"].min()
    improvement = (1 - rmse / baselines) * 100 if baselines else 0.0
    return {"forecast": fc_df, "metrics": metrics, "backtest": bt_frame,
            "importance": importance, "improvement_pct": float(improvement)}


# --------------------------------------------------------------------------
# 2. ANOMALY DETECTION
# --------------------------------------------------------------------------
def detect_anomalies(df: pd.DataFrame, contamination: float = 0.03) -> pd.DataFrame:
    X = StandardScaler().fit_transform(df)
    iso = IsolationForest(n_estimators=200, contamination=contamination,
                          random_state=42).fit(X)
    out = df.copy()
    out["anomaly_score"] = -iso.score_samples(X)
    out["is_anomaly"] = iso.predict(X) == -1
    return out


# --------------------------------------------------------------------------
# 3. REGIME DISCOVERY (clustering)
# --------------------------------------------------------------------------
def suggest_k(df: pd.DataFrame, k_range=range(2, 7)) -> int:
    X = StandardScaler().fit_transform(df)
    best_k, best = 2, -1
    for k in k_range:
        labels = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X)
        score = silhouette_score(X, labels)
        if score > best:
            best_k, best = k, score
    return best_k


def cluster_regimes(df: pd.DataFrame, k: int):
    X = StandardScaler().fit_transform(df)
    labels = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X)
    pcs = PCA(n_components=2, random_state=42).fit_transform(X)
    out = df.copy()
    out["regime"] = [f"Regime {l + 1}" for l in labels]
    out["pc1"], out["pc2"] = pcs[:, 0], pcs[:, 1]
    profile = out.groupby("regime")[list(df.columns)].mean().round(2)
    profile["hours"] = out["regime"].value_counts()
    return out, profile, float(silhouette_score(X, labels))


# --------------------------------------------------------------------------
# 4. AUTO-INSIGHTS
# --------------------------------------------------------------------------
def generate_insights(df, col, name, unit, fc_df, anomalies, improvement_pct,
                      nice=lambda c: c):
    s = df[col]
    notes = []

    recent = s.iloc[-6:]
    slope = np.polyfit(np.arange(len(recent)), recent.values, 1)[0]
    thr = max(s.std() * 0.05, 1e-9)
    trend = "rising" if slope > thr else "falling" if slope < -thr else "steady"
    notes.append(f"{name} is **{trend}** over the last 6 hours "
                 f"({slope:+.2f}{unit}/hour).")

    end_val, peak_t = fc_df["forecast"].iloc[-1], fc_df["forecast"].idxmax()
    notes.append(f"The model expects {name} to reach **{end_val:.1f}{unit}** by "
                 f"{fc_df.index[-1]:%a %H:%M}, peaking near "
                 f"{fc_df['forecast'].max():.1f}{unit} at {peak_t:%a %H:%M}.")

    n_recent = int(anomalies["is_anomaly"].iloc[-48:].sum())
    notes.append(f"**{n_recent}** unusual reading(s) detected in the last 48 hours "
                 f"({int(anomalies['is_anomaly'].sum())} in the full window).")

    corr = df.corr()[col].drop(col)
    if len(corr):
        top = corr.abs().idxmax()
        notes.append(f"{name} is most strongly linked to **{nice(top)}** "
                     f"(correlation {corr[top]:+.2f}).")

    v_now, v_prev = s.iloc[-24:].std(), s.iloc[-48:-24].std()
    if v_prev > 0 and v_now > 1.5 * v_prev:
        notes.append("Volatility over the last 24h is **much higher** than the day before.")

    if improvement_pct > 0:
        notes.append(f"The ML model beats the best naive baseline by "
                     f"**{improvement_pct:.0f}%** (RMSE) in back-testing.")
    else:
        notes.append("The ML model did **not** beat a naive baseline in back-testing; "
                     "treat the forecast with caution.")
    return notes
