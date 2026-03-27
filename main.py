import logging
from dotenv import load_dotenv
from src.graph import build_graph

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(name)-13s] %(message)s",
)
# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

log = logging.getLogger("MAIN")

def main():
    log.info("Starting AI Digest pipeline...")
    graph = build_graph()
    result = graph.invoke({
        "search_queries": [],
        "search_results": [],
        "scraped_articles": [],
        "summaries": [],
        "digest_tldr": "",
        "email_html": "",
        "email_sent": False,
        "messages": [],
    })
    log.info("Pipeline complete. Email sent: %s", result["email_sent"])


if __name__ == "__main__":
    main()
