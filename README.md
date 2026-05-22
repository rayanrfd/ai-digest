# AI News Digest

A LangGraph multi-agent pipeline that researches, reads, summarizes and emails a daily AI news digest. Built as a sequence of three specialized agents sharing a single `AgentState`.

## Architecture

```text
START → researcher → summarizer → email_crafter → send_email → END
```

- **Researcher** ([src/agents/researcher.py](src/agents/researcher.py)) — a ReAct agent (`create_react_agent`) that loops over two tools:
  - `search_web` ([src/tools/search.py](src/tools/search.py)) — Tavily Search across multiple angles (research, product launches, regulation, open-source).
  - `scrape_url` ([src/tools/scrape.py](src/tools/scrape.py)) — Firecrawl to pull full markdown content for promising hits.
  The agent stops once it has collected 5–10 quality articles from the last 7 days.
- **Summarizer** ([src/agents/summarizer.py](src/agents/summarizer.py)) — single LLM call with Pydantic structured output (`DigestOutput`) producing one short summary per article plus an overall TLDR paragraph.
- **Email crafter** ([src/agents/email_crafter.py](src/agents/email_crafter.py)) — single LLM call rendering the summaries into clean HTML, followed by a deterministic `send_email_node` that ships it via `smtplib` over STARTTLS.

State flows through the graph as a single `AgentState` TypedDict ([src/state.py](src/state.py)) — no per-agent state.

## Stack

- Python 3.11+
- LangGraph + LangChain (OpenAI provider)
- Tavily (search) and Firecrawl (scrape)
- Pydantic for structured output
- `smtplib` for delivery
- `uv` for dependency management

## Installation

```bash
git clone https://github.com/rayanrfd/ai-digest.git
cd ai-digest
uv sync
cp .env.example .env
# then fill in the values in .env
```

## Environment variables

All read from `.env` at startup. None have defaults except `SMTP_PORT`.

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | LLM calls for all three agents |
| `TAVILY_API_KEY` | Web search tool used by the researcher |
| `FIRECRAWL_API_KEY` | Article scraping tool used by the researcher |
| `SMTP_HOST` | SMTP server hostname (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port — defaults to `587` (STARTTLS) |
| `SMTP_USER` | SMTP username for authentication |
| `SMTP_PASSWORD` | SMTP password or app-specific password |
| `SMTP_FROM` | `From:` address on the outgoing digest |
| `RECIPIENT_EMAIL` | Inbox that receives the digest |

## Usage

```bash
uv run python -m main
```

The pipeline runs end-to-end: searches the web, scrapes the best hits, generates summaries and a TLDR, builds the HTML email, and sends it to `RECIPIENT_EMAIL`. Progress is logged at INFO level for each stage.

To schedule a daily digest, wire `uv run python -m main` into a cron job, GitHub Actions schedule, or any other scheduler.

## Project layout

```text
.
├── main.py                       # entry point — loads env, builds the graph, invokes it
├── src/
│   ├── state.py                  # AgentState TypedDict
│   ├── graph.py                  # LangGraph wiring (nodes + edges)
│   ├── agents/
│   │   ├── researcher.py         # ReAct researcher
│   │   ├── summarizer.py         # structured-output summarizer
│   │   └── email_crafter.py      # HTML formatter + SMTP send node
│   └── tools/
│       ├── search.py             # Tavily wrapper
│       └── scrape.py             # Firecrawl wrapper
├── tests/                        # standalone tests for each stage
├── pyproject.toml
└── .env.example
```

## Tests

Standalone scripts under [tests/](tests/) exercise each stage in isolation (`test_research.py`, `test_summarizer.py`, `test_email.py`). Run any of them with `uv run python -m tests.test_<stage>`.
