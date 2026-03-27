"""Test the email crafter node with fake summaries (no API calls except LLM)."""
from dotenv import load_dotenv
load_dotenv()

import sys
from src.agents.email_crafter import email_crafter_node, send_email_node

FAKE_STATE = {
    "search_queries": [],
    "search_results": [],
    "scraped_articles": [],
    "summaries": [
        {"url": "https://example.com/1", "title": "GPT-5 Released", "summary": "OpenAI released GPT-5 with major improvements in reasoning and multimodal capabilities."},
        {"url": "https://example.com/2", "title": "EU AI Act Kicks In", "summary": "The EU begins enforcing the AI Act, requiring risk classification for all AI systems."},
    ],
    "digest_tldr": "This week saw a major model release from OpenAI and the start of EU AI regulation enforcement.",
    "email_html": "",
    "email_sent": False,
    "messages": [],
}


def run():
    print("Running email crafter...\n")
    result = email_crafter_node(FAKE_STATE)
    html = result["email_html"]

    print("Generated HTML (first 1000 chars):")
    print(html[:1000])
    print(f"\n... ({len(html)} chars total)")

    if "--send" in sys.argv:
        print("\nSending email...")
        state = {**FAKE_STATE, "email_html": html}
        send_result = send_email_node(state)
        print(f"Email sent: {send_result['email_sent']}")
    else:
        print("\nSkipping send. Pass --send to actually send the email.")


if __name__ == "__main__":
    run()
