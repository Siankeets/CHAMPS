# ============================================
# CHAMPS - Member Qualification Profiling
# Random Forest | Eligibility Confidence Score
# ============================================

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, confusion_matrix)
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# ── PROMOTION CRITERIA ──────────────────────
CRITERIA = {
    "Initiate":          {"breakfasts": 0,  "agm": 0,  "seminars": 0, "training": 0,  "months": 0},
    "BCLP":              {"breakfasts": 4,  "agm": 0,  "seminars": 0, "training": 0,  "months": 1},
    "Candidate":         {"breakfasts": 4,  "agm": 4,  "seminars": 4, "training": 0,  "months": 3},
    "Full Member":       {"breakfasts": 12, "agm": 12, "seminars": 4, "training": 4,  "months": 6},
    "Servant":           {"breakfasts": 20, "agm": 20, "seminars": 4, "training": 4,  "months": 6},
    "Secretariat":       {"breakfasts": 30, "agm": 30, "seminars": 4, "training": 4,  "months": 9},
    "AGL":               {"breakfasts": 40, "agm": 40, "seminars": 4, "training": 8,  "months": 12},
    "GL":                {"breakfasts": 52, "agm": 52, "seminars": 4, "training": 12, "months": 18},
    "Chapter Head":      {"breakfasts": 65, "agm": 65, "seminars": 4, "training": 16, "months": 24},
    "Regional Director": {"breakfasts": 80, "agm": 80, "seminars": 4, "training": 20, "months": 36},
}

ROLES = [
    "Initiate", "BCLP", "Candidate", "Full Member",
    "Servant", "Secretariat", "AGL", "GL",
    "Chapter Head", "Regional Director"
]
ROLE_LEVELS = {r: i for i, r in enumerate(ROLES)}

METRIC_LABELS = {
    "breakfasts": "Breakfasts Attended",
    "agm":        "AGM Attended",
    "seminars":   "Formation Seminars",
    "training":   "Training Sessions",
    "months":     "Months in Role"
}

# ── REQUIREMENTS GAP ANALYSIS ───────────────
def get_requirements_status(row):
    """Returns met/unmet requirements vs next role."""
    current_role = row['current_role']
    role_idx = ROLE_LEVELS.get(current_role, -1)
    
    if role_idx == -1 or role_idx + 1 >= len(ROLES):
        return ["Already at highest role."]
    
    next_role = ROLES[role_idx + 1]
    req = CRITERIA[next_role]
    
    member_vals = {
        "breakfasts": row['breakfasts_attended'],
        "agm":        row['agm_attended'],
        "seminars":   row['formation_seminars_completed'],
        "training":   row['training_sessions_completed'],
        "months":     row['months_in_current_role']
    }
    
    status = []
    for key, needed in req.items():
        if needed == 0:
            continue
        have = member_vals[key]
        label = METRIC_LABELS[key]
        if have >= needed:
            status.append(f"  ✔ {label}: {have}/{needed} (met)")
        else:
            gap = needed - have
            status.append(f"  ✘ {label}: {have}/{needed} "
                         f"({gap} more needed)")
    return status, next_role

# ── 1. LOAD DATA ────────────────────────────
print("=" * 55)
print("  CHAMPS — Member Qualification Profiling Service")
print("  Random Forest | Eligibility Confidence Scoring")
print("=" * 55)

df = pd.read_csv('bcbp_members_500_noisy.csv')
print(f"\n[+] Loaded {len(df)} member records")

# ── 2. ENCODE & PREPARE ─────────────────────
le = LabelEncoder()
le.fit(ROLES)
df['role_encoded'] = le.transform(df['current_role'])

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

# ── 3. TRAIN / TEST SPLIT ───────────────────
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X, y, df.index, test_size=0.2, random_state=42, stratify=y
)
print(f"[+] Training: {len(X_train)} | Testing: {len(X_test)}")

# ── 4. RANDOM FOREST ────────────────────────
print("\n[+] Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=100, random_state=42, class_weight='balanced'
)
rf.fit(X_train, y_train)
rf_proba      = rf.predict_proba(X_test)[:, 1]
rf_pred       = (rf_proba >= 0.5).astype(int)
rf_cv_scores  = cross_val_score(rf, X, y, cv=5, scoring='accuracy')

# ── 5. LOGISTIC REGRESSION BASELINE ────────
print("[+] Training Logistic Regression baseline...")
lr = LogisticRegression(
    random_state=42, class_weight='balanced', max_iter=1000
)
lr.fit(X_train, y_train)
lr_proba     = lr.predict_proba(X_test)[:, 1]
lr_pred      = (lr_proba >= 0.5).astype(int)
lr_cv_scores = cross_val_score(lr, X, y, cv=5, scoring='accuracy')

# ── 6. PERFORMANCE COMPARISON ───────────────
print("\n" + "=" * 55)
print("  MODEL PERFORMANCE COMPARISON")
print("=" * 55)

rf_acc  = accuracy_score(y_test, rf_pred)
rf_prec = precision_score(y_test, rf_pred, zero_division=0)
rf_rec  = recall_score(y_test, rf_pred, zero_division=0)
lr_acc  = accuracy_score(y_test, lr_pred)
lr_prec = precision_score(y_test, lr_pred, zero_division=0)
lr_rec  = recall_score(y_test, lr_pred, zero_division=0)

print(f"\n{'Metric':<25} {'Random Forest':>14} {'Logistic Reg':>14}")
print("-" * 55)
print(f"{'Accuracy':<25} {rf_acc:>13.2%} {lr_acc:>13.2%}")
print(f"{'Precision':<25} {rf_prec:>13.2%} {lr_prec:>13.2%}")
print(f"{'Recall':<25} {rf_rec:>13.2%} {lr_rec:>13.2%}")
print(f"{'CV Accuracy (5-fold)':<25} "
      f"{rf_cv_scores.mean():>13.2%} "
      f"{lr_cv_scores.mean():>13.2%}")
print(f"{'CV Std Dev':<25} "
      f"{rf_cv_scores.std():>13.4f} "
      f"{lr_cv_scores.std():>13.4f}")

cm = confusion_matrix(y_test, rf_pred)
print(f"\n[Random Forest] Confusion Matrix:")
print(f"  True Negative  (correctly not eligible): {cm[0][0]}")
print(f"  False Positive (incorrectly eligible):   {cm[0][1]}")
print(f"  False Negative (missed eligible):        {cm[1][0]}")
print(f"  True Positive  (correctly eligible):     {cm[1][1]}")

print(f"\n[Random Forest] Feature Importance:")
importances = pd.Series(rf.feature_importances_, index=features)
for feat, imp in importances.sort_values(ascending=False).items():
    bar = "█" * int(imp * 40)
    print(f"  {feat:<38} {imp:.4f} {bar}")

# ── 7. ELIGIBILITY CONFIDENCE SCORES ────────
print("\n" + "=" * 55)
print("  ELIGIBILITY CONFIDENCE SCORES (Full Dataset)")
print("=" * 55)

all_proba = rf.predict_proba(X)[:, 1]
df['eligibility_confidence'] = (all_proba * 100).round(1)
df['recommendation'] = df['eligibility_confidence'].apply(
    lambda x: "Strong"   if x >= 75 else
              "Moderate" if x >= 50 else
              "Low"
)

# ── 8. ROLE-BASED SUMMARY ───────────────────
print(f"\n{'Role':<20} {'Total':>6} {'Strong':>7} "
      f"{'Moderate':>9} {'Low':>5} {'Avg Score':>10}")
print("-" * 60)
for role in ROLES:
    rdf = df[df['current_role'] == role]
    if len(rdf) == 0:
        continue
    strong   = len(rdf[rdf['recommendation'] == 'Strong'])
    moderate = len(rdf[rdf['recommendation'] == 'Moderate'])
    low      = len(rdf[rdf['recommendation'] == 'Low'])
    avg      = rdf['eligibility_confidence'].mean()
    print(f"{role:<20} {len(rdf):>6} {strong:>7} "
          f"{moderate:>9} {low:>5} {avg:>9.1f}%")

# ── 9. SAMPLE MEMBER PROFILES ───────────────
print("\n" + "=" * 55)
print("  SAMPLE MEMBER PROFILES (10 members)")
print("=" * 55)

samples = df.sample(10, random_state=7).reset_index(drop=True)

for _, row in samples.iterrows():
    print(f"\n{'─'*50}")
    print(f"  Member     : {row['member_name']}")
    print(f"  Current    : {row['current_role']}")
    print(f"  Eligibility: {row['eligibility_confidence']}% "
          f"({row['recommendation']} recommendation)")

    result = get_requirements_status(row)
    if isinstance(result, list):
        print(f"  {result[0]}")
    else:
        statuses, next_role = result
        print(f"  Next Role  : {next_role}")
        print(f"  Requirements:")
        for s in statuses:
            print(f"  {s}")

print(f"\n{'─'*50}")
print("\n[+] Complete.")
print("=" * 55)
