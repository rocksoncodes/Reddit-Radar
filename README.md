# Reddit Radar

Reddit Radar is a backend service that helps identify real, recurring problems in niche Reddit communities by automatically ingesting discussions, analyzing sentiment, and validating problem relevance using an LLM.

It is designed to support founders, developers, and researchers who want structured, actionable insights instead of manually scanning Reddit threads.


# Problem
Manually researching niche Reddit communities to discover meaningful problems is time-consuming, inconsistent and difficult to scale.

High-signal insights are often buried across posts and comment threads, making it hard to:
- Identify recurring pain points
- Validate whether an issue represents a real market problem
- Store and prioritize findings for later use


# Solution
Reddit Radar automates this workflow through a backend-first, modular architecture.

The system:
1. Ingests posts and comments from configured subreddits via Reddit’s API
2. Processes and analyzes text using sentiment and filtering pipelines
3. Uses an LLM (Gemini) to validate whether detected issues represent meaningful problems
4. Produces structured outputs that can be stored in external systems (e.g. Notion, database)

The project is designed as a set of composable services and pipelines, making it easy to extend or integrate with other tools.

# Tech Stack
- Python 3.11+
- Reddit API (OAuth)
- Gemini (Google LLM)
- SQLAlchemy (data models)
- Structured logging
- Environment-based configuration
  

# Key Features
- OAuth-based Reddit data ingestion
- Modular agent and pipeline architecture
- LLM-powered problem validation
- Sentiment analysis and text processing helpers
- Structured logging for observability
- Designed for downstream storage (Notion / database)


# Project Structure (High-Level)

- `clients/` – Thin API clients (Reddit, Gemini)
- `engines/` – Runnable entry points (ingestion, curation)
- `services/` – Core business logic and integrations
- `pipelines/` – Data processing and analysis pipelines
- `database/` – SQLAlchemy models and DB setup
- `utils/` – Shared helpers and utilities


# How to Run

### Prerequisites
- Python 3.11+
- Reddit API credentials
- Gemini API key

### 1. Clone the repository

```bash
    git clone https://github.com/[your-username]/Reddit-Radar.git
   ```

### 2. Create a virtual environment and install dependencies

```bash
    python -m venv .venv
    .\.venv\Scripts\activate    # Windows
    pip install -r requirements.txt
```

### 3. Copy and edit environment variables

```bash
   cp .env.example .env
```

The following environment variables are used by the project (add any others required by your integrations):

``` bash
REDDIT_CLIENT_ID       # Reddit API client ID
REDDIT_CLIENT_SECRET   # Reddit API secret
REDDIT_USER_AGENT      # Reddit API user agent string
GEMINI_API_KEY         # Gemini / Google LLM API key
NOTION_API_KEY         # Notion integration key
NOTION_DB_ID           # Notion database id
```

Notes:
```bash
Keep secrets out of version control. Use a secrets manager for production.
```

### 4. Run the ingest agent (example)

```bash
   python engines\ingest_engine.py
```

Depending on the agent/engine you want to run, use the corresponding script under `engines/`.

# What I Learned

- Designing modular backend systems using services and pipelines
- Structuring long-running data ingestion workflows
- Safely integrating third-party APIs with OAuth and environment-based config
- Using LLMs as part of a deterministic backend process
- Building systems intended for extension, not one-off scripts

# Development Status

Branch: MSAA-05-Curator-Agent-Development

- ✅ Project skeleton and core modules
- ✅ Reddit ingestion and basic data collection
- ✅ Gemini integration for evaluation
- 🔄 Ongoing: Problem processing and storage
- 📝 Planned: Notion sync, richer problem-ranking, Email notifications


# Contributing

Contributions and PRs are welcome. Suggested ways to help:
- Implement planned features from the roadmap
- Improve data processing and validation prompts
- Add tests and CI
- Improve documentation and examples

When opening a PR, include tests or a short demo showing the change.

