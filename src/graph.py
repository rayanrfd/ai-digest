import logging
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, ToolMessage
from src.state import AgentState
from src.agents.researcher import researcher_agent
from src.agents.summarizer import summarizer_node
from src.agents.email_crafter import email_crafter_node, send_email_node

log = logging.getLogger("RESEARCH")


def researcher_node(state: AgentState) -> AgentState:
    log.info("Starting research agent...")
    result = researcher_agent.invoke({"messages": state.get("messages", [])})
    messages = result["messages"]

    # Pass 1: collect search queries and map tool_call_id -> url for scrape calls
    search_queries = []
    scrape_calls: dict[str, str] = {}  # tool_call_id -> url

    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["name"] == "search_web":
                    search_queries.append(tc["args"].get("query", ""))
                elif tc["name"] == "scrape_url":
                    scrape_calls[tc["id"]] = tc["args"].get("url", "")

    # Pass 2: match ToolMessages back to their scrape call to build scraped_articles
    scraped_articles = []
    for msg in messages:
        if isinstance(msg, ToolMessage) and msg.tool_call_id in scrape_calls:
            url = scrape_calls[msg.tool_call_id]
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            # Use first markdown heading as title, fall back to url
            title = next(
                (line[2:].strip() for line in content.splitlines() if line.startswith("# ")),
                url,
            )
            scraped_articles.append({
                "url": url,
                "title": title,
                "content": content,
                "word_count": len(content.split()),
            })

    log.info("Research complete: %d articles scraped, %d search queries issued",
             len(scraped_articles), len(search_queries))
    for art in scraped_articles:
        log.info("  - %s (%d words)", art["title"][:60], art["word_count"])

    return {
        "messages": messages,
        "search_queries": search_queries,
        "scraped_articles": scraped_articles,
    }


def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("researcher", researcher_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("email_crafter", email_crafter_node)
    builder.add_node("send_email", send_email_node)

    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "summarizer")
    builder.add_edge("summarizer", "email_crafter")
    builder.add_edge("email_crafter", "send_email")
    builder.add_edge("send_email", END)

    return builder.compile()
