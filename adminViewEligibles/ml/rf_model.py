# ============================================
# CHAMPS - Member Qualification Profiling
# Random Forest Classification Model
# ============================================

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, confusion_matrix,
                             classification_report)
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# ── 1. LOAD DATA ────────────────────────────
print("=" * 50)
print("  CHAMPS Member Qualification Profiling")
print("  Random Forest Classification Model")
print("=" * 50)

df = pd.read_csv('bcbp_members.csv')
print(f"\n[+] Loaded {len(df)} member records")

# ── 2. ENCODE ROLES ─────────────────────────
role_order = [
    "Initiate", "BCLP", "Candidate", "Full Member",
    "Servant", "Secretariat", "AGL", "GL",
    "Chapter Head", "Regional Director"
]
le = LabelEncoder()
le.fit(role_order)
df['role_encoded'] = le.transform(df['current_role'])

# ── 3. FEATURES & TARGET ────────────────────
features = [
    'role_encoded',
    'breakfasts_attended',
    'agm_attended',
    'formation_seminars_completed',
    'training_sessions_completed',
    'months_in_current_role'
]

X = df[features]
y = df['eligible']

# ── 4. TRAIN/TEST SPLIT ─────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"[+] Training set: {len(X_train)} records")
print(f"[+] Testing set:  {len(X_test)} records")

# ── 5. TRAIN RANDOM FOREST ──────────────────
print("\n[+] Training Random Forest model...")
rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced'
)
rf.fit(X_train, y_train)
rf_predictions = rf.predict(X_test)
rf_proba = rf.predict_proba(X_test)

# ── 6. TRAIN BASELINE (LOGISTIC REGRESSION) ─
print("[+] Training Logistic Regression baseline...")
lr = LogisticRegression(
    random_state=42,
    class_weight='balanced',
    max_iter=1000
)
lr.fit(X_train, y_train)
lr_predictions = lr.predict(X_test)

# ── 7. EVALUATION ───────────────────────────
print("\n" + "=" * 50)
print("  MODEL PERFORMANCE COMPARISON")
print("=" * 50)

rf_acc  = accuracy_score(y_test, rf_predictions)
rf_prec = precision_score(y_test, rf_predictions, zero_division=0)
rf_rec  = recall_score(y_test, rf_predictions, zero_division=0)

lr_acc  = accuracy_score(y_test, lr_predictions)
lr_prec = precision_score(y_test, lr_predictions, zero_division=0)
lr_rec  = recall_score(y_test, lr_predictions, zero_division=0)

print(f"\n{'Metric':<20} {'Random Forest':>15} {'Logistic Reg':>15}")
print("-" * 52)
print(f"{'Accuracy':<20} {rf_acc:>14.2%} {lr_acc:>14.2%}")
print(f"{'Precision':<20} {rf_prec:>14.2%} {lr_prec:>14.2%}")
print(f"{'Recall':<20} {rf_rec:>14.2%} {lr_rec:>14.2%}")

# Confusion matrix
print("\n[Random Forest] Confusion Matrix:")
cm = confusion_matrix(y_test, rf_predictions)
print(f"  True Negative  (correctly not eligible): {cm[0][0]}")
print(f"  False Positive (incorrectly eligible):   {cm[0][1]}")
print(f"  False Negative (missed eligible):        {cm[1][0]}")
print(f"  True Positive  (correctly eligible):     {cm[1][1]}")

# Feature importance
print("\n[Random Forest] Feature Importance:")
importances = pd.Series(rf.feature_importances_, index=features)
importances = importances.sort_values(ascending=False)
for feat, imp in importances.items():
    bar = "█" * int(imp * 40)
    print(f"  {feat:<35} {imp:.4f} {bar}")

# ── 8. SAMPLE PREDICTIONS ───────────────────
print("\n" + "=" * 50)
print("  SAMPLE MEMBER ELIGIBILITY PREDICTIONS")
print("=" * 50)

# Show 10 sample predictions from test set
sample_indices = X_test.index[:10]
sample_df = df.loc[sample_indices].copy()
sample_proba = rf.predict_proba(X_test[:10])

print(f"\n{'#':<4} {'Member':<22} {'Current Role':<18} {'Eligible?':<12} {'Confidence'}")
print("-" * 75)

for i, (idx, row) in enumerate(sample_df.iterrows()):
    pred = rf_predictions[i]
    confidence = sample_proba[i][1] if pred == 1 else sample_proba[i][0]
    result = "YES" if pred == 1 else "NO"
    print(f"{i+1:<4} {row['member_name']:<22} {row['current_role']:<18} "
          f"{result:<12} {confidence:.1%}")

# ── 9. ROLE-BASED ELIGIBILITY SUMMARY ───────
print("\n" + "=" * 50)
print("  ELIGIBILITY SUMMARY BY ROLE")
print("=" * 50)

all_proba = rf.predict_proba(X)
df['rf_eligible'] = rf.predict(X)
df['rf_confidence'] = [p[1] for p in all_proba]

print(f"\n{'Role':<20} {'Total':>7} {'Eligible':>10} {'Avg Confidence':>16}")
print("-" * 55)
for role in role_order:
    role_df = df[df['current_role'] == role]
    if len(role_df) == 0:
        continue
    eligible_count = role_df['rf_eligible'].sum()
    avg_conf = role_df[role_df['rf_eligible'] == 1]['rf_confidence'].mean()
    avg_conf_str = f"{avg_conf:.1%}" if eligible_count > 0 else "N/A"
    print(f"{role:<20} {len(role_df):>7} {int(eligible_count):>10} "
          f"{avg_conf_str:>16}")

print("\n[+] Model training and evaluation complete.")
print("=" * 50)
