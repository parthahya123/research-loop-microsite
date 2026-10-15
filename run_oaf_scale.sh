#!/bin/bash
# Standalone research loop for OAF scale potential
# Bypasses research_loop_fixed2.sh (which has a broken heredoc)
# Uses env -u CLAUDECODE to allow nested claude calls

set -euo pipefail

RUN_DIR="/Users/parthahya/tools/research_loop_tool/research_runs/OAF_scale_potential_big_proposal_20261005_154317"
PROMPT="$RUN_DIR/prompt.md"
MAX_ITER=8
MODEL_FLAG="--model claude-opus-4-6"

echo "=== OAF Scale Potential Research Loop ==="
echo "=== Run dir: $RUN_DIR ==="
echo "=== Max iterations: $MAX_ITER ==="
echo ""

mkdir -p "$RUN_DIR/research"

for i in $(seq 1 "$MAX_ITER"); do
  echo ""
  echo "=== Iteration $i / $MAX_ITER  [$(date '+%H:%M:%S')] ==="

  OUTPUT=$(env -u CLAUDECODE claude --print $MODEL_FLAG --dangerously-skip-permissions < "$PROMPT" 2>&1)
  echo "$OUTPUT"

  # Update iteration count in progress.json
  python3 -c "
import json
with open('$RUN_DIR/progress.json') as f:
    p = json.load(f)
p['total_iterations'] = $i
with open('$RUN_DIR/progress.json', 'w') as f:
    json.dump(p, f, indent=2)
"

  # Check for completion
  if echo "$OUTPUT" | grep -q '<promise>DONE</promise>'; then
    echo ""
    echo "=== Research complete at iteration $i ==="
    break
  fi
done

# Check for synthesis and upload
SYNTH=""
if [ -f "$RUN_DIR/synthesis.md" ]; then
  SYNTH="$RUN_DIR/synthesis.md"
elif [ -f "$RUN_DIR/research/synthesis.md" ]; then
  cp "$RUN_DIR/research/synthesis.md" "$RUN_DIR/synthesis.md"
  SYNTH="$RUN_DIR/synthesis.md"
fi

if [ -n "$SYNTH" ]; then
  echo ""
  echo "=== Uploading to Google Doc ==="
  cd /Users/parthahya/tools/research_loop_tool
  python3 deep_research/upload_to_gdoc.py "$RUN_DIR"
else
  echo "WARNING: No synthesis.md found."
fi

# Update config with end time
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -c "
import json
with open('$RUN_DIR/config.json') as f:
    c = json.load(f)
c['ended_at'] = '$END_TIME'
with open('$RUN_DIR/config.json', 'w') as f:
    json.dump(c, f, indent=2)
"

echo ""
echo "=== DONE ==="
