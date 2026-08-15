# ============================================================
# ALEPHZERO TOOL REGISTRY
# ============================================================

"""
Central registry for ALEPHZERO tools.

All executable tools available to the agent system
are registered here.
"""

from tools.calculator import calculate
from tools.system_tools import get_system_info
from tools.time_tools import get_current_time
from tools.api_tool import call_api


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = {

    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    "calculator": {

        "name":
            "calculator",

        "description":
            (
                "Safely evaluates mathematical "
                "expressions."
            ),

        "function":
            calculate,
    },


    # --------------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------------

    "system_information": {

        "name":
            "system_information",

        "description":
            (
                "Returns information about the "
                "computer running ALEPHZERO."
            ),

        "function":
            get_system_info,
    },


    # --------------------------------------------------------
    # TIME INFORMATION
    # --------------------------------------------------------

    "time_information": {

        "name":
            "time_information",

        "description":
            (
                "Returns the actual current time "
                "in Nigeria."
            ),

        "function":
            get_current_time,
    },


    # --------------------------------------------------------
    # API INTEGRATION
    # --------------------------------------------------------

    "api": {

        "name":
            "api",

        "description":
            (
                "Makes HTTP API requests to external "
                "services using GET or POST."
            ),

        "function":
            call_api,
    },

}


# ============================================================
# GET AVAILABLE TOOLS
# ============================================================

def get_available_tools():

    """
    Return information about all registered tools.
    """

    return [

        {

            "name":
                tool["name"],

            "description":
                tool["description"],

        }

        for tool in TOOLS.values()

    ]


# ============================================================
# GET TOOL
# ============================================================

def get_tool(tool_name):

    """
    Retrieve a registered tool by name.
    """

    return TOOLS.get(tool_name)


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_tool(
    tool_name,
    argument=None
):

    """
    Execute a registered tool.

    Tools that require no argument are called
    without one.

    Tools that require an argument receive it
    through the argument parameter.
    """

    tool = get_tool(tool_name)


    if tool is None:

        raise ValueError(
            f"Tool '{tool_name}' is not registered."
        )


    function = tool["function"]


    if argument is None:

        return function()


    return function(argument)