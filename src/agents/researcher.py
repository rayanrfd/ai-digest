from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from src.tools.search import search_web
from src.tools.scrape import scrape_url
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-5.2",
)

SYSTEM_PROMPT = """You are an AI news researcher. Your job is to find 5-10 high-quality,
recent AI news articles worth reading.

Use the search tool to find articles on multiple angles:
- AI research breakthroughs
- New AI product launches
- AI regulation and policy
- Open source AI releases

Use the scrape tool to get full content for articles that look promising based on their snippet.
Avoid duplicates. Prioritize articles from the last 7 days. Stop when you have 5-10 solid articles."""

tools = [search_web, scrape_url]

researcher_agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)
