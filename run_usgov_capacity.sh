#!/bin/bash
set -euo pipefail

BASE="/Users/parthahya/tools/research_loop_tool/research_runs"
TS="20261013_120000"

echo "=== Launching 7 US Gov Capacity research runs in parallel ==="

bash "$BASE/USGov_Salience_Fix_${TS}/run.sh"    > /tmp/usgov_salience.log    2>&1 &
PID1=$!
bash "$BASE/USGov_TrustResidual_${TS}/run.sh"   > /tmp/usgov_trust.log       2>&1 &
PID2=$!
bash "$BASE/USGov_SubmergedState_${TS}/run.sh"  > /tmp/usgov_submerged.log   2>&1 &
PID3=$!
bash "$BASE/USGov_CrisisResponse_${TS}/run.sh"  > /tmp/usgov_crisis.log      2>&1 &
PID4=$!
bash "$BASE/USGov_FinancialCrisis_${TS}/run.sh" > /tmp/usgov_financial.log   2>&1 &
PID5=$!
bash "$BASE/USGov_Touchpoints_${TS}/run.sh"     > /tmp/usgov_touchpoints.log 2>&1 &
PID6=$!
bash "$BASE/USGov_ReverseArrow_${TS}/run.sh"    > /tmp/usgov_reverse.log     2>&1 &
PID7=$!

echo "PIDs: $PID1 $PID2 $PID3 $PID4 $PID5 $PID6 $PID7"
echo "Logs: /tmp/usgov_*.log"
echo ""
echo "=== Launching synthesis run (will wait for all 7) ==="

bash "$BASE/USGov_Synthesis_${TS}/run.sh" > /tmp/usgov_synthesis.log 2>&1 &
PID_SYNTH=$!
echo "Synthesis PID: $PID_SYNTH"

echo ""
echo "=== All 8 runs launched. Monitor with: ==="
echo "  tail -f /tmp/usgov_salience.log"
echo "  tail -f /tmp/usgov_synthesis.log"
echo "  for f in /tmp/usgov_*.log; do echo \"=== \$f ===\"; tail -3 \$f; done"
