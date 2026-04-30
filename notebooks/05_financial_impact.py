import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the 225k dataset
DATA_PATH = "../data/telco_churn_225k_v120.csv"
df = pd.read_csv(DATA_PATH)

# 2. Define "Friction Churners"
# These are customers who churned AND had an unresolved issue in the first 60 days
friction_mask = (
    (df['churn'] == 1) & 
    ((df['billing_call_resolved'] == 0) | (df['tech_issue_resolved'] == 0))
)

friction_churners = df[friction_mask].copy()

# 3. Calculate Baseline Metrics
total_churners_count = df['churn'].sum()
friction_churners_count = len(friction_churners)
pct_friction_of_total = (friction_churners_count / total_churners_count) * 100

total_cltv_at_risk = friction_churners['cltv'].sum()
avg_cltv_per_friction_churner = friction_churners['cltv'].mean()

print("--- Financial Impact Analysis: Friction-Driven Churn ---")
print(f"Total Churners: {total_churners_count:,}")
print(f"Friction-Driven Churners (Unresolved Issues): {friction_churners_count:,}")
print(f"Friction Share of Total Churn: {pct_friction_of_total:.1f}%")
print(f"Total 24-Month CLTV at Risk: ${total_cltv_at_risk:,.2f}")
print(f"Average CLTV per Friction Churner: ${avg_cltv_per_friction_churner:,.2f}")

# 4. Save-Rate Simulation
# What if we saved X% of these customers through a "Rapid Resolution" program?
save_rates = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
results = []

for rate in save_rates:
    saved_count = int(friction_churners_count * rate)
    cltv_retained = saved_count * avg_cltv_per_friction_churner
    results.append({
        'Save Rate (%)': int(rate * 100),
        'Customers Saved': saved_count,
        'CLTV Retained ($)': cltv_retained
    })

sim_df = pd.DataFrame(results)

# 5. Visualization (Using Project Color Palette)
plt.figure(figsize=(10, 6), facecolor='white')
ax = sns.barplot(
    data=sim_df, 
    x='Save Rate (%)', 
    y='CLTV Retained ($)', 
    palette=['#deebf7', '#9ecae1', '#4292c6', '#084594', '#08306b', '#081d58']
)

# Highlight the 20% "Target Scenario" in Green
target_idx = 2 # Index for 20%
ax.patches[target_idx].set_facecolor('#238b45') 

# Formatting
plt.title('Financial Impact: CLTV Retained by Save Rate Scenario', color='#08306b', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Program Save Rate (%)', color='#08306b', fontsize=12)
plt.ylabel('24-Month CLTV Retained ($)', color='#08306b', fontsize=12)
plt.grid(axis='y', alpha=0.3)

# Add dollar labels on top of bars
for p in ax.patches:
    ax.annotate(f'${p.get_height():,.0f}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha = 'center', va = 'center', 
                xytext = (0, 9), 
                textcoords = 'offset points',
                color='#08306b', fontweight='bold')

plt.tight_layout()
plt.savefig("../reports/Financial_Impact_CLTV_Simulation.png", dpi=150)
plt.show()

print("\nPhase 4 Complete. Financial simulation saved to /reports.")