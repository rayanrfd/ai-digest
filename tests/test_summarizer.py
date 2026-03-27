"""Test the summarizer node with fake articles (no API calls except LLM)."""
from dotenv import load_dotenv
load_dotenv()

from src.agents.summarizer import summarizer_node

FAKE_ARTICLES = [
    {
        "url": "https://example.com/article-1",
        "title": "OpenAI Releases GPT-5",
        "content": "OpenAI has released GPT-5, their most capable model yet. It features improved reasoning, multimodal understanding, and a 1M token context window. Early benchmarks show significant improvements over GPT-4o across coding, math, and creative tasks.",
        "word_count": 42,
    },
    {
        "url": "https://example.com/article-2",
        "title": "EU AI Act Enforcement Begins",
        "content": "The European Union has begun enforcing the AI Act, requiring companies to classify their AI systems by risk level. High-risk systems like hiring tools and credit scoring must undergo conformity assessments. Fines of up to 35 million euros apply for violations.",
        "word_count": 45,
    },
]


def run():
    print("Running summarizer with fake articles...\n")
    fake_state = {
        "search_queries": [],
        "search_results": [],
        "scraped_articles": FAKE_ARTICLES,
        "summaries": [],
        "digest_tldr": "",
        "email_html": "",
        "email_sent": False,
        "messages": [],
    }
    result = summarizer_node(fake_state)

    print("TLDR:")
    print(f"  {result['digest_tldr']}\n")

    print("Summaries:")
    for s in result["summaries"]:
        print(f"\n  {s['title']}")
        print(f"  {s['summary']}")


if __name__ == "__main__":
    run()
