import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# ==========================================
# PROJECT COLOR PALETTE
# ==========================================
STEEL_BLUE_900  = "#003865"   # Main font & main callouts
STEEL_BLUE_500  = "#0072CE"   # Minor callouts
WHITE_BG        = "#FFFFFF"
POSITIVE_GREEN  = "#2E7D32"
NEGATIVE_RED    = "#C62828"
BLUE_VARIATIONS = ["#003865", "#005696", "#0072CE", "#4192D9", "#82B1FF"]

# Global Plotting Defaults
plt.rcParams["figure.facecolor"]  = WHITE_BG
plt.rcParams["axes.facecolor"]    = WHITE_BG
plt.rcParams["text.color"]        = STEEL_BLUE_900
plt.rcParams["axes.labelcolor"]   = STEEL_BLUE_900
plt.rcParams["xtick.color"]       = STEEL_BLUE_900
plt.rcParams["ytick.color"]       = STEEL_BLUE_900
plt.rcParams["font.family"]       = "sans-serif"

# ==========================================
# LOAD DATA
# ==========================================
df = pd.read_csv("telco_churn_225k_v120.csv")

# Re-cast nullable columns after CSV read
df["billing_call_resolved"] = df["billing_call_resolved"].astype("Int64")
df["tech_issue_resolved"]   = df["tech_issue_resolved"].astype("Int64")

CHURN_COL = "churn"

def churn_rate(series):
    return series.mean() * 100

def annotate_bars(ax):
    for p in ax.patches:
        ax.annotate(
            f"{p.get_height():.1f}%",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center", va="center", xytext=(0, 9),
            textcoords="offset points",
            color=STEEL_BLUE_900, fontweight="bold",
        )

# ==========================================
# FIGURE 1: CORE BUSINESS DRIVERS
# Contract Type | Internet Service | Sales Channel
# ==========================================
fig1, axes = plt.subplots(1, 3, figsize=(18, 6))
fig1.patch.set_facecolor(WHITE_BG)
fig1.suptitle("Figure 1: Core Business Drivers", fontsize=16, fontweight="bold", color=STEEL_BLUE_900)

# Contract Type
contract_rates = df.groupby("contract_type")[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=contract_rates, x="contract_type", y=CHURN_COL,
            palette=BLUE_VARIATIONS[:3], ax=axes[0])
axes[0].set_title("Churn by Contract Type", fontweight="bold")
axes[0].set_ylabel("Churn Rate (%)")
axes[0].yaxis.set_major_formatter(mtick.PercentFormatter())
annotate_bars(axes[0])

# Internet Service
internet_rates = df.groupby("internet_service")[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=internet_rates, x="internet_service", y=CHURN_COL,
            palette=BLUE_VARIATIONS[:3], ax=axes[1])
axes[1].set_title("Churn by Internet Service", fontweight="bold")
axes[1].set_ylabel("Churn Rate (%)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
annotate_bars(axes[1])

# Sales Channel
channel_rates = df.groupby("sales_channel")[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=channel_rates, x="sales_channel", y=CHURN_COL,
            palette=BLUE_VARIATIONS[:4], ax=axes[2])
axes[2].set_title("Churn by Sales Channel", fontweight="bold")
axes[2].set_ylabel("Churn Rate (%)")
axes[2].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[2].tick_params(axis="x", rotation=15)
annotate_bars(axes[2])

plt.tight_layout()
plt.savefig("Presentation_Fig1_Drivers.png", dpi=150, bbox_inches="tight")
plt.close()
print("Figure 1 saved.")

# ==========================================
# FIGURE 2: PROMO & PRICING
# Promo Status | Discount Tier
# ==========================================
fig2, axes = plt.subplots(1, 2, figsize=(14, 6))
fig2.patch.set_facecolor(WHITE_BG)
fig2.suptitle("Figure 2: Promo & Pricing Dynamics", fontsize=16, fontweight="bold", color=STEEL_BLUE_900)

# Promo Status
df["promo_status"] = np.where(df["is_on_promo"] == 1, "On Promo", "Full Rate")
promo_rates = df.groupby("promo_status")[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=promo_rates, x="promo_status", y=CHURN_COL,
            palette=[STEEL_BLUE_900, STEEL_BLUE_500], ax=axes[0])
axes[0].set_title("Churn: On Promo vs. Full Rate", fontweight="bold")
axes[0].set_ylabel("Churn Rate (%)")
axes[0].yaxis.set_major_formatter(mtick.PercentFormatter())
annotate_bars(axes[0])

# Discount Tier
promo_df = df[df["is_on_promo"] == 1].copy()
promo_df["discount_tier"] = pd.cut(
    promo_df["promo_discount_pct"],
    bins=[0, 0.15, 0.25, 0.35, 1.0],
    labels=["Low (≤15%)", "Mid (16–25%)", "High (26–35%)", "Very High (>35%)"],
)
tier_rates = promo_df.groupby("discount_tier", observed=True)[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=tier_rates, x="discount_tier", y=CHURN_COL,
            palette=BLUE_VARIATIONS[:4], ax=axes[1])
axes[1].set_title("Churn by Discount Tier (Promo Customers Only)", fontweight="bold")
axes[1].set_ylabel("Churn Rate (%)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[1].tick_params(axis="x", rotation=10)
annotate_bars(axes[1])

plt.tight_layout()
plt.savefig("Presentation_Fig2_Pricing.png", dpi=150, bbox_inches="tight")
plt.close()
print("Figure 2 saved.")

# ==========================================
# FIGURE 3: EARLY FRICTION
# Billing Resolution | Tech Resolution
# ==========================================
fig3, axes = plt.subplots(1, 2, figsize=(14, 6))
fig3.patch.set_facecolor(WHITE_BG)
fig3.suptitle("Figure 3: First 60-Day Friction Impact", fontsize=16, fontweight="bold", color=STEEL_BLUE_900)

# Billing Resolution
billing_df = df[df["first_60d_billing_call"] == 1].copy()
billing_df["resolution"] = billing_df["billing_call_resolved"].map(
    {1: "Resolved", 0: "Unresolved"}
)
billing_rates = billing_df.groupby("resolution")[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=billing_rates, x="resolution", y=CHURN_COL,
            palette=[POSITIVE_GREEN, NEGATIVE_RED], ax=axes[0])
axes[0].set_title("Billing Issue Resolution vs. Churn", fontweight="bold")
axes[0].set_ylabel("Churn Rate (%)")
axes[0].yaxis.set_major_formatter(mtick.PercentFormatter())
annotate_bars(axes[0])

# Tech Resolution
tech_df = df[df["first_60d_tech_call"] == 1].copy()
tech_df["resolution"] = tech_df["tech_issue_resolved"].map(
    {1: "Resolved", 0: "Unresolved"}
)
tech_rates = tech_df.groupby("resolution")[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=tech_rates, x="resolution", y=CHURN_COL,
            palette=[POSITIVE_GREEN, NEGATIVE_RED], ax=axes[1])
axes[1].set_title("Tech Issue Resolution vs. Churn", fontweight="bold")
axes[1].set_ylabel("Churn Rate (%)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
annotate_bars(axes[1])

plt.tight_layout()
plt.savefig("Presentation_Fig3_Friction.png", dpi=150, bbox_inches="tight")
plt.close()
print("Figure 3 saved.")

# ==========================================
# FIGURE 4: TENURE & BILLING RISK
# Tenure Buckets | Autopay Impact
# ==========================================
fig4, axes = plt.subplots(1, 2, figsize=(14, 6))
fig4.patch.set_facecolor(WHITE_BG)
fig4.suptitle("Figure 4: Tenure & Payment Behavior", fontsize=16, fontweight="bold", color=STEEL_BLUE_900)

# Tenure Buckets
df["tenure_bucket"] = pd.cut(
    df["tenure_months"],
    bins=[0, 12, 24, 36, 48, 72],
    labels=["0–12 mo", "13–24 mo", "25–36 mo", "37–48 mo", "49–72 mo"],
)
tenure_rates = df.groupby("tenure_bucket", observed=True)[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=tenure_rates, x="tenure_bucket", y=CHURN_COL,
            palette=BLUE_VARIATIONS[:5], ax=axes[0])
axes[0].set_title("Churn by Tenure Bucket", fontweight="bold")
axes[0].set_ylabel("Churn Rate (%)")
axes[0].yaxis.set_major_formatter(mtick.PercentFormatter())
annotate_bars(axes[0])

# Autopay Impact
df["pay_method_label"] = np.where(df["is_autopay"] == 1, "Autopay", "Manual Pay")
pay_rates = df.groupby("pay_method_label")[CHURN_COL].apply(churn_rate).reset_index()
sns.barplot(data=pay_rates, x="pay_method_label", y=CHURN_COL,
            palette=[POSITIVE_GREEN, NEGATIVE_RED], ax=axes[1])
axes[1].set_title("Churn by Payment Method", fontweight="bold")
axes[1].set_ylabel("Churn Rate (%)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
annotate_bars(axes[1])

plt.tight_layout()
plt.savefig("Presentation_Fig4_TenureRisk.png", dpi=150, bbox_inches="tight")
plt.close()
print("Figure 4 saved.")

# ==========================================
# FIGURE 5: CORRELATION HEATMAP
# ==========================================
fig5, ax = plt.subplots(figsize=(12, 10))
fig5.patch.set_facecolor(WHITE_BG)

numeric_cols = [
    "tenure_months", "monthly_charges", "monthly_charges_billed", "total_charges",
    "is_on_promo", "promo_discount_pct", "first_60d_billing_call",
    "is_autopay", "billing_risk_score", "churn_score",
]
corr_df = df[numeric_cols].copy()
corr_df["churned"] = df[CHURN_COL].astype(int)
corr_matrix = corr_df.corr()

sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="Blues", center=0, ax=ax,
            annot_kws={"color": STEEL_BLUE_900})
ax.set_title("Figure 5: Correlation Heatmap", fontsize=16, fontweight="bold", color=STEEL_BLUE_900)

plt.tight_layout()
plt.savefig("Presentation_Fig5_Correlation.png", dpi=150, bbox_inches="tight")
plt.close()
print("Figure 5 saved.")

print("\nAll EDA figures saved successfully.")