# Data Dictionary – Synthetic Telco/Insurance Churn Dataset (`telco_churn_225k_v120.csv`)

This dataset simulates a 225k-customer subscription base designed to mirror key dynamics of **personal lines insurance** using a **telecom-style churn framework**. Each row represents a single active or churned customer at a snapshot in time.

---

## Identification & Core Outcome

### `customer_id`
- **Type:** string
- **Description:** Unique identifier for each customer. No business meaning; used only for tracking and joins.

### `churn`
- **Type:** integer (0/1)
- **Description:** Target variable.  
  - `1` = customer churned within the prediction window  
  - `0` = customer remained active
- **Notes:** All modeling and lift/gain analysis is built to predict this outcome.

---

## Tenure & Lifecycle

### `tenure_months`
- **Type:** integer
- **Description:** Number of months the customer has been with the company.
- **Notes:** Short-tenure customers are typically more volatile, especially if they encounter early service friction.

### `contract_type`
- **Type:** categorical (`"Month-to-Month"`, `"One Year"`, `"Two Year"`)
- **Description:** Contract structure governing renewal and pricing.
- **Notes (Insurance Translation):**
  - `"Month-to-Month"` ~ Legacy / non-12‑month terms
  - `"One Year"` / `"Two Year"` ~ 12‑month policy terms with more rate stability

### `is_on_promo`
- **Type:** integer (0/1)
- **Description:** Indicates whether the customer is currently receiving a promotional discount.
- **Notes:** High churn risk when customers transition from promo to standard pricing.

### `months_since_promo_end`
- **Type:** integer
- **Description:** Months elapsed since the end of the last promotional period.
- **Notes:** Spike in churn commonly observed in the first few months after promo expiry.

---

## Revenue & Pricing

### `monthly_charges_list`
- **Type:** float
- **Description:** List price of the customer’s monthly service bundle before discounts.
- **Notes:** Analogous to full premium before applied discounts.

### `promo_discount_pct`
- **Type:** float (0–1 range)
- **Description:** Fractional discount applied while on promotion.
- **Example:** `0.20` = 20% off list price.

### `monthly_charges_billed`
- **Type:** float
- **Description:** Actual monthly charges billed after discounts.
- **Notes:** This is the realized revenue per month.

### `total_charges`
- **Type:** float
- **Description:** Cumulative billed charges over the customer’s lifetime-to-date.
- **Notes:** Influenced by both tenure and effective monthly charges.

---

## Value & Risk Metrics

### `cltv`
- **Type:** float
- **Description:** Estimated Customer Lifetime Value.
- **Notes:** Derived from tenure, risk, and pricing profile; used in financial impact simulations.

### `estimated_margin_pct`
- **Type:** float (0–1 range)
- **Description:** Estimated gross margin percentage for the customer.
- **Notes:** Higher values correspond to “high-value” customers worth more intensive retention efforts.

### `billing_risk_score`
- **Type:** float (0–1 range)
- **Description:** Synthetic score indicating risk of payment issues or delinquency.
- **Notes:** Correlated with payment method, autopay, and past friction. Excluded from the core model to reduce leakage.

---

## Sales Channel & Market Context

### `sales_channel`
- **Type:** categorical (`"Direct"`, `"Third-Party"`, `"Partner Portal"`)
- **Description:** Channel through which the customer was acquired.
- **Notes (Insurance Translation):**
  - `"Direct"` ~ Direct-to-consumer online or call center
  - `"Third-Party"` / `"Partner Portal"` ~ Independent agents or partner platforms

### `fiber_competition_flag`
- **Type:** integer (0/1)
- **Description:** Whether the customer resides in a high-competition “fiber” market.
- **Notes (Insurance Translation):** Represents markets with heavier competitor presence and more aggressive pricing.

### `region`
- **Type:** categorical
- **Description:** Broad geographic segment (e.g., `"North"`, `"South"`, `"East"`, `"West"`).
- **Notes:** Used for segmentation and potential regional strategy differences.

---

## Service Configuration (Product Mix)

### `internet_service`
- **Type:** categorical (`"DSL"`, `"Fiber"`, `"None"`)
- **Description:** Primary internet service type.
- **Notes (Insurance Translation):**
  - Service type can be mapped to basic vs. advanced coverage tiers.

### `phone_service`
- **Type:** integer (0/1)
- **Description:** Whether the customer has phone service as part of the bundle.

### `streaming_tv`
- **Type:** integer (0/1)
- **Description:** Whether the customer subscribes to TV streaming service.

### `streaming_movies`
- **Type:** integer (0/1)
- **Description:** Whether the customer subscribes to movie streaming service.

### `mobile_service`
- **Type:** integer (0/1)
- **Description:** Whether the customer has mobile service.
- **Notes:** In this synthetic design, mobile typically co-exists with internet service.

### `service_segment`
- **Type:** categorical (`"internet_only"`, `"internet_plus_other"`, `"cable_only"`, `"mobile"`)
- **Description:** High-level service configuration category.
- **Notes (Insurance Translation):**
  - `"internet_plus_other"` ~ Bundled multi‑policy customer
  - `"internet_only"` / `"mobile"` ~ Monoline or lightly bundled customer

### `streaming_addons_active`
- **Type:** integer
- **Description:** Count of active streaming add-ons (TV, movies, etc.).
- **Notes:** Higher values typically indicate deeper product engagement.

---

## Engagement & Digital Behavior

### `app_logins_last_30d`
- **Type:** integer
- **Description:** Number of logins to the customer app in the last 30 days.
- **Notes (Insurance Translation):** Proxy for digital engagement (e.g., policy app usage, digital ID cards).

### `engagement_score`
- **Type:** float (0–1 range)
- **Description:** Composite engagement score derived from usage patterns, logins, and add-ons.
- **Notes:** Lower engagement is generally associated with higher churn risk.

---

## Billing, Payments & Early Friction

### `payment_method`
- **Type:** categorical (`"Electronic Check"`, `"Mailed Check"`, `"Bank Transfer"`, `"Credit Card"`)
- **Description:** Primary billing/payment method.

### `is_autopay`
- **Type:** integer (0/1)
- **Description:** Indicates whether the customer is on automatic payments.
- **Notes:** Autopay customers usually exhibit lower involuntary churn.

### `first_60d_billing_call`
- **Type:** integer (0/1)
- **Description:** Whether the customer contacted support about a billing issue within their first 60 days.
- **Notes:** Captures early misunderstanding or dissatisfaction with charges.

### `billing_call_resolved`
- **Type:** integer (`-1`, `0`, `1`)
- **Description:** Resolution status of early billing issues.
  - `-1` = Not applicable (no early billing call)  
  - `0`  = Issue *not* resolved satisfactorily  
  - `1`  = Issue resolved
- **Notes:** Unresolved early billing friction is a strong churn driver.

### `first_60d_tech_call`
- **Type:** integer (0/1)
- **Description:** Whether the customer contacted support about a technical/service issue within their first 60 days.
- **Notes:** Analogous to early claims or service problems in insurance.

### `tech_issue_resolved`
- **Type:** integer (`-1`, `0`, `1`)
- **Description:** Resolution status of early technical issues.
  - `-1` = Not applicable (no early tech call)  
  - `0`  = Issue *not* resolved satisfactorily  
  - `1`  = Issue resolved
- **Notes:** Persistent service problems in the first 60 days significantly increase churn risk.

### `unresolved_tickets`
- **Type:** integer
- **Description:** Count of unresolved support tickets at the time of snapshot.
- **Notes:** Captures cumulative friction beyond the initial 60-day window.

---

## Derived / Modeling-Specific Fields

### `churn_score`
- **Type:** float (0–1 range)
- **Description:** Synthetic churn propensity score used when generating the dataset.
- **Notes:** Dropped from the final modeling to avoid leakage; kept here for transparency and experimentation.

---

## Usage Notes

- **Prediction Target:** `churn`
- **Key Risk Drivers (as observed in modeling):**
  - Contract type (`contract_type`)
  - Early friction (`first_60d_billing_call`, `first_60d_tech_call`, `billing_call_resolved`, `tech_issue_resolved`)
  - Competition (`fiber_competition_flag`)
  - Product mix and engagement (`service_segment`, `streaming_addons_active`, `engagement_score`)
- **Excluded from Final Model:**  
  Certain variables (e.g., `churn_score`, `billing_risk_score`, `cltv`, `estimated_margin_pct`) are excluded or treated carefully in the predictive model to reduce leakage and preserve interpretability.

This dictionary is designed to support both **technical users** (data scientists, analysts) and **business stakeholders** (product, marketing, strategy) in understanding how each field ties back to real-world retention levers.