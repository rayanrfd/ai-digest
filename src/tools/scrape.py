import logging
from langchain_core.tools import tool
from firecrawl import Firecrawl
import os
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("SCRAPE")

@tool
def scrape_url(url: str) -> str:
    """Scrape the full content of a webpage and return clean markdown."""
    log.info("Scraping %s...", url)
    app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    try:
        result = app.scrape(url, formats=["markdown"])
        word_count = len(result.markdown.split())
        log.info("OK (%d words)", word_count)
        return result.markdown
    except Exception as e:
        log.warning("FAILED: %s", e)
        return f"SCRAPE_FAILED: Could not scrape {url} — {e}. Try a different source."
