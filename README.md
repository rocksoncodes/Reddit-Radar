# Reddit Problem Discovery Service (Reddit-only)

This repository implements a backend-first AI agent that discovers recurring problems and sentiment signals in niche Reddit communities. The project is intentionally focused on Reddit as the single input source; other platforms are out of scope for now.

Quick summary
- Input: Reddit posts & comments (via Reddit API)
- Process: Text cleaning, heuristic filtering, sentiment scoring, LLM-based validation (Gemini)
- Output: Structured problem briefs persisted to the local database and optional exporters (email, Notion)

Collect posts and comments exclusively from configured subreddits.

# 1. Why Reddit-only?
Focusing on one platform keeps ingestion, privacy and evaluation requirements simple and makes prompts and data controllers more effective for the conversational structure Reddit provides (posts + nested comments). If you later want other platforms, add an input client and a matching ingress service.

# 2. Problem
Manual discovery of recurring, real-world problems across subreddits is slow and noisy. This service automates discovery, validation, and packaging of those findings so teams can act faster.

# 3. Solution
- Periodic collection of posts and comments from configured subreddits
- Architecture centered around controllers to orchestrate data flow
- LLM-based (Gemini) checks to validate whether a detected issue is a meaningful, recurring problem
- Outputs: curated briefs persisted to the local DB and optionally exported (email / Notion)

# 4. Quick start

### 4.1 Prerequisites
- Python 3.11+ (tested with 3.13)
- A Reddit app (client ID & secret)
- Optional: Gemini (Google LLM) API key
- Recommended: create a virtual environment

### 4.2 Clone and install

```powershell
git clone https://github.com/rocksoncodes/Problem-Discovery-Backend-Service.git
cd Problem-Discovery-Backend-Service
python -m venv .venv
.\.venv\Scripts\activate       
pip install -r requirements.txt
```

Copy environment template:

```cmd
copy .env.example .env
```

### 4.3 Run the Scheduler
The system is designed to run periodically. The main entry point is `agent.py`, which uses APScheduler to run the full controller sequence every 2 weeks.

```cmd
python agent.py
```

You can also run controllers manually for testing:
```cmd
python main.py
```

# 5. Project organization
This codebase is organized into Input, Process, and Output layers.

- **Main Entry Point**
  - `agent.py`: The background scheduler that orchestrates all jobs.
  - `main.py`: Manual entry point to run the full sequence.

- **Controllers (Orchestration)**
  - `controllers/ingress_controller.py`: Orchestrates the ingestion flow.
  - `controllers/sentiment_controller.py`: Processes sentiment for collected data.
  - `controllers/core_controller.py`: Orchestrates the agentic reasoning flow.
  - `controllers/egress_controller.py`: Orchestrates the export flow.

- **Input & Scaping**
  - `clients/reddit_client.py`: Reddit API adapter.
  - `services/ingress_service.py`: Reddit-specific data collection logic.
  - `handlers/reddit_handler.py`: High-level handlers for Reddit data.

- **Process (Business Logic)**
  - `services/core_service.py`: Business logic for the Curator Agent (Gemini).
  - `services/sentiment_service.py`: Sentiment analysis logic.

- **Output (Egress / Storage)**
  - `services/egress_service.py`: Exporters (Email, Notion).
  - `services/storage_service.py`: Database interaction logic.
  - `database/`: SQLAlchemy models and persistence.


- **Utilities & Config**
  - `config/settings.py`: System settings and environment variable mapping.
  - `utils/`: Shared helpers (logger, templates).

# 6. Environment variables
The following environment variables are used by the project (add any others required by your integrations).

```cmd
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT
GEMINI_API_KEY         
NOTION_API_KEY         # optional (Notion sync)
NOTION_DB_ID           # optional
EMAIL_ADDRESS
EMAIL_APP_PASSWORD
RECIPIENT_ADDRESS
```

Keep secrets out of version control. Use a secrets manager for production.


# 7. How the system thinks (short)
1. Input: collect posts + comments from selected subreddits via Reddit OAuth
2. Process: normalize text, filter noise, run sentiment & heuristic checks, produce candidates
3. Validate: run structured LLM prompts (Gemini) + deterministic rules to confirm if a candidate is a real problem
4. Output: persist validated briefs and export to configured sinks


# 8. Development status
- Branch: MSAA-05-Curator-Agent-Development (current)
- ✅ Project skeleton and core modules
- ✅ Reddit ingestion and basic data collection
- ✅ Gemini integration for evaluation
- ✅ Notion sync and email notifications

---

# 9. Contributing
Contributions and PRs are welcome. Suggested ways to help:
- Improve signal quality and filtering
- Improve processing and validation prompts
- Add tests and examples for new features

When opening a PR, include tests or a short demo showing the change.

# 10. Notes & limitations
- This is backend infrastructure, not a UI
- Focused exclusively on Reddit as a source
- LLM costs may apply depending on usage


# 11. Project Wiki
See `project wiki/Home.md` for extended rationale, architecture notes and running notes.
