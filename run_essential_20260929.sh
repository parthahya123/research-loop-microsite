#!/bin/bash
set -euo pipefail
cd /Users/parthahya/tools/research_loop_tool

MODEL="claude-opus-4-8"
LOG="logs/essential_20260929.log"
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

run_loop "research_runs/Essential_protein_BOTEC_stress_test_20260929"   6 "Essential BOTEC stress test"
sleep 10
run_loop "research_runs/Essential_competitive_landscape_20260929"        6 "Essential competitive landscape"
sleep 10
run_loop "research_runs/Essential_injera_microbiota_opportunity_20260929" 6 "Essential injera/microbiota"
sleep 10
run_loop "research_runs/Essential_philanthropic_entry_points_20260929"   6 "Essential entry points"

echo "=== ALL 4 ESSENTIAL RUNS COMPLETE — $(date) ===" | tee -a "$LOG"

# Upload to Google Docs
for RUN_DIR in \
  "research_runs/Essential_protein_BOTEC_stress_test_20260929" \
  "research_runs/Essential_competitive_landscape_20260929" \
  "research_runs/Essential_injera_microbiota_opportunity_20260929" \
  "research_runs/Essential_philanthropic_entry_points_20260929"; do
  echo "Uploading $RUN_DIR..." | tee -a "$LOG"
  upload "$RUN_DIR" | tee -a "$LOG" || echo "Upload failed for $RUN_DIR" | tee -a "$LOG"
done

echo "=== UPLOADS COMPLETE — $(date) ===" | tee -a "$LOG"
