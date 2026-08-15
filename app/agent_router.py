# ============================================================
# ALEPHZERO AGENT ROUTER
# ============================================================

"""
Agent Router for ALEPHZERO.

The router determines which capability should handle
an incoming user request.

Current routes:

    calculator
    time_information
    system_information
    api
    rag
    general

Architecture:

    User Request
         |
         v
    Agent Router
         |
         +---- calculator
         |
         +---- time_information
         |
         +---- system_information
         |
         +---- api
         |
         +---- rag
         |
         +---- general
"""

import re


# ============================================================
# RAG
# ============================================================

from app.rag import retrieve


# ============================================================
# ROUTE DEFINITIONS
# ============================================================

ROUTE_CALCULATOR = "calculator"

ROUTE_SYSTEM = "system_information"

ROUTE_TIME = "time_information"

ROUTE_API = "api"

ROUTE_RAG = "rag"

ROUTE_GENERAL = "general"


# ============================================================
# TIME DETECTION
# ============================================================

def is_time_request(message: str) -> bool:

    text = message.lower().strip()

    patterns = [

        r"\bwhat time is it\b",
        r"\bwhat's the time\b",
        r"\bwhats the time\b",
        r"\bwhat is the time\b",
        r"\bcurrent time\b",
        r"\btime right now\b",
        r"\btime now\b",
        r"\bcurrent local time\b",
        r"\btell me the time\b",
        r"\bcan you tell me the time\b",
        r"\bdo you know the time\b",
        r"\bwhat time do we have\b",
        r"\bwhat time is it now\b",
        r"\bwhat is the current time\b",
        r"\bwhat's the current time\b",
        r"\btime in nigeria\b",
        r"\btime in lagos\b"

    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


# ============================================================
# SYSTEM INFORMATION DETECTION
# ============================================================

def is_system_request(message: str) -> bool:

    text = message.lower().strip()

    keywords = [

        "what processor",
        "what cpu",
        "which processor",
        "which cpu",
        "what operating system",
        "which operating system",
        "what os",
        "which os",
        "system information",
        "system info",
        "computer information",
        "pc information",
        "computer specs",
        "pc specs",
        "system specs",
        "my computer",
        "my pc",
        "computer processor",
        "computer cpu"

    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# ============================================================
# CALCULATOR DETECTION
# ============================================================

def is_calculator_request(message: str) -> bool:

    text = message.lower().strip()

    calculator_words = [

        "calculate",
        "compute",
        "solve"

    ]

    if any(
        word in text
        for word in calculator_words
    ):

        return True


    # --------------------------------------------------------
    # Mathematical expression
    # --------------------------------------------------------

    if re.search(
        r"\d+\s*[\+\-\*/%\^]\s*\d+",
        text
    ):

        return True


    # --------------------------------------------------------
    # Pure mathematical expression
    # --------------------------------------------------------

    if re.fullmatch(
        r"[\d\s\+\-\*/%\(\)\.\^]+",
        text
    ):

        return True


    # --------------------------------------------------------
    # "What is 25 + 25?"
    # --------------------------------------------------------

    if text.startswith("what is"):

        if any(
            symbol in text
            for symbol in [
                "+",
                "-",
                "*",
                "/",
                "%",
                "^"
            ]
        ):

            return True


    return False


# ============================================================
# API REQUEST DETECTION
# ============================================================

def is_api_request(message: str) -> bool:

    """
    Determine whether the user is asking ALEPHZERO
    to interact with an external HTTP API.
    """

    text = message.lower().strip()


    # --------------------------------------------------------
    # Explicit API terminology
    # --------------------------------------------------------

    api_keywords = [

        "call an api",
        "call the api",
        "call this api",
        "use an api",
        "use the api",
        "use this api",
        "api request",
        "api call",
        "make an api request",
        "make an api call",
        "send an api request",
        "send an api call",
        "query an api",
        "query the api",
        "access an api",
        "access the api",
        "fetch from an api",
        "fetch from the api",
        "get data from an api",
        "get data from the api",
        "post to an api",
        "post to the api",
        "api endpoint",
        "http request",
        "https request",
        "http endpoint",
        "https endpoint"

    ]


    if any(
        keyword in text
        for keyword in api_keywords
    ):

        return True


    # --------------------------------------------------------
    # Detect HTTP/HTTPS URLs
    # --------------------------------------------------------

    if re.search(
        r"https?://[^\s]+",
        text
    ):

        return True


    return False


# ============================================================
# RAG / KNOWLEDGE DETECTION
# ============================================================

def is_rag_request(message: str) -> bool:

    """
    Determine whether a request is likely asking for
    information from ALEPHZERO's local knowledge base.
    """

    text = message.lower().strip()


    # --------------------------------------------------------
    # Explicit knowledge/retrieval language
    # --------------------------------------------------------

    knowledge_keywords = [

        "according to the knowledge base",
        "according to your knowledge",
        "from the knowledge base",
        "from your knowledge base",
        "search your knowledge",
        "search the knowledge",
        "look in the knowledge base",
        "retrieve from the knowledge base",
        "retrieve information",
        "find in the knowledge base",
        "what does the knowledge base say",
        "what do you know about alephzero",
        "tell me about alephzero",
        "what is alephzero",
        "what does alephzero do",
        "what technologies does alephzero use",
        "what features does alephzero have",
        "what are alephzero's features",
        "what is this project",
        "tell me about this project"

    ]


    if any(
        keyword in text
        for keyword in knowledge_keywords
    ):

        return True


    # --------------------------------------------------------
    # Project-specific terms
    # --------------------------------------------------------

    project_keywords = [

        "alephzero",
        "rag architecture",
        "rag system",
        "agent router",
        "model gateway",
        "local ai engineering platform"

    ]


    if any(
        keyword in text
        for keyword in project_keywords
    ):

        return True


    return False


# ============================================================
# RAG AVAILABILITY
# ============================================================

def has_rag_result(message: str) -> bool:

    """
    Check whether the knowledge base actually contains
    information relevant to the request.
    """

    try:

        results = retrieve(
            message,
            top_k=1
        )

        return bool(results)

    except Exception as error:

        print(
            f"RAG routing error: {error}"
        )

        return False


# ============================================================
# AGENT ROUTER
# ============================================================

def route_request(message: str) -> str:

    """
    Determine which ALEPHZERO capability should
    handle the request.

    Priority:

        calculator
        time
        system
        api
        rag
        general
    """

    if not message or not message.strip():

        return ROUTE_GENERAL


    # --------------------------------------------------------
    # Calculator
    # --------------------------------------------------------

    if is_calculator_request(message):

        return ROUTE_CALCULATOR


    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    if is_time_request(message):

        return ROUTE_TIME


    # --------------------------------------------------------
    # System information
    # --------------------------------------------------------

    if is_system_request(message):

        return ROUTE_SYSTEM


    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    if is_api_request(message):

        return ROUTE_API


    # --------------------------------------------------------
    # RAG / knowledge
    # --------------------------------------------------------

    if is_rag_request(message):

        if has_rag_result(message):

            return ROUTE_RAG


    # --------------------------------------------------------
    # General model
    # --------------------------------------------------------

    return ROUTE_GENERAL


# ============================================================
# RAG RETRIEVAL
# ============================================================

def get_rag_context(
    message: str,
    top_k: int = 3
):

    """
    Retrieve relevant knowledge for a user request.

    Returns:

        {
            "route": "rag",
            "results": [...],
            "context": "..."
        }
    """

    try:

        results = retrieve(
            message,
            top_k=top_k
        )


        if not results:

            return {

                "route":
                    ROUTE_RAG,

                "results":
                    [],

                "context":
                    ""

            }


        context_parts = []


        for result in results:

            context_parts.append(

                "Source: "
                + str(result["source"])
                + "\n"
                + str(result["content"])

            )


        context = "\n\n".join(
            context_parts
        )


        return {

            "route":
                ROUTE_RAG,

            "results":
                results,

            "context":
                context

        }


    except Exception as error:

        return {

            "route":
                ROUTE_RAG,

            "results":
                [],

            "context":
                "",

            "error":
                str(error)

        }


# ============================================================
# ROUTE DESCRIPTION
# ============================================================

def describe_route(route: str) -> str:

    descriptions = {

        ROUTE_CALCULATOR:
            "Calculator agent",

        ROUTE_TIME:
            "Time information agent",

        ROUTE_SYSTEM:
            "System information agent",

        ROUTE_API:
            "API integration agent",

        ROUTE_RAG:
            "Retrieval-Augmented Generation agent",

        ROUTE_GENERAL:
            "General AI agent"

    }


    return descriptions.get(
        route,
        "Unknown agent"
    )
