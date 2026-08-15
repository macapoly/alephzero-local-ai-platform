---

API

ALEPHZERO exposes a FastAPI interface for interacting with the platform and monitoring its operation.

Endpoints

Endpoint| Method| Purpose
"/"| GET| Platform information
"/health"| GET| Application and model health
"/metrics"| GET| Runtime telemetry
"/tools"| GET| Available tools
"/chat"| POST| Text-based AI interaction
"/vision"| POST| Multimodal image analysis
"/api/test"| POST| API integration testing

Chat

Send a natural-language request through the "/chat" endpoint.

Request

{
  "message": "What is 2 + 2?"
}

Response

{
  "response": "The answer is 4.",
  "agent": "calculator",
  "tool_used": "calculator",
  "latency_ms": 0.94
}

This demonstrates the agent-routing flow:

User Request
     ↓
Agent Router
     ↓
Calculator Tool
     ↓
Result
     ↓
AI Response

Vision

The "/vision" endpoint accepts an image and an optional message for multimodal analysis.

POST /vision
Content-Type: multipart/form-data

message: "Analyze this image."
image: <image file>

Health

The "/health" endpoint exposes the current application and model configuration.

{
  "status": "online",
  "application": "ALEPHZERO",
  "version": "3.0.0",
  "model": "mistral:latest",
  "provider": "ollama",
  "vision_model": "gemma3",
  "ollama": true,
  "architecture": "agent_router + model_gateway"
}

Available Tools

ALEPHZERO currently exposes:

- "time_information" — Returns current Nigerian time.
- "system_information" — Returns computer information.
- "calculator" — Evaluates mathematical expressions.
- "vision" — Analyzes uploaded images.
- "api_integration" — Connects ALEPHZERO to external APIs.

Runtime Metrics

The "/metrics" endpoint provides runtime telemetry including:

- Total requests
- Successful requests
- Failed requests
- Vision requests
- API requests
- Total latency
- Average latency
- Success rate

Example development metrics:

{
  "total_requests": 19,
  "successful_requests": 19,
  "failed_requests": 0,
  "vision_requests": 2,
  "api_requests": 0,
  "success_rate": 100.0
}

«Note: Runtime metrics represent a local development session and should not be interpreted as production performance benchmarks.»