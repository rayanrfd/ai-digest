"""Test the researcher agent in isolation.
Runs a real search + scrape cycle and prints extracted articles.
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import AIMessage, ToolMessage
from src.agents.researcher import researcher_agent


def run():
    print("Starting researcher agent...\n")
    result = researcher_agent.invoke({"messages": []})
    messages = result["messages"]

    # Extract scraped articles (same logic as graph.py)
    scrape_calls: dict[str, str] = {}
    search_queries = []

    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["name"] == "search_web":
                    search_queries.append(tc["args"].get("query", ""))
                elif tc["name"] == "scrape_url":
                    scrape_calls[tc["id"]] = tc["args"].get("url", "")

    scraped_articles = []
    for msg in messages:
        if isinstance(msg, ToolMessage) and msg.tool_call_id in scrape_calls:
            url = scrape_calls[msg.tool_call_id]
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            title = next(
                (line[2:].strip() for line in content.splitlines() if line.startswith("# ")),
                url,
            )
            scraped_articles.append({
                "url": url,
                "title": title,
                "content": content[:500] + "...",  # truncate for display
                "word_count": len(content.split()),
            })

    print(f"Search queries issued: {len(search_queries)}")
    for q in search_queries:
        print(f"  - {q}")

    print(f"\nScraped articles: {len(scraped_articles)}")
    for art in scraped_articles:
        print(f"\n  Title: {art['title']}")
        print(f"  URL:   {art['url']}")
        print(f"  Words: {art['word_count']}")

    if not scraped_articles:
        print("\nWARNING: No articles scraped. Check tool call names in messages:")
        for i, msg in enumerate(messages):
            print(f"  [{i}] {type(msg).__name__}: {str(msg)[:200]}")


if __name__ == "__main__":
    run()
