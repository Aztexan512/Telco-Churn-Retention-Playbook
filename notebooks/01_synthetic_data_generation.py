import pandas as pd
import numpy as np
import json
from datetime import datetime

# ==========================================
# CONFIGURATION / CONSTANTS BLOCK (v1.2.0)
# ==========================================
N_CUSTOMERS = 225_000
SEED = 42
VERSION = "1.2.0"

# Contract Distribution
P_CONTRACT = [0.55, 0.25, 0.20]  # month_to_month, one_year, two_year
CONTRACT_TYPES = ["month_to_month", "one_year", "two_year"]

# Service Segment Distribution
P_SEGMENT = [0.30, 0.40, 0.15, 0.15]  # internet_only, internet_plus_other, cable_only, mobile
SEGMENTS = ["internet_only", "internet_plus_other", "cable_only", "mobile"]

# Churn Logic Thresholds
CHURN_SIGMOID_THRESHOLD = 45
CHURN_LOGISTIC_SCALE = 12

# Pricing
BASE_MONTHLY_FIBER = 70.0
BASE_MONTHLY_DSL = 45.0
PROMO_DISCOUNT_AVG = 0.25

# ==========================================
# GENERATION START
# ==========================================
np.random.seed(SEED)

# 1. Basic Demographics & Tenure
customer_id = [f"{i:07d}-TEL" for i in range(N_CUSTOMERS)]
gender = np.random.choice(["male", "female"], N_CUSTOMERS)
senior_citizen = np.random.choice([0, 1], N_CUSTOMERS, p=[0.84, 0.16])
partner = np.random.choice(["yes", "no"], N_CUSTOMERS)
dependents = np.random.choice(["yes", "no"], N_CUSTOMERS, p=[0.3, 0.7])
tenure_months = np.random.randint(1, 73, N_CUSTOMERS)

# 2. Contract & Billing Setup
contract = np.random.choice(CONTRACT_TYPES, N_CUSTOMERS, p=P_CONTRACT)
paperless_billing = np.random.choice(["yes", "no"], N_CUSTOMERS, p=[0.6, 0.4])
payment_method = np.random.choice(
    ["electronic_check", "mailed_check", "bank_transfer_auto", "credit_card_auto"],
    N_CUSTOMERS, p=[0.34, 0.23, 0.22, 0.21]
)
is_autopay = np.where(np.isin(payment_method, ["bank_transfer_auto", "credit_card_auto"]), 1, 0)

# 3. Service Segments & Internet Logic
# internet_only, internet_plus_other, and mobile MUST have internet.
# cable_only does NOT have internet.
service_segment = np.random.choice(SEGMENTS, N_CUSTOMERS, p=P_SEGMENT)

internet_service = []
for s in service_segment:
    if s == "cable_only":
        internet_service.append("no")
    else:
        internet_service.append(np.random.choice(["fiber", "dsl"], p=[0.7, 0.3]))
internet_service = np.array(internet_service)

# 4. Phone & Add-ons
phone_service = np.where(np.isin(service_segment, ["internet_plus_other", "mobile"]), "yes", "no")
multiple_lines = np.where(
    phone_service == "yes",
    np.random.choice(["no", "yes", "no_phone_service"], N_CUSTOMERS, p=[0.5, 0.4, 0.1]),
    "no_phone_service",
)

# Security/Backup/Support (Only for Internet customers)
online_security = np.where(
    internet_service != "no",
    np.random.choice(["no", "yes"], N_CUSTOMERS, p=[0.7, 0.3]),
    "no_internet_service",
)
online_backup = np.where(
    internet_service != "no",
    np.random.choice(["no", "yes"], N_CUSTOMERS, p=[0.6, 0.4]),
    "no_internet_service",
)
device_protection = np.where(
    internet_service != "no",
    np.random.choice(["no", "yes"], N_CUSTOMERS, p=[0.6, 0.4]),
    "no_internet_service",
)
tech_support = np.where(
    internet_service != "no",
    np.random.choice(["no", "yes"], N_CUSTOMERS, p=[0.7, 0.3]),
    "no_internet_service",
)

# Streaming
streaming_tv = np.where(
    internet_service != "no",
    np.random.choice(["no", "yes"], N_CUSTOMERS, p=[0.5, 0.5]),
    "no_internet_service",
)
streaming_movies = np.where(
    internet_service != "no",
    np.random.choice(["no", "yes"], N_CUSTOMERS, p=[0.5, 0.5]),
    "no_internet_service",
)

# 5. Strategic Columns (Promo, Channel, Friction)
sales_channel = np.random.choice(
    ["online", "store", "agent_call_center", "third_party_retailer"],
    N_CUSTOMERS,
    p=[0.4, 0.25, 0.25, 0.1],
)

is_on_promo = np.random.choice([1, 0], N_CUSTOMERS, p=[0.35, 0.65])
promo_discount_pct = np.where(
    is_on_promo == 1,
    np.random.choice([0.1, 0.2, 0.3, 0.5], N_CUSTOMERS),
    0.0,
)

# Friction Events (First 60 Days)
first_60d_billing_call = np.random.choice([1, 0], N_CUSTOMERS, p=[0.15, 0.85])
billing_call_resolved = np.where(
    first_60d_billing_call == 1,
    np.random.choice([1, 0], N_CUSTOMERS, p=[0.7, 0.3]),
    np.nan,
)

first_60d_tech_call = np.random.choice([1, 0], N_CUSTOMERS, p=[0.12, 0.88])
tech_issue_resolved = np.where(
    first_60d_tech_call == 1,
    np.random.choice([1, 0], N_CUSTOMERS, p=[0.6, 0.4]),
    np.nan,
)

# 6. Pricing & Total Charges (Piecewise Logic)
monthly_charges = np.where(internet_service == "fiber", BASE_MONTHLY_FIBER, BASE_MONTHLY_DSL)
monthly_charges = np.where(internet_service == "no", 30.0, monthly_charges)  # cable only base

# Add variability for add-ons
monthly_charges += (streaming_tv == "yes").astype(int) * 15.0
monthly_charges += (streaming_movies == "yes").astype(int) * 15.0
monthly_charges += (phone_service == "yes").astype(int) * 10.0
monthly_charges += np.random.normal(0, 3, N_CUSTOMERS)  # small noise
monthly_charges = np.round(np.clip(monthly_charges, 20.0, 150.0), 2)

# Billed amount (with promo if active)
monthly_charges_billed = np.where(
    is_on_promo == 1,
    monthly_charges * (1 - promo_discount_pct),
    monthly_charges,
)

# Total Charges Calculation (Piecewise)
promo_duration = 12
total_charges = []
for i in range(N_CUSTOMERS):
    t = tenure_months[i]
    full_rate = monthly_charges[i]
    if is_on_promo[i] == 1:
        p_rate = monthly_charges_billed[i]
        if t <= promo_duration:
            total = p_rate * t
        else:
            total = (p_rate * promo_duration) + (full_rate * (t - promo_duration))
    else:
        total = full_rate * t
    total_charges.append(round(total, 2))

# 7. Derived Scores
# NOTE: billing_risk_score is deterministic from existing columns.
# Intended for segmentation/dashboard use only. Excluded from ML features.
risk_score = (
    (is_autopay == 0) * 40
    + (paperless_billing == "no") * 20
    + (contract == "month_to_month") * 40
)
billing_risk_score = risk_score.astype(int)

# NOTE: cltv is derived from monthly_charges × 24 × estimated_margin_pct.
# Represents estimated 24-month contribution margin.
# Excluded from ML features; intended for business segmentation and dashboard use only.
estimated_margin_pct = np.round(np.random.uniform(0.15, 0.35, N_CUSTOMERS), 4)
cltv = np.round(monthly_charges * 24 * estimated_margin_pct, 2)

# 8. Churn Probability Logic (Synthetic Driver)
# NOTE: churn_score is the synthetic driver of the target variable.
# Excluded from ML features to prevent leakage.
churn_score = np.zeros(N_CUSTOMERS)
churn_score += (contract == "month_to_month") * 35
churn_score += (is_on_promo == 1) * 10
churn_score += (internet_service == "fiber") * 15
churn_score += (is_autopay == 0) * 12
churn_score += (first_60d_billing_call == 1) * 10
churn_score += (billing_call_resolved == 0) * 25
churn_score += (tech_issue_resolved == 0) * 20
churn_score += (tenure_months < 12) * 15
churn_score += (senior_citizen == 1) * 5
churn_score += np.random.normal(0, 10, N_CUSTOMERS)
churn_score = np.clip(churn_score, 0, 100)

# Sigmoid Churn Probability
sigmoid = lambda x: 1 / (1 + np.exp(-(x - CHURN_SIGMOID_THRESHOLD) / CHURN_LOGISTIC_SCALE))
churn_prob = sigmoid(churn_score)
churn = np.random.binomial(1, churn_prob)

# 9. Assemble DataFrame
df = pd.DataFrame({
    "customer_id": customer_id,
    "gender": gender,
    "senior_citizen": senior_citizen,
    "partner": partner,
    "dependents": dependents,
    "tenure_months": tenure_months,
    "phone_service": phone_service,
    "multiple_lines": multiple_lines,
    "internet_service": internet_service,
    "online_security": online_security,
    "online_backup": online_backup,
    "device_protection": device_protection,
    "tech_support": tech_support,
    "streaming_tv": streaming_tv,
    "streaming_movies": streaming_movies,
    "service_segment": service_segment,
    "contract_type": contract,
    "paperless_billing": paperless_billing,
    "payment_method": payment_method,
    "monthly_charges": np.round(monthly_charges, 2),
    "monthly_charges_billed": np.round(monthly_charges_billed, 2),
    "total_charges": total_charges,
    "is_on_promo": is_on_promo,
    "promo_discount_pct": promo_discount_pct,
    "sales_channel": sales_channel,
    "first_60d_billing_call": first_60d_billing_call,
    "billing_call_resolved": billing_call_resolved,
    "first_60d_tech_call": first_60d_tech_call,
    "tech_issue_resolved": tech_issue_resolved,
    "is_autopay": is_autopay,
    "estimated_margin_pct": np.round(estimated_margin_pct, 4),
    "cltv": cltv,
    "billing_risk_score": billing_risk_score,
    "churn_score": np.round(churn_score, 2),
    "churn": churn.astype("int64"),
})

# Nullable flags for resolution columns
df["billing_call_resolved"] = df["billing_call_resolved"].astype("Int64")
df["tech_issue_resolved"] = df["tech_issue_resolved"].astype("Int64")

file_name = "telco_churn_225k_v120.csv"
df.to_csv(file_name, index=False)

# ==========================================
# METADATA / DATA CONTRACT
# ==========================================
metadata = {
    "filename": file_name,
    "version": VERSION,
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "row_count": int(N_CUSTOMERS),
    "random_seed": SEED,
    "column_convention": "snake_case",
    "target_column": {
        "name": "churn",
        "dtype": "int64",
        "encoding": "0 = retained, 1 = churned",
    },
    "notes": {
        "churn_score": "Synthetic driver of the target variable. Excluded from ML features to prevent leakage.",
        "billing_risk_score": "Deterministic score derived from is_autopay, paperless_billing, and contract_type. Dashboard use only; excluded from ML features.",
        "cltv": "Derived column: monthly_charges × 24 × estimated_margin_pct. Represents estimated 24-month contribution margin. Excluded from ML features.",
        "billing_call_resolved": "Nullable Int64. <NA> = no billing call in first 60 days. 0 = unresolved. 1 = resolved.",
        "tech_issue_resolved": "Nullable Int64. <NA> = no tech call in first 60 days. 0 = unresolved. 1 = resolved.",
        "total_charges": "Piecewise calculation: promo_rate for first 12 months when is_on_promo = 1, then full monthly_charges thereafter.",
    },
}

with open("dataset_metadata_v120.json", "w") as f:
    json.dump(metadata, f, indent=4)

print(f"Generated {file_name} with {N_CUSTOMERS:,} rows.")
print("Target value counts (churn):\n", df["churn"].value_counts())