# Architecture

## High-Level Architecture

User
?
Web UI / REST Client
?
FastAPI
?
Agent Router
?
Specialized Agent / Tool
?
Model Gateway
?
Ollama
?
Local LLM

## Components

### FastAPI

Provides the application API and web interface.

### Agent Router

Determines which capability should process the request.

### Tools

Current tools include:

- Calculator
- System Information
- Current Time
- External API

### RAG

Retrieves relevant information from the local knowledge base before generating an answer.

### Model Gateway

Provides a centralized interface between ALEPHZERO and Ollama.

### Ollama

Provides local LLM inference.

## Design Principles

- Modular architecture
- Local-first AI
- Separation of concerns
- Tool-based execution
- Retrieval before generation
- API-first design
- Observability
- Reproducibility
