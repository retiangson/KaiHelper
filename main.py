import os
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

# Optional debug log
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY not found in environment after load_dotenv()")
else:
    print(f"OPENAI_API_KEY loaded ({os.getenv('OPENAI_API_KEY')[:8]}...)")

import uvicorn
from kaihelper.api.main_api import app

if __name__ == "__main__":
    uvicorn.run(
        "kaihelper.api.main_api:app",
        host="0.0.0.0", #127.0.0.1 local, 0.0.0.0 for network
        port=8000,
        reload=True,
    )
