# NeoTest BOTEC v4.1 — Reference Context for Research Agents
*Corrected September 2026 after primary document review. All corrections are grounded in the primary NeoTest documents: main report (CGD 2026), appendices (TPP, HTA = Fedorov et al. CGD WP 744), operational note, and funder two-pager.*

## The Facility
**NeoTest AMC** — $60M pull-funding facility for a point-of-care neonatal sepsis diagnostic (finger-prick, <30 min). Three components:
- $20M milestone prize (first TPP-compliant product: ≥90% Se, ≥80% Sp, ≤$5/test, regulatory approval, COGS audit, LMIC commercialization commitment)
- $10M implementation support (2027–2032): regulatory, training, demand activation
- $30M AMC: $7/test (first 2M qualifying tests), $5/test (next 2M), $3/test (final 2M)

Fund hosted at Renaissance Philanthropy. Lead: Akhil Bansal (CGD/MSA). Administrator: MedAccess (advanced discussions). $10M anchor commitment secured. 8 target countries: Brazil, Ethiopia, Ghana, India, Kenya, Nigeria, South Africa, Tanzania.

## WHO TPP (Appendix A, confirmed)
| Parameter | Essential | Desirable |
|-----------|-----------|-----------|
| Sensitivity | **≥90%** | ≥95% |
| Specificity | **≥80%** | ≥90% |
| Price | **≤$5** | ≤$3 |
| TTFR | ≤60 min | ≤30 min |

**CRITICAL**: The test is NOT intended to de-escalate, cease, or choose antibiotics. Its intended use is: **whether to INITIATE antibiotics** (initiation-gate). De-escalation is explicitly out of scope of the WHO TPP.

## Source Health Technology Assessment: Fedorov et al. CGD WP 744 (April 2026)
**Source**: Fedorov, Maxim Sharakin, et al. "Cost-Effectiveness of a Target Point-of-Care Triage Test for Neonatal Sepsis in Low- and Middle-Income Countries." CGD Working Paper 744. April 2026. (Appendix D of the appendices document.)

*Note: Chevalier et al. (Open Forum Infect Dis 2025, ofaf652) is cited as reference #29 in the main report and reference #13 in the HTA as prior literature — it is NOT the source model.*

### HTA Model Structure
- **Two cohorts**: c1 = facility-of-birth (inborn), c2 = community-presenting
- **Three risk strata per cohort**: Low (L), Moderate (M), High (H)
- **High-risk safety override**: H-risk infants bypass POCT → immediate treatment regardless of result
- **L/M-risk guided by POCT**: positive → initiate antibiotics; negative → no treatment (initiation-gate)
- **Base parameters**: Se=0.90, Sp=0.80, p_NS (inborn L/M/H) = 0.23/0.47/0.93; community = 0.08/0.175/0.34
- **Clinical judgment comparator**: CJ Sens = 0.70 (c1 L/M), 0.65 (c2 L/M); both cohorts 0% false-negative rate for H-risk
- **BCR discount rate**: 2% (social), costs discounted at firm's 9.8% hurdle rate for sizing

### HTA Results (Table 3, Fedorov et al.)
Per 1,000 PSBI infants tested:

| | c1 (Inborn) | c2 (Community) |
|--|-------------|----------------|
| DALYs averted | **206** | **127** |
| Cost saving | **$37,342** | **$5,715** |
| Deaths averted | 6 | 4 |

- **c1 dominant in 93.2% of PSA iterations**
- **c2 dominant in 84.8% of PSA iterations**
- Test is **cost-saving AND health-improving** at $5/test
- Minimum Se for net benefit: **72% (c1)**, **66% (c2)** (at $5/test, WTP=$1,500/DALY)

### Key HTA Parameters (Table 1, Fedorov et al.)
| Parameter | c1 | c2 |
|-----------|----|----|
| Bacterial prevalence (overall PSBI pool) | ~25.1% weighted | ~12.5% weighted |
| BC positivity fraction | 6% | 6% |
| HAI risk per inpatient stay | 6% | 6% |
| HAI risk per inpatient day | 0.0058 | 0.00580 |
| CFR treated NS (L/M/H) | 0.04/0.09/0.20 | 0.04/0.09/0.20 |
| CFR untreated NS (L/M/H) | 0.11/0.26/0.57 | 0.11/0.26/0.57 |
| Referral rates c2 (L/M/H) | N/A | 0/0.30/0.60 |
| RR mortality treated vs untreated | 0.35 | 0.35 |

## Benefit–Cost Ratio Calculations (Appendix H)
- **BCR horizon**: 15 years (2030–2045), discounted at 2% social rate
- **Per-test DALY**: 0.167 (50/50 weighted average of c1=0.206 and c2=0.127)
- **Per-test healthcare saving**: $22 (50/50 weighted of $37.34 c1 and $5.72 c2)
- **BCR (at GDP per capita DALY valuation)**: **78**
- **Cost per DALY (excluding healthcare savings)**: **$39/DALY**
- **Including healthcare savings**: net cost-saving (~$91 in net benefit per DALY)
- **P(success) used in BCR**: 65% (conservative; 71% used for facility sizing)
- **Counterfactual**: product arrives 7 years later without NeoTest, diffuses more slowly (t_mid doubled), commercialization ×0.8
- **Adoption calibrated to**: malaria RDTs and GeneXpert TB (reached ~50% of addressable in 5–8 years)

## BOTEC v4.1 Central Numbers (P50, costs @9%, DALYs @4%)
- **Headline CE: $111/DALY** (P25=$224, P75=$78)
- At 4%/4%: $172/DALY. At 12%/4%: $88/DALY.
- Nominal costs: $50.4M (AMC disburses $20.4M of $30M cap at P50)
- PV DALYs: 191,000. Peak tests/yr: ~399,000.
- Acceleration: 7 years (product launch 2033 vs counterfactual 2040)

*Note: CGD uses 2% social discount and credits healthcare savings → $39/DALY. Our BOTEC uses 9%/4% and excludes healthcare savings → $111/DALY. Both are defensible; the difference is discount rate convention and cost perspective, not a modeling error.*

## TAM Architecture (BOTEC uses SNCU admissions, NOT PSBI presentations)
| Country | TAM | Peak adopt (P50) | Peak tests/yr | Track |
|---------|-----|-----------------|---------------|-------|
| India public | 1,907k/yr | 6.8% | 130k | AMC |
| India private | 850k/yr | 8.0% | 68k | Commercial |
| Nigeria | 840k/yr | 5.0% | 39k | AMC |
| Brazil | 189k/yr | 35% | 66k | AMC |
| Ethiopia | 200k/yr | 20% | 39k | AMC |
| Kenya | 132k/yr | 25% | 33k | AMC |
| Ghana | 93k/yr | 25% | 23k | AMC |

India public TAM = 1.64M HB-cluster + 267k Leader-cluster SNCU admissions (HMIS 2023-24).
India private TAM = Apollo/Rainbow/Fortis/Cloudnine NICU admissions; commercial track, no AMC draw.

## DALYs per Test Decomposition (BOTEC v4.1 — our model)
- Mortality: 0.1098 (78.9%)
- AMR reduction: 0.0128 (9.2%)
- HAI averted: 0.0105 (7.5%)
- Long-term complications: 0.0025 (1.8%)
- Hospital cost savings: 0.0037 (2.7%)
- **Total: 0.1392 DALYs/test**
- Model parameters: 50/50 inpatient-community mix, c2=0.50 referral adherence, Se=0.90

*CGD's HTA gives 0.167 DALYs/test on 50/50 weighting — higher than our 0.1392, primarily because CGD includes healthcare cost savings in the benefit numerator while we count them separately. At GDP/capita DALY valuation, CGD gets BCR=78.*

## Key Assumptions
| Assumption | Central | Range |
|-----------|---------|-------|
| Acceleration (years) | 7 | 5-10 |
| India HB peak adoption | 5.5% | 3.5-8% |
| India Leader peak adoption | 15% | 10-20% |
| India private peak adoption | 8% | 4-12% |
| Community adherence c2 | 0.50 | 0.30-0.70 |
| NEDL listing year | 2031 | 2029-2033 |
| Cost discount | 9% central | 4-12% |
| DALY discount | 4% | 3-5% |

## Clinical Design (Confirmed from Primary Documents)
The test operates as an **INITIATION-GATE** in both cohorts:
- **Inborn (c1)**: grey-zone infants at facility of birth get POCT; positive → initiate antibiotics; negative → no treatment
- **Community (c2)**: presenting infants get POCT; positive → treat and/or refer; negative → no treatment/referral withheld
- **High-risk safety override**: critically unwell bypass the test entirely
- This is the design validated in use-case consultation (32 physicians, Appendix B, Figure B.2)
- Clinician compliance with negative POCT result: ~70-80% expected (malaria RDT precedent: 83% adherence)
- De-escalation (stopping antibiotics after initiation) is explicitly NOT the intended use

## Completed Research Findings (September 2026)

### Prior research loops (pre-primary document review) — findings requiring revision
The following findings from prior loops were based on the incorrect assumption that Chevalier 2025 OFID was the source model and that "de-escalation" was the intended clinical mode. They need to be re-evaluated:
- "STRUCTURAL INCOHERENCE CONFIRMED" claim → WRONG. The actual source model (Fedorov et al.) correctly uses initiation-gate, which is consistent with the TPP.
- "AMC milestone floor (85%)" → WRONG. The milestone requires full TPP compliance (≥90% Se).
- "5pp disbursement gap" → WRONG. This was based on false 85% Se assumption.
- "de-escalation dm_tx ≈ 0.005 for 72% hospital arm" → Needs re-evaluation under initiation-gate framing.

### Findings from prior loops that remain valid
- India adoption corrections: Leader P50 15%, HB P50 5.5%, peak ~130k tests/yr (vs inflated 434k/yr in v3)
- Nigeria missing from v3 BOTEC — added: TAM 840k, P50 5%, 39k tests/yr
- Ethiopia TAM corrected: 545k → 200k (facility-adjusted)
- Discount rate correction: PV costs at 9%, not nominal
- AMR DALY credit: should be ~0.001/test not 0.013 (13× overstatement in early models)
- HAI DALY credit: 0.001/test is a reasonable central estimate
- Community arm c2 (referral adherence): real uncertainty, central 0.38 (AFRINEST), range 0.25-0.55

### Run X: Net-harm mechanism (now re-framed under initiation-gate)
Under initiation-gate, net harm occurs when Se < f_cf (fraction who would receive antibiotics under standard of care). For the CGD model's high-risk safety override, effectively f_cf_tested = 0 for H-risk (they always get antibiotics). For L/M-risk (the tested subset), f_cf is lower. The minimum Se for net benefit is 72% (c1) / 66% (c2) — confirmed from Figure 2 of HTA.

### Run Y: Care-seeking chain validation
Still valid. BOTEC uses facility-admissions denominator (correct). Community arm relies on PSBI presenting to PHC/CHW. CGD BCR uses 50/50 c1/c2 weighting for the headline BCR — this may overweight c2 for near-term deployment where community infrastructure is limited.

### India Regulatory Run
Still valid. Median 10 years WHO-PQ to national scale. NEDL 2031 is the critical gate. Binding constraint is diffusion tail.

## Open Empirical Questions (Priority for Research Agents)
1. **p (bacterial prevalence)**: CGD uses 25.1% among PSBI-presenting (251/1000). Prior BOTEC used 12%. Which is correct for each facility tier?
2. **50/50 c1/c2 weighting**: CGD notes this is a simplification. Near-term deployment is more c1-weighted (facility-of-birth). What is the realistic near-term vs long-term weighting?
3. **Se achievability**: Is ≥90% Se on neonatal capillary blood before antibiotic exposure achievable? NeoSep-SAA Phase 3 is the key trial.
4. **Counterfactual validity**: Is 7-year acceleration the right counterfactual? Does any test exist that could reach market without NeoTest in <10 years?
5. **dm_tx calibration**: BARNARDS I/II shows first-line amp-gent coverage ~25-31%. How does this feed into the initiation-gate model's effective treatment benefit?
6. **Community referral rates**: CGD uses Ref_M=0.30, Ref_H=0.60 for c2. What are empirical rates from Nigeria/Ethiopia PSBI programs?

## Structural Risks
1. NeoSep-SAA fails culture-confirmed pivotal (most likely failure mode)
2. NEDL 2031 listing missed — stalls India public track until ~2037
3. Post-AMC price spike above $5/test (GeneXpert held at $9.98/cartridge for a decade)
4. India private adoption stalls — Apollo/Rainbow don't pilot early
5. Community arm c2 lower than 0.30 in Nigeria/Ethiopia — entire community arm becomes net-zero

## Staged Commitment Recommendation
- Tranche 1 ~$3-5M: co-fund NeoSep-SAA culture-confirmed pivotal with Indian SNCU sites; prospective neonatal capillary Se validation required
- Tranche 2 ~$15-20M: milestone prize contingent on (a) ≥90% sensitivity on capillary blood pre-antibiotic (full TPP), (b) tail-price cap + second-source trigger at 2M units, (c) LMIC commercialization commitment
- Tranche 3 ~$10-15M: AMC contribution contingent on (a) verified procurement in ≥3 target countries, (b) COGS audit rights retained

## Discount Rate Comparison
| Model | Cost rate | DALY rate | CE |
|-------|-----------|-----------|-----|
| CGD BCR (Appendix H) | 2% (social) | 2% | $39/DALY |
| Our BOTEC v4.1 | 9% (payer OC) | 4% | $111/DALY |
| GiveWell-comparable | 8-10% | 4% | ~$100-150/DALY |

All three are defensible framings. The $39 is not wrong — it reflects total societal benefit including healthcare savings, at a social discount rate. The $111 is a donor opportunity-cost framing excluding healthcare savings.
