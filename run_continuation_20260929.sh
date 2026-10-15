#!/bin/bash
set -euo pipefail
cd /Users/parthahya/tools/research_loop_tool

MODEL="claude-opus-4-8"
LOG="logs/continuation_20260929.log"
mkdir -p logs

run_loop() {
  local RUN_DIR="$1"
  local MAX_ITER="$2"
  local LABEL="$3"
  echo "=== Starting: $LABEL — $(date) ===" | tee -a "$LOG"
  for i in $(seq 1 "$MAX_ITER"); do
    echo "[$LABEL] iter $i — $(date)" | tee -a "$LOG"
    OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print --model "$MODEL" --dangerously-skip-permissions 2>&1)
    echo "$OUTPUT" >> "$RUN_DIR/iteration_${i}.log"
    if echo "$OUTPUT" | grep -q "<promise>DONE</promise>"; then
      echo "[$LABEL] DONE at iter $i" | tee -a "$LOG"
      break
    fi
    sleep 8
  done
  echo "=== Done: $LABEL — $(date) ===" | tee -a "$LOG"
}

upload() {
  local RUN_DIR="$1"
  echo "Uploading $RUN_DIR..." | tee -a "$LOG"
  python3 deep_research/upload_to_gdoc.py "$RUN_DIR" 2>&1 | tail -2 | tee -a "$LOG" || echo "Upload failed for $RUN_DIR" | tee -a "$LOG"
}

# ===== ESSENTIAL (upload competitive landscape + remaining 2) =====
echo "=== ESSENTIAL BATCH — $(date) ===" | tee -a "$LOG"
upload "research_runs/Essential_competitive_landscape_20260929"
sleep 5
run_loop "research_runs/Essential_injera_microbiota_opportunity_20260929" 6 "Essential injera/microbiota"
sleep 10
run_loop "research_runs/Essential_philanthropic_entry_points_20260929"   6 "Essential entry points"
sleep 10
upload "research_runs/Essential_injera_microbiota_opportunity_20260929"
upload "research_runs/Essential_philanthropic_entry_points_20260929"

# ===== PULA / ENERGY FOR GROWTH HUB =====
echo "=== PULA + EFORGH BATCH — $(date) ===" | tee -a "$LOG"
run_loop "research_runs/Pula_philanthropic_entry_points_20260929"             6 "Pula entry points"
sleep 10
run_loop "research_runs/Pula_government_buyer_landscape_20260929"             6 "Pula govt landscape"
sleep 10
run_loop "research_runs/Pula_Foundation_vs_commercial_evaluation_20260929"    6 "Pula Foundation eval"
sleep 10
run_loop "research_runs/EforGH_WB_GEP_integration_deep_dive_20260929"        6 "EforGH WB integration"
sleep 10
run_loop "research_runs/EforGH_government_adoption_Ghana_Kenya_20260929"      6 "EforGH govt adoption"
sleep 10
run_loop "research_runs/EforGH_demand_estimation_evidence_20260929"           6 "EforGH demand evidence"
sleep 10
for run in \
  "research_runs/Pula_philanthropic_entry_points_20260929" \
  "research_runs/Pula_government_buyer_landscape_20260929" \
  "research_runs/Pula_Foundation_vs_commercial_evaluation_20260929" \
  "research_runs/EforGH_WB_GEP_integration_deep_dive_20260929" \
  "research_runs/EforGH_government_adoption_Ghana_Kenya_20260929" \
  "research_runs/EforGH_demand_estimation_evidence_20260929"; do
  upload "$run"
done

# ===== MATERNAL HEALTH (remaining 6) =====
echo "=== MATERNAL HEALTH BATCH — $(date) ===" | tee -a "$LOG"
run_loop "research_runs/Ultrasound_aspirin_pathway_crux_20260928"                6 "Aspirin pathway"
sleep 10
run_loop "research_runs/Ultrasound_India_PCPNDT_regulatory_20260928"             6 "India PC-PNDT"
sleep 10
run_loop "research_runs/Ultrasound_referral_treatment_capacity_20260928"         6 "Referral capacity"
sleep 10
run_loop "research_runs/Ultrasound_Ethiopia_AI_POCUS_RCT_20260928"              6 "Ethiopia AI-POCUS RCT"
sleep 10
run_loop "research_runs/Gates_maternal_health_2025_portfolio_20260928"           6 "Gates portfolio"
sleep 10
run_loop "research_runs/Maternal_health_philanthropic_portfolio_design_20260928" 6 "Portfolio design"
sleep 10
for run in \
  "research_runs/Ultrasound_aspirin_pathway_crux_20260928" \
  "research_runs/Ultrasound_India_PCPNDT_regulatory_20260928" \
  "research_runs/Ultrasound_referral_treatment_capacity_20260928" \
  "research_runs/Ultrasound_Ethiopia_AI_POCUS_RCT_20260928" \
  "research_runs/Gates_maternal_health_2025_portfolio_20260928" \
  "research_runs/Maternal_health_philanthropic_portfolio_design_20260928"; do
  upload "$run"
done

echo "=== ALL CONTINUATION RUNS COMPLETE — $(date) ===" | tee -a "$LOG"
