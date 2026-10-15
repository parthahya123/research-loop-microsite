# Deep Research & Research Loop — Setup Guide

Two tools for running iterative AI research loops using Claude. Each tool feeds the same prompt to Claude repeatedly; Claude sees its own prior work in files and builds incrementally toward a comprehensive research document, which is then uploaded to Google Docs.

**Deep Research** (`ralph.sh`) — Uses a fixed, battle-tested prompt template designed for DALY/health intervention analysis. Has focus modes (multi-intervention, single, develop).

**Research Loop** (`research_loop.sh`) — Works for ANY topic. Claude first generates a custom research prompt tailored to your topic, then runs the iterative loop with that prompt.

---

## Prerequisites (Starting from Scratch)

### 1. Install Homebrew (macOS only)

Open Terminal and paste:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the instructions it prints (you may need to add it to your PATH).

### 2. Install Python 3

```bash
brew install python
```

Verify: `python3 --version` (should show 3.11+)

### 3. Install Claude Code CLI

**Important: Claude Code is a CLI (command-line) tool. It does NOT run inside the Claude Desktop app.** Your friend needs the CLI specifically.

```bash
npm install -g @anthropic-ai/claude-code
```

If you don't have npm/Node.js:
```bash
brew install node
npm install -g @anthropic-ai/claude-code
```

After installing, authenticate:
```bash
claude
```

This opens a browser window to log in with your Anthropic account. You need an active Claude Pro or Team subscription, OR an Anthropic API key.

Verify it works:
```bash
echo "Say hello" | claude --print
```

You should see Claude's response printed to your terminal.

### 4. Install Python dependencies

```bash
pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv openai httplib2
```

### 5. Set up Google Cloud credentials (for Google Docs upload)

The tools upload research results to Google Docs. If you want this feature:

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable these APIs:
   - Google Docs API
   - Google Drive API
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Name: anything (e.g. "Research Tool")
6. Download the JSON file and save it as `credentials.json` in the tool's root directory

**First-time auth** — the first time you run the tool, it will open a browser window asking you to authorize. This creates `token.json` automatically. After that, it works headlessly.

If you DON'T want Google Docs upload, the research loop still works — it just saves files locally instead of uploading.

---

## Tool 1: Deep Research (`deep_research_tool/`)

### What it does

Runs a structured research loop on DALY/health interventions with these phases:
- Scale analysis (Fermi estimates)
- Evidence gathering
- Cost analysis
- Timeline & feasibility
- Cross-checking
- Cost decline curves
- Red-teaming
- Synthesis

### Directory structure

```
deep_research_tool/
├── deep_research/
│   ├── ralph.sh              # Main script
│   ├── PROMPT.md             # Research prompt template (628 lines)
│   ├── upload_to_gdoc.py     # Google Docs uploader
│   ├── accumulate_to_sheet.py # Master spreadsheet accumulator
│   ├── split_by_intervention.py # Per-intervention doc splitter
│   ├── master_sheet_id.txt   # Google Sheet ID (you'll update this)
│   └── runs/                 # Output goes here
├── .env.example              # Copy to .env and add keys
└── credentials.json          # Your Google OAuth credentials (you provide)
```

### Setup

```bash
cd deep_research_tool

# Set up environment
cp .env.example .env
# Edit .env with your API keys (nano .env or open in editor)

# Place your credentials.json in this directory (see step 5 above)

# Make the script executable
chmod +x deep_research/ralph.sh
```

### Running it

**Must run from the `deep_research_tool/` directory** (the script uses relative paths):

```bash
cd deep_research_tool
bash deep_research/ralph.sh "Indoor air quality filtration in schools"
```

It will ask you:
1. Which model (Opus = better but ~$3-5/run, Sonnet = cheaper ~$0.70/run)
2. Focus mode:
   - **Multi** — surveys 3-4 approaches, compares them
   - **Single** — picks the best one, goes deep
   - **Develop** — you already know the intervention, explore variations within it

Then it runs 15-17 iterations (configurable as second argument):
```bash
bash deep_research/ralph.sh "Iodine fortification in sub-Saharan Africa" 20
```

Output lands in `deep_research/runs/<topic>_<timestamp>/`.

### Optional: Shell alias

Add to your `~/.zshrc` or `~/.bashrc`:
```bash
alias deepresearch='cd ~/deep_research_tool && bash deep_research/ralph.sh'
```

Then: `deepresearch "Your topic here"`

---

## Tool 2: Research Loop (`research_loop_tool/`)

### What it does

Works for **any research topic** (not just health/DALYs). It:
1. Asks Claude to design a custom research prompt for your topic
2. Runs the iterative loop with that AI-generated prompt
3. Uploads the final synthesis to Google Docs

### Directory structure

```
research_loop_tool/
├── research_loop.sh          # Main script
├── deep_research/
│   └── upload_to_gdoc.py     # Google Docs uploader
├── research_runs/            # Output goes here
├── .env.example              # Copy to .env and add keys
└── credentials.json          # Your Google OAuth credentials (you provide)
```

### Setup

```bash
cd research_loop_tool

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Place your credentials.json in this directory

# Make executable
chmod +x research_loop.sh
```

### Running it

**Must run from the `research_loop_tool/` directory:**

```bash
cd research_loop_tool
bash research_loop.sh "Effect of sleep quality on cognitive decline"
```

With custom iteration count:
```bash
bash research_loop.sh "Universal basic income pilot programs" 20
```

### Optional: Shell alias

```bash
alias loop='cd ~/research_loop_tool && bash research_loop.sh'
```

Then: `loop "Your topic here" 20`

---

## FAQ

### Does this work with the Claude Desktop app?

**No.** These tools require **Claude Code** (the CLI tool), not the Claude Desktop app. Claude Code runs in your terminal and provides the `claude --print` command that the scripts use to pipe prompts to Claude. Install it with `npm install -g @anthropic-ai/claude-code`.

### How much does it cost per run?

- **Opus 4.6**: ~$3-5 per run (highest quality)
- **Sonnet 4.5**: ~$0.50-0.70 per run (good enough for most topics)

This uses your Anthropic account credits (included with Claude Pro subscription, or billed via API key).

### Can I skip the Google Docs upload?

Yes. If `credentials.json` / `token.json` are missing, the upload step will fail but your research is still saved locally in the run directory. You can read `synthesis.md` directly.

### Where do I find my research output?

- Deep Research: `deep_research_tool/deep_research/runs/<topic>_<timestamp>/`
- Research Loop: `research_loop_tool/research_runs/<topic>_<timestamp>/`

Key files in each run:
- `synthesis.md` — the final research document
- `research/` — intermediate phase files
- `config.json` — run metadata
- `prompt.md` — the prompt that was used

### It says "claude: command not found"

Claude Code isn't installed or isn't on your PATH. Run:
```bash
npm install -g @anthropic-ai/claude-code
```

If npm isn't found, install Node.js first: `brew install node`

### Token refresh / Google auth expired

Delete `token.json` and run again. It will re-open the browser auth flow.

### Can I edit the research prompt?

- **Deep Research**: Edit `deep_research/PROMPT.md` to change what Claude researches and how.
- **Research Loop**: The prompt is auto-generated each time, but you can edit `<run_dir>/prompt.md` mid-run if needed (stop the script, edit, restart with the same run dir).

### What is the `master_sheet_id.txt`?

Used by Deep Research's `accumulate_to_sheet.py` to add intervention summaries to a shared Google Sheet. Replace the ID in that file with your own Google Sheet ID, or remove the accumulate step from `ralph.sh` if you don't need it.
