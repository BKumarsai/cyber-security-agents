# 🛡️ Cyber Security LLM Agents

An AI-powered multi-agent framework for cybersecurity research and red-team exercises.

> ⚠️ **Legal warning:** Use this ONLY on systems you own or have explicit written permission to test.

---

## 📐 Architecture

```
┌─────────────────────────────────────────┐
│           CoordinatorAgent              │  ← orchestrates everything
│  (plans tasks, routes to specialists)   │
└──────┬─────────────┬─────────────┬──────┘
       │             │             │
  ┌────▼────┐  ┌─────▼────┐  ┌────▼────┐
  │Caldera  │  │  Code    │  │  Text   │
  │ Agent   │  │  Agent   │  │  Agent  │
  └────┬────┘  └─────┬────┘  └────┬────┘
       │             │             │
  ┌────▼────────────────────────────▼────┐
  │              Tools                   │
  │  caldera_tools │ code_tools │ web_tools │
  └──────────────────────────────────────┘
```

### Agent types

| Agent | File | Purpose |
|---|---|---|
| **TextAgent** | `agents/text_agents.py` | Summarise findings, write reports, explain techniques |
| **CodeAgent** | `agents/code_agents.py` | Execute shell commands and Python code in an agentic loop |
| **CalderaAgent** | `agents/caldera_agents.py` | Plan and run MITRE Caldera operations |
| **CoordinatorAgent** | `agents/coordinator_agents.py` | Orchestrate the other three agents |

---

## 🚀 Quick Start

### Step 1 — Clone / download the project

Place the project folder anywhere, e.g. `C:\Users\YourName\cyber-security-llm-agents`

### Step 2 — Install Python (if not installed)

Download from https://python.org  (Python 3.11 or 3.12 recommended)

During install, **tick "Add Python to PATH"**.

### Step 3 — Open a terminal in VS Code

1. Open VS Code
2. `File → Open Folder` → select the project folder
3. Press `` Ctrl+` `` to open the Terminal panel

### Step 4 — Create a virtual environment

```bash
python -m venv venv
```

### Step 5 — Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of the terminal prompt.

### Step 6 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 7 — Create your .env file

```bash
# Windows
copy .env_template .env

# Mac / Linux
cp .env_template .env
```

Open `.env` in VS Code and paste your **Anthropic API key**:

```
ANTHROPIC_API_KEY=sk-ant-...your key here...
```

You can get a free API key at https://console.anthropic.com

### Step 8 — Run your first agent!

```bash
# Text agent — no tools, just a smart answer
python run_agents.py --agent text --task "Explain what SQL injection is and how to prevent it"

# Code agent — executes real commands
python run_agents.py --agent code --task "List all running processes and find any suspicious ones"

# Coordinator — full multi-agent run
python run_agents.py --agent coord --task "Perform a web reconnaissance on http://testphp.vulnweb.com and write a report"
```

---

## 📁 Project Structure

```
cyber-security-llm-agents/
├── .env_template          ← copy to .env, add your API key
├── .env                   ← your secrets (never commit this!)
├── requirements.txt       ← Python dependencies
├── run_agents.py          ← main CLI runner
├── run_servers.py         ← starts HTTP + FTP helper servers
│
├── agents/
│   ├── text_agents.py         ← single-shot LLM responses
│   ├── code_agents.py         ← agentic code/shell executor
│   ├── caldera_agents.py      ← MITRE Caldera orchestrator
│   └── coordinator_agents.py  ← meta-orchestrator
│
├── actions/
│   └── agent_actions.py   ← action schema + dispatcher
│
├── tools/
│   ├── caldera_tools.py   ← Caldera REST API wrappers
│   ├── code_tools.py      ← shell / Python / file helpers
│   └── web_tools.py       ← HTTP / recon helpers
│
└── utils/
    ├── constants.py       ← app-wide constants
    ├── logs.py            ← coloured logger
    ├── shared_config.py   ← loads .env → Config object
    ├── web_server.py      ← HTTP file server
    └── ftp_server.py      ← FTP receive server
```

---

## 🔑 API Key

You need an **Anthropic API key**.

1. Go to https://console.anthropic.com
2. Sign up (free)
3. Click "API Keys" → "Create Key"
4. Copy the key and paste it in your `.env` file

The key looks like: `sk-ant-api03-...`

---

## ⚙️ Configuration

All settings are in your `.env` file:

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | **Required.** Your Claude API key |
| `LLM_MODEL` | `claude-opus-4-6` | Which Claude model to use |
| `MAX_ITERATIONS` | `10` | Max steps per agent loop |
| `CALDERA_URL` | `http://localhost:8888` | Caldera server address |
| `CALDERA_API_KEY` | `ADMIN123` | Caldera API key |
| `WEB_SERVER_PORT` | `8080` | HTTP server port |
| `FTP_SERVER_PORT` | `2121` | FTP server port |

---

## 🧪 Using MITRE Caldera (optional)

Caldera is a free red-team automation platform by MITRE.

1. Install: https://caldera.readthedocs.io/en/latest/Installing-Caldera.html
2. Start: `python server.py --insecure`
3. Open browser at http://localhost:8888
4. Default credentials: `admin / admin`
5. Set `CALDERA_URL` and `CALDERA_API_KEY` in `.env`
6. Run: `python run_agents.py --agent caldera --task "Your objective"`

---

## 💡 Example Tasks

```bash
# Explain a vulnerability
python run_agents.py --agent text --task "Explain Log4Shell (CVE-2021-44228)"

# Recon a test site (NEVER use on real targets without permission)
python run_agents.py --agent code --task "Check common admin paths on http://testphp.vulnweb.com"

# Full engagement simulation
python run_agents.py --agent coord --task "Recon http://testphp.vulnweb.com: find forms, extract links, identify server tech, and write a penetration test report"
```
