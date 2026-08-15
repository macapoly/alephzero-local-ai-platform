# ============================================================
# ALEPHZERO MODEL GATEWAY
# ============================================================

"""
Central model interface for ALEPHZERO.

Responsibilities:

    - Communicate with Ollama
    - Manage model configuration
    - Build context-aware prompts
    - Provide model information

The rest of ALEPHZERO should communicate with the
language model through this module.
"""

from __future__ import annotations

import os
from typing import List, Dict, Optional

import requests


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "mistral:latest"
)

OLLAMA_TIMEOUT = int(
    os.getenv(
        "OLLAMA_TIMEOUT",
        "120"
    )
)

MAX_CONTEXT_MESSAGES = int(
    os.getenv(
        "MAX_CONTEXT_MESSAGES",
        "20"
    )
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are ALEPHZERO, a helpful local AI assistant.

You are running locally on the user's computer.

Your language model is provided through the ALEPHZERO
Model Gateway.

IMPORTANT RULES:

1. Be accurate.

2. Do not invent facts.

3. Do not pretend to have access to information
   that you do not have.

4. ALEPHZERO has access to Python tools for:
   - current time
   - system information
   - calculations

5. When tool results are provided, treat those results
   as authoritative.

6. Do not claim that you used a tool if you did not.

7. Give clear and useful answers.

8. Keep responses reasonably concise.

9. If you do not know something, say so.

10. Do not claim internet access unless an explicit
    internet capability has been provided.

11. Previous conversation messages are context.
    Use them when relevant to the current request.

12. Do not assume that every previous message is
    relevant to the current request.
"""


# ============================================================
# CONTEXT FORMATTER
# ============================================================

def format_conversation_context(
    conversation_context: Optional[
        List[Dict[str, str]]
    ] = None
) -> str:

    """
    Convert conversation messages into a readable
    prompt section for the local model.
    """

    if not conversation_context:

        return ""

    messages = conversation_context[
        -MAX_CONTEXT_MESSAGES:
    ]

    lines = []

    for message in messages:

        role = message.get(
            "role",
            "user"
        )

        content = message.get(
            "content",
            ""
        ).strip()

        if not content:

            continue

        if role == "system":

            label = "System"

        elif role == "assistant":

            label = "Assistant"

        else:

            label = "User"

        lines.append(
            f"{label}:\n{content}"
        )

    if not lines:

        return ""

    return (
        "\n\n"
        "Previous conversation:\n"
        "----------------------\n"
        + "\n\n".join(lines)
        + "\n"
        "----------------------\n"
    )


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(
    message: str,
    system_prompt: str = SYSTEM_PROMPT,
    conversation_context: Optional[
        List[Dict[str, str]]
    ] = None
) -> str:

    """
    Build the final prompt sent to Ollama.
    """

    context = format_conversation_context(
        conversation_context
    )

    return f"""
{system_prompt}

{context}

Current user message:
{message}

Assistant:
""".strip()


# ============================================================
# MODEL RESPONSE
# ============================================================

def generate(
    message: str,
    system_prompt: str = SYSTEM_PROMPT,
    conversation_context: Optional[
        List[Dict[str, str]]
    ] = None
) -> str:

    """
    Send a prompt to the configured local model.

    Backward compatible:

        generate("Hello")

    Context-aware:

        generate(
            "What is my project called?",
            conversation_context=[...]
        )
    """

    if not message or not message.strip():

        raise ValueError(
            "Message cannot be empty."
        )

    prompt = build_prompt(
        message=message,
        system_prompt=system_prompt,
        conversation_context=conversation_context
    )

    payload = {

        "model":
            OLLAMA_MODEL,

        "prompt":
            prompt,

        "stream":
            False

    }

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=OLLAMA_TIMEOUT

        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "response",
            ""
        ).strip()

        if not answer:

            raise RuntimeError(
                "The model returned an empty response."
            )

        return answer

    except requests.exceptions.ConnectionError as error:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        ) from error

    except requests.exceptions.Timeout as error:

        raise RuntimeError(
            "The model request timed out."
        ) from error

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"Model gateway request failed: {error}"
        ) from error

    except ValueError:

        raise

    except Exception as error:

        raise RuntimeError(
            f"Unexpected model gateway error: {error}"
        ) from error


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info():

    return {

        "provider":
            "ollama",

        "model":
            OLLAMA_MODEL,

        "endpoint":
            OLLAMA_URL,

        "timeout":
            OLLAMA_TIMEOUT,

        "max_context_messages":
            MAX_CONTEXT_MESSAGES

    }