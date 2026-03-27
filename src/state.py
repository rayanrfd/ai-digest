from typing import TypedDict


class AgentState(TypedDict):
    search_queries: list[str]          # queries issued by the research agent (for dedup)
    search_results: list[dict]         # raw search hits: url, title, snippet
    scraped_articles: list[dict]       # full content: url, title, content, word_count
    summaries: list[dict]              # per-article: url, title, summary
    digest_tldr: str                   # top-level summary paragraph
    email_html: str                    # final formatted email
    email_sent: bool                   # confirmation flag
    messages: list                     # LangGraph message history for the research agent loop
