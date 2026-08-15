# ============================================================
# ALEPHZERO TOOL ROUTER
# ============================================================

import re

from tools.system_tools import get_system_info
from tools.calculator import calculate


# ============================================================
# TIME TOOL
# ============================================================

from datetime import datetime, timezone, timedelta


WAT = timezone(
    timedelta(hours=1),
    name="WAT"
)


def get_current_time():

    now = datetime.now(WAT)

    return {

        "current_time":
            now.strftime("%I:%M:%S %p"),

        "current_time_24h":
            now.strftime("%H:%M:%S"),

        "date":
            now.strftime("%A, %B %d, %Y"),

        "timezone":
            "WAT",

        "timezone_name":
            "West Africa Time",

        "utc_offset":
            "UTC+1",

        "iso":
            now.isoformat()

    }


# ============================================================
# TIME DETECTOR
# ============================================================

def is_time_question(message: str) -> bool:

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
# SYSTEM INFORMATION DETECTOR
# ============================================================

def is_system_question(message: str) -> bool:

    text = message.lower()

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
# CALCULATOR DETECTOR
# ============================================================

def is_calculator_question(message: str) -> bool:

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


    if re.search(
        r"\d+\s*[\+\-\*/%\^]\s*\d+",
        text
    ):

        return True


    if re.fullmatch(
        r"[\d\s\+\-\*/%\(\)\.\^]+",
        text
    ):

        return True


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
# ROUTER
# ============================================================

def route_tool(message: str):

    """
    Determine whether the user's request should
    be handled by a Python tool.

    Returns:

        {
            "tool": "...",
            "input": message
        }

    or:

        None

    when no deterministic tool matches.
    """


    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if is_time_question(message):

        return {

            "tool":
                "time_information",

            "input":
                message

        }


    # --------------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------------

    if is_system_question(message):

        return {

            "tool":
                "system_information",

            "input":
                message

        }


    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    if is_calculator_question(message):

        return {

            "tool":
                "calculator",

            "input":
                message

        }


    # --------------------------------------------------------
    # NO TOOL
    # --------------------------------------------------------

    return None


# ============================================================
# EXECUTE ROUTED TOOL
# ============================================================

def execute_tool(
    tool_name: str,
    message: str
):

    """
    Execute a tool selected by the router.
    """


    if tool_name == "time_information":

        return get_current_time()


    if tool_name == "system_information":

        return get_system_info()


    if tool_name == "calculator":

        return calculate(message)


    raise ValueError(
        f"Unknown tool: {tool_name}"
    )