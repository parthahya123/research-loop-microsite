#!/bin/bash
# Overnight research runs — starts at 11pm when rate limits reset
# 5 runs total: 2 Nexleaf + 3 ImpulsoGov

set -euo pipefail
cd /Users/parthahya/tools/research_loop_tool

MODEL="claude-opus-4-8"

RUNS=(
  "research_runs/Nexleaf_sensor_only_CE_20260928_092857|6|Nexleaf sensor-only CE"
  "research_runs/Nexleaf_maintenance_institutionalization_CE_20260928_094702|6|Nexleaf maintenance-only CE"
  "research_runs/ImpulsoGov_scale_trajectory_NCD_mechanism_20260928_092857|6|ImpulsoGov scale+NCD mechanism"
  "research_runs/ImpulsoGov_syphilis_pathway_deepdive_20260928_094702|5|ImpulsoGov syphilis pathway"
  "research_runs/ImpulsoGov_RCT_results_cervical_evidence_20260928_094702|5|ImpulsoGov RCT+cervical"
)

run_loop() {
  local RUN_DIR="$1"
  local MAX_ITER="$2"
  local LABEL="$3"
  echo ""
  echo "======================================"
  echo "=== Starting: $LABEL ==="
  echo "=== $(date) ==="
  echo "======================================"
  for i in $(seq 1 $MAX_ITER); do
    echo "[$LABEL] Iteration $i / $MAX_ITER — $(date)"
    OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print --model $MODEL --dangerously-skip-permissions 2>&1)
    echo "$OUTPUT" >> "$RUN_DIR/iteration_${i}.log"
    if echo "$OUTPUT" | grep -q "<promise>DONE</promise>"; then
      echo "[$LABEL] DONE at iteration $i"
      break
    fi
    sleep 8
  done
  echo "=== Finished: $LABEL — $(date) ==="
}

# Sleep until 11pm EDT
TARGET=$(date -v 23H -v 0M -v 0S +%s)
NOW=$(date +%s)
WAIT=$((TARGET - NOW))
if [ $WAIT -gt 0 ]; then
  echo "Sleeping $WAIT seconds until 11pm EDT..."
  echo "Will start at: $(date -r $TARGET)"
  sleep $WAIT
fi

echo ""
echo "=========================================="
echo "=== OVERNIGHT RUNS STARTING: $(date) ==="
echo "=========================================="

for ENTRY in "${RUNS[@]}"; do
  IFS='|' read -r DIR MAX_ITER LABEL <<< "$ENTRY"
  run_loop "$DIR" "$MAX_ITER" "$LABEL"
  sleep 15  # brief pause between runs
done

# Upload all to Google Docs
echo ""
echo "=== Uploading all runs to Google Docs ==="
for ENTRY in "${RUNS[@]}"; do
  IFS='|' read -r DIR MAX_ITER LABEL <<< "$ENTRY"
  echo "Uploading: $LABEL"
  python3 deep_research/upload_to_gdoc.py "$DIR" 2>&1 | tail -2
  sleep 5
done

echo ""
echo "=========================================="
echo "=== ALL DONE: $(date) ==="
echo "=========================================="
