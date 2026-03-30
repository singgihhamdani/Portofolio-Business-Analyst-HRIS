# How I Automated HR Operations & Saved 85% of Administrative Time using Python & Google Apps Script

*By Singgih Hamdani Ma'ruf | Data & System Analyst | Business Process Optimizer*

Have you ever looked at your Human Resources (HR) department and wondered why they are drowning in spreadsheets? From tracking daily attendance, calculating monthly overtime, to chasing down recruitment pipelines—the modern HR team is often paralyzed by repetitive administrative tasks. 

In this case study, I will break down exactly how I engineered an end-to-end **HR Analytics & Automation System** for a mid-sized tech company. By adopting a "Cloud-Native Lightweight" mindset, I transformed scattered CSV files and manual data entry into a centralized, automated powerhouse using **Python, Plotly**, and **Google Apps Script (GAS)**.

---

## 🛑 The Pain Points: Identifying the "Why"

Before writing a single line of code, I drafted a comprehensive **Business Requirement Document (BRD)**. Interviews with the HR stakeholders revealed three critical bottlenecks:

1. **The Overtime Bleed:** Management had no visibility into which departments were burning the budget on overtime pay. The calculation was done manually every month-end.
2. **"Ghost" Lateness:** Employees who were consistently late slipped under the radar unless a manager explicitly requested an attendance audit. There was no proactive tracking.
3. **The Recruitment Blackhole:** Candidates were getting stuck in the "Screening" phase for weeks. Without an intervention system, top talents were snatched by competitors.

**The Goal:** Build an automated pipeline that ingests data, flags anomalies proactively (without human intervention), and delivers a secure visual dashboard for C-Level executives.

---

## 🏗️ The Architectural Solution: Hybrid & Lightweight

Instead of jumping straight into expensive Enterprise Resource Planning (ERP) software, I proposed a lightweight MVP (*Minimum Viable Product*) stack:

*   **Google Sheets / CSV Master (Storage):** A flexible, universal data adapter that acts as our central database.
*   **Google Apps Script (The Watchdog):** An event-driven Javascript engine running on Google's cloud. It acts as our automated ETL (*Extract, Transform, Load*) and Alerting system via CRON Jobs.
*   **Python + Pandas + Plotly (Analytics Engine):** The heavy-lifter. Python runs complex Calculus (turnover rates, time-to-hire averages) that would otherwise freeze Google Sheets.

> **💡 The Architectural "AHA!" Moment**
> One specific challenge was **Role-Based Access Control (RBAC)**. Python Jupyter Notebooks are great for Data Scientists, but they are dangerous for executives who just want to see charts without accidentally breaking the source code.
> **The Fix:** I designed a Python script (`export_dashboard.py`) that completely separates the Analytics Engine from the Presentation Layer. It renders the Plotly charts and injects them into a **Standalone Single-Page HTML Application**. Directors get a beautiful, interactive "Clean Corporate" dashboard file that works natively in the browser without requiring Python installation!

---

## 🚀 The Execution: System in Action

### 1. Proactive Alerts via Google Apps Script
I programmed a `CRON Job` to run at `08:30 AM` every morning. The script scans the incoming biometric attendance log. If an employee accumulates more than **3 late check-ins** in a single week, GAS automatically structures an HTML email and shoots a warning directly to their Department Head. It also checks the Recruitment pipeline for candidates stagnating for >5 days.
*Result: Zero manual audit required. Discipline is enforced dynamically.*

### 2. Overhaul of The Executive Dashboard
Using `Pandas` and `Plotly`, I generated a dashboard that updates instantly. Let's look at the actionable insights derived from the mock dataset:

*   **The Cost Optimization Insight:** The visualization instantly revealed that the **Tech & Operations departments** were consistently racking up >500 hours of overtime monthly. 
    * *Business Decision:* It is mathematically cheaper to hire 2 new full-time Junior Backend Developers than to continue paying punishing overtime rates for an exhausted current team.
*   **The Pipeline Bottleneck:** The *Recruitment Funnel* chart exposed a massive 60% drop-off rate between the `Screening` and `Interview` stages.
    * *Business Decision:* The recruitment team was instructed to tighten up the initial Job Posting criteria. They were receiving too many unqualified "spam" applicants, which wasted screening time.

### 3. One-Click Payroll Export (FR-04)
I automated the monthly Payroll wrap-up. A Python module (`build_notebook.py`) cleans daily absences, calculcates total valid overtime minutes, and exports a clean `payroll_ready_export.csv` bridging directly into our 3rd-party payroll gateway.
*Result: A process that traditionally took 3-4 days of manual VLOOKUPs now takes 3 seconds.*

---

## 📊 Business Impact & Conclusion

By treating HR operations not just as an administrative burden, but as a Data Engineering challenge, the resulting system delivered massive ROI:

1. **85% Reduction in Admin Time:** Reporting tasks and anomaly tracking were fully automated.
2. **Cost Containment:** Exposed hidden Overtime drains, allowing management to make data-driven hiring decisions rather than emotional ones.
3. **Scalability:** The architecture is perfectly primed. When the data exceeds Google Sheets' capacity, the logic can be ported 1:1 into PostgreSQL and Apache Airflow.

*Building dashboards is easy. Building systems that solve actual business bleeding points is where the true value of a System Analyst shines.* 

---
👉 **Curious about the code or the BRD?** Check out the full source code, Technical Documentation, and the Interactive Dashboard output in my GitHub Repository: [Portofolio-Business-Analyst-HRIS](https://github.com/singgihhamdani/Portofolio-Business-Analyst-HRIS)
