# 📊 Research Report: AI-Augmented Self-Healing CI/CD Pipelines

## 1. Introduction

Modern DevOps workflows rely on Continuous Integration and Continuous Deployment (CI/CD) pipelines. While these pipelines improve software delivery speed, they often suffer from failures due to **dependency mismatches, test errors, missing environment variables, or misconfigurations**.  
Traditionally, engineers manually inspect logs and fix issues, which increases **Mean Time to Recovery (MTTR)** and can cause **SLA (Service Level Agreement) violations**.

This project implements a **Self-Healing CI/CD pipeline** enhanced by **AI log analysis** (via LangChain + OpenAI/HuggingFace). The system:

1. Detects failures in GitHub Actions CI/CD.
2. Parses logs into a structured format.
3. Uses an LLM to analyze the logs and suggest fixes.
4. Simulates automated healing actions (rollback, retries, env injection).
5. Provides a **Streamlit dashboard** for visualization.
6. Evaluates improvements in failure distribution, SLA compliance, and MTTR.

---

## 2. Methodology

- **CI/CD Setup**: GitHub Actions pipeline (`build → test → deploy`). Failures intentionally introduced for experimentation.
- **Log Parsing**: Structured logs (`structured_logs.csv`) generated from raw CI/CD logs.
- **AI Analysis**: Logs passed to **GPT / HuggingFace models** to suggest fixes (saved in `ai_analysis.json`).
- **Auto-Fix Simulation**: Scripts apply simulated recovery strategies.
- **Visualization**: Streamlit dashboard for real-time view; Jupyter Notebook for research analysis.

---

## 3. Results & Analysis

### 3.1 Failure Distribution (Before Healing)

The initial logs showed that **dependency errors and failing tests** were the most common failure types.

![Failure Distribution](results/failure_distribution.png)

---

### 3.2 SLA Compliance Improvement

- **SLA target**: pipeline step must finish in `< 15s`.
- **Before Healing**: SLA compliance = ~55%.
- **After Healing**: SLA compliance improved to ~80%.

This shows the **AI-assisted healing** reduced slow-running jobs and improved reliability.

![SLA Compliance](results/sla_compliance.png)

---

### 3.3 MTTR Trend (Recovery Speed)

- **Before Healing**: MTTR ~ 20–25 seconds.
- **After Healing**: MTTR reduced to ~12–15 seconds.

This indicates the self-healing system helps the pipeline recover faster from failures.

![MTTR Trend](results/mttr_trend.png)

---

### 3.4 AI-Generated Suggestions

The LLM provided actionable insights such as:

- **Dependency Error** → _“Rollback requirements.txt to stable version.”_
- **Unit Test Failure** → _“Fix or mock failing test.”_
- **Missing Environment Variable** → _“Inject default value or update CI secrets.”_

These were automatically surfaced in both the dashboard and logs.

---

## 4. Discussion

The results demonstrate that:

- **Failure patterns** can be identified automatically.
- **SLA compliance** improved by ~25%.
- **MTTR reduced** by ~40%.
- **AI log analysis** provides clear and actionable suggestions for developers.

While the auto-fixes here are **simulated**, in production they could integrate with:

- Package managers (pip, npm) for dependency rollbacks.
- GitHub API for automated PR fixes.
- Cloud APIs for container restarts and resource scaling.

---

## 5. Conclusion

This project successfully demonstrates an **AI-Augmented Self-Healing CI/CD Pipeline**.  
By combining **DevOps workflows** with **AI log analysis**, we achieve:

- Faster recovery from failures.
- Improved SLA compliance.
- Actionable insights for developers.

This approach bridges **AI & DevOps (AIDevOps)** — making pipelines more **robust, intelligent, and autonomous**.

---

## 6. Future Work

- Deploy auto-healing in a **real cloud-native environment** (e.g., AWS/GCP).
- Integrate **Prometheus + Grafana** for live monitoring.
- Extend auto-fixes to real dependency management and config patching.
- Benchmark different LLMs (OpenAI GPT vs HuggingFace Mistral/LLaMA) for log analysis.

---

## 7. References

- GitHub Actions Documentation
- LangChain Framework
- OpenAI & HuggingFace APIs
- BMU Course Handout: _AI and DevOps Workflows_
