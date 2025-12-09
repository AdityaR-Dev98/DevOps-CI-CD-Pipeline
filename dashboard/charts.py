# charts.py
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import random
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def _apply_seed(seed):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

def failure_distribution(df, seed=None):
    _apply_seed(seed)
    if "status" not in df.columns:
        return go.Figure()
    counts = df["status"].value_counts()
    fig = px.pie(values=counts.values, names=counts.index)
    return fig

def status_trend(df, df_hist, seed=None):
    _apply_seed(seed)
    df = df.copy()
    df_hist = df_hist.copy()
    if "timestamp" not in df.columns or "status" not in df.columns:
        return go.Figure()
    df["day"] = df["timestamp"].dt.date
    df_hist["day"] = df_hist["timestamp"].dt.date
    real = df.groupby("day")["status"].apply(lambda x: (x.str.contains("pass").sum(), x.str.contains("fail").sum()))
    hist = df_hist.groupby("day")["status"].apply(lambda x: (x.str.contains("pass").sum(), x.str.contains("fail").sum()))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(real.index), y=[r[1] for r in real], mode="lines+markers", name="Failures"))
    fig.add_trace(go.Scatter(x=list(hist.index), y=[h[1] for h in hist], mode="lines+markers", name="Historical Failures"))
    return fig

def sla_gauge(df, seed=None):
    _apply_seed(seed)
    if "status" not in df.columns:
        return go.Figure()
    fail_rate = df["status"].str.contains("fail").mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=100 - fail_rate * 100,
        gauge={"axis": {"range": [0, 100]}},
        title={"text": "SLA %"}
    ))
    return fig

def mttr_trend(df, seed=None):
    _apply_seed(seed)
    df = df.copy()
    if "timestamp" not in df.columns:
        return go.Figure()
    df = df.sort_values("timestamp")
    df["mttr"] = np.abs(np.random.normal(20, 5, len(df)))
    fig = px.line(df, x="timestamp", y="mttr")
    return fig

def anomaly_timeline(df, seed=None):
    _apply_seed(seed)
    df = df.copy()
    if "timestamp" not in df.columns:
        return go.Figure()
    df = df.sort_values("timestamp")
    base = np.random.normal(0, 1, len(df))
    anomalies = np.abs(base) > 2
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=base, mode="lines", name="signal"))
    fig.add_trace(go.Scatter(
        x=df["timestamp"][anomalies],
        y=base[anomalies],
        mode="markers",
        marker=dict(size=10),
        name="anomaly"
    ))
    return fig

def ai_conf_hist(df, seed=None):
    _apply_seed(seed)
    if "ai_confidence" not in df.columns:
        return go.Figure()
    fig = px.histogram(df, x="ai_confidence", nbins=20)
    return fig

def correlation_matrix(df, seed=None):
    _apply_seed(seed)
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty:
        return go.Figure()
    fig = px.imshow(num_df.corr(), text_auto=True)
    return fig

def intervention_sankey(df, seed=None):
    _apply_seed(seed)
    if "issue_type" not in df.columns or "status" not in df.columns:
        return go.Figure()
    issue_counts = df["issue_type"].value_counts()
    status_counts = df["status"].value_counts()
    labels = list(issue_counts.index) + list(status_counts.index)
    source = list(range(len(issue_counts)))
    target = [len(issue_counts) + (0 if s.lower()=="fail" else 1) for s in df["status"]]
    value = [1] * len(df)
    fig = go.Figure(go.Sankey(
        node=dict(label=labels),
        link=dict(source=source * 2, target=target[: len(source) * 2], value=value[: len(source) * 2])
    ))
    return fig

def failure_probability_gauge(df, seed=None, override_value=None):
    _apply_seed(seed)
    if override_value is not None:
        prob = override_value
    else:
        if "status" not in df.columns:
            prob = 0
        else:
            prob = df["status"].str.contains("fail").mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        gauge={"axis": {"range": [0, 100]}},
        title={"text": "Failure Probability %"}
    ))
    return fig

def severity_execution_boxplot(df, seed=None):
    _apply_seed(seed)
    if "execution_time" not in df.columns or "severity" not in df.columns:
        return go.Figure()
    fig = px.box(df, x="severity", y="execution_time")
    return fig

def historical_comparison_panel(df, df_hist, seed=None):
    _apply_seed(seed)
    fail = df["status"].str.contains("fail").mean()
    hist = df_hist["status"].str.contains("fail").mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Current", "Historical"], y=[fail, hist]))
    return fig

def clustering_visualization(df, seed=None):
    _apply_seed(seed)
    if "execution_time" not in df.columns or "ai_confidence" not in df.columns:
        return go.Figure()
    data = df[["execution_time", "ai_confidence"]].dropna()
    if data.empty:
        return go.Figure()
    scaler = StandardScaler()
    X = scaler.fit_transform(data)
    n_clusters = min(4, len(X))
    if n_clusters < 2:
        return go.Figure()
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=seed)
    labels = km.fit_predict(X)
    fig = px.scatter(
        x=data["execution_time"],
        y=data["ai_confidence"],
        color=labels.astype(str),
        labels={"x": "execution_time", "y": "ai_confidence"}
    )
    return fig

def drift_detection_plot(df, df_hist, seed=None):
    _apply_seed(seed)
    a = df["execution_time"].dropna().values if "execution_time" in df else np.array([1])
    b = df_hist["execution_time"].dropna().values if "execution_time" in df_hist else np.array([1])
    if len(a) == 0: a = np.array([1])
    if len(b) == 0: b = np.array([1])
    drift = abs(a.mean() - b.mean())
    fig = go.Figure(go.Indicator(
        mode="number",
        value=drift,
        title={"text": "Execution Time Drift"}
    ))
    return fig
