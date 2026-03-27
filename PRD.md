# AI News Digest — Product Requirements Document

## Overview

An automated pipeline that discovers, reads, summarizes, and emails a daily/weekly AI news digest. Built as a LangGraph multi-agent system in Python, it uses three specialized agents with different models optimized for cost and capability.

## Problem

Keeping up with AI news is time-consuming. There are dozens of sources, most content is noise, and manually curating a digest takes 30–60 minutes. This pipeline automates the entire loop: find what matters, summarize it, deliver it to your inbox.

## Architecture

The system is a single LangGraph graph with three sequential stages. Agent 1 is a real agentic loop (search → evaluate → scrape → decide). Agents 2 and 3 are single-pass nodes — they don't need tool-calling loops.

**Agent 1 — Research Agent**
The only true agent. It has access to two tools (Tavily Search and Firecrawl Scrape) and runs an autonomous loop: it searches for recent AI news across multiple angles (research breakthroughs, product launches, policy, open source), evaluates which results are worth reading, scrapes the full content, and decides when it has enough material (target: 5–10 high-quality articles). Model: Claude Sonnet — needs strong judgment for source selection and deduplication. This is the most expensive step but it runs few LLM calls relative to the content volume.

**Agent 2 — Summarizer**
Receives the raw scraped content from Agent 1. Produces a per-article summary (2–3 sentences each) and a top-level "TLDR" paragraph for the full digest. Model: Gemini 2.0 Flash or Claude Haiku 4.5 — cheap, fast, large context window. The task is straightforward extraction, no reasoning needed.

**Agent 3 — Email Crafter**
Takes the structured summaries and formats them into a clean HTML email with sections, links back to original sources, and a brief editorial intro. Model: Claude Haiku — good enough for templated formatting. After crafting, a deterministic step (no LLM) sends the email via Resend API.

## State Schema

A single `AgentState` TypedDict flows through the whole graph:

- `search_queries: list[str]` — queries the research agent has issued (for dedup)
- `search_results: list[dict]` — raw search hits with url, title, snippet
- `scraped_articles: list[dict]` — full content from Firecrawl: url, title, content, word_count
- `summaries: list[dict]` — per-article summaries: url, title, summary
- `digest_tldr: str` — the top-level summary paragraph
- `email_html: str` — the final formatted email
- `email_sent: bool` — confirmation flag
- `messages: list` — LangGraph message history for the research agent's tool-calling loop

## Tools

**Tavily Search** — integrated via `langchain-community` TavilySearchResults tool. The research agent calls this with different queries ("AI research breakthroughs this week", "new AI product launches", "AI regulation news", etc.). Returns title, url, snippet, and relevance score.

**Firecrawl Scrape** — custom LangChain tool wrapping the Firecrawl Python SDK. Takes a URL, returns clean markdown content. The research agent decides which search results are worth scraping based on snippet quality and source reputation.

## Graph Structure

```
START
  │
  ▼
research_agent ◄──── tool_node (tavily + firecrawl)
  │       ▲               │
  │       └───────────────┘  (loop until enough articles)
  │
  ▼
summarizer_node  (single pass, cheap model)
  │
  ▼
email_crafter_node  (single pass, formats HTML)
  │
  ▼
send_email_node  (no LLM, just Resend API call)
  │
  ▼
END
```

The research agent → tool node loop uses LangGraph's standard conditional edge: if the agent's last message has tool calls, route to `tool_node`; otherwise, route to `summarizer_node`.

## Tech Stack

- **Python 3.11+**
- **langgraph** — orchestration, state management, conditional routing
- **langchain-anthropic** — Claude Sonnet and Haiku
- **langchain-google-genai** — Gemini Flash for the summarizer
- **tavily-python** + langchain integration — web search
- **firecrawl-py** — website scraping
- **resend** — email delivery
- **pydantic** — state validation
- **python-dotenv** — env config

## File Structure

```
ai-digest/
├── src/
│   ├── graph.py              # Main graph definition + build_graph()
│   ├── state.py              # AgentState TypedDict
│   ├── agents/
│   │   ├── researcher.py     # Research agent node + routing logic
│   │   ├── summarizer.py     # Summarizer node
│   │   └── email_crafter.py  # Email crafter node + send function
│   └── tools/
│       ├── search.py         # Tavily tool definition
│       └── scrape.py         # Firecrawl tool definition
├── templates/
│   └── email.html            # Jinja2 email template
├── .env.example              # Required API keys
├── requirements.txt
└── main.py                   # Entry point: build graph, invoke, optionally schedule
```

## Configuration (`.env`)

```
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=
FIRECRAWL_API_KEY=
RESEND_API_KEY=
RECIPIENT_EMAIL=
```

## Cost Estimate (per run)

Assuming ~8 articles scraped, ~40k tokens of raw content:

- Agent 1 (Sonnet, ~5 LLM calls for search/eval loop): ~$0.03–0.05
- Agent 2 (Flash/Haiku, single call with ~40k input): ~$0.01–0.02
- Agent 3 (Haiku, single call): ~$0.001
- Tavily: free tier covers 1,000 searches/month
- Firecrawl: free tier covers 500 scrapes/month
- Resend: free tier covers 100 emails/day

**Total per run: ~$0.05–0.08**. Running daily, that's roughly $1.50–2.50/month.

## Scheduling

For v1, just run `main.py` manually or via a cron job. Later options: GitHub Actions scheduled workflow (free), a simple Railway/Render cron, or a Cloud Function with Cloud Scheduler.

## Success Criteria

- The research agent finds 5–10 relevant, recent articles without hardcoded sources
- No duplicate articles in the digest
- Summaries are accurate and concise (2–3 sentences each)
- Email arrives formatted and readable in Gmail/Outlook
- Total cost stays under $0.10 per run
- End-to-end execution under 2 minutes

## Open Questions

1. **Search scope** — should the research agent have a configurable "topic focus" (e.g., "focus on LLM research this week") or always cast a wide net?
2. **Dedup across runs** — should we persist previously seen URLs to avoid re-sending the same articles? A simple SQLite or JSON file would work.
3. **Error handling** — if Firecrawl fails on a URL (paywall, timeout), the agent should skip and try another source. How many retries before moving on?
4. **Frequency** — daily or weekly? A weekly digest with 10–15 articles might be more useful than a daily one with 3–5.
