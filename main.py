"""
KaiHelper Main Entry Point
--------------------------
Launches the KaiHelper FastAPI backend.
Use this file to start the API server directly with Python.
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting KaiHelper FastAPI backend ...")
    try:
        uvicorn.run(
            "kaihelper.api.main_api:app",  # module:variable path
            host="0.0.0.0",              # use 0.0.0.0 if testing from another device
            port=8000,
            reload=False                    # auto-reload on code changes (for dev)
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unhandled error while starting API: {e}")
        sys.exit(1)
