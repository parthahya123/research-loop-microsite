#!/bin/bash
set -euo pipefail
cd /Users/parthahya/tools/research_loop_tool

MODEL="claude-opus-4-8"
LOG="logs/pula_eforgh_20260929.log"
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

# --- PULA RUNS (4) ---
run_loop "research_runs/Pula_agricultural_insurance_CE_BOTEC_20260929"       6 "Pula CE BOTEC"
sleep 10
run_loop "research_runs/Pula_philanthropic_entry_points_20260929"             6 "Pula entry points"
sleep 10
run_loop "research_runs/Pula_government_buyer_landscape_20260929"             6 "Pula govt landscape"
sleep 10
run_loop "research_runs/Pula_Foundation_vs_commercial_evaluation_20260929"    6 "Pula Foundation eval"
sleep 10

# --- ENERGY FOR GROWTH HUB RUNS (3) ---
run_loop "research_runs/EforGH_WB_GEP_integration_deep_dive_20260929"        6 "EforGH WB integration"
sleep 10
run_loop "research_runs/EforGH_government_adoption_Ghana_Kenya_20260929"      6 "EforGH govt adoption"
sleep 10
run_loop "research_runs/EforGH_demand_estimation_evidence_20260929"           6 "EforGH demand evidence"
sleep 10

echo "=== ALL 7 RUNS COMPLETE — $(date) ===" | tee -a "$LOG"
echo "=== Uploading to Google Docs... ===" | tee -a "$LOG"

for run in \
  "research_runs/Pula_agricultural_insurance_CE_BOTEC_20260929" \
  "research_runs/Pula_philanthropic_entry_points_20260929" \
  "research_runs/Pula_government_buyer_landscape_20260929" \
  "research_runs/Pula_Foundation_vs_commercial_evaluation_20260929" \
  "research_runs/EforGH_WB_GEP_integration_deep_dive_20260929" \
  "research_runs/EforGH_government_adoption_Ghana_Kenya_20260929" \
  "research_runs/EforGH_demand_estimation_evidence_20260929"; do
  upload "$run"
done

echo "=== ALL UPLOADED ===" | tee -a "$LOG"
