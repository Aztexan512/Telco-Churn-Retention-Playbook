import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import xgboost as xgb

# Colors
STEEL_BLUE_900 = "#003865"
STEEL_BLUE_500 = "#0072CE"

# ── 1. LOAD & SPLIT ──────────────────────────────────────────────────────────
df = pd.read_csv("telco_churn_225k_v120.csv")
X = df.drop(columns=["customer_id", "churn", "churn_score", "billing_risk_score",
                      "cltv", "estimated_margin_pct"], errors="ignore")
y = df["churn"]

for col in ["billing_call_resolved", "tech_issue_resolved"]:
    if col in X.columns:
        X[col] = X[col].fillna(-1).astype("int64")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── 2. TRAIN ─────────────────────────────────────────────────────────────────
cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
model = Pipeline(steps=[
    ("pre", ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)],
        remainder="passthrough"
    )),
    ("clf", xgb.XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.08,
        random_state=42, n_jobs=-1
    ))
])
model.fit(X_train, y_train)
y_proba = model.predict_proba(X_test)[:, 1]

# ── 3. DECILE ASSIGNMENT (Rank-Based, Transparent) ───────────────────────────
# Sort descending by predicted probability so row 0 = highest risk customer.
# qcut on the integer index then gives perfectly even-sized bins.
# Label 1 = top 10% (highest risk), Label 10 = bottom 10% (lowest risk).
results_df = pd.DataFrame({"actual": y_test.values, "prob": y_proba})
results_df = results_df.sort_values("prob", ascending=False).reset_index(drop=True)

results_df["decile"] = pd.qcut(
    results_df.index,
    q=10,
    labels=np.arange(1, 11),   # 1 = highest risk, 10 = lowest risk
    duplicates="drop"
)

# ── 4. AGGREGATE STATS ───────────────────────────────────────────────────────
decile_stats = (
    results_df
    .groupby("decile", observed=True)
    .agg(total_customers=("actual", "count"),
         actual_churners=("actual", "sum"))
    .sort_index()
    .reset_index()
)

baseline_rate = results_df["actual"].mean()
decile_stats["churn_rate"]   = decile_stats["actual_churners"] / decile_stats["total_customers"]
decile_stats["lift"]         = decile_stats["churn_rate"] / baseline_rate
decile_stats["cum_gain_pct"] = (
    decile_stats["actual_churners"].cumsum() / results_df["actual"].sum() * 100
)

n_deciles = decile_stats.shape[0]

# ── 5. EXECUTIVE PRINT SUMMARY ───────────────────────────────────────────────
# Raw volume first (scale/budget context), then rates (efficiency context)
total_churners      = results_df["actual"].sum()
top_decile_churners = decile_stats.iloc[0]["actual_churners"]

idx_20      = min(1, n_deciles - 1)
top_20_gain = decile_stats.iloc[idx_20]["cum_gain_pct"]

print("=== Decile Table ===")
print(decile_stats[["decile", "total_customers", "churn_rate", "lift", "cum_gain_pct"]].to_string(index=False))
print()
print("=== Executive Summary Metrics ===")
print(f"Actual decile bins generated: {n_deciles}")
print(f"Total churners in test set:   {int(total_churners):,}")
print(f"Churners in top decile:       {int(top_decile_churners):,}")
print(f"Baseline churn rate:          {baseline_rate:.2%}")
print(f"Top decile churn rate:        {decile_stats.iloc[0]['churn_rate']:.1%}")
print(f"Top decile lift:              {decile_stats.iloc[0]['lift']:.2f}x")
print(f"Recall at top 20%:            {top_20_gain:.1f}%")
print()
print("=== Story Framing (Executive Summary Language) ===")
print(f"'The top 10% of customers by predicted churn risk have {decile_stats.iloc[0]['lift']:.2f}x the average churn rate.'")
print(f"'Targeting the top 20% highest-risk customers captures {top_20_gain:.1f}% of all churners.'")
print()
print("=== Interview Note ===")
print("If asked why test set counts vs. full population:")
print("'This represents a 20% holdout sample to prove model validity;")
print(" scaled to the full 225k population, we are looking at identifying")
print(f" over {int(top_decile_churners * 5):,} high-certainty churners in the top decile alone.'")

# ── 6. LIFT BAR CHART ────────────────────────────────────────────────────────
colors = [STEEL_BLUE_900, "#005696"] + [STEEL_BLUE_500] * max(0, n_deciles - 2)

plt.figure(figsize=(10, 5))
sns.barplot(data=decile_stats, x="decile", y="lift", palette=colors[:n_deciles])
plt.axhline(1, color=STEEL_BLUE_900, linestyle="--", alpha=0.6, label="Baseline (1x)")
plt.title("Model Lift by Decile: Prioritizing High-Risk Segments",
          fontsize=14, fontweight="bold")
plt.xlabel("Risk Decile (1 = Highest Risk)")
plt.ylabel("Lift (× Average Churn Rate)")
plt.legend()
plt.tight_layout()
plt.savefig("Model_Decile_Lift_Final.png", dpi=150)
plt.close()

# ── 7. CUMULATIVE GAIN CHART (Hardened) ──────────────────────────────────────
x_20   = decile_stats.iloc[idx_20]["decile"]
x_rand = np.arange(1, n_deciles + 1)
y_rand = (x_rand / n_deciles) * 100

plt.figure(figsize=(10, 5))

plt.plot(decile_stats["decile"], decile_stats["cum_gain_pct"],
         marker="o", color=STEEL_BLUE_900, linewidth=2, label="Model")

plt.plot(x_rand, y_rand,
         linestyle="--", color="gray", alpha=0.7, label="Random Guess")

plt.annotate(
    f"Top 20% captures {top_20_gain:.1f}% of churn",
    xy=(x_20, top_20_gain),
    xytext=(min(4, n_deciles), top_20_gain - 10),
    arrowprops=dict(facecolor=STEEL_BLUE_900, shrink=0.05),
    fontsize=11, fontweight="bold"
)

plt.title("Cumulative Gain: Efficiency of Targeted Retention",
          fontsize=14, fontweight="bold")
plt.xlabel("Risk Decile (Cumulative)")
plt.ylabel("% of Total Churners Captured")
plt.xticks(np.arange(1, n_deciles + 1))
plt.legend()
plt.tight_layout()
plt.savefig("Model_Cumulative_Gain_Final.png", dpi=150)
plt.close()

print("Both charts saved.")