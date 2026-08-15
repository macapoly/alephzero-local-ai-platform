# ============================================================
# ALEPHZERO CONVERSATION MANAGER
# ============================================================

"""
Conversation management layer for ALEPHZERO.

Responsibilities:

    - Create conversations
    - Store conversation messages
    - Retrieve conversation context
    - Limit context size
    - Clear conversations
    - Track conversation metadata

This module does NOT communicate with Ollama.

The Model Gateway remains responsible for model inference.
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional
from uuid import uuid4


# ============================================================
# CONFIGURATION
# ============================================================

MAX_MESSAGES = 20

MAX_MESSAGE_LENGTH = 12000


# ============================================================
# STORAGE
# ============================================================

_conversations: Dict[str, dict] = {}

_lock = Lock()


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _timestamp() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def _create_id() -> str:

    return str(uuid4())


# ============================================================
# CREATE CONVERSATION
# ============================================================

def create_conversation() -> dict:

    conversation_id = _create_id()

    conversation = {

        "conversation_id":
            conversation_id,

        "created_at":
            _timestamp(),

        "updated_at":
            _timestamp(),

        "message_count":
            0,

        "messages":
            []

    }

    with _lock:

        _conversations[
            conversation_id
        ] = conversation

    return conversation


# ============================================================
# GET CONVERSATION
# ============================================================

def get_conversation(
    conversation_id: str
) -> Optional[dict]:

    with _lock:

        return _conversations.get(
            conversation_id
        )


# ============================================================
# GET OR CREATE
# ============================================================

def get_or_create_conversation(
    conversation_id: Optional[str] = None
) -> dict:

    if conversation_id:

        conversation = get_conversation(
            conversation_id
        )

        if conversation:

            return conversation

    return create_conversation()


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(
    conversation_id: str,
    role: str,
    content: str
) -> dict:

    if not content or not content.strip():

        raise ValueError(
            "Message content cannot be empty."
        )

    if role not in {
        "system",
        "user",
        "assistant"
    }:

        raise ValueError(
            "Invalid message role."
        )

    content = content.strip()

    if len(content) > MAX_MESSAGE_LENGTH:

        content = (
            content[
                :MAX_MESSAGE_LENGTH
            ]
            + "\n[Message truncated]"
        )

    with _lock:

        conversation = _conversations.get(
            conversation_id
        )

        if conversation is None:

            raise ValueError(
                "Conversation not found."
            )

        conversation[
            "messages"
        ].append({

            "role":
                role,

            "content":
                content,

            "timestamp":
                _timestamp()

        })

        # Keep only the most recent messages.
        if len(
            conversation["messages"]
        ) > MAX_MESSAGES:

            conversation[
                "messages"
            ] = conversation[
                "messages"
            ][-MAX_MESSAGES:]

        conversation[
            "message_count"
        ] = len(
            conversation["messages"]
        )

        conversation[
            "updated_at"
        ] = _timestamp()

        return conversation


# ============================================================
# GET MESSAGES
# ============================================================

def get_messages(
    conversation_id: str
) -> List[dict]:

    conversation = get_conversation(
        conversation_id
    )

    if conversation is None:

        return []

    return list(
        conversation["messages"]
    )


# ============================================================
# GET MODEL CONTEXT
# ============================================================

def get_context(
    conversation_id: str
) -> List[dict]:

    """
    Return conversation messages in a format suitable
    for the Model Gateway.
    """

    messages = get_messages(
        conversation_id
    )

    return [

        {

            "role":
                message["role"],

            "content":
                message["content"]

        }

        for message in messages

    ]


# ============================================================
# CLEAR CONVERSATION
# ============================================================

def clear_conversation(
    conversation_id: str
) -> bool:

    with _lock:

        if conversation_id not in _conversations:

            return False

        del _conversations[
            conversation_id
        ]

        return True


# ============================================================
# LIST CONVERSATIONS
# ============================================================

def list_conversations() -> List[dict]:

    with _lock:

        return [

            {

                "conversation_id":
                    conversation[
                        "conversation_id"
                    ],

                "created_at":
                    conversation[
                        "created_at"
                    ],

                "updated_at":
                    conversation[
                        "updated_at"
                    ],

                "message_count":
                    conversation[
                        "message_count"
                    ]

            }

            for conversation
            in _conversations.values()

        ]


# ============================================================
# CONVERSATION COUNT
# ============================================================

def conversation_count() -> int:

    with _lock:

        return len(
            _conversations
        )


# ============================================================
# MESSAGE COUNT
# ============================================================

def message_count(
    conversation_id: str
) -> int:

    conversation = get_conversation(
        conversation_id
    )

    if conversation is None:

        return 0

    return conversation[
        "message_count"
    ]