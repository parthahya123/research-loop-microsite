#!/bin/bash
set -euo pipefail

RUN_DIR="research_runs/RSV_vaccine_AMC_facility_20261002"
MAX_ITER=8
MODEL_FLAG="--model claude-opus-4-6"

echo "=== RSV Facility Research Loop ==="
echo "=== Run: $RUN_DIR ==="

for i in $(seq 1 "$MAX_ITER"); do
  echo ""
  echo "=== Iteration $i / $MAX_ITER === $(date '+%H:%M:%S') ==="
  OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print $MODEL_FLAG --dangerously-skip-permissions 2>&1)
  echo "$OUTPUT"
  if echo "$OUTPUT" | grep -q '<promise>DONE</promise>'; then
    echo "=== DONE at iter $i ==="
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
  echo "=== Uploading to Google Doc ==="
  python3 deep_research/upload_to_gdoc.py "$RUN_DIR"
fi
