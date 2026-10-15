#!/bin/bash
# Launch research loops for directories with pre-crafted prompt.md files.
# Iterates until progress.json has "done": true or max iterations reached.
#
# Usage: ./launch_existing_runs.sh <run_dir> [max_iterations]
#   OR:  ./launch_existing_runs.sh --all-neotest-2022 [max_iterations]

set -euo pipefail

MODEL_FLAG="--model claude-opus-4-6"
MODEL_NAME="Opus 4.6"

run_single() {
  local RUN_DIR="$1"
  local MAX_ITER="${2:-8}"

  if [ ! -f "$RUN_DIR/prompt.md" ]; then
    echo "ERROR: No prompt.md in $RUN_DIR" >&2
    return 1
  fi

  mkdir -p "$RUN_DIR/research"

  # Initialize progress.json if it doesn't exist or is malformed
  if [ ! -f "$RUN_DIR/progress.json" ]; then
    echo '{"current_phase":"not_started","done":false,"phases":{},"key_numbers":{}}' > "$RUN_DIR/progress.json"
  fi

  echo ""
  echo "=== Launching: $(basename $RUN_DIR) ==="
  echo "=== Model: $MODEL_NAME | Max iterations: $MAX_ITER ==="

  local ITER=0
  while [ $ITER -lt $MAX_ITER ]; do
    ITER=$((ITER + 1))
    echo ""
    echo "--- Iteration $ITER / $MAX_ITER ---"

    # Check if already done
    if python3 -c "import json,sys; d=json.load(open('$RUN_DIR/progress.json')); sys.exit(0 if d.get('done') else 1)" 2>/dev/null; then
      echo "Done (progress.json done=true). Stopping."
      break
    fi

    # Run one iteration (|| true prevents set -e from killing on non-zero exit)
    OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print $MODEL_FLAG --dangerously-skip-permissions 2>&1) || true
    echo "$OUTPUT" | tail -20

    # Check for promise DONE signal
    if echo "$OUTPUT" | grep -q '<promise>DONE</promise>'; then
      echo "Done (DONE signal). Stopping."
      # Mark done in progress.json
      python3 -c "
import json
with open('$RUN_DIR/progress.json','r') as f: d=json.load(f)
d['done']=True
with open('$RUN_DIR/progress.json','w') as f: json.dump(d,f,indent=2)
" 2>/dev/null || true
      break
    fi

    # Check if synthesis.md now exists (another completion signal)
    if [ -f "$RUN_DIR/synthesis.md" ]; then
      DONE_VAL=$(python3 -c "import json; d=json.load(open('$RUN_DIR/progress.json')); print(d.get('done','false'))" 2>/dev/null || echo "false")
      if [ "$DONE_VAL" = "True" ] || [ "$DONE_VAL" = "true" ]; then
        echo "Done (synthesis.md written + done=true). Stopping."
        break
      fi
    fi

    sleep 2
  done

  echo "=== Completed: $(basename $RUN_DIR) (iterations used: $ITER) ==="

  # Upload to Google Docs if synthesis exists
  if [ -f "$RUN_DIR/synthesis.md" ]; then
    echo "Uploading to Google Docs..."
    python3 /Users/parthahya/tools/research_loop_tool/deep_research/upload_to_gdoc.py "$RUN_DIR" 2>/dev/null || echo "(Upload failed or not configured)"
  fi
}

# Main logic
if [ "${1:-}" = "--all-neotest-2022" ] || [ "${1:-}" = "--all-neotest" ]; then
  MAX_ITER="${2:-8}"
  TOOL_DIR="$(dirname "$0")"
  for dir in "$TOOL_DIR"/research_runs/NeoTest_*_20260921_223544; do
    run_single "$dir" "$MAX_ITER" &
    sleep 10  # Stagger starts to avoid rate limits
  done
  wait
  echo ""
  echo "=== All NeoTest 20260921_223544 runs complete ==="
elif [ -n "${1:-}" ]; then
  run_single "$1" "${2:-8}"
else
  echo "Usage: $0 <run_dir> [max_iter]"
  echo "       $0 --all-neotest [max_iter]"
  exit 1
fi
