# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AI News Digest — an automated pipeline that discovers, reads, summarizes, and emails a daily/weekly AI news digest. Built as a LangGraph multi-agent system in Python.

## Architecture

Three-stage LangGraph graph with a shared `AgentState` TypedDict:

1. **Research Agent** (Claude Sonnet) — agentic loop with Tavily Search and Firecrawl Scrape tools. Searches multiple angles, evaluates results, scrapes full content, loops until 5–10 quality articles collected.
2. **Summarizer** (Gemini Flash or Haiku) — single-pass node producing per-article summaries and a TLDR paragraph.
3. **Email Crafter** (Haiku) — single-pass node formatting HTML email, followed by a deterministic Resend API send step.

The research agent uses LangGraph's conditional edge: tool calls → `tool_node` loop; no tool calls → `summarizer_node`.

## Tech Stack

- Python 3.11+
- langgraph, langchain-anthropic, langchain-google-genai
- tavily-python (search), firecrawl-py (scraping)
- resend (email delivery)
- pydantic (state validation), python-dotenv (env config)

## Commands

```bash
# Install dependencies
uv sync

# Run the digest pipeline
uv run python -m main
```

## Required Environment Variables

Copy `.env.example` to `.env` and fill in:
- `OPENAI_API_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`

## Key Design Decisions

- Only Agent 1 (researcher) uses a tool-calling loop; Agents 2 and 3 are single-pass nodes to minimize cost.
- State is a single `AgentState` TypedDict flowing through the entire graph — no separate state per agent.
