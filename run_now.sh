#!/bin/bash
set -euo pipefail
cd /Users/parthahya/tools/research_loop_tool

MODEL="claude-opus-4-8"
mkdir -p logs

run_loop() {
  local RUN_DIR="$1"
  local MAX_ITER="$2"
  local LABEL="$3"
  echo "=== Starting: $LABEL — $(date) ===" | tee -a logs/overnight_20260928.log
  for i in $(seq 1 "$MAX_ITER"); do
    echo "[$LABEL] iter $i — $(date)" | tee -a logs/overnight_20260928.log
    OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print --model "$MODEL" --dangerously-skip-permissions 2>&1)
    echo "$OUTPUT" >> "$RUN_DIR/iteration_${i}.log"
    if echo "$OUTPUT" | grep -q "<promise>DONE</promise>"; then
      echo "[$LABEL] DONE at iter $i" | tee -a logs/overnight_20260928.log
      break
    fi
    sleep 8
  done
  echo "=== Done: $LABEL — $(date) ===" | tee -a logs/overnight_20260928.log
}

run_loop "research_runs/Nexleaf_sensor_only_CE_20260928_092857"                  6 "Nexleaf sensor-only CE"
sleep 15
run_loop "research_runs/Nexleaf_maintenance_institutionalization_CE_20260928_094702" 6 "Nexleaf maintenance CE"
sleep 15
run_loop "research_runs/ImpulsoGov_scale_trajectory_NCD_mechanism_20260928_092857"  6 "ImpulsoGov scale+NCD"
sleep 15
run_loop "research_runs/ImpulsoGov_syphilis_pathway_deepdive_20260928_094702"       5 "ImpulsoGov syphilis"
sleep 15
run_loop "research_runs/ImpulsoGov_RCT_results_cervical_evidence_20260928_094702"   5 "ImpulsoGov RCT+cervical"

echo "=== All runs done, uploading to Docs ===" | tee -a logs/overnight_20260928.log
python3 deep_research/upload_to_gdoc.py "research_runs/Nexleaf_sensor_only_CE_20260928_092857" 2>&1 | tail -2
python3 deep_research/upload_to_gdoc.py "research_runs/Nexleaf_maintenance_institutionalization_CE_20260928_094702" 2>&1 | tail -2
python3 deep_research/upload_to_gdoc.py "research_runs/ImpulsoGov_scale_trajectory_NCD_mechanism_20260928_092857" 2>&1 | tail -2
python3 deep_research/upload_to_gdoc.py "research_runs/ImpulsoGov_syphilis_pathway_deepdive_20260928_094702" 2>&1 | tail -2
python3 deep_research/upload_to_gdoc.py "research_runs/ImpulsoGov_RCT_results_cervical_evidence_20260928_094702" 2>&1 | tail -2
echo "=== All uploaded ===" | tee -a logs/overnight_20260928.log
