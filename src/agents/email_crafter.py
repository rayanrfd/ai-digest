import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.state import AgentState
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-5.4-mini",
)

SYSTEM_PROMPT = """You are an email formatter. Given summaries and a TLDR, produce a clean HTML email.
Structure:
- A brief editorial intro paragraph
- A section per article with its title (linked to source), summary, and a "Read more" link
- Clean, readable HTML — no heavy styling, works in Gmail and Outlook

Return only the HTML string, nothing else."""


log = logging.getLogger("EMAIL")


def email_crafter_node(state: AgentState) -> AgentState:
    log.info("Crafting HTML email...")
    payload = json.dumps({
        "tldr": state["digest_tldr"],
        "summaries": state["summaries"],
    })
    response = model.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=payload),
    ])
    log.info("HTML generated (%d chars)", len(response.content))
    return {"email_html": response.content}


def send_email_node(state: AgentState) -> AgentState:
    log.info("Sending to %s via %s...", os.environ["RECIPIENT_EMAIL"], os.environ["SMTP_HOST"])
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AI News Digest"
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = os.environ["RECIPIENT_EMAIL"]
    msg.attach(MIMEText(state["email_html"], "html"))

    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", 587))) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.sendmail(os.environ["SMTP_FROM"], os.environ["RECIPIENT_EMAIL"], msg.as_string())

    log.info("Sent!")
    return {"email_sent": True}
