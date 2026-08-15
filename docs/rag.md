# RAG Documentation

## Purpose

Retrieval-Augmented Generation allows ALEPHZERO to retrieve relevant information from a local knowledge base before generating a response.

## Pipeline

User Query
?
RAG Router
?
Retriever
?
Knowledge Base
?
Relevant Context
?
Model Gateway
?
Ollama / Mistral
?
Response

## Knowledge Base

Current knowledge is stored under:

    knowledge/

Example:

    knowledge/alephzero.txt

## Retrieval

The RAG module exposes:

    retrieve(message, top_k=3)

The router checks whether relevant information exists before selecting the RAG route.

## Benefits

- Reduces unsupported answers
- Grounds responses in project knowledge
- Keeps knowledge local
- Separates retrieval from generation
- Provides a foundation for future vector databases
