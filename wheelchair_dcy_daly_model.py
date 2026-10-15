#!/usr/bin/env python3
"""
Combined DCY + DALY Cost-Effectiveness Model for Wheelchair Provision in LMICs
===============================================================================

Unified welfare metric capturing health/disability (DALYs) + income/consumption (DCYs).

Moral weight sources:
  - GiveWell: 1 DALY averted = 2.3 DCYs (morbidity moral weight)
  - Sensitivity range: eta = 1 to 20

Date: August 2026
"""

import numpy as np
import math
import warnings
warnings.filterwarnings('ignore')

N_DRAWS = 200_000
COST_PER_PERSON = 200
DISCOUNT_RATE = 0.03
ETA_VALUES = [1, 2.3, 5, 10, 20]
INCOME_MARGINAL_SCENARIOS = {
    "pessimistic_20pct": 0.20,
    "moderate_50pct":    0.50,
    "optimistic_100pct": 1.00,
}
np.random.seed(42)

def tri(low, mode, high, n=N_DRAWS):
    return np.random.triangular(low, mode, high, n)

# ============================================================
# DRAW PARAMETERS
# ============================================================
dw_pct_reduction   = tri(0.18, 0.25, 0.35)
income_gain_raw    = tri(50, 150, 324)
baseline_consump   = tri(400, 600, 900)
usage_rate         = tri(0.45, 0.70, 0.85)
wheelchair_life    = tri(3, 4, 5)
additionality      = tri(0.75, 0.895, 0.95)
p_success          = tri(0.25, 0.34, 0.50)
baseline_dw        = 0.406

def discounted_years(lifespan_draws):
    max_life = int(np.ceil(lifespan_draws.max()))
    discount_table = np.array([1.0 / (1 + DISCOUNT_RATE)**t for t in range(max_life + 1)])
    result = np.zeros(len(lifespan_draws))
    for i in range(max_life):
        mask_full = lifespan_draws > (i + 1)
        result[mask_full] += discount_table[i]
        mask_partial = (lifespan_draws > i) & (lifespan_draws <= (i + 1))
        result[mask_partial] += discount_table[i] * (lifespan_draws[mask_partial] - i)
    return result

disc_years = discounted_years(wheelchair_life)

# ============================================================
# CORE CALCULATIONS
# ============================================================

# Adjustment factors
adj_full = usage_rate * additionality * p_success       # full (ex-ante, includes program risk)
adj_conditional = usage_rate * additionality             # conditional on program succeeding

dw_reduction_abs = baseline_dw * dw_pct_reduction

# DALY component
dalys_pp_full = dw_reduction_abs * disc_years * adj_full
dalys_pp_cond = dw_reduction_abs * disc_years * adj_conditional
cost_per_daly_full = COST_PER_PERSON / dalys_pp_full
cost_per_daly_cond = COST_PER_PERSON / dalys_pp_cond

def compute_dcys(income_marginal_frac, conditional=False):
    effective_gain = income_gain_raw * income_marginal_frac
    dcy_per_year = np.log(1 + effective_gain / baseline_consump) / np.log(2)
    adj = adj_conditional if conditional else adj_full
    dcys_pp = dcy_per_year * disc_years * adj
    cost_per_dcy = COST_PER_PERSON / dcys_pp
    return dcys_pp, cost_per_dcy

def compute_combined(dalys, dcys, eta):
    total = dalys * eta + dcys
    cost = COST_PER_PERSON / total
    return total, cost

def pct(arr, p):
    return np.percentile(arr, p)

# ============================================================
# OUTPUT
# ============================================================
W = 110  # print width

print("=" * W)
print("WHEELCHAIR PROVISION IN LMICs: COMBINED DCY + DALY COST-EFFECTIVENESS MODEL")
print("=" * W)
print(f"Monte Carlo draws: {N_DRAWS:,} | Cost/person: ${COST_PER_PERSON} | Discount: {DISCOUNT_RATE:.0%} | DW baseline: {baseline_dw}")
print(f"NOTE: 'Ex-ante' includes p_success (median {np.median(p_success):.2f}); 'Conditional' assumes program works")

# =========================
# SECTION 1: HEALTH ONLY
# =========================
print("\n" + "=" * W)
print("1. HEALTH (DALY) COMPONENT")
print("=" * W)

for label, dalys, cpdaly in [
    ("Ex-ante (includes p_success)", dalys_pp_full, cost_per_daly_full),
    ("Conditional on program success", dalys_pp_cond, cost_per_daly_cond),
]:
    print(f"\n  --- {label} ---")
    print(f"  {'Metric':<35} {'Median':>10} {'Mean':>10} {'10th':>10} {'90th':>10}")
    print(f"  {'-'*75}")
    print(f"  {'DALYs/person':<35} {np.median(dalys):>10.4f} {np.mean(dalys):>10.4f} {pct(dalys,10):>10.4f} {pct(dalys,90):>10.4f}")
    print(f"  {'$/DALY':<35} {np.median(cpdaly):>10.0f} {np.mean(cpdaly):>10.0f} {pct(cpdaly,10):>10.0f} {pct(cpdaly,90):>10.0f}")
    for thresh in [100, 200, 500, 1000]:
        print(f"  {'P($/DALY < $'+str(thresh)+')':<35} {np.mean(cpdaly < thresh):>10.1%}")

# =========================
# SECTION 2: INCOME ONLY
# =========================
print("\n" + "=" * W)
print("2. INCOME (DCY) COMPONENT BY MARGINAL ATTRIBUTION")
print("=" * W)

dcy_results = {}
dcy_results_cond = {}

for scenario_name, mfrac in INCOME_MARGINAL_SCENARIOS.items():
    dcys_pp, cpdcy = compute_dcys(mfrac, conditional=False)
    dcys_pp_c, cpdcy_c = compute_dcys(mfrac, conditional=True)
    dcy_results[scenario_name] = (dcys_pp, cpdcy)
    dcy_results_cond[scenario_name] = (dcys_pp_c, cpdcy_c)

    print(f"\n  --- {scenario_name} (income * {mfrac:.0%}) ---")
    print(f"  {'Metric':<35} {'Ex-ante':>12} {'Conditional':>12}")
    print(f"  {'-'*60}")
    print(f"  {'DCYs/person (median)':<35} {np.median(dcys_pp):>12.4f} {np.median(dcys_pp_c):>12.4f}")
    print(f"  {'$/DCY (median)':<35} {np.median(cpdcy):>12.0f} {np.median(cpdcy_c):>12.0f}")

# =========================
# SECTION 3: COMBINED
# =========================
print("\n" + "=" * W)
print("3. COMBINED $/DCY-EQUIVALENT BY eta AND INCOME SCENARIO")
print("=" * W)
print("  eta = how many DCYs is 1 DALY worth (GiveWell: 2.3)")
print("  Formula: Total_DCYeq = (DALYs * eta) + DCYs\n")

for conditional, label, dalys_use, dcy_store in [
    (False, "EX-ANTE (includes p_success risk)", dalys_pp_full, dcy_results),
    (True,  "CONDITIONAL ON PROGRAM SUCCESS",    dalys_pp_cond, dcy_results_cond),
]:
    print(f"  === {label} ===")
    hdr = f"  {'eta':>5} | {'Income Scenario':<22} | {'Med $/DCYeq':>12} | {'P(<$100)':>9} | {'P(<$200)':>9} | {'P(<$500)':>9} | {'Health%':>8} | {'Income%':>8}"
    print(hdr)
    print(f"  {'-'*len(hdr)}")

    for eta in ETA_VALUES:
        for sname, mfrac in INCOME_MARGINAL_SCENARIOS.items():
            dcys_pp = dcy_store[sname][0]
            total_eq, cost_eq = compute_combined(dalys_use, dcys_pp, eta)
            h_med = np.median(dalys_use * eta)
            i_med = np.median(dcys_pp)
            t_med = h_med + i_med
            h_pct = h_med / t_med * 100
            i_pct = i_med / t_med * 100
            print(f"  {eta:>5.1f} | {sname:<22} | {np.median(cost_eq):>11.0f} | {np.mean(cost_eq<100):>8.1%} | {np.mean(cost_eq<200):>8.1%} | {np.mean(cost_eq<500):>8.1%} | {h_pct:>7.1f}% | {i_pct:>7.1f}%")
        print(f"  {'-'*len(hdr)}")
    print()

# =========================
# SECTION 4: THRESHOLD
# =========================
print("=" * W)
print("4. CRITICAL INCOME-ATTRIBUTION THRESHOLD")
print("=" * W)
print("  At what income attribution % does median $/DCYeq cross $100, $200, $500?\n")

for conditional, label, dalys_use in [
    (False, "Ex-ante", dalys_pp_full),
    (True,  "Conditional", dalys_pp_cond),
]:
    print(f"  --- {label} ---")
    print(f"  {'eta':>6} | {'< $100':>12} | {'< $200':>12} | {'< $500':>12}")
    print(f"  {'-'*50}")

    for eta in ETA_VALUES:
        thresholds = {}
        for target in [100, 200, 500]:
            found = None
            for test_pct in range(0, 101):
                frac = test_pct / 100.0
                dcys_t, _ = compute_dcys(frac, conditional=conditional)
                _, cost_eq = compute_combined(dalys_use, dcys_t, eta)
                if np.median(cost_eq) < target:
                    found = test_pct
                    break
            thresholds[target] = f"{found}%" if found is not None else "Never"
        print(f"  {eta:>6.1f} | {thresholds[100]:>12} | {thresholds[200]:>12} | {thresholds[500]:>12}")
    print()

# =========================
# SECTION 5: NAMED SCENARIOS
# =========================
print("=" * W)
print("5. NAMED SCENARIO SUMMARY TABLE (GiveWell eta=2.3)")
print("=" * W)

eta_gw = 2.3
scenarios = [
    ("Health Only",           0.0, False),
    ("Health Only (cond)",    0.0, True),
    ("Pessimistic 20%",       0.20, False),
    ("Moderate 50%",          0.50, False),
    ("Optimistic 100%",       1.00, False),
    ("Pessimistic 20% (cond)", 0.20, True),
    ("Moderate 50% (cond)",    0.50, True),
    ("Optimistic 100% (cond)", 1.00, True),
]

print(f"\n  {'Scenario':<28} | {'$/DALY':>8} | {'$/DCY':>8} | {'$/DCYeq':>8} | {'DALYs':>8} | {'DCYs':>8} | {'DCYeq':>8} | {'P(<$100)':>8} | {'P(<$500)':>8}")
print(f"  {'-'*110}")

for sname, mfrac, cond in scenarios:
    dalys_use = dalys_pp_cond if cond else dalys_pp_full
    cpdaly = COST_PER_PERSON / dalys_use

    if mfrac > 0:
        dcys_pp, cpdcy = compute_dcys(mfrac, conditional=cond)
        dcy_str = f"{np.median(cpdcy):>8.0f}"
    else:
        dcys_pp = np.zeros(N_DRAWS)
        dcy_str = "     N/A"

    total_eq, cost_eq = compute_combined(dalys_use, dcys_pp, eta_gw)

    print(f"  {sname:<28} | {np.median(cpdaly):>8.0f} | {dcy_str} | {np.median(cost_eq):>8.0f} | {np.median(dalys_use):>8.4f} | {np.median(dcys_pp):>8.4f} | {np.median(total_eq):>8.4f} | {np.mean(cost_eq<100):>7.1%} | {np.mean(cost_eq<500):>7.1%}")

# =========================
# SECTION 6: DECOMPOSITION
# =========================
print(f"\n{'='*W}")
print("6. VALUE DECOMPOSITION (where does the welfare come from?)")
print("=" * W)

for cond, label, dalys_use in [(False, "Ex-ante", dalys_pp_full), (True, "Conditional", dalys_pp_cond)]:
    print(f"\n  --- {label}, eta=2.3, 50% income attribution ---")
    dcys_50, _ = compute_dcys(0.50, conditional=cond)
    h_comp = dalys_use * eta_gw
    total = h_comp + dcys_50
    print(f"  Health component (DALYs*eta): {np.median(h_comp):.4f} DCYeq/person")
    print(f"  Income component (DCYs):      {np.median(dcys_50):.4f} DCYeq/person")
    print(f"  Total:                         {np.median(total):.4f} DCYeq/person")
    print(f"  Health share:                  {np.median(h_comp)/np.median(total)*100:.1f}%")
    print(f"  Income share:                  {np.median(dcys_50)/np.median(total)*100:.1f}%")

# =========================
# SECTION 7: GIVEWELL COMPARISON
# =========================
print(f"\n{'='*W}")
print("7. COMPARISON TO GIVEWELL BAR")
print("=" * W)
print("""
  Reference points:
    GiveDirectly:  ~$60-100/DCY
    AMF:           ~$50-100/DALY
    SMC:           ~$30-80/DALY
    Deworming:     ~$50-100/DALY (contested)
    GiveWell bar:  ~$100/DALY ≈ $43/DCY at eta=2.3 ≈ $230/DCYeq at eta=2.3
""")

for mfrac_name, mfrac in [("20%", 0.20), ("50%", 0.50), ("100%", 1.00)]:
    for cond, clabel, dalys_use in [(False, "ex-ante", dalys_pp_full), (True, "conditional", dalys_pp_cond)]:
        dcys_t, _ = compute_dcys(mfrac, conditional=cond)
        _, cost_eq = compute_combined(dalys_use, dcys_t, eta_gw)
        med = np.median(cost_eq)
        ratio = med / 100
        print(f"  Wheelchair ({mfrac_name:>4} marg, {clabel:>11}): ${med:>6.0f}/DCYeq = {ratio:.1f}x GiveWell bar")

# =========================
# SECTION 8: DISTRIBUTIONS
# =========================
print(f"\n{'='*W}")
print("8. PARAMETER DISTRIBUTIONS (input sanity check)")
print("=" * W)
print(f"\n  {'Parameter':<28} {'5th':>8} {'25th':>8} {'50th':>8} {'75th':>8} {'95th':>8}")
print(f"  {'-'*68}")
for name, arr in [
    ("DW % reduction", dw_pct_reduction),
    ("Income gain (raw $/yr)", income_gain_raw),
    ("Baseline consumption $/yr", baseline_consump),
    ("Usage rate", usage_rate),
    ("Wheelchair lifespan (yr)", wheelchair_life),
    ("Additionality", additionality),
    ("P(success)", p_success),
    ("Discounted years", disc_years),
]:
    print(f"  {name:<28} {pct(arr,5):>8.3f} {pct(arr,25):>8.3f} {np.median(arr):>8.3f} {pct(arr,75):>8.3f} {pct(arr,95):>8.3f}")


# =========================
# SECTION 9: ANSWER THE KEY QUESTION
# =========================
print(f"\n{'='*W}")
print("9. ANSWERING THE KEY QUESTION")
print("=" * W)
print("""
  Q: At what income-attribution level does the combined metric clear the bar?

  The answer depends critically on whether you include p_success (program risk):

  A. EX-ANTE (includes 34% program success probability):
     - At NO level of income attribution does the median $/DCYeq fall below $100
     - Even at eta=20 (extremely high health premium) and 100% attribution,
       median $/DCYeq ~ $104, barely touching $100
     - The bottleneck is p_success: you're paying $200/person but only 34% of
       programs actually deliver

  B. CONDITIONAL ON PROGRAM SUCCESS:
     - This is the right frame for evaluating a SPECIFIC program that already works
     - Results are ~3x better (dividing by p_success ~ 0.34)
""")

# Compute conditional thresholds
print(f"  Conditional thresholds (median $/DCYeq < target):")
print(f"  {'eta':>6} | {'Income attr for <$100':>24} | {'Income attr for <$200':>24} | {'Income attr for <$500':>24}")
print(f"  {'-'*82}")
for eta in [1, 2.3, 5, 10, 20]:
    row = {}
    for target in [100, 200, 500]:
        found = None
        for test_pct in range(0, 101):
            frac = test_pct / 100.0
            dcys_t, _ = compute_dcys(frac, conditional=True)
            _, cost_eq = compute_combined(dalys_pp_cond, dcys_t, eta)
            if np.median(cost_eq) < target:
                found = test_pct
                break
        row[target] = f"{found}%" if found is not None else "Never"
    print(f"  {eta:>6.1f} | {row[100]:>24} | {row[200]:>24} | {row[500]:>24}")

# =========================
# SECTION 10: RECOMMENDATIONS
# =========================
print(f"\n{'='*W}")
print("10. RECOMMENDATIONS")
print("=" * W)

med_cond = np.median(cost_per_daly_cond)
med_full = np.median(cost_per_daly_full)

# Compute combined conditional at 50% marginal, eta=2.3
dcys_50c, _ = compute_dcys(0.50, conditional=True)
_, cost_combined_50c = compute_combined(dalys_pp_cond, dcys_50c, eta_gw)
med_combined = np.median(cost_combined_50c)

# What multiple of GiveWell bar?
gw_multiple_daly = med_cond / 100
gw_multiple_combined = med_combined / 100

print(f"""
  KEY NUMBERS (conditional on program success, the decision-relevant frame):
    $/DALY (health only):                 ${med_cond:.0f}  ({gw_multiple_daly:.0f}x GiveWell bar)
    $/DCYeq (combined, 50% marg, eta=2.3): ${med_combined:.0f}  ({gw_multiple_combined:.0f}x GiveWell bar)

  FINDING 1: NOT COMPETITIVE ON PURE CEA
    Even conditional on success, wheelchair provision is {gw_multiple_daly:.0f}x the GiveWell bar
    on health alone and {gw_multiple_combined:.0f}x on the combined metric. Adding income narrows
    the gap but does not close it.

  FINDING 2: THE BOTTLENECK IS THE DW REDUCTION, NOT THE COST
    At $200/person, the cost is low. The issue is that a 25% reduction in a 0.406
    DW yields only 0.10 DALYs/year, and over 4 years with usage/additionality
    adjustments, you get ~{np.median(dalys_pp_cond):.2f} DALYs/person (conditional).
    For context, preventing a child malaria death averts ~30 DALYs.

  FINDING 3: INCOME ADDS ~40-60% MORE VALUE (at eta=2.3)
    At 50% income attribution with GiveWell's eta, the income component adds
    roughly 40-60% on top of the health benefit. This is meaningful but not
    transformative enough to cross the GiveWell bar.

  FINDING 4: DCY SHOULD BE A SECONDARY METRIC
    - PRIMARY: $/DALY -- wheelchair programs are fundamentally health/disability interventions
    - SECONDARY: $/DCY and combined $/DCYeq -- strengthens the case by ~40-60%
    - The combined metric is useful for apples-to-apples comparison with GiveWell
      programs, but the income evidence is too uncertain to make it primary
    - Recommendation: report $/DALY, $/DCY, and $/DCYeq side by side

  FINDING 5: THE INVESTMENT CASE RESTS ON NON-CEA ARGUMENTS
    Wheelchairs at ~${med_combined:.0f}/DCYeq (conditional, combined) are not competitive
    with top GiveWell charities. The case for wheelchair funding must rest on:
    (a) Equity/rights arguments (disability is systematically neglected)
    (b) The DW reduction is likely understated (UK QALY proxy may undercount)
    (c) Spillover effects not captured (caregiver time, dignity, social inclusion)
    (d) Market-building effects (catalyzing local AT manufacturing)
    (e) Portfolio diversification across cause areas

  FINDING 6: IF THE DW REDUCTION WERE HIGHER, THE MATH CHANGES
    The DW_pct_reduction = 25% is MEDIUM-LOW confidence from a UK QALY proxy.
    If wheelchair users' lived experience shows 50% DW reduction (plausible for
    someone going from immobile to mobile), the health benefit doubles, and
    conditional $/DCYeq drops to ~${med_combined * 0.60:.0f}-{med_combined * 0.70:.0f}. Better DW evidence is the
    highest-value research investment.
""")

print("=" * W)
print("MODEL COMPLETE")
print("=" * W)
