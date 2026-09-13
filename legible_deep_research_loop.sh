#!/bin/bash
# Founders Pledge Style Research Loop
# Usage: ./research_loop_fp.sh "topic" [max_iterations]
#
# Like research_loop.sh but the synthesis is structured as a Founders Pledge
# cause area report: readable prose, clear verdicts, FP-style section headings,
# accessible to non-technical readers while remaining rigorous.
#
# Examples:
#   ./research_loop_fp.sh "Isothermal PCR diagnostics for LMICs"
#   ./research_loop_fp.sh "Lead exposure elimination in South Asia" 12

set -euo pipefail

TOPIC="$1"
MAX_ITER="${2:-15}"

# Ask which model to use
echo ""
echo "Which model for this run?"
echo "  1) Opus 4.8  (~\$3-5/run, highest quality)"
echo "  2) Sonnet 4.5 (~\$0.70/run, fast and cheap)"
read -rp "Choice [1/2]: " model_choice
if [[ "$model_choice" == "2" ]]; then
  MODEL_FLAG="--model claude-sonnet-4-5-20250929"
  MODEL_NAME="Sonnet 4.5"
else
  MODEL_FLAG="--model claude-opus-4-8"
  MODEL_NAME="Opus 4.8"
fi

# Create run directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SAFE_NAME=$(echo "$TOPIC" | tr ' ' '_' | tr -cd '[:alnum:]_' | head -c 50)
RUN_DIR="research_runs/${SAFE_NAME}_${TIMESTAMP}"
mkdir -p "$RUN_DIR/research"

# Create config.json for upload script
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "$RUN_DIR/config.json" << EOF
{
  "topic": $(printf '%s' "$TOPIC" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))"),
  "max_iterations": $MAX_ITER,
  "model": "$MODEL_NAME",
  "started_at": "$START_TIME"
}
EOF

echo ""
echo "=== AI-Generated Research Loop ==="
echo "=== Topic: $TOPIC ==="
echo "=== Model: $MODEL_NAME ==="
echo "=== Run directory: $RUN_DIR ==="
echo "=== Max iterations: $MAX_ITER ==="

# Initialize progress.json
cat > "$RUN_DIR/progress.json" << 'EOF'
{
  "current_phase": "research",
  "total_iterations": 0,
  "complete": false
}
EOF

# ── Step 1: Generate a custom research prompt ──
echo ""
echo "=== Generating custom research prompt... ==="

# Build meta-prompt via Python to avoid shell quoting issues
TMPPY=$(mktemp /tmp/gen_prompt_XXXXXX.py)
cat > "$TMPPY" << 'PYEOF'
import sys

topic = sys.argv[1]
run_dir = sys.argv[2]
max_iter = sys.argv[3]
meta_prompt = f'''You are a research prompt engineer. Write a self-contained iterative research prompt for an AI agent that will research the following topic across multiple iterations.

**Topic**: {topic}

**Run directory**: {run_dir}

The prompt you write will be fed to Claude repeatedly in a loop (up to {max_iter} iterations). Each iteration is a fresh context -- the agent has NO memory between iterations. The ONLY way to persist state is through files in the run directory.

## Requirements for the prompt you generate

1. **Progress tracking**: The prompt must instruct the agent to read \`{run_dir}/progress.json\` at the start of every iteration to determine what phase it is in and what work has been done. It must update progress.json after each iteration.

2. **Phased research**: Design 4-8 research phases appropriate for this specific topic. Each phase should build on prior phases by reading files written in earlier iterations. Example phases might include: landscape survey, data gathering, quantitative analysis, evidence review, synthesis -- but tailor them to what makes sense for the topic.

3. **File output**: Each phase writes its findings to files in \`{run_dir}/research/\` (e.g., \`landscape.md\`, \`data.md\`, \`analysis.md\`). The agent must READ prior phase files before starting a new phase.

4. **Web search**: The prompt must instruct the agent to use web search heavily for real data, statistics, academic papers, and current information. Before each search, check \`{run_dir}/research/search_log.md\` to avoid repeating queries. After each search, append a one-liner: \`- [query] -> [key finding]\`.

5. **Quantitative rigor**: Where applicable, instruct the agent to use Python/bash for calculations, build Fermi estimates with explicit assumptions, and cite sources.

6. **Citation standard — hyperlinks required**: Instruct the agent that every factual claim, statistic, and data point MUST include an inline hyperlink to its source. Format: \`[Author/Source YEAR](URL)\`. Use the actual URL from web search. Prefer DOI links for papers (\`https://doi.org/...\`). For datasets (GBD, WHO, World Bank), link the specific data/report page — not the homepage. Never write a bare URL, a parenthetical like "(WHO)" without a link, or an author-year citation without a URL. If a source is paywalled or unlinkable, write \`[Author YEAR — verify manually](https://pubmed.ncbi.nlm.nih.gov/?term=...)\`. This applies to ALL research files and the synthesis — not just a references section.

6. **Synthesis**: The final phase must produce \`{run_dir}/synthesis.md\` structured EXACTLY as a Founders Pledge cause area report. This is the most important requirement. The synthesis must be written in clear, accessible prose — not bullet-point summaries — and follow this structure precisely:

   **FOUNDERS PLEDGE REPORT STRUCTURE:**

   - **Executive Summary** (1 page max): A plain-language verdict. Should answer: Is this a strong cause area? Why or why not? What are the 2-3 most important facts? What do we recommend? Written for a non-expert philanthropist.

   - **Introduction**: What is the problem? Why does it matter? Hook the reader with the human stakes.

   - **Scale of the Problem**: Quantified burden — deaths, DALYs, people affected, economic cost. Cite everything. Use GBD/WHO/academic sources. Include a summary table where helpful.

   - **Neglectedness**: Is this cause underfunded relative to its scale? Who is already working on it and how much are they spending? Where are the gaps?

   - **Tractability**: Can we actually make progress? What interventions exist? What is the evidence base? What are the key uncertainties?

   - **Intervention Landscape**: For each promising intervention — what is it, what does it cost, what is the evidence, what are the limitations?

   - **Cost-Effectiveness**: Quantitative estimates with explicit assumptions. Compare to GiveWell benchmarks (~$50-100/DALY for top charities). Use ranges, not false precision. Show your work.

   - **Our Recommendation**: Clear, direct funding recommendation. Which organizations or interventions to fund? How much? In what sequence? What conditions would change the recommendation?

   - **What We Don't Know**: Honest about key uncertainties, data gaps, and what would change the verdict.

   - **Conclusion**: Restate the verdict in plain language.

   - **References**: Full citation list with URLs.

   **STYLE REQUIREMENTS:**
   - Write in flowing prose paragraphs, not bullet points (except in tables and lists where appropriate)
   - Active voice, plain English — a smart non-expert should understand every sentence
   - No jargon without explanation
   - Every factual claim hyperlink-cited inline: \`[Author/Source YEAR](URL)\`
   - Confident verdicts — don't hedge everything, take a position
   - Length: 600-1000 lines — thorough but not padded
   - Tone: rigorous but readable, like a good longform journalism piece backed by academic sources

7. **Completion signal**: When the synthesis is written and the agent is satisfied with quality, it must output exactly \`<promise>DONE</promise>\` (this text, literally). This signals the loop to stop.

8. **Iteration budget**: Design phases so the research completes in roughly 8-12 iterations. Each phase should take 1-3 iterations.

## Format

Output ONLY the research prompt -- no preamble, no explanation. The prompt should be ready to feed directly to Claude. Write it in markdown with clear headers and instructions.
'''

with open(f'{run_dir}/meta_prompt.md', 'w') as f:
    f.write(meta_prompt)
PYEOF
python3 "$TMPPY" "$TOPIC" "$RUN_DIR" "$MAX_ITER"
rm -f "$TMPPY"

cat "$RUN_DIR/meta_prompt.md" | env -u CLAUDECODE claude --print $MODEL_FLAG --dangerously-skip-permissions > "$RUN_DIR/prompt.md" 2>&1

if [ ! -s "$RUN_DIR/prompt.md" ]; then
  echo "ERROR: Failed to generate prompt. Check Claude CLI."
  exit 1
fi

PROMPT_LINES=$(wc -l < "$RUN_DIR/prompt.md")
echo "=== Generated prompt: $PROMPT_LINES lines ==="

# ── Step 2: Ralph loop with generated prompt ──
echo ""
echo "=== Starting research loop ==="

for i in $(seq 1 "$MAX_ITER"); do
  echo ""
  echo "=== Iteration $i / $MAX_ITER ==="
  echo "=== $(date '+%H:%M:%S') ==="

  OUTPUT=$(cat "$RUN_DIR/prompt.md" | env -u CLAUDECODE claude --print $MODEL_FLAG --dangerously-skip-permissions 2>&1)
  echo "$OUTPUT"

  # Check for completion
  if echo "$OUTPUT" | grep -q '<promise>DONE</promise>'; then
    echo ""
    echo "=== Completed at iteration $i ==="
    break
  fi
done

# Update config.json with end time and iterations used
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    c = json.load(f)
c['ended_at'] = sys.argv[2]
c['iterations_used'] = int(sys.argv[3])
with open(sys.argv[1], 'w') as f:
    json.dump(c, f, indent=2)
" "$RUN_DIR/config.json" "$END_TIME" "$i"

# ── Step 3: Upload to Google Doc ──
SYNTHESIS_PATH=""
if [ -f "$RUN_DIR/synthesis.md" ]; then
  SYNTHESIS_PATH="$RUN_DIR/synthesis.md"
elif [ -f "$RUN_DIR/research/synthesis.md" ]; then
  # Agent sometimes writes synthesis into research/ subfolder — move it up
  cp "$RUN_DIR/research/synthesis.md" "$RUN_DIR/synthesis.md"
  SYNTHESIS_PATH="$RUN_DIR/synthesis.md"
fi

if [ -n "$SYNTHESIS_PATH" ]; then
  echo ""
  echo "=== Uploading to Google Doc ==="
  python3 deep_research/upload_to_gdoc.py "$RUN_DIR"
else
  echo ""
  echo "WARNING: No synthesis.md found in $RUN_DIR -- skipping upload."
  echo "Research files are in $RUN_DIR/research/"
fi

# Write structured results file
RESULTS="$RUN_DIR/RESULTS.txt"
{
  echo "=== RESEARCH COMPLETE ==="
  echo "Topic: $TOPIC"
  echo "Iterations: $i / $MAX_ITER"
  echo ""
  if [ -f "$RUN_DIR/doc_url.txt" ]; then
    echo "Summary Doc: $(cat "$RUN_DIR/doc_url.txt")"
  fi
  if [ -f "$RUN_DIR/full_doc_url.txt" ]; then
    echo "Full Doc: $(cat "$RUN_DIR/full_doc_url.txt")"
  fi
} > "$RESULTS"
echo ""
cat "$RESULTS"
