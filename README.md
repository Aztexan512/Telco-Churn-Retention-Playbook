# Telecom Customer Churn — Cross-Industry Retention Playbook

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-latest-F7931E?logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-latest-189AB4?logo=xgboost&logoColor=white)
![SHAP](https://img.shields.io/badge/SHAP-explainability-lightgrey)
![License](https://img.shields.io/badge/License-MIT-2E7D32)

---

## Live Dashboard

[Telecom Churn - Retention Dashboard]([https://your-app-url.streamlit.app](https://jba3qjyqv25gztqbzkgwxu.streamlit.app/)

---

## Project Summary

This project builds an end-to-end **telecom customer churn prediction system** and translates its findings into a retention framework applicable to **auto insurance**. It demonstrates how a Senior/Lead Data Analyst can own the full analytical lifecycle — from synthetic dataset design through ML modeling, SHAP explainability, and executive-ready financial impact quantification.

The core narrative:
> *"The same behaviors that drive telecom churn — pricing changes, early service friction, payment habits, channel mix — also drive insurance non-renewal. Here's a concrete, data-backed framework that transfers across industries."*

**What's included:**
- A 225,000-row synthetic dataset engineered to mirror real retention dynamics
- XGBoost churn model with full SHAP explainability (AUC = 0.84)
- Lift and decile analysis translating model performance into operational targeting efficiency
- A $32.45M CLTV-at-risk simulation quantifying the ROI of a retention intervention program
- A live Streamlit dashboard for interactive exploration

---

## Business Problem

Customer churn is one of the highest-leverage problems in subscription and recurring-revenue businesses. The challenge is not identifying that churn happens — it's answering three operational questions:

1. **Who** is most likely to churn, and how confident are we?
2. **Why** are they churning — and which drivers are actionable?
3. **What is the financial case** for investing in retention, and how do we size the program?

This project addresses all three. In telecom, the annual cost of churn is measured in lost subscriber revenue. In personal lines insurance, the analogue is **premium non-renewal** — policyholders who don't renew at term, representing lost premium and the acquisition cost of replacement.

The specific operational focus here is **early friction churn**: customers who leave because of an unresolved billing or technical issue in their first 60 days. This segment is:
- **Identifiable in real-time** — the signal appears within 60 days of acquisition
- **Preventable** — resolution rate, not issue occurrence, is the lever
- **Directly translatable** to insurance (underwriting delays, first-payment failures, claims friction)

---

## Key Findings

### Model Performance
| Metric | Value |
|---|---|
| ROC AUC (20% holdout) | **0.84** |
| Top decile lift | **1.84×** the average churn rate |
| Recall at top 20% | **35.2%** of all churners captured |

Targeting the highest-risk 20% of customers captures more than a third of all future churners — **1.76× better than random outreach**.

### Top Churn Drivers — SHAP Feature Importance
| Rank | Feature | Business Interpretation |
|---|---|---|
| 1 | `contract_type_month_to_month` | Dominant driver — no lock-in means high flight risk |
| 2 | `is_autopay` | Manual payers churn at ~2× the rate of autopay customers |
| 3 | `internet_service_fiber` | Fiber markets are competitive; customers have more alternatives |
| 4 | `is_on_promo` | Promo customers are price-sensitive; they leave when discounts end |
| 5 | `tenure_months` | Short-tenure customers carry the highest risk (first 12 months) |
| 6 | `first_60d_tech_call` | Early friction signal — unresolved tech issues predict churn |
| 7 | `first_60d_billing_call` | Early friction signal — unresolved billing issues predict churn |

### Financial Impact — Friction Churn Segment
| Metric | Value |
|---|---|
| Friction-driven churners | **19,147** customers (16.7% of total churn) |
| Average 24-month CLTV | **~$1,695** per customer |
| Total CLTV at risk | **$32.45 million** |
| CLTV retained at 20% save rate | **$6.49 million** |

---

## Technical Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Dashboard | Streamlit 1.35+, Plotly 5.x |
| Modeling | XGBoost, scikit-learn (Pipeline, train/test split, metrics) |
| Explainability | SHAP (TreeExplainer, beeswarm, global importance) |
| Data | pandas, NumPy |
| Visualization | Matplotlib, Seaborn |

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the dashboard:**
```bash
streamlit run app.py
```

---

## Project Structure

```text
telecommunications-churn-analysis/
├── data/
│   ├── telco_churn_225k_v120.csv          # Synthetic dataset — run notebook 01 to generate (gitignored)
│   └── data_dictionary.md                 # Column-level documentation
├── notebooks/
│   ├── 01_synthetic_data_generation.ipynb # Generate the 225k synthetic dataset
│   ├── 02_eda_visualizations.ipynb        # EDA + presentation-ready charts
│   ├── 03_model_training_explainability.ipynb  # XGBoost + SHAP explainability
│   ├── 04_modeling_and_lift_analysis.ipynb     # Lift curve & decile analysis
│   └── 05_financial_impact.ipynb          # CLTV & "what-if" save-rate scenarios
├── reports/
│   ├── Model_ConfusionMatrix.png
│   ├── Model_ROC_Curve.png
│   ├── Model_SHAP_Summary.png
│   ├── Model_SHAP_Beeswarm.png
│   ├── Model_SHAP_GlobalImportance.png
│   ├── Model_Cumulative_Gain_Final.png
│   ├── Model_Decile_Lift_Final.png
│   ├── Financial_Impact_CLTV_Simulation.png
│   └── Luciano_Casillas_Retention_Analytics_Case_Study.pdf
├── .streamlit/
│   └── config.toml                        # Streamlit theme config
├── app.py                                 # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## Synthetic Dataset Design

**File:** `data/telco_churn_225k_v120.csv` · **Rows:** 225,000 · **Target:** `churn` (0 = retained, 1 = churned)

The dataset is fully synthetic, built to mimic real retention dynamics. Key design principles:

**Scale & realism** — 225k customers approximate a meaningful slice of a large carrier's subscriber base. Churn distributions are tuned by contract type, promo status, service segment, early friction events, and payment behavior.

**Leakage-aware feature design** — three columns are intentionally excluded from ML features:
- `churn_score` — latent synthetic driver of the target variable
- `billing_risk_score` — deterministic from payment/contract fields (dashboard use only)
- `cltv` — 24-month contribution margin (financial impact use only)

### Key Column Groups

| Group | Columns |
|---|---|
| Demographics & tenure | `gender`, `senior_citizen`, `partner`, `dependents`, `tenure_months` |
| Contract & billing | `contract_type`, `paperless_billing`, `payment_method`, `is_autopay` |
| Service & internet | `service_segment`, `internet_service`, `phone_service`, add-ons, streaming |
| Promo & channel | `is_on_promo`, `promo_discount_pct`, `sales_channel` |
| Early friction (60-day) | `first_60d_billing_call`, `billing_call_resolved`, `first_60d_tech_call`, `tech_issue_resolved` |
| Pricing | `monthly_charges`, `monthly_charges_billed`, `total_charges` |
| Financial / scoring (non-ML) | `cltv`, `billing_risk_score`, `churn_score` |

---

## Financial Impact & Business Case

### The "Friction Churn" Segment

By cross-referencing the model's top drivers with support data, we identified **Friction Churners**: customers who churned and had at least one unresolved billing or tech issue within their first 60 days.

- **Friction-Driven Churners:** 19,147 customers (16.7% of total churn)
- **Average 24-Month CLTV:** ~$1,695 per customer
- **Total CLTV at Risk:** $32.45 Million

### "What-If" Retention Simulation

| Program Save Rate | Customers Retained | 24-Month CLTV Retained |
|---|---|---|
| 5% (Conservative) | 957 | $1.62 Million |
| 10% (Moderate) | 1,914 | $3.24 Million |
| **20% (Target)** | **3,829** | **$6.49 Million** |
| 50% (Aggressive) | 9,573 | $16.22 Million |

---

## Telecom → Insurance Translation

| Telecom Concept | Insurance Analogue |
|---|---|
| Contract type (month-to-month vs term) | Policy term / renewal structure |
| Promo discount & promo end | Intro rates vs. renewal price changes ("rate disruption") |
| Early billing/tech friction | Early claims/billing/underwriting friction |
| Sales channel | Agent vs. direct vs. online aggregator |
| Autopay & paperless billing | EFT, automatic renewal, e-delivery |
| Streaming/add-on bundles | Multi-product bundling (auto + home + renters) |
| Tenure buckets | Policy age / tenure segments |
| CLTV & save-rate simulation | Premium-at-risk & retention program ROI |

---

## How to Reproduce

```bash
# 1. Clone and install
git clone https://github.com/Aztexan512/Telco-Churn-Retention-Playbook.git
cd Telco-Churn-Retention-Playbook
pip install -r requirements.txt

# 2. Generate the synthetic dataset
jupyter notebook notebooks/01_synthetic_data_generation.ipynb

# 3. Run EDA
jupyter notebook notebooks/02_eda_visualizations.ipynb

# 4. Train model + SHAP explainability
jupyter notebook notebooks/03_model_training_explainability.ipynb

# 5. Lift & decile analysis
jupyter notebook notebooks/04_modeling_and_lift_analysis.ipynb

# 6. Financial impact simulation
jupyter notebook notebooks/05_financial_impact.ipynb

# 7. Launch the dashboard
streamlit run app.py
```
