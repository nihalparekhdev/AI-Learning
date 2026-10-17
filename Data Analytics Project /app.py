"""
app.py - Live AI Analytics Dashboard (Streamlit)

Run:  streamlit run app.py

Everything on the page is data-bound: change the city, metric, model or
horizon in the sidebar and every chart, KPI, forecast and insight rebuilds
from the freshly fetched API data. With auto-refresh on, the live panel
re-pulls the API on a timer without a full page reload.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import api_client as api
import ml_engine as ml

st.set_page_config(page_title="Live AI Analytics Lab", page_icon="📡", layout="wide")


# ----------------------------- cached helpers -----------------------------
@st.cache_data(ttl=60, show_spinner=False)
def load_data(lat, lon, past_days):
    return api.fetch_live_data(lat, lon, past_days)


@st.cache_data(show_spinner="Training forecast model…")
def run_forecast(series, model_name, horizon):
    return ml.forecast(series, model_name, horizon)


@st.cache_data(show_spinner=False)
def run_anomalies(df, contamination):
    return ml.detect_anomalies(df, contamination)


@st.cache_data(show_spinner=False)
def run_clusters(df, k):
    return ml.cluster_regimes(df, k)


@st.cache_data(show_spinner=False)
def run_suggest_k(df):
    return ml.suggest_k(df)


# --------------------------------- sidebar --------------------------------
st.title("📡 Live AI Analytics Lab")
st.caption("Real-time API data → cleaning → ML forecasting, anomaly detection "
           "& clustering → auto-generated insights")

with st.sidebar:
    st.header("1 · Data source")
    city = st.selectbox("Location", list(api.CITIES) + ["Custom"])
    if city == "Custom":
        lat = st.number_input("Latitude", -90.0, 90.0, 51.51)
        lon = st.number_input("Longitude", -180.0, 180.0, -0.13)
    else:
        lat, lon = api.CITIES[city]
    past_days = st.slider("History window (days)", 7, 30, 14)

    st.header("2 · Live refresh")
    auto = st.toggle("Auto-refresh", value=False)
    interval = st.slider("Every (seconds)", 30, 600, 60, step=30, disabled=not auto)
    if st.button("🔄 Refresh now"):
        st.cache_data.clear()
        st.rerun()

# initial load only to discover which columns the API returned
_df0, _, _, _ = load_data(lat, lon, past_days)
columns = list(_df0.columns)

with st.sidebar:
    st.header("3 · AI settings")
    metric = st.selectbox("Metric to analyse", columns, format_func=api.label)
    model_name = st.selectbox("Forecast model", list(ml.MODELS))
    horizon = st.slider("Forecast horizon (hours)", 6, 48, 24, step=6)
    contamination = st.slider("Anomaly sensitivity", 0.01, 0.10, 0.03, step=0.01)
    auto_k = st.checkbox("Auto-select number of regimes", value=True)
    k_manual = st.slider("Regimes (K)", 2, 6, 3, disabled=auto_k)


# ------------------------------ live dashboard ----------------------------
@st.fragment(run_every=interval if auto else None)
def live_dashboard():
    df, current, source, note = load_data(lat, lon, past_days)
    name, unit = api.LABELS.get(metric, (metric, ""))

    if source == "live":
        st.success(f"🟢 LIVE · {note}")
    else:
        st.warning(f"🟠 {note}")
    st.caption(f"Latest reading: {current['time']:%d %b %Y %H:%M} · "
               f"page updated {pd.Timestamp.now():%H:%M:%S}")

    # ---- KPI row (bound to the API's latest values) ----
    kpi_cols = st.columns(len(columns))
    for box, c in zip(kpi_cols, columns):
        val = current.get(c)
        prev = df[c].iloc[-2] if len(df) > 1 else None
        delta = None if (val is None or prev is None) else round(val - prev, 2)
        n, u = api.LABELS.get(c, (c, ""))
        box.metric(n, f"{val:.1f} {u}" if val is not None else "n/a", delta)

    # ---- run the ML pipeline ----
    series = ml.prepare_series(df, metric)
    result = run_forecast(series, model_name, horizon)
    anomalies = run_anomalies(df, contamination)
    k = run_suggest_k(df) if auto_k else k_manual
    clustered, profile, sil = run_clusters(df, k)

    with st.container(border=True):
        st.subheader("💡 AI insights")
        for line in ml.generate_insights(df, metric, name, unit, result["forecast"],
                                         anomalies, result["improvement_pct"],
                                         nice=api.label):
            st.markdown(f"- {line}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Live overview", "🔮 Forecast", "🚨 Anomalies", "🧩 Regimes", "🗂 Data"])

    # ---------- Tab 1: overview ----------
    with tab1:
        fig = go.Figure()
        fig.add_scatter(x=df.index, y=df[metric], name=name, mode="lines")
        fig.add_scatter(x=df.index, y=df[metric].rolling(24, min_periods=1).mean(),
                        name="24h average", line=dict(dash="dash"))
        fig.update_layout(title=f"{api.label(metric)} – live history",
                          height=380, margin=dict(t=50, b=10))
        st.plotly_chart(fig)

        left, right = st.columns(2)
        hourly = df[metric].groupby(df.index.hour).mean()
        left.plotly_chart(px.line(hourly, markers=True,
                                  title="Average by hour of day",
                                  labels={"value": api.label(metric), "time": "Hour"})
                          .update_layout(showlegend=False, height=340))
        right.plotly_chart(px.imshow(df.corr().round(2), text_auto=True,
                                     color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                                     title="Correlation matrix")
                           .update_layout(height=340))

    # ---------- Tab 2: forecast ----------
    with tab2:
        fc, bt = result["forecast"], result["backtest"]
        hist = series.iloc[-72:]
        fig = go.Figure()
        fig.add_scatter(x=hist.index, y=hist, name="Actual", line=dict(color="#4c78a8"))
        fig.add_scatter(x=bt.index, y=bt["predicted"], name="Back-test prediction",
                        line=dict(color="#f58518", dash="dot"))
        fig.add_scatter(x=fc.index, y=fc["upper"], line=dict(width=0),
                        showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=fc.index, y=fc["lower"], fill="tonexty", line=dict(width=0),
                        fillcolor="rgba(84,162,75,0.2)", name="≈95% band")
        fig.add_scatter(x=fc.index, y=fc["forecast"], name="Forecast",
                        line=dict(color="#54a24b", width=3))
        fig.update_layout(title=f"{horizon}h forecast – {model_name}",
                          height=420, margin=dict(t=50, b=10))
        st.plotly_chart(fig)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Back-test accuracy** (last forecast window hidden from the model)")
            st.dataframe(result["metrics"])
            st.caption("Lower is better. A useful model must beat both naive baselines.")
        with c2:
            st.plotly_chart(px.bar(result["importance"], orientation="h",
                                   title="What drives the forecast?")
                            .update_layout(showlegend=False, height=320))

    # ---------- Tab 3: anomalies ----------
    with tab3:
        flagged = anomalies[anomalies["is_anomaly"]]
        fig = go.Figure()
        fig.add_scatter(x=df.index, y=df[metric], name=name, mode="lines")
        fig.add_scatter(x=flagged.index, y=flagged[metric], mode="markers",
                        name="Anomaly", marker=dict(color="red", size=10, symbol="x"))
        fig.update_layout(title="Isolation Forest anomalies (all variables considered)",
                          height=380, margin=dict(t=50, b=10))
        st.plotly_chart(fig)
        st.markdown(f"**{len(flagged)} anomalous hours** (top 10 by score)")
        st.dataframe(flagged.sort_values("anomaly_score", ascending=False).head(10).round(2))

    # ---------- Tab 4: clustering ----------
    with tab4:
        st.markdown(f"K-Means found **{k} regimes** · silhouette score **{sil:.2f}** "
                    "(closer to 1 = better separated)")
        c1, c2 = st.columns([3, 2])
        c1.plotly_chart(px.scatter(clustered, x="pc1", y="pc2", color="regime",
                                   hover_data=[metric], title="Regimes (PCA projection)")
                        .update_layout(height=400))
        c2.markdown("**Regime profiles (mean values)**")
        c2.dataframe(profile)
        timeline = clustered.reset_index().rename(columns={"index": "time"})
        st.plotly_chart(px.scatter(timeline, x="time", y=metric, color="regime",
                                   title="Regimes over time")
                        .update_layout(height=320))

    # ---------- Tab 5: raw data ----------
    with tab5:
        st.dataframe(df.sort_index(ascending=False).round(2))
        st.download_button("⬇ Download CSV", df.to_csv().encode(),
                           file_name="live_data.csv", mime="text/csv")


live_dashboard()
