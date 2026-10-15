#!/bin/bash
set -euo pipefail

MODEL_FLAG="--model claude-opus-4-6"
MAX_ITER=8

run_loop() {
  local RUN_DIR="$1"
  local LABEL="$2"

  echo "=== Starting: $LABEL ==="
  for i in $(seq 1 "$MAX_ITER"); do
    echo "[$LABEL] iter $i — $(date '+%H:%M:%S')"
    OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print $MODEL_FLAG --dangerously-skip-permissions 2>&1)
    echo "$OUTPUT"
    if echo "$OUTPUT" | grep -q '<promise>DONE</promise>'; then
      echo "[$LABEL] DONE at iter $i"
      break
    fi
  done

  END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    c = json.load(f)
c['ended_at'] = sys.argv[2]
with open(sys.argv[1], 'w') as f:
    json.dump(c, f, indent=2)
" "$RUN_DIR/config.json" "$END_TIME"

  if [ -f "$RUN_DIR/synthesis.md" ]; then
    echo "=== Uploading $LABEL to Google Doc ==="
    python3 deep_research/upload_to_gdoc.py "$RUN_DIR"
  fi
  echo "=== Done: $LABEL ==="
}

run_loop "research_runs/IntrapartumSensing_INFANT_applicability_20261002" "INFANT applicability"
run_loop "research_runs/IntrapartumSensing_EffectSize_prior_20261002" "Effect size prior"
run_loop "research_runs/IntrapartumSensing_Surrogate_endpoints_20261002" "Surrogate endpoints"

echo "=== ALL THREE RUNS COMPLETE ==="
