"""Initializes access to frontier AI models using environment variables."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API Key is missing!")

openai = OpenAI(api_key=OPENAI_API_KEY)
OPENAI_MODEL = "gpt-4o-mini"
