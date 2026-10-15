#!/usr/bin/env python3
"""
Launch a multi-phase, multi-iteration deep CEA research loop for a single org.
Forces 6+ iterations by requiring specific files from prior phases before DONE is allowed.
"""

import sys, os, json, subprocess, time, textwrap

def make_prompt(org, concept_note_text, run_dir):
    return f"""# OAIF Deep CEA Research Agent — {org}

You are conducting a multi-phase cost-effectiveness analysis of **{org}** for the OpenAI Foundation's AI × Global Health portfolio.

## YOUR CURRENT RUN DIRECTORY
`{run_dir}`

## STRICT PHASE REQUIREMENTS
At the START of every iteration, read `{run_dir}/progress.json` to find your current phase.
You MUST complete phases in order. You CANNOT skip phases. You CANNOT declare DONE until phase 7 is complete.

The phases and their required output files:

| Phase | Name | Required output file | Min web searches |
|-------|------|---------------------|-----------------|
| 1 | Org & Proposal Research | `research/1_org_proposal.md` | 5 |
| 2 | Mortality Evidence | `research/2_mortality_evidence.md` | 6 |
| 3 | Analogues & Comparators | `research/3_analogues.md` | 4 |
| 4 | Burden & Additionality | `research/4_burden_additionality.md` | 4 |
| 5 | CEA Model (Python) | `research/5_cea_model.py` + run it + `research/5_model_outputs.json` | 0 |
| 6 | AI Centrality & 50/50 | `research/6_ai_centrality.md` | 2 |
| 7 | Full Synthesis | `synthesis.md` | 0 |

**COMPLETION RULE**: Output `<promise>DONE</promise>` ONLY after:
- All 7 phase files exist in `{run_dir}/`
- `progress.json` shows `"complete": true` and `"phase": 7`
- `synthesis.md` exists and is >3000 words
- DO NOT output DONE in phases 1-6 under any circumstances.

---

## CONCEPT NOTE (read carefully — this is the actual proposal):
{concept_note_text}

---

## METHODOLOGY (apply rigorously):
- **Full-proposal CEA**: grant cost (as stated in concept note) ÷ total program DALYs averted. NOT marginal-AI.
- **Best-guess mortality**: calibrate from mechanism plausibility + non-RCT evidence. Do NOT assume zero. Give point estimate + P10-P90 interval.
- **50/50 score** = `0.5 * ce_norm(daly) + 0.5 * (ai_centrality/10)`
  where `ce_norm(d) = max(0, min(1, 1-(ln(max(d,50))-ln(100))/(ln(100000)-ln(100))))`
- **Cash benchmark**: $250/DALY (GiveDirectly). GiveWell bar: ~$50-100/DALY.
- **AI centrality rubric** (0-10): labor replacement, cost floor/scale ceiling, causal-chain quality, evidence AI drives health outcomes, additionality of AI specifically.
- **Monte Carlo**: 200,000 draws, numpy only, triangular distributions, seed=20260909. Run the model and save outputs.

---

## PHASE INSTRUCTIONS

### PHASE 1 — Org & Proposal Research
Write `research/1_org_proposal.md` covering:
- What the org actually does (not what they claim — verify independently)
- Exactly what they are proposing to OAIF (program, geographies, beneficiaries, budget)
- Track record: what has been independently verified vs self-reported
- Funder landscape: who else funds this, what is the additionality
- The AI technology: what specifically it does, what it replaces, where it is in development
- CITATION REQUIREMENT: every factual claim needs an inline hyperlink [Source YEAR](URL)
- Search `research/search_log.md` before each query, append results after

### PHASE 2 — Mortality Evidence
Write `research/2_mortality_evidence.md` covering:
- The specific causal chain from this intervention to mortality reduction
- Every relevant RCT, quasi-experimental study, and observational study
- Key null results and what they imply
- Analogous programs and what their mortality evidence shows
- Your best-guess mortality effect: point estimate + P10-P90 + explicit reasoning
- The single crux assumption that most determines the $/DALY

### PHASE 3 — Analogues & Comparators
Write `research/3_analogues.md` covering:
- 3-5 closest analogous interventions with their measured mortality effects
- Why each analogue is/isn't applicable to this specific program
- How the analogues inform the mortality mixture distribution
- Portfolio comparators: how this org compares to Noora ($97/DALY), Dimagi/KMC ($93/DALY), SLF ($157/DALY)

### PHASE 4 — Burden & Additionality
Write `research/4_burden_additionality.md` covering:
- Target population burden (disease-specific DALYs, deaths, incidence)
- Addressable fraction (what share does this intervention actually reach)
- Headroom (is there room to move the needle, or are other constraints binding)
- Additionality (what happens counterfactually without this grant)
- Absorptive capacity ceiling (max capital deployable at this CE level, in $/yr)

### PHASE 5 — CEA Model
Write `research/5_cea_model.py` — a complete, runnable numpy Monte Carlo:
- 200,000 draws, seed=20260909
- Triangular distributions on all key parameters, anchored to your research
- Full-program frame AND marginal-AI-layer frame
- Output: median $/DALY, P10, P90, P(≤$100), P(≤$800), total DALYs, Spearman tornado
- Save results to `research/5_model_outputs.json`
- RUN the script: `python3 research/5_cea_model.py`

### PHASE 6 — AI Centrality
Write `research/6_ai_centrality.md` covering:
- Score each dimension (0-10): labor replacement, cost floor, scale ceiling, causal-chain quality, evidence
- Swap test: what happens if you replace the AI with a competent non-AI equivalent
- Final AI centrality score with justification
- 50/50 weighted score calculation (show the math)

### PHASE 7 — Full Synthesis
Write `synthesis.md` — the definitive assessment. MUST include:
(a) $/DALY: median, P10-P90, risk-adjusted. Full-program AND marginal-AI frames.
(b) AI centrality score (0-10) with rubric breakdown
(c) 50/50 weighted score (show formula)
(d) Verdict: FUND / FUND-WITH-CONDITIONS / DECLINE — one-sentence rationale
(e) Key assumption driving the $/DALY (from tornado)
(f) Y1/Y2/Y3 recommended commitment with specific milestone gates and kill-switches
(g) 5 due diligence questions to ask at the OAIF meeting
(h) Org profile (~500 words): proposal summary, AI role, evidence base, risks, cruxes
(i) Scenario table: red-team / conservative / base / upside $/DALY
(j) Absorptive capacity ceiling (prominent, in executive summary)
(k) All claims hyperlinked inline

Synthesis must be >3000 words. Do not abbreviate.

---

## PROGRESS TRACKING
At the start of each iteration, read `{run_dir}/progress.json`.
At the end of each iteration, update it:

```json
{{
  "phase": <current phase number 1-7>,
  "complete": <true only when phase 7 synthesis.md is written>,
  "phases_done": [list of completed phase numbers],
  "key_numbers": {{
    "daly_median": null,
    "ai_centrality": null,
    "score_5050": null,
    "absorptive_capacity_usd_per_yr": null
  }}
}}
```

## SEARCH LOG
Before each web search, check `{run_dir}/research/search_log.md`. After each search append:
`- [query] -> [key finding + URL]`

Never repeat a query already in the log.

---

## REMINDER
- You are in a loop. You have NO memory between iterations. Read progress.json and all prior phase files at the start of each iteration.
- Do ONE phase per iteration (or at most two if a phase is very short).
- Do NOT output `<promise>DONE</promise>` until phase 7 synthesis.md exists and is >3000 words.
- Every factual claim needs an inline hyperlink.
"""

def launch_org(org, concept_note_text, tool_dir):
    import datetime
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in f"OAIF_Deep_CEA_{org}")[:60]
    run_dir = os.path.join(tool_dir, 'research_runs', f"{safe_name}_{ts}")
    os.makedirs(os.path.join(run_dir, 'research'), exist_ok=True)

    # Write progress.json
    with open(os.path.join(run_dir, 'progress.json'), 'w') as f:
        json.dump({"phase": 0, "complete": False, "phases_done": [], "key_numbers": {}}, f)

    # Write config.json
    with open(os.path.join(run_dir, 'config.json'), 'w') as f:
        json.dump({"topic": f"OAIF Deep CEA: {org}", "max_iterations": 10, "model": "Opus 4.8"}, f)

    # Write the prompt directly
    prompt = make_prompt(org, concept_note_text, run_dir)
    prompt_path = os.path.join(run_dir, 'prompt.md')
    with open(prompt_path, 'w') as f:
        f.write(prompt)

    # Write the loop script
    loop_script = f"""#!/bin/bash
set -euo pipefail
RUN_DIR="{run_dir}"
MAX_ITER=10
MODEL_FLAG="--model claude-opus-4-8"

for i in $(seq 1 $MAX_ITER); do
  echo "=== Iteration $i / $MAX_ITER ==="
  echo "=== $(date '+%H:%M:%S') ==="
  OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print $MODEL_FLAG --dangerously-skip-permissions 2>&1)
  echo "$OUTPUT"
  if echo "$OUTPUT" | grep -q '<promise>DONE</promise>'; then
    echo "=== Completed at iteration $i ==="
    break
  fi
done

# Upload
if [ -f "$RUN_DIR/synthesis.md" ]; then
  cd "{tool_dir}" && python3 deep_research/upload_to_gdoc.py "$RUN_DIR"
fi

echo "RESEARCH COMPLETE: {org}"
cat "$RUN_DIR/progress.json"
"""
    script_path = os.path.join(run_dir, 'run.sh')
    with open(script_path, 'w') as f:
        f.write(loop_script)
    os.chmod(script_path, 0o755)

    log_path = f"/tmp/deep2_{org.replace(' ', '_').replace('/', '_')}.log"
    p = subprocess.Popen(
        ['bash', script_path],
        stdout=open(log_path, 'w'),
        stderr=subprocess.STDOUT,
        cwd=tool_dir
    )
    return p, run_dir, log_path


if __name__ == '__main__':
    import json as _json

    tool_dir = '/Users/parthahya/tools/research_loop_tool'
    notes = _json.load(open('/tmp/concept_note_texts.json'))

    procs = []
    for org, text in notes.items():
        print(f"Launching: {org}")
        p, run_dir, log = launch_org(org, text, tool_dir)
        procs.append((org, p, run_dir, log))
        time.sleep(2)  # stagger

    print(f"\nLaunched {len(procs)} loops:")
    for org, p, run_dir, log in procs:
        print(f"  {org}: PID {p.pid}, log {log}")
