# ALEPHZERO Local AI Engineering Platform

ALEPHZERO is a local AI engineering platform built with Python, FastAPI and Ollama.

It demonstrates local LLM inference, agent routing, tool execution, API integration, Retrieval-Augmented Generation (RAG), memory, observability and MLOps foundations.

## Core Architecture

User
?
FastAPI API
?
Agent Router
+-- Calculator
+-- System Information
+-- Time
+-- External API
+-- RAG
+-- General AI
?
Model Gateway
?
Ollama
?
Mistral

## Technologies

- Python
- FastAPI
- Ollama
- Mistral
- RAG
- REST APIs
- SQLite / JSON memory
- PowerShell
- Git / GitHub

## Project Status

Version: 3.0.0

Current capabilities:

- Local LLM inference
- Agent routing
- Calculator tool
- System information tool
- Time tool
- External API integration
- RAG
- Conversation memory
- Metrics and telemetry
- Vision model integration
- MLOps foundations

## Running

Activate the environment:

    .\sentinel_env\Scripts\Activate.ps1

Start the server:

    py -m uvicorn AI_CHATBOX:app --host 127.0.0.1 --port 8000

Web UI:

    http://127.0.0.1:8000/

API documentation:

    http://127.0.0.1:8000/docs

## Repository

GitHub:

https://github.com/macapoly/alephzero-local-ai-platform
