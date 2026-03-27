import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from src.state import AgentState
import json
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-5.4-mini",
)

SYSTEM_PROMPT = """You are a concise news summarizer. Given a list of scraped articles, produce:
1. A 2-3 sentence summary for each article
2. A single TLDR paragraph (3-4 sentences) summarizing the overall digest"""


class ArticleSummary(BaseModel):
    url: str
    title: str
    summary: str


class DigestOutput(BaseModel):
    summaries: list[ArticleSummary]
    digest_tldr: str


structured_model = model.with_structured_output(DigestOutput)


log = logging.getLogger("SUMMARIZE")


def summarizer_node(state: AgentState) -> AgentState:
    articles = state["scraped_articles"]
    log.info("Summarizing %d articles...", len(articles))
    result = structured_model.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(articles)),
    ])
    log.info("Done — %d summaries + TLDR generated", len(result.summaries))
    return {
        "summaries": [s.model_dump() for s in result.summaries],
        "digest_tldr": result.digest_tldr,
    }
