# 🚀 AI-Driven Self-Healing CI/CD Pipeline with Real-Time Monitoring Dashboard

### Autonomous Fault Detection, Debugging & Recovery for Continuous Delivery

This project introduces an **AI-powered Self-Healing CI/CD pipeline** designed to automatically **detect, diagnose, and repair** code-level faults within modern DevOps environments—reducing manual intervention, minimizing downtime, and improving deployment reliability.  
The framework integrates **ML-based anomaly detection**, **LLM-based automated code repair**, and a **Streamlit real-time dashboard** for visibility and analytics.


---

## 🌟 Key Features

- 🤖 **AI-powered fault detection & debugging** using log analysis, anomaly detection & Random Forest classification
- 🛠 **LLM-driven code patching & automatic retesting loop**
- 🔁 **Closed feedback loop for continuous learning & recovery**
- 📊 **Real-time Streamlit dashboard** with SLA metrics, error analytics & pipeline telemetry
- 🧠 **Self-healing loop for automated rollback, patching & redeployment**
- 🧱 **Modular microservice-based architecture compatible with GitHub Actions**

---

## 🧠 System Workflow

The workflow includes the automated recovery loop from fault detection to dashboard visualization.  
It includes: commit → pipeline execution → anomaly detection → AI fix suggestion → auto retest → dashboard update.  

---

## 📈 Performance Results

| Metric | Result |
|--------|--------|
| 🔧 Automatic Fix Success Rate | **90%** |
| ⏱ Mean Time to Recovery | **10.9 seconds** |
| 🧩 Fault Types Covered | Syntax, Import, Logic, Runtime, API Timeout |
| 📉 Pipeline Downtime Reduction | **−77.6%** |
| 🎯 Improvement vs Manual Debugging | **+28.6% higher success rate** |

> Validated against 10 real failure scenarios, where **9 out of 10 errors were fully repaired automatically.**

---

## 📊 Real-Time Monitoring Dashboard

The Streamlit dashboard visualizes:

- Active vs recovered failures
- Recovery timeline & MTTR trend
- AI intervention rate & fix-history logs
- Error type distribution
- Confidence scores for AI suggestions  

---

## 🏗 Tech Stack

| Category | Tools |
|----------|-------|
| CI/CD | GitHub Actions |
| AI/ML | PyTorch, TensorFlow, Scikit-Learn, GPT-based LLM |
| Monitoring | Streamlit, Plotly |
| DevOps Runtime | Docker, Kubernetes |
| Testing | PyTest |
| Storage | MongoDB / SQLite |

---

## 📌 Architecture Components

- **Fault Detector** – anomaly detection via Autoencoder & Random Forest model
- **AI Code Suggester** – LLM-based repair system reading logs & stack traces
- **Self-Healing Engine** – applies patch & validates using automated tests
- **Log Analytics Layer** – tracks incidents for model improvement
- **Dashboard** – observes pipeline status & SLA compliance

---

## 🧪 Experimental Evaluation

| Improvement Metric | Baseline | Self-Healing System |
|--------------------|-----------|---------------------|
| Mean Recovery Time | 48.6s | **10.9s** |
| Success Rate | 70% | **90%** |
| Downtime | 35.2s | **8.1s** |

---

## 🎯 Use Cases

- Enterprise CI/CD acceleration & reliability
- Production-scale microservices deployments
- Autonomous DevOps environments without manual debugging
- Mission-critical systems (FinTech, Healthcare, Cloud Infra)
