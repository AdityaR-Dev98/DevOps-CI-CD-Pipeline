# dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import uuid

from charts import (
    failure_distribution,
    status_trend,
    sla_gauge,
    mttr_trend,
    anomaly_timeline,
    ai_conf_hist,
    correlation_matrix,
    intervention_sankey,
    failure_probability_gauge,
    severity_execution_boxplot,
    historical_comparison_panel,
    clustering_visualization,
    drift_detection_plot,
)

LOG_DIR = Path.cwd() / "logs" / "self_healing"
LOG_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Self-Healing CI/CD Analytics", layout="wide")
st.markdown(
    """
    <h1 style='text-align:center;color:#1f2937;margin-bottom:4px;'>Self-Healing CI/CD Analytics & Diagnostics</h1>
    <h4 style='text-align:center;color:#6b7280;margin-top:0;margin-bottom:12px;'>AI-augmented observability, synthetic augmentation for resilient analytics</h4>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Configuration")
    refresh_seconds = st.number_input("Auto-refresh every (seconds)", min_value=5, max_value=600, value=15)
    window_days = st.slider("Current analysis window (days)", min_value=1, max_value=365, value=30)
    historical_days = st.slider("Historical comparison window (days)", min_value=7, max_value=365, value=90)
    synth_size = st.number_input("Synthetic samples for augmentation (if needed)", min_value=10, max_value=2000, value=200)
    st.button("Refresh dashboard")

def load_logs(directory: Path, days: int):
    records = []
    cutoff = datetime.now() - timedelta(days=days)
    for p in directory.glob("*.json"):
        try:
            # try normal json load
            dfp = pd.read_json(p, orient="records")
            if isinstance(dfp, pd.DataFrame):
                records.append(dfp)
        except Exception:
            try:
                # fallback for newline-delimited json / other formats
                with open(p, "r", encoding="utf-8") as f:
                    txt = f.read()
                    dfp = pd.json_normalize(pd.read_json(txt))
                    records.append(dfp)
            except Exception:
                continue
    if not records:
        return pd.DataFrame()
    df = pd.concat(records, ignore_index=True, sort=False)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df[df["timestamp"] >= cutoff]
    else:
        df["timestamp"] = pd.to_datetime(datetime.now())
    if "status" not in df.columns and "final_status" in df.columns:
        df["status"] = df["final_status"]
    df["status"] = df["status"].astype(str).fillna("")
    for col in ["ai_explanation", "file", "issue_type", "severity", "ai_confidence", "execution_time"]:
        if col not in df.columns:
            df[col] = np.nan if col in ["ai_confidence", "execution_time"] else ""
    # coerce numerics
    df["ai_confidence"] = pd.to_numeric(df["ai_confidence"], errors="coerce")
    df["execution_time"] = pd.to_numeric(df["execution_time"], errors="coerce")
    return df

def synthesize_numeric_features(df_real: pd.DataFrame, size: int = 200):
    """
    Create a synthetic DataFrame based on real numeric stats.
    We'll use execution_time and ai_confidence as example features.
    """
    rng = np.random.default_rng(seed=42)
    # Start with baseline stats extracted from df_real (if present)
    et = df_real["execution_time"].dropna()
    ac = df_real["ai_confidence"].dropna()
    if not et.empty:
        et_mean, et_std = float(et.mean()), float(max(et.std(), 1.0))
    else:
        et_mean, et_std = 60.0, 30.0
    if not ac.empty:
        ac_mean, ac_std = float(ac.mean()), float(max(ac.std(), 0.05))
    else:
        ac_mean, ac_std = 0.6, 0.15
    # produce synthetic arrays (clipped to realistic ranges)
    synthetic_et = np.clip(rng.normal(et_mean, et_std, size), 0.1, None)
    synthetic_ac = np.clip(rng.normal(ac_mean, ac_std, size), 0.0, 1.0)
    # produce timestamps spread over the requested window
    now = datetime.now()
    timestamps = [now - timedelta(minutes=int(x)) for x in np.linspace(0, size * 60, size)]
    # produce status labels consistent with observed failure rate
    real_fail_rate = df_real["status"].str.contains("fail", case=False, na=False).mean()
    if np.isnan(real_fail_rate):
        real_fail_rate = 0.1
    status_choices = ["fail", "pass"]
    status_probs = [real_fail_rate, 1 - real_fail_rate]
    synthetic_status = rng.choice(status_choices, size=size, p=status_probs)
    # produce severity distribution from real data if available
    severity_vals = df_real["severity"].dropna().astype(str).unique().tolist()
    if not severity_vals:
        severity_vals = ["low", "medium", "high"]
    synthetic_severity = rng.choice(severity_vals, size=size)
    # build DataFrame
    df_synth = pd.DataFrame({
        "timestamp": timestamps,
        "execution_time": synthetic_et,
        "ai_confidence": synthetic_ac,
        "status": synthetic_status,
        "severity": synthetic_severity,
        "ai_explanation": rng.choice([ "", "AI suggested fix", "AI suggested change" ], size=size, p=[0.6, 0.3, 0.1]),
        "issue_type": rng.choice(["DependencyError", "RuntimeError", "TestFailure", "Other"], size=size),
        "file": rng.choice(["buggy_examples/buggy1_syntax_error.py", "buggy_examples/buggy4_import_error.py", "app.py"], size=size)
    })
    return df_synth

# load real logs
df = load_logs(LOG_DIR, window_days)
df_hist = load_logs(LOG_DIR, historical_days)

if df.empty:
    st.warning("No logs found in logs/self_healing. Place JSON logs there and refresh.")
    st.stop()

# Keep original KPIs strictly from real df
total = len(df)
passed = df["status"].str.contains("pass", case=False, na=False).sum()
failed = total - passed
ai_actions = df["ai_explanation"].astype(str).str.strip().ne("").sum()
# safe mean
mean_conf = float(df["ai_confidence"].dropna().mean()) if not df["ai_confidence"].dropna().empty else None

col1, col2, col3, col4, col5 = st.columns([1.2,1,1,1,1])
col1.metric("Total records", total)
col2.metric("Passed", passed)
col3.metric("Failed", failed)
col4.metric("AI suggestions", ai_actions)
col5.metric("Mean AI confidence", f"{mean_conf:.2f}" if mean_conf is not None else "N/A")

st.markdown("---")

# Create a synthetic dataset for advanced analysis if real numeric features missing or sparse
need_synth = False
numeric_count = df[["execution_time", "ai_confidence"]].dropna().shape[0]
if numeric_count < max(50, synth_size // 4):
    need_synth = True

if need_synth:
    df_synth = synthesize_numeric_features(df, size=int(synth_size))
    # mix real numeric rows (if any) to make hybrid realistic
    real_numeric = df.dropna(subset=["execution_time", "ai_confidence"])
    if not real_numeric.empty:
        # sample up to 30% real numeric rows and append
        sample_count = max(1, int(0.3 * len(df_synth)))
        sample_real = real_numeric.sample(min(sample_count, len(real_numeric)))
        df_synth = pd.concat([df_synth, sample_real[ df_synth.columns.intersection(sample_real.columns) ]], ignore_index=True, sort=False)
else:
    # when we have good numeric data - use the real rows for detailed analysis
    df_synth = df[["timestamp", "execution_time", "ai_confidence", "status", "severity", "ai_explanation", "issue_type", "file"]].dropna(axis=0, how="all").copy()

# Ensure timestamps are datetimes
df_synth["timestamp"] = pd.to_datetime(df_synth["timestamp"], errors="coerce")

st.header("Trends and Distribution")
left, right = st.columns([2, 1])
with left:
    st.subheader("Status Trend")
    try:
        st.plotly_chart(status_trend(df, df_hist), use_container_width=True, key=f"trend-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Trend chart error: {e}")

with right:
    st.subheader("Failure distribution and SLA")
    try:
        st.plotly_chart(failure_distribution(df_synth), use_container_width=True, key=f"dist-{uuid.uuid4().hex}")
        st.plotly_chart(sla_gauge(df_synth), use_container_width=True, key=f"sla-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Distribution chart error: {e}")

st.markdown("---")
st.header("AI & Anomaly Insights")

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("AI confidence distribution")
    try:
        st.plotly_chart(ai_conf_hist(df_synth), use_container_width=True, key=f"aihist-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"AI histogram error: {e}")

with c2:
    st.subheader("Anomaly timeline on primary numeric metric")
    try:
        st.plotly_chart(anomaly_timeline(df_synth), use_container_width=True, key=f"anomaly-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Anomaly chart error: {e}")

with c3:
    st.subheader("Recent failure probability")
    try:
        st.plotly_chart(failure_probability_gauge(df_synth), use_container_width=True, key=f"gauge-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Gauge error: {e}")

st.markdown("---")
st.header("Advanced Statistical & Structural Analysis")

a1, a2 = st.columns([2, 1])
with a1:
    st.subheader("Correlation heatmap")
    try:
        st.plotly_chart(correlation_matrix(df_synth), use_container_width=True, key=f"corr-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Correlation error: {e}")

    st.subheader("Execution time by severity")
    try:
        st.plotly_chart(severity_execution_boxplot(df_synth), use_container_width=True, key=f"box-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Boxplot error: {e}")

    st.subheader("Historical comparison (failure rate vs baseline)")
    try:
        st.plotly_chart(historical_comparison_panel(df_synth, df_hist if not df_hist.empty else df_synth), use_container_width=True, key=f"hist-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Historical comparison error: {e}")

with a2:
    st.subheader("Intervention Sankey (issue->action->result)")
    try:
        st.plotly_chart(intervention_sankey(df_synth), use_container_width=True, key=f"sankey-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Sankey error: {e}")

    st.subheader("Drift detection vs historical")
    try:
        st.plotly_chart(drift_detection_plot(df_synth, df_hist if not df_hist.empty else df_synth), use_container_width=True, key=f"drift-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Drift chart error: {e}")

    st.subheader("KMeans clustering (numeric metrics)")
    try:
        st.plotly_chart(clustering_visualization(df_synth), use_container_width=True, key=f"cluster-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"Clustering error: {e}")

st.markdown("---")
st.header("Recovery Metrics & Raw Logs")

m1, m2 = st.columns([1, 2])

with m1:
    st.subheader("MTTR trend (approx)")
    try:
        st.plotly_chart(mttr_trend(df_synth), use_container_width=True, key=f"mttr-{uuid.uuid4().hex}")
    except Exception as e:
        st.error(f"MTTR chart error: {e}")

with m2:
    st.subheader("Raw logs (real)")
    df_view = df.copy().sort_values("timestamp", ascending=False).reset_index(drop=True)
    st.dataframe(df_view.fillna(""), use_container_width=True)

st.markdown("---")
st.header("Modeling & Prediction (safe, synthetic fallback)")

colA, colB = st.columns(2)
with colA:
    if st.button("Train failure model (safe)"):
        from sklearn.linear_model import LogisticRegression
        # prepare training set from df_synth (ensures numeric columns are present)
        train_df = df_synth.copy()
        train_df["failed_flag"] = train_df["status"].str.contains("fail", case=False, na=False).astype(int)
        # choose features available
        features = []
        for f in ["execution_time", "ai_confidence"]:
            if f in train_df.columns and train_df[f].notna().sum() > 0:
                features.append(f)
        if not features:
            st.error("No numeric features present for training.")
        else:
            X = train_df[features].fillna(train_df[features].median()).values
            y = train_df["failed_flag"].values
            # safe: ensure at least two classes
            if len(np.unique(y)) < 2:
                st.warning("Only one class present in labels; synthesizing a second class to enable training.")
                synth_count = max(10, int(0.2 * X.shape[0]))
                X_syn = np.tile(X.mean(axis=0), (synth_count, 1)) + np.random.normal(0, 0.05, (synth_count, X.shape[1]))
                y_syn = np.array([1 - int(y[0])] * synth_count)
                X = np.vstack([X, X_syn])
                y = np.concatenate([y, y_syn])
            try:
                model = LogisticRegression(max_iter=1000)
                model.fit(X, y)
                st.success("Model trained and saved to session")
                st.session_state["failure_model"] = (model, features)
            except Exception as ex:
                st.error(f"Model training failed: {ex}")

with colB:
    model_info = st.session_state.get("failure_model", None)
    if model_info:
        model, model_features = model_info
        st.write("Model features:", model_features)
        # take sample inputs
        sample_vals = {}
        for f in model_features:
            median_val = float(df_synth[f].dropna().median()) if f in df_synth.columns and not df_synth[f].dropna().empty else 0.0
            sample_vals[f] = st.number_input(f"Input {f}", value=median_val, key=f"pred_{f}")
        if st.button("Predict sample"):
            Xs = np.array([[sample_vals[f] for f in model_features]])
            prob = float(model.predict_proba(Xs)[0, 1])
            st.metric("Predicted failure probability", f"{prob:.2%}")
            st.plotly_chart(failure_probability_gauge(df_synth, override_value=prob), use_container_width=True, key=f"pred_gauge_{uuid.uuid4().hex}")
    else:
        st.info("Train the model to enable prediction.")

st.markdown("---")
st.header("Export & Controls")
exp1, exp2 = st.columns(2)
with exp1:
    if st.button("Export real logs to CSV"):
        fname = Path.cwd() / f"export_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_view.to_csv(fname, index=False)
        st.success(f"Exported real logs to {fname}")
with exp2:
    if st.button("Force refresh now"):
        st.experimental_rerun()

st.write("Dashboard updated. Real KPIs are preserved; analyses use hybrid/synthetic data when needed.")
