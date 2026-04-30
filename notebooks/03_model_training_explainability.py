import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve

# 1. Load the 225k dataset
# Since this script is in /notebooks, we go up one level to /data
DATA_PATH = "../data/telco_churn_225k_v120.csv" 
df = pd.read_csv(DATA_PATH)

print(f"Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")

# 2. Define Features and Target
# We EXCLUDE columns that would cause "Data Leakage" or are non-predictive
drop_cols = [
    'customer_id', 'churn', 'churn_score', 'churn_prob', 
    'cltv', 'billing_risk_score', 'monthly_charges_billed'
]

X = df.drop(columns=[c for c in drop_cols if c in df.columns])
y = df['churn']

# 3. Preprocessing: Convert Categorical to Dummies
X_encoded = pd.get_dummies(X, drop_first=True)

# 4. Train/Test Split (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Training set size: {X_train.shape[0]}")
print(f"Testing set size: {X_test.shape[0]}")

# 5. Train XGBoost Model
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

print("Training XGBoost model (this may take a moment with 225k rows)...")
model.fit(X_train, y_train)

# 6. Model Evaluation
y_pred_prob = model.predict_proba(X_test)[:, 1]
auc_score = roc_auc_score(y_test, y_pred_prob)
print(f"ROC AUC Score: {auc_score:.4f}")

# Plot ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='steelblue', lw=2, label=f'XGBoost (AUC = {auc_score:.2f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.title('Receiver Operating Characteristic (ROC) Curve', color='#08306b', fontsize=14)
plt.xlabel('False Positive Rate', color='#08306b')
plt.ylabel('True Positive Rate', color='#08306b')
plt.legend(loc="lower right")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("../reports/Model_ROC_Curve.png")
plt.show()

# 7. Explainability with SHAP
print("Generating SHAP values (explaining the churn drivers)...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_test, show=False)
plt.title("SHAP Feature Importance (Churn Drivers)", color='#08306b', fontsize=16)
plt.tight_layout()
plt.savefig("../reports/Model_SHAP_Summary.png")
plt.show()

print("\nPhase 3 Complete. Files saved to /reports.")