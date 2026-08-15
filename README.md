# ALEPHZERO — Local AI Engineering Platform

> A local-first AI engineering platform combining LLM inference, agent routing, tool execution, RAG, API integration, memory, observability and MLOps foundations.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black)
![Mistral](https://img.shields.io/badge/LLM-Mistral-orange)
![RAG](https://img.shields.io/badge/AI-RAG-purple)
![MLOps](https://img.shields.io/badge/MLOps-Foundations-red)

---

## Overview

ALEPHZERO is a locally hosted AI engineering platform designed to demonstrate how modern AI systems can be built by combining a Large Language Model with deterministic tools, retrieval, APIs, memory and operational monitoring.

Rather than functioning as a simple chatbot, ALEPHZERO uses an **agent-routing architecture** to determine how each request should be processed.

---

## Architecture

```text
                         USER
                          │
                          ▼
                   ┌─────────────┐
                   │   FastAPI   │
                   │     API     │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │    Agent    │
                   │   Router    │
                   └──────┬──────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
     ┌─────────┐     ┌─────────┐     ┌─────────┐
     │  Tools  │     │   RAG   │     │ General │
     │         │     │         │     │   AI    │
     └────┬────┘     └────┬────┘     └────┬────┘
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                  ┌──────────────┐
                  │ Model Gateway│
                  └──────┬───────┘
                         │
                         ▼
                    ┌─────────┐
                    │ Ollama  │
                    │ Mistral │
                    └─────────┘