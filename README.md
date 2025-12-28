# Reddit-Problem-Discovery-Service

The Reddit-Problem-Discovery-Service is a backend service that helps identify real, recurring problems in niche Reddit communities by automatically ingesting discussions, analyzing sentiment and validating problem relevance using an LLM.

It is designed to support founders, developers, and researchers who want structured, actionable insights instead of manually scanning Reddit threads.


# Problem
Manually researching niche Reddit communities to discover meaningful problems is time-consuming, inconsistent and difficult to scale.

High-signal insights are often buried across posts and comment threads, making it hard to:
- Identify recurring pain points
- Validate whether an issue represents a real market problem
- Store and prioritize findings for later use


# Solution
The Reddit-Problem-Discovery-Service automates this workflow through a backend-first, modular architecture.

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

# Key features
- OAuth-based Reddit ingestion
- Modular services & pipelines
- Sentiment analysis and filtering helpers
- Gemini LLM for problem validation
- Template-driven HTML email output
- Local persistence via SQLAlchemy


# Project Structure (High-Level)

- Input (acquisition)
  - `clients/reddit_client.py`  low-level Reddit API wrapper
  - `services/ingress/`  higher-level ingestion logic & Reddit-specific services
  - `engines/ingress.py`  runnable ingest engine
  

- Process (analysis)
  - `pipelines/`  processing and sentiment pipelines (`sentiment_pipeline.py`, etc.)
  - `services/core/`  core business logic and LLM validation (`core_service.py`, `sentiment_service.py`)
  - `engines/core.py`  orchestrates processing runs
  

- Output (delivery)
  - `services/egress/`  email/Notion/sink logic (`egress_service.py`, `storage_service.py`)
  - `engines/egress.py`  runnable egress engine
  - `database/`  where processed briefs are persisted
  - `emails/` + `utils/templates/` email templates and rendering assets


# Environment variables
Copy `.env.example` to `.env` and fill in the values. The project requires at minimum:

- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT
- GEMINI_API_KEY

Optional / output-related:
- NOTION_API_KEY  (Notion sync is currently under review; set only if you plan to enable)
- NOTION_DB_ID
- EMAIL_ADDRESS
- EMAIL_APP_PASSWORD  (Gmail app password recommended)
- RECIPIENT_ADDRESS

Security note: keep these secrets out of version control and use a secure secrets manager in production.


# How to run locally
1. Create and activate a virtualenv

``` bash
REDDIT_CLIENT_ID       # Reddit API client ID
REDDIT_CLIENT_SECRET   # Reddit API secret
REDDIT_USER_AGENT      # Reddit API user agent string
GEMINI_API_KEY         # Gemini / Google LLM API key
NOTION_API_KEY         # Notion integration key
NOTION_DB_ID           # Notion database id
EMAIL_ADDRESS          # Your email address
EMAIL_APP_PASSWORD     # Your email app password
RECIPIENT_ADDRESS      # Recipient email address
```

1. Copy environment file and edit

```powershell
copy .env.example .env
```

2. Run these engines inorder

```powershell
python engines\ingress.py
python engines\core.py
python engines\egress.py
```


# Notes & current limitations (explicit)
- This project is focused on Reddit; other platforms are not supported by the current clients.
- Notion integration code is present but commented / marked as "under review" in `services/egress/egress_service.py`.
- The email template at `utils/templates/card.html` is required by the egress email renderer; missing templates will raise at runtime.
- SMTP example uses Gmail (smtp.gmail.com:587) and requires an app password for secure authentication.


# Development status
- ✅ Reddit ingestion implemented
- ✅ Basic sentiment and processing pipelines
- ✅ Gemini LLM integration (thin client)
- ⚠️ Notion sync: present but under maintenance/commented
- ✅ Email egress implemented (Gmail example)


# Contributing

Contributions and PRs are welcome. Suggested ways to help:
- Implement planned features from the roadmap
- Improve data processing and validation prompts
- Add tests and CI
- Improve documentation and examples

When opening a PR, include tests or a short demo showing the change.

# Wiki

If the README answers *what*, the wiki explains *how* and *why*.

👉 https://github.com/rocksoncodes/Reddit-Problem-Discovery-Service/wiki
