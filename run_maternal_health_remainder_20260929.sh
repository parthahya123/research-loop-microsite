#!/bin/bash
set -euo pipefail
cd /Users/parthahya/tools/research_loop_tool

MODEL="claude-opus-4-8"
LOG="logs/maternal_health_20260928.log"
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
  python3 deep_research/upload_to_gdoc.py "$RUN_DIR" 2>&1 | tail -2
}

# --- BIRTH ASPHYXIA RUNS (6) ---
run_loop "research_runs/BirthAsphyxia_Janitri_Keyar_deep_dive_20260928"          6 "Janitri deep dive"
sleep 10
run_loop "research_runs/BirthAsphyxia_SBBC_bundle_decomposition_20260928"        6 "SBBC decomposition"
sleep 10
run_loop "research_runs/BirthAsphyxia_EmOC_response_capacity_20260928"           6 "EmOC response"
sleep 10
run_loop "research_runs/BirthAsphyxia_AI_CTG_interpretation_20260928"            6 "AI CTG"
sleep 10
run_loop "research_runs/BirthAsphyxia_newborn_care_HBB_HT_20260928"             6 "HBB + TH"
sleep 10
run_loop "research_runs/BirthAsphyxia_India_LaQshya_20260928"                   6 "India LaQshya"
sleep 10

# --- ULTRASOUND RUNS (5) ---
run_loop "research_runs/Ultrasound_First_Look_null_lessons_20260928"             6 "First Look null"
sleep 10
run_loop "research_runs/Ultrasound_aspirin_pathway_crux_20260928"                6 "Aspirin pathway"
sleep 10
run_loop "research_runs/Ultrasound_India_PCPNDT_regulatory_20260928"             6 "India PC-PNDT"
sleep 10
run_loop "research_runs/Ultrasound_referral_treatment_capacity_20260928"         6 "Referral capacity"
sleep 10
run_loop "research_runs/Ultrasound_Ethiopia_AI_POCUS_RCT_20260928"              6 "Ethiopia RCT"
sleep 10

# --- CROSS-CUTTING RUNS (2) ---
run_loop "research_runs/Gates_maternal_health_2025_portfolio_20260928"           6 "Gates portfolio"
sleep 10
run_loop "research_runs/Maternal_health_philanthropic_portfolio_design_20260928" 6 "Portfolio design"
sleep 10

echo "=== ALL 13 REMAINING RUNS COMPLETE — $(date) ===" | tee -a "$LOG"
echo "=== Uploading to Google Docs... ===" | tee -a "$LOG"

for run in \
  "research_runs/BirthAsphyxia_Janitri_Keyar_deep_dive_20260928" \
  "research_runs/BirthAsphyxia_SBBC_bundle_decomposition_20260928" \
  "research_runs/BirthAsphyxia_EmOC_response_capacity_20260928" \
  "research_runs/BirthAsphyxia_AI_CTG_interpretation_20260928" \
  "research_runs/BirthAsphyxia_newborn_care_HBB_HT_20260928" \
  "research_runs/BirthAsphyxia_India_LaQshya_20260928" \
  "research_runs/Ultrasound_First_Look_null_lessons_20260928" \
  "research_runs/Ultrasound_aspirin_pathway_crux_20260928" \
  "research_runs/Ultrasound_India_PCPNDT_regulatory_20260928" \
  "research_runs/Ultrasound_referral_treatment_capacity_20260928" \
  "research_runs/Ultrasound_Ethiopia_AI_POCUS_RCT_20260928" \
  "research_runs/Gates_maternal_health_2025_portfolio_20260928" \
  "research_runs/Maternal_health_philanthropic_portfolio_design_20260928"; do
  upload "$run"
done

echo "=== ALL UPLOADED ===" | tee -a "$LOG"
