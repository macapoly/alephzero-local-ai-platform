# ============================================================
# ALEPHZERO AI ASSISTANT
# FastAPI + Agent Router + API Integration + Vision + MLOps
# ============================================================
from tools.api_tool import call_api
from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


from app.agent_router import (
    route_request,
    ROUTE_CALCULATOR,
    ROUTE_SYSTEM,
    ROUTE_TIME,
    ROUTE_API,
)

from app.model_gateway import (
    generate,
    get_model_info,
)

from tools.calculator import calculate
from tools.system_tools import get_system_info
from tools.time_tools import get_current_time


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "ALEPHZERO"

APP_VERSION = "3.0.0"

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434"
)

VISION_MODEL = os.getenv(
    "VISION_MODEL",
    "gemma3"
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024

TELEMETRY_DIR = Path("data")

TELEMETRY_FILE = (
    TELEMETRY_DIR /
    "telemetry.jsonl"
)

TELEMETRY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(

    title=APP_NAME,

    version=APP_VERSION,

    description=(
        "ALEPHZERO local AI assistant with "
        "agent routing, API integration, "
        "multimodal vision and MLOps telemetry."
    )
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):

    message: str


# ============================================================
# MLOPS METRICS
# ============================================================

metrics = {

    "total_requests": 0,

    "successful_requests": 0,

    "failed_requests": 0,

    "vision_requests": 0,

    "api_requests": 0,

    "total_latency_ms": 0.0,

}


def record_telemetry(data):

    try:

        with open(
            TELEMETRY_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    data,
                    ensure_ascii=False
                ) + "\n"
            )

    except Exception as error:

        print(
            "Telemetry error:",
            error
        )


def start_request():

    metrics["total_requests"] += 1

    return time.perf_counter()


def finish_request(
    start_time,
    success=True,
    agent=None,
    request_type="chat"
):

    latency = (
        time.perf_counter() -
        start_time
    ) * 1000

    metrics["total_latency_ms"] += latency

    if success:

        metrics["successful_requests"] += 1

    else:

        metrics["failed_requests"] += 1

    record_telemetry({

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "request_type":
            request_type,

        "agent":
            agent,

        "success":
            success,

        "latency_ms":
            round(latency, 2),

    })

    return latency


# ============================================================
# CALCULATOR
# ============================================================

def execute_calculator(message):

    try:

        import re

        # Extract a mathematical expression from natural language.
        match = re.search(
            r"[-+]?\d+(?:\.\d+)?(?:\s*[\+\-\*/%\^]\s*[-+]?\d+(?:\.\d+)?)+",
            message
        )

        expression = (
            match.group(0)
            if match
            else message.strip()
        )

        result = calculate(
            expression
        )

        if (
            isinstance(result, float)
            and result.is_integer()
        ):

            result = int(result)

        return str(result)

    except Exception as error:

        return (
            "I could not calculate that expression. "
            f"{error}"
        )

# ============================================================
# TIME
# ============================================================

def execute_time():

    time_data = get_current_time()

    if "error" in time_data:

        return (

            "I was unable to retrieve "
            "the current time. "

            f"Error: {time_data['error']}"

        ), time_data

    response = (

        "The current time in Nigeria is "

        f"{time_data['current_time']} "

        f"({time_data['current_time_24h']}) "

        f"on {time_data['date']}. "

        f"Timezone: "
        f"{time_data['timezone_name']} "

        f"({time_data['utc_offset']})."

    )

    return response, time_data


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def execute_system():

    system_data = get_system_info()

    if "error" in system_data:

        return (

            "Unable to retrieve system information: "

            f"{system_data['error']}"

        ), system_data

    response = (

        "Here is the information obtained "
        "directly from this computer:\n\n"

        f"• Processor: "
        f"{system_data.get('processor')}\n"

        f"• Operating system: "
        f"{system_data.get('operating_system')}\n"

        f"• OS version: "
        f"{system_data.get('os_version')}\n"

        f"• Architecture: "
        f"{system_data.get('architecture')}\n"

        f"• Hostname: "
        f"{system_data.get('hostname')}\n"

        f"• Python version: "
        f"{system_data.get('python_version')}\n"

        f"• CPU count: "
        f"{system_data.get('cpu_count')}"

    )

    return response, system_data

# ============================================================
# API INTEGRATION
# ============================================================

def execute_api(message):

    """
    Execute an API request using the registered API tool.

    The API request is extracted from the user's message.

    Currently supports explicit URLs and defaults to GET.
    """

    import re

    url_match = re.search(
        r"https?://[^\s]+",
        message
    )

    if not url_match:

        raise ValueError(
            "No HTTP or HTTPS API URL was found in the request."
        )

    url = url_match.group(0).rstrip(
        ".,!?;:)"
    )

    result = call_api({

        "url":
            url,

        "method":
            "GET"

    })

    return result
# ============================================================
# API INTEGRATION
# ============================================================

def call_external_api(
    url,
    method="GET",
    payload=None,
    headers=None
):

    start = time.perf_counter()

    metrics["api_requests"] += 1

    try:

        if method.upper() == "GET":

            response = requests.get(
                url,
                headers=headers or {},
                timeout=15
            )

        elif method.upper() == "POST":

            response = requests.post(
                url,
                json=payload or {},
                headers=headers or {},
                timeout=15
            )

        else:

            raise ValueError(
                "Unsupported HTTP method."
            )

        response.raise_for_status()

        try:

            result = response.json()

        except ValueError:

            result = response.text

        latency = (
            time.perf_counter() -
            start
        ) * 1000

        record_telemetry({

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "request_type":
                "external_api",

            "url":
                url,

            "method":
                method.upper(),

            "success":
                True,

            "latency_ms":
                round(latency, 2)

        })

        return {

            "success":
                True,

            "status_code":
                response.status_code,

            "data":
                result,

            "latency_ms":
                round(latency, 2)

        }

    except Exception as error:

        return {

            "success":
                False,

            "error":
                str(error)

        }


# ============================================================
# VISION
# ============================================================

def analyze_image(
    image_bytes,
    filename,
    prompt
):

    if len(image_bytes) > MAX_IMAGE_SIZE:

        raise ValueError(
            "Image is larger than 10 MB."
        )

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    payload = {

        "model":
            VISION_MODEL,

        "messages": [

            {

                "role":
                    "user",

                "content":
                    prompt,

                "images": [
                    encoded_image
                ]

            }

        ],

        "stream":
            False

    }

    response = requests.post(

        f"{OLLAMA_URL}/api/chat",

        json=payload,

        timeout=180

    )

    response.raise_for_status()

    data = response.json()

    return {

        "response":
            data["message"]["content"],

        "model":
            data.get(
                "model",
                VISION_MODEL
            ),

        "filename":
            filename

    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return FileResponse(
        "static/index.html"
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    try:

        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5
        )

        ollama_online = response.ok

    except Exception:

        ollama_online = False

    model_info = get_model_info()

    return {

        "status":
            "online"
            if ollama_online
            else "degraded",

        "application":
            APP_NAME,

        "version":
            APP_VERSION,

        "model":
            model_info["model"],

        "provider":
            model_info["provider"],

        "vision_model":
            VISION_MODEL,

        "ollama":
            ollama_online,

        "architecture":
            "agent_router + model_gateway",

        "features": [

            "agent_routing",

            "api_integration",

            "vision",

            "mlops_telemetry",

            "local_inference"

        ]

    }


# ============================================================
# METRICS
# ============================================================

@app.get("/metrics")
def get_metrics():

    total = metrics["total_requests"]

    average_latency = (

        metrics["total_latency_ms"] /
        total

        if total
        else 0

    )

    return {

        **metrics,

        "average_latency_ms":
            round(
                average_latency,
                2
            ),

        "success_rate":

            round(

                (
                    metrics[
                        "successful_requests"
                    ] / total
                ) * 100,

                2

            )

            if total

            else 0

    }


# ============================================================
# TOOLS
# ============================================================

@app.get("/tools")
def tools():

    return {

        "tools": [

            {

                "name":
                    "time_information",

                "description":
                    "Returns current Nigerian time."

            },

            {

                "name":
                    "system_information",

                "description":
                    "Returns computer information."

            },

            {

                "name":
                    "calculator",

                "description":
                    "Evaluates mathematical expressions."

            },

            {

                "name":
                    "vision",

                "description":
                    "Analyzes uploaded images."

            },

            {

                "name":
                    "api_integration",

                "description":
                    "Connects ALEPHZERO to external APIs."

            }

        ]

    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    start = start_request()

    message = request.message.strip()

    if not message:

        raise HTTPException(

            status_code=400,

            detail="Message cannot be empty."

        )

    route = route_request(
        message
    )

    try:

        # ----------------------------------------------------
        # CALCULATOR
        # ----------------------------------------------------

        if route == ROUTE_CALCULATOR:

            result = execute_calculator(
                message
            )

            latency = finish_request(

                start,

                True,

                route,

                "calculator"

            )

            return {

                "response":
                    f"The answer is {result}.",

                "agent":
                    route,

                "tool_used":
                    "calculator",

                "latency_ms":
                    round(latency, 2),

                "tool_data": {

                    "expression":
                        message,

                    "result":
                        result

                }

            }


        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        if route == ROUTE_TIME:

            response_text, time_data = (
                execute_time()
            )

            latency = finish_request(

                start,

                True,

                route,

                "time"

            )

            return {

                "response":
                    response_text,

                "agent":
                    route,

                "tool_used":
                    "time_information",

                "latency_ms":
                    round(latency, 2),

                "tool_data":
                    time_data

            }


        # ----------------------------------------------------
        # SYSTEM
        # ----------------------------------------------------

        if route == ROUTE_SYSTEM:

            response_text, system_data = (
                execute_system()
            )

            latency = finish_request(

                start,

                True,

                route,

                "system"

            )

            return {

                "response":
                    response_text,

                "agent":
                    route,

                "tool_used":
                    "system_information",

                "latency_ms":
                    round(latency, 2),

                "tool_data":
                    system_data

            }

# ----------------------------------------------------
        # API INTEGRATION
        # ----------------------------------------------------

        if route == ROUTE_API:

            api_result = execute_api(
                message
            )

            if not api_result.get("success"):

                raise RuntimeError(
                    api_result.get(
                        "error",
                        "API request failed."
                    )
                )

            latency = finish_request(

                start,

                True,

                route,

                "api"

            )

            return {

                "response":
                    (
                        "API request completed successfully."
                    ),

                "agent":
                    route,

                "tool_used":
                    "api",

                "latency_ms":
                    round(
                        latency,
                        2
                    ),

                "tool_data":
                    api_result

            }


        # ----------------------------------------------------
        # GENERAL AI
        # ----------------------------------------------------
        # ----------------------------------------------------
        # GENERAL AI
        # ----------------------------------------------------

        response_text = generate(
            message
        )

        latency = finish_request(

            start,

            True,

            route,

            "chat"

        )

        return {

            "response":
                response_text,

            "agent":
                route,

            "tool_used":
                None,

            "model":
                get_model_info()["model"],

            "latency_ms":
                round(latency, 2)

        }

    except Exception as error:

        finish_request(

            start,

            False,

            route,

            "chat"

        )

        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ============================================================
# IMAGE CHAT
# ============================================================

@app.post("/vision")
async def vision(
    message: str = Form(
        "Analyze this image."
    ),
    image: UploadFile = File(...)
):

    start = start_request()

    try:

        allowed_types = {

            "image/jpeg",

            "image/png",

            "image/webp",

            "image/gif"

        }

        if image.content_type not in allowed_types:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Unsupported image format. "
                    "Use JPG, PNG, WEBP or GIF."
                )

            )

        image_bytes = await image.read()

        result = analyze_image(

            image_bytes,

            image.filename,

            message

        )

        metrics["vision_requests"] += 1

        latency = finish_request(

            start,

            True,

            "vision_agent",

            "vision"

        )

        result["agent"] = "vision_agent"

        result["tool_used"] = "vision"

        result["latency_ms"] = round(
            latency,
            2
        )

        return result

    except HTTPException:

        finish_request(

            start,

            False,

            "vision_agent",

            "vision"

        )

        raise

    except Exception as error:

        finish_request(

            start,

            False,

            "vision_agent",

            "vision"

        )

        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ============================================================
# API TEST ENDPOINT
# ============================================================

@app.post("/api/test")
def api_test():

    result = call_external_api(

        "https://jsonplaceholder.typicode.com/todos/1"

    )

    return result


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    model_info = get_model_info()

    print()

    print("=" * 65)

    print(
        f"{APP_NAME} v{APP_VERSION}"
    )

    print("=" * 65)

    print(
        f"Model:          {model_info['model']}"
    )

    print(
        f"Provider:        {model_info['provider']}"
    )

    print(
        f"Vision Model:    {VISION_MODEL}"
    )

    print(
        "Architecture:    Agent Router + Model Gateway"
    )

    print(
        "Capabilities:    API / Vision / MLOps"
    )

    print(
        "Web UI:          http://127.0.0.1:8000/"
    )

    print(
        "API Docs:        http://127.0.0.1:8000/docs"
    )

    print(
        "Metrics:         http://127.0.0.1:8000/metrics"
    )

    print(
        "Telemetry:       data/telemetry.jsonl"
    )

    print("=" * 65)

    print()