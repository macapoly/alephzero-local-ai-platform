# ============================================================
# ALEPHZERO / SENTINEL
# MAIN FASTAPI APPLICATION
# ============================================================

from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"


# ============================================================
# CREATE APPLICATION
# ============================================================

app = FastAPI(
    title="ALEPHZERO AI Assistant",
    description="Local AI assistant powered by Ollama",
    version="1.0.0",
)


# ============================================================
# STATIC FILES
# ============================================================

# This serves:
#
# /static/style.css
# /static/script.js
# /static/index.html
#
# The directory must exist at:
#
# SENTINEL/
#     static/
#         index.html
#         style.css
#         script.js

if not STATIC_DIR.exists():
    print(
        f"WARNING: Static directory not found: {STATIC_DIR}"
    )

else:
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )


# ============================================================
# ROOT WEB INTERFACE
# ============================================================

@app.get("/", include_in_schema=False)
async def serve_frontend():

    index_file = STATIC_DIR / "index.html"

    if not index_file.exists():

        return {
            "status": "error",
            "message": "Frontend index.html was not found.",
            "expected_path": str(index_file),
        }

    return FileResponse(
        str(index_file),
        media_type="text/html",
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "online",
        "message": "Sentinel AI Assistant backend is running",
    }


# ============================================================
# EXISTING APPLICATION ROUTES
# ============================================================

# Your project already contains:
#
# app/
#     agent_router.py
#     router.py
#     model_gateway.py
#     rag.py
#
# We attempt to load the existing router without breaking
# application startup if the router is not available yet.


try:

    from app.router import router as main_router

    app.include_router(
        main_router
    )

    print(
        "✓ Main application router loaded"
    )

except Exception as error:

    print(
        "WARNING: Main router could not be loaded:"
    )

    print(error)


# ============================================================
# AI AGENT ROUTER
# ============================================================

try:

    from app.agent_router import router as agent_router

    app.include_router(
        agent_router,
        prefix="/agent",
    )

    print(
        "✓ AI agent router loaded"
    )

except Exception as error:

    print(
        "WARNING: Agent router could not be loaded:"
    )

    print(error)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():

    print()
    print("=" * 60)
    print("ALEPHZERO AI ASSISTANT")
    print("=" * 60)

    print()
    print("API:")
    print("  http://127.0.0.1:8000")

    print()
    print("Web UI:")
    print("  http://127.0.0.1:8000/")

    print()
    print("Health:")
    print("  http://127.0.0.1:8000/health")

    print()
    print("Static CSS:")
    print("  http://127.0.0.1:8000/static/style.css")

    print()
    print("Static JavaScript:")
    print("  http://127.0.0.1:8000/static/script.js")

    print()
    print("API Docs:")
    print("  http://127.0.0.1:8000/docs")

    print()
    print("=" * 60)
    print()


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event("shutdown")
async def shutdown_event():

    print()
    print("ALEPHZERO backend shutting down...")
    print()