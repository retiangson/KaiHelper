"""
Quick OpenAI connection test for KaiHelper.
Run using:
    python -m kaihelper.config.test_openai
"""

from openai import OpenAI
from kaihelper.config.settings import settings

settings.SMTP_HOST
print(f"Loaded OpenAI Key (first 8 chars): {settings.OPENAI_API_KEY[:8]}...")

if not settings.OPENAI_API_KEY:
    raise ValueError("❌ Missing OPENAI_API_KEY in .env or environment variables.")

# Initialize client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Test call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "KaiHelper connected successfully!"}]
)

print("✅ OpenAI connection successful!")
print("Model:", response.model)
print("Response:", response.choices[0].message.content)
