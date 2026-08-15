# API Documentation

## Base URL

http://127.0.0.1:8000

## POST /chat

Main conversational endpoint.

### Request

    {
      "message": "What is ALEPHZERO?"
    }

### Response

    {
      "response": "...",
      "agent": "rag",
      "tool_used": null,
      "model": "mistral:latest",
      "latency_ms": 58506
    }

## GET /health

Returns application health information.

## GET /docs

FastAPI interactive API documentation.

## API Integration

ALEPHZERO can identify HTTP/HTTPS API requests and execute supported external API calls through the API tool.

Example:

    Call this API:
    https://jsonplaceholder.typicode.com/todos/1

The response contains:

- status code
- HTTP method
- URL
- returned data
- latency
- execution status
