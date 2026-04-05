"""
CIS 7026 — Business Process and Data Analysis
Q3D: Advanced Techniques — Object-Centric Process Mining (OCPM)
Dataset: BPI Challenge 2017 (CSV format)
Created by:  Seneth
Date : 29-03-2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("Q3D: Object-Centric Process Mining (OCPM)")
print("BPI Challenge 2017 — Applications & Offers")
print("=" * 60)

df = pd.read_csv("dataset/BPI Challenge 2017.csv")
print(f"\nTotal events loaded: {len(df):,}")

# ─────────────────────────────────────────────
# STEP 1: SEPARATE INTO OBJECT TYPES
# ─────────────────────────────────────────────
print("\n" + "-" * 50)
print("STEP 1: Separating Events by Object Type")
print("-" * 50)

app_events      = df[(df["EventOrigin"] == "Application") | (df["concept:name"].str.startswith("A_"))].copy()
offer_events    = df[(df["EventOrigin"] == "Offer")       | (df["concept:name"].str.startswith("O_"))].copy()
workflow_events = df[df["EventOrigin"] == "Workflow"].copy()

print(f"\nApplication events : {len(app_events):,}")
print(f"Offer events       : {len(offer_events):,}")
print(f"Workflow events    : {len(workflow_events):,}")

print("\nApplication Activity Distribution:")
print(app_events["concept:name"].value_counts().to_string())
print("\nOffer Activity Distribution:")
print(offer_events["concept:name"].value_counts().to_string())

# ─────────────────────────────────────────────
# STEP 2: OBJECT-CENTRIC DFGs
# ─────────────────────────────────────────────
print("\n" + "-" * 50)
print("STEP 2: Object-Centric DFGs per Object Type")
print("-" * 50)

def compute_dfg(event_df):
    dfg = {}
    for case_id, group in event_df.groupby("case:concept:name"):
        activities = group["concept:name"].tolist()
        for i in range(len(activities) - 1):
            edge = (activities[i], activities[i + 1])
            dfg[edge] = dfg.get(edge, 0) + 1
    return dfg

app_dfg   = compute_dfg(app_events)
offer_dfg = compute_dfg(offer_events)

print("\nTop 10 Application DFG transitions:")
for (s, t), f in sorted(app_dfg.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {s:35s} -> {t:35s}  [{f:,}]")

print("\nTop 10 Offer DFG transitions:")
for (s, t), f in sorted(offer_dfg.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {s:35s} -> {t:35s}  [{f:,}]")

def plot_dfg_bar(dfg, title, color, filename, top_n=10):
    top    = sorted(dfg.items(), key=lambda x: x[1], reverse=True)[:top_n]
    labels = [f"{s[:15]}->{t[:15]}" for (s, t), _ in top]
    freqs  = [f for _, f in top]
    plt.figure(figsize=(12, 5))
    plt.barh(labels[::-1], freqs[::-1], color=color, edgecolor="#1e293b")
    plt.xlabel("Transition Frequency", fontsize=11)
    plt.title(title, fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"[SAVED] {filename}")

plot_dfg_bar(app_dfg,   "OCPM: Application Object Lifecycle", "#2563eb", "outputs/ocpm_application_dfg.png")
plot_dfg_bar(offer_dfg, "OCPM: Offer Object Lifecycle",       "#7c3aed", "outputs/ocpm_offer_dfg.png")

# ─────────────────────────────────────────────
# STEP 3: 1-TO-MANY RELATIONSHIP
# ─────────────────────────────────────────────
print("\n" + "-" * 50)
print("STEP 3: Application to Offer Relationship (1-to-Many)")
print("-" * 50)

offer_per_app = (
    df[df["concept:name"].str.startswith("O_Create")]
    .groupby("case:concept:name")
    .size()
    .reset_index(name="offer_count")
)

print(f"\nApplications with offers: {len(offer_per_app):,}")
print("\nOffer count distribution:")
print(offer_per_app["offer_count"].value_counts().sort_index().to_string())

offer_dist = offer_per_app["offer_count"].value_counts().sort_index()
plt.figure(figsize=(9, 5))
plt.bar(offer_dist.index.astype(str), offer_dist.values, color="#0891b2", edgecolor="#0e7490")
plt.xlabel("Number of Offers per Application", fontsize=11)
plt.ylabel("Number of Applications", fontsize=11)
plt.title("OCPM: Offers Generated per Application\n(Classical PM distorts this with event duplication)",
          fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/ocpm_offers_per_application.png", dpi=150)
plt.close()
print("[SAVED] outputs/ocpm_offers_per_application.png")

# ─────────────────────────────────────────────
# STEP 4: CONVERGENCE ANALYSIS
# ─────────────────────────────────────────────
print("\n" + "-" * 50)
print("STEP 4: Convergence Problem Analysis")
print("-" * 50)

multi_offer_cases  = offer_per_app[offer_per_app["offer_count"] > 1]
single_offer_cases = offer_per_app[offer_per_app["offer_count"] == 1]

print(f"\nCases with single offer  : {len(single_offer_cases):,}")
print(f"Cases with multiple offers: {len(multi_offer_cases):,}")

if len(offer_per_app) > 0:
    pct = len(multi_offer_cases) / len(offer_per_app) * 100
    print(f"Convergence risk rate    : {pct:.1f}%")

fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(
    [len(single_offer_cases), len(multi_offer_cases)],
    labels=["1 Offer (No Convergence)", "2+ Offers (Convergence Risk)"],
    colors=["#16a34a", "#dc2626"],
    autopct="%1.1f%%",
    startangle=140,
    textprops={"fontsize": 12}
)
ax.set_title("OCPM: Cases Affected by Convergence in Classical PM", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/ocpm_convergence_analysis.png", dpi=150)
plt.close()
print("[SAVED] outputs/ocpm_convergence_analysis.png")

# ─────────────────────────────────────────────
# STEP 5: OBJECT TYPE SUMMARY
# ─────────────────────────────────────────────
print("\n" + "-" * 50)
print("STEP 5: OCPM Object Type Summary")
print("-" * 50)

summary = pd.DataFrame({
    "Object Type":        ["Application", "Offer", "Workflow"],
    "Total Events":       [len(app_events), len(offer_events), len(workflow_events)],
    "Unique Cases":       [app_events["case:concept:name"].nunique(),
                           offer_events["case:concept:name"].nunique(),
                           workflow_events["case:concept:name"].nunique()],
    "Unique Activities":  [app_events["concept:name"].nunique(),
                           offer_events["concept:name"].nunique(),
                           workflow_events["concept:name"].nunique()]
})
print("\n" + summary.to_string(index=False))

fig, ax = plt.subplots(figsize=(10, 5))
x = range(len(summary))
ax.bar([i - 0.25 for i in x], summary["Total Events"],      width=0.25, label="Total Events",       color="#2563eb")
ax.bar([i         for i in x], summary["Unique Cases"],      width=0.25, label="Unique Cases",        color="#16a34a")
ax.bar([i + 0.25 for i in x], summary["Unique Activities"], width=0.25, label="Unique Activities",   color="#dc2626")
ax.set_xticks(list(x))
ax.set_xticklabels(summary["Object Type"], fontsize=12)
ax.set_ylabel("Count", fontsize=11)
ax.set_title("OCPM: Object Type Summary — BPI Challenge 2017", fontsize=12, fontweight="bold")
ax.legend()
plt.tight_layout()
plt.savefig("outputs/ocpm_object_summary.png", dpi=150)
plt.close()
print("[SAVED] outputs/ocpm_object_summary.png")

print("\n" + "=" * 60)
print("ALL Q3D OCPM ANALYSIS COMPLETE")
print("=" * 60)
