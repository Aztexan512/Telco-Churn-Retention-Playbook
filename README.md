# Telecom Customer Churn – Cross-Industry Retention Playbook for Insurance

## Overview

This project builds a **telecom customer churn** model and then **translates the insights into an auto insurance context** (e.g., auto insurance). The goal is to show how a Senior/Lead Data Analyst can:

- Design a **realistic synthetic dataset** at scale  
- Build and explain a **churn prediction model**  
- Quantify **financial impact** of interventions  
- **Generalize** learnings from telecom (subscription business) to **personal lines insurance** (policyholder retention)

The core narrative:  
> “The same behaviors that drive telecom churn (pricing changes, early service friction, payment habits, channel mix) also drive insurance retention. Here’s a concrete, data-backed framework that transfers across industries.”

---

## Project Structure

```text
telecommunications-churn-analysis/
├── data/
│   ├── telco_churn_225k_v120.csv          # Synthetic dataset — run script 01 to generate (gitignored)
│   └── data_dictionary.md                 # Column-level documentation
├── notebooks/
│   ├── 01_synthetic_data_generation.py    # Generate synthetic dataset
│   ├── 02_eda_visualizations.py           # EDA + presentation-ready charts
│   ├── 03_model_training_explainability.py# XGBoost + SHAP explainability
│   ├── 04_modeling_and_lift_analysis.py   # Lift curve & decile analysis
│   └── 05_financial_impact.py             # CLTV & “what-if” save-rate scenarios
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


Synthetic Dataset Design
File: data/telco_churn_225k_v120.csv
Rows: 225,000 customers
Target: churn (0 = retained, 1 = churned)

The dataset is fully synthetic, but built to mimic real retention dynamics. Key design principles:

Scale & realism
225k customers to approximate a small slice of a large carrier base.
Distributions tuned to produce realistic churn patterns by:
Contract type (month-to-month vs term)
Promo vs. full rate
Service segment (internet-only, bundles, mobile, cable-only)
Early friction events (first 60 days)
Payment behavior (autopay vs manual)
Leakage-aware feature design
A small set of columns are intentionally excluded from ML features:
churn_score: latent synthetic driver of the target (used only to generate churn).
billing_risk_score: deterministic from payment/contract fields (dashboard only).
cltv: synthetic 24‑month contribution margin used for financial impact.
Transparent data contract
dataset_metadata_v120.json documents:
Version and generation timestamp
Target definition
Column-level notes (especially for derived/leakage-prone features)
Key Columns
Core Demographics & Tenure
customer_id: synthetic ID (e.g., 0000123-TEL)
gender: male / female
senior_citizen: 0 / 1
partner: yes / no
dependents: yes / no
tenure_months: 1–72 months
Contract & Billing
contract_type: month_to_month, one_year, two_year
paperless_billing: yes / no
payment_method:
electronic_check, mailed_check,
bank_transfer_auto, credit_card_auto
is_autopay: 1 if on automatic payment, else 0
Service Segments & Internet
service_segment:
internet_only
internet_plus_other
cable_only
mobile
internet_service: fiber, dsl, or no
(cable-only has no; other segments require internet)
phone_service, multiple_lines
Add-ons & Support
online_security, online_backup, device_protection, tech_support
streaming_tv, streaming_movies
Promo, Channel & Early Friction
is_on_promo: 1 on discounted promo, 0 otherwise
promo_discount_pct: magnitude of discount if on promo
sales_channel:
online, store, agent_call_center, third_party_retailer
first_60d_billing_call: 1 if billing call in first 60 days
billing_call_resolved: Int64 (<NA>, 0 = unresolved, 1 = resolved)
first_60d_tech_call: 1 if tech support call in first 60 days
tech_issue_resolved: Int64 (<NA>, 0 = unresolved, 1 = resolved)
Pricing & Revenue
monthly_charges: base monthly price (before promo)
monthly_charges_billed: actual billed amount (after promo, if active)
total_charges: piecewise calculation:
If on promo:
Promo rate for first 12 months, then full price thereafter
Else:
Full price across tenure
Financial/Scoring Columns (Non-ML Features)
estimated_margin_pct: synthetic margin percentage
cltv: monthly_charges * 24 * estimated_margin_pct
(approx. 24‑month contribution margin)
billing_risk_score: deterministic score from is_autopay, paperless_billing, and contract_type
churn_score: latent synthetic churn driver (not used as a feature)
churn: target (0/1)
Scripts
1. 01_synthetic_data_generation.py
Purpose:
Generate the synthetic telecom churn dataset and a JSON metadata file.

Key Steps:

Set global configuration:
N_CUSTOMERS, random seed, version
Simulate demographics, contract types, service segments, and channels
Enforce business logic:
Cable-only customers do not have internet
Non–cable-only segments always have internet (fiber or DSL)
Autopay is derived from payment method
Construct pricing:
Base internet pricing + add-ons + small noise
Promo discount applied to monthly_charges_billed
total_charges computed via promo-first, then full rate logic
Compute synthetic scores:
billing_risk_score (deterministic, dashboard-only)
cltv (for financial impact)
churn_score and churn_prob via a logistic transform
Sample the binary target churn from churn_prob
Save:
telco_churn_225k_v120.csv
dataset_metadata_v120.json
How to run:

bash
Copy
python notebooks/01_synthetic_data_generation.py
2. 02_eda_visualizations.py
Purpose:
Produce presentation-ready EDA figures using a consistent color palette (steel blue 900 / 500, white background, green for positive, red for negative).

Outputs (saved in reports/):

Presentation_Fig1_Drivers.png
Churn by contract type, internet service, and sales channel
Presentation_Fig2_Pricing.png
Churn by promo vs full rate
Churn by promo discount tier
Presentation_Fig3_Friction.png
Churn for customers with billing issues (resolved vs unresolved)
Churn for customers with tech issues (resolved vs unresolved)
Presentation_Fig4_TenureRisk.png
Churn by tenure bucket
Churn by autopay vs manual payment
Presentation_Fig5_Correlation.png
Correlation heatmap for key numeric drivers + churn
Highlights:

All plots use:
White background
Steel Blue 900 for main labels/titles
Steel Blue 500 / Blues for secondary series
Green for “good” (e.g., resolved issues, autopay)
Red for “bad” (e.g., unresolved issues)
Churn rates shown in percent, with labeled bars.
How to run:

bash
Copy
python notebooks/02_eda_visualizations.py
3. 03_model_training_explainability.py
Purpose:
Train a churn prediction model and explain it in plain business terms.

Approach:

Train / test split
XGBoost classifier
Proper feature set that excludes:
churn_score, billing_risk_score, cltv, and any obvious leakage fields
Evaluate:
ROC AUC, lift, and calibration
Interpretability:
Global feature importance (model-native)
SHAP summary, beeswarm, and global importance plots
This script powers the “modeling” section of the story:

“Here’s how well we can predict churn before it happens, and here’s what the model says are the top drivers.”

4. 05_financial_impact.py
Purpose:
Translate churn insights into dollars and headcount via a simple CLTV-based simulation.

Key Logic:

Define friction-driven churners:
Customers who churned AND had an unresolved billing or tech issue in the first 60 days.
Quantify:
Number of friction churners
Their share of total churn
Total and average CLTV at risk
Run a scenario simulation:
For save rates from 5% to 50%, compute:
Number of friction churners “saved”
Total CLTV retained
Highlight a 20% save rate scenario as a realistic program target and visualize it.
Output:

Console summary:
Counts, shares, CLTV at risk, and interpretation
Chart:
Financial_Impact_CLTV_Simulation.png – bar chart of CLTV retained by save rate
(20% bar highlighted in green as the target scenario)
How to run:

bash
Copy
python notebooks/05_financial_impact.py
Telecom → Insurance Translation
Although the dataset and scripts are telecom-flavored, many drivers map directly into insurance retention levers:

Telecom Concept	Insurance Analogue
Contract type (month-to-month vs term)	Policy term / renewal structure
Promo discount & promo end	Intro rates vs. renewal price changes (“rate disruption”)
Early billing/tech friction	Early claims/billing/underwriting friction
Sales channel	Agent vs. direct vs. online aggregator
Autopay & paperless billing	EFT, automatic renewal, e-delivery
Streaming/add-on bundles	Multi-product bundling (auto + home + renters + toys)
Tenure buckets	Policy age / tenure segments
CLTV & save-rate simulation	Premium-at-risk & retention program ROI
In a portfolio or interview, this becomes a discussion slide:

“Here’s what drove churn in telecom, and here is how I’d operationalize that thinking in an auto insurance setting (e.g., Progressive).”

## Financial Impact & Business Case

A predictive model is only as valuable as the revenue it protects. This phase translates the model's findings into a **24-month Contribution Margin (CLTV)** simulation to quantify the cost of "Service Friction" and the ROI of a retention program.

### The "Friction Churn" Segment
By cross-referencing the model's top drivers with customer support data, we identified a high-risk segment: **Friction Churners**. These are customers who churned and had at least one **unresolved** billing or technical issue within their first 60 days.

- **Friction-Driven Churners:** 19,147 customers (16.7% of total churn)
- **Average 24-Month CLTV per Customer:** ~$1,695
- **Total Value at Risk:** **$32.45 Million**

### "What-If" Retention Simulation
We simulated the financial upside of a "Rapid Resolution" task force designed to intervene and resolve these early friction points before the customer churns.

| Program Save Rate | Customers Retained | 24-Month CLTV Retained |
|-------------------|--------------------|------------------------|
| 5% (Conservative) | 957                | $1.62 Million          |
| 10% (Moderate)    | 1,914              | $3.24 Million          |
| **20% (Target)**  | **3,829**          | **$6.49 Million**      |
| 50% (Aggressive)  | 9,573              | $16.22 Million         |

**Strategic Takeaway for Insurance:**  
By identifying the ~$6.5M upside of a 20% save rate in telecom, we create a blueprint for Progressive. We can apply this same logic to "Early Policy Friction" (e.g., underwriting delays or billing setup issues) to quantify the premium-at-risk and justify the headcount for specialized retention teams.


Technical Stack
Language: Python (3.x)
Core Libraries:
pandas, numpy
matplotlib, seaborn
Planned for Modeling:
scikit-learn
xgboost (or similar gradient boosting library)
SHAP or similar explainability tools
How to Reproduce
Clone the repo or download this project.
Create and activate a virtual environment (optional but recommended).
Install dependencies:
bash
Copy
pip install -r requirements.txt
Generate the dataset:
bash
Copy
python notebooks/01_synthetic_data_generation.py
Run EDA and export charts:
bash
Copy
python notebooks/02_eda_visualizations.py
Train model and run explainability (once 03_model_training_explainability.py is added).
Run financial impact scenarios:
bash
Copy
python notebooks/05_financial_impact.py
Why This Project for a Senior/Lead Analyst Role
This project is designed to showcase:

End-to-end ownership: data design → modeling → financial impact → storytelling
Cross-industry thinking: how to port a churn framework from telecom to insurance
Strategic focus: early friction, pricing changes, channel performance, and payment behavior
Executive-ready outputs: clean visuals, CLTV simulations, and clear translation to business levers
It is intentionally modular, so it can be:

Walked through live in an interview
Paired with a slide deck
Extended into a more formal case study