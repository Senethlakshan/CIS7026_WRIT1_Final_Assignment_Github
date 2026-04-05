"""
CIS 7026 — Business Process and Data Analysis
Q3C: Process Mining Implementation
Dataset: BPI Challenge 2017 (CSV format)
Created by:  Seneth
Date : 29-03-2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# STEP 1: LOAD AND EXPLORE EVENT LOG
# ─────────────────────────────────────────────

print("=" * 60)
print("STEP 1: Loading BPI Challenge 2017 Dataset")
print("=" * 60)

df = pd.read_csv("dataset/BPI Challenge 2017.csv")

print(f"\nColumns: {list(df.columns)}")
print(f"Total events     : {len(df):,}")
print(f"Unique cases     : {df['case:concept:name'].nunique():,}")
print(f"Unique activities: {df['concept:name'].nunique():,}")
print(f"Unique resources : {df['org:resource'].nunique():,}")

print("\nTop 15 Activity Frequencies:")
print(df['concept:name'].value_counts().head(15).to_string())

print("\nSample Data (first 3 rows):")
print(df.head(3).to_string())


# ─────────────────────────────────────────────
# STEP 2: PROCESS DISCOVERY — Directly-Follows Graph
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 2: Process Discovery — Directly-Follows Graph")
print("=" * 60)

dfg = {}
start_activities = {}
end_activities   = {}
total_cases = df['case:concept:name'].nunique()

for case_id, group in df.groupby("case:concept:name"):
    activities = group["concept:name"].tolist()
    if not activities:
        continue
    start_act = activities[0]
    end_act   = activities[-1]
    start_activities[start_act] = start_activities.get(start_act, 0) + 1
    end_activities[end_act]     = end_activities.get(end_act, 0) + 1
    for i in range(len(activities) - 1):
        edge = (activities[i], activities[i + 1])
        dfg[edge] = dfg.get(edge, 0) + 1

dfg_sorted = sorted(dfg.items(), key=lambda x: x[1], reverse=True)
print("\nTop 20 Directly-Follows Transitions:")
for (src, tgt), freq in dfg_sorted[:20]:
    print(f"  {src:35s} -> {tgt:35s}  [{freq:,}]")

top_edges   = dfg_sorted[:15]
edge_labels = [f"{s[:18]}->{t[:18]}" for (s, t), _ in top_edges]
edge_freqs  = [f for _, f in top_edges]

plt.figure(figsize=(14, 6))
plt.barh(edge_labels[::-1], edge_freqs[::-1], color="#2563eb", edgecolor="#1e40af")
plt.xlabel("Frequency", fontsize=12)
plt.title("Top 15 Directly-Follows Transitions — BPI Challenge 2017", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/dfg_frequency.png", dpi=150)
plt.close()
print("\n[SAVED] outputs/dfg_frequency.png")


# ─────────────────────────────────────────────
# STEP 3: CONFORMANCE CHECKING
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 3: Conformance Checking")
print("=" * 60)

normative_path = [
    "A_Create Application",
    "A_Submitted",
    "A_Concept",
    "A_Accepted",
    "O_Create Offer",
    "O_Created",
    "O_Sent (mail and online)",
    "A_Complete",
    "A_Validating",
    "A_Approved"
]

conforming    = 0
non_conforming = 0
deviation_counts = {}

for case_id, group in df.groupby("case:concept:name"):
    activities = group["concept:name"].tolist()
    norm_idx = 0
    for act in activities:
        if norm_idx < len(normative_path) and act == normative_path[norm_idx]:
            norm_idx += 1
    fitness = norm_idx / len(normative_path)
    if fitness >= 0.7:
        conforming += 1
    else:
        non_conforming += 1
        missed = normative_path[norm_idx] if norm_idx < len(normative_path) else "Unknown"
        deviation_counts[missed] = deviation_counts.get(missed, 0) + 1

fitness_rate = conforming / total_cases * 100
print(f"\nTotal Cases         : {total_cases:,}")
print(f"Conforming Cases    : {conforming:,}  ({fitness_rate:.1f}%)")
print(f"Non-Conforming Cases: {non_conforming:,}  ({100 - fitness_rate:.1f}%)")
print(f"\nDeviation Breakdown:")
for step, count in sorted(deviation_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {step:40s}: {count:,} cases")

fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(
    [conforming, non_conforming],
    labels=["Conforming", "Non-Conforming"],
    colors=["#16a34a", "#dc2626"],
    autopct="%1.1f%%",
    startangle=140,
    textprops={"fontsize": 13}
)
ax.set_title("Conformance Rate — BPI Challenge 2017", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/conformance_pie.png", dpi=150)
plt.close()
print("[SAVED] outputs/conformance_pie.png")


# ─────────────────────────────────────────────
# STEP 4: BOTTLENECK IDENTIFICATION
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 4: Bottleneck Identification")
print("=" * 60)

rework_data = []
for case_id, group in df.groupby("case:concept:name"):
    activity_counts = group["concept:name"].value_counts()
    for act, count in activity_counts.items():
        if count > 1:
            rework_data.append({"Activity": act, "Rework_Count": count - 1, "Case": case_id})

rework_df = pd.DataFrame(rework_data)

if not rework_df.empty:
    bottleneck_summary = (
        rework_df.groupby("Activity")["Rework_Count"]
        .agg(["sum", "count", "mean"])
        .reset_index()
        .rename(columns={"sum": "Total_Rework", "count": "Cases_Affected", "mean": "Avg_Rework"})
        .sort_values("Total_Rework", ascending=False)
    )
    print("\nTop 10 Bottleneck Activities (rework frequency):")
    print(bottleneck_summary.head(10).to_string(index=False))

    top_bottlenecks = bottleneck_summary.head(10)
    plt.figure(figsize=(13, 6))
    plt.bar(
        range(len(top_bottlenecks)),
        top_bottlenecks["Total_Rework"],
        color="#f59e0b",
        edgecolor="#b45309"
    )
    plt.xticks(
        range(len(top_bottlenecks)),
        [a[:25] for a in top_bottlenecks["Activity"]],
        rotation=40, ha="right", fontsize=9
    )
    plt.ylabel("Total Rework Events", fontsize=11)
    plt.title("Top 10 Bottleneck Activities (Rework Count) — BPI Challenge 2017",
              fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("outputs/bottleneck_rework.png", dpi=150)
    plt.close()
    print("[SAVED] outputs/bottleneck_rework.png")


# ─────────────────────────────────────────────
# STEP 5: PROCESS ENHANCEMENT
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 5: Process Enhancement — Variant Analysis")
print("=" * 60)

variant_counts = {}
for case_id, group in df.groupby("case:concept:name"):
    variant = tuple(group["concept:name"].tolist())
    variant_counts[variant] = variant_counts.get(variant, 0) + 1

variant_sorted = sorted(variant_counts.items(), key=lambda x: x[1], reverse=True)
print(f"\nTotal unique variants: {len(variant_sorted):,}")
print(f"\nTop 10 Most Common Process Variants:")
for i, (variant, count) in enumerate(variant_sorted[:10], 1):
    coverage = count / total_cases * 100
    print(f"  Variant {i:2d}: {count:5,} cases ({coverage:.1f}%)  |  {len(variant)} steps")

cumulative = 0
coverages = []
for _, count in variant_sorted:
    cumulative += count
    coverages.append(cumulative / total_cases * 100)

plt.figure(figsize=(11, 5))
plt.plot(range(1, len(coverages) + 1), coverages, color="#7c3aed", linewidth=2)
plt.axhline(y=80, color="#dc2626", linestyle="--", label="80% coverage threshold")
plt.xlabel("Number of Variants Included", fontsize=11)
plt.ylabel("% of Cases Covered", fontsize=11)
plt.title("Process Variant Coverage — BPI Challenge 2017", fontsize=12, fontweight="bold")
plt.legend()
plt.xlim(1, min(500, len(coverages)))
plt.tight_layout()
plt.savefig("outputs/variant_coverage.png", dpi=150)
plt.close()
print("[SAVED] outputs/variant_coverage.png")

activity_freq = df["concept:name"].value_counts().head(20)
plt.figure(figsize=(13, 6))
activity_freq.plot(kind="bar", color="#0891b2", edgecolor="#0e7490")
plt.xlabel("Activity", fontsize=11)
plt.ylabel("Event Count", fontsize=11)
plt.title("Top 20 Activity Frequencies — BPI Challenge 2017", fontsize=12, fontweight="bold")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig("outputs/activity_frequency.png", dpi=150)
plt.close()
print("[SAVED] outputs/activity_frequency.png")

resource_freq = df["org:resource"].value_counts().head(15)
plt.figure(figsize=(11, 5))
resource_freq.plot(kind="bar", color="#059669", edgecolor="#047857")
plt.xlabel("Resource (User)", fontsize=11)
plt.ylabel("Number of Events Handled", fontsize=11)
plt.title("Top 15 Resource Workload — BPI Challenge 2017", fontsize=12, fontweight="bold")
plt.xticks(rotation=30, ha="right", fontsize=9)
plt.tight_layout()
plt.savefig("outputs/resource_workload.png", dpi=150)
plt.close()
print("[SAVED] outputs/resource_workload.png")

print("\n" + "=" * 60)
print("ALL Q3C ANALYSIS COMPLETE")
print("Output files saved in: outputs/")
print("=" * 60)
