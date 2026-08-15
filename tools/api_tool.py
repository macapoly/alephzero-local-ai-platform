# ============================================================
# ALEPHZERO API TOOL
# ============================================================

"""
Controlled external API integration tool for ALEPHZERO.

Supports:
    - GET requests
    - POST requests
    - JSON payloads
    - Custom headers
    - Query parameters
    - JSON and text responses

The tool is designed to be called through the
ALEPHZERO tool registry.
"""

import json
import time
from urllib.parse import urlparse

import requests


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_TIMEOUT = 30

MAX_RESPONSE_SIZE = 5 * 1024 * 1024


# ============================================================
# URL VALIDATION
# ============================================================

def validate_url(url: str) -> str:
    """
    Validate that the supplied URL uses HTTP or HTTPS.
    """

    if not isinstance(url, str) or not url.strip():
        raise ValueError("API URL is required.")

    url = url.strip()

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            "Only HTTP and HTTPS URLs are supported."
        )

    if not parsed.netloc:
        raise ValueError(
            "Invalid API URL."
        )

    return url


# ============================================================
# RESPONSE PARSER
# ============================================================

def parse_response(response):
    """
    Convert an HTTP response into a JSON-compatible value.
    """

    content_length = len(
        response.content
    )

    if content_length > MAX_RESPONSE_SIZE:

        raise ValueError(
            "API response is larger than 5 MB."
        )

    content_type = (
        response.headers.get(
            "content-type",
            ""
        ).lower()
    )

    if "application/json" in content_type:

        try:

            return response.json()

        except ValueError:

            return response.text

    try:

        return response.json()

    except ValueError:

        return response.text


# ============================================================
# API REQUEST
# ============================================================

def call_api(argument=None):
    """
    Execute a controlled HTTP API request.

    Expected argument:

    {
        "url": "https://example.com/api",
        "method": "GET",
        "params": {},
        "payload": {},
        "headers": {},
        "timeout": 30
    }

    The argument may also be supplied as a JSON string.
    """

    if argument is None:

        raise ValueError(
            "API request configuration is required."
        )


    # --------------------------------------------------------
    # Accept dictionary or JSON string
    # --------------------------------------------------------

    if isinstance(argument, str):

        try:

            argument = json.loads(argument)

        except json.JSONDecodeError as error:

            raise ValueError(
                "API argument must be valid JSON."
            ) from error


    if not isinstance(argument, dict):

        raise ValueError(
            "API argument must be a dictionary."
        )


    # --------------------------------------------------------
    # Extract configuration
    # --------------------------------------------------------

    url = validate_url(
        argument.get("url")
    )

    method = str(
        argument.get(
            "method",
            "GET"
        )
    ).upper()

    params = argument.get(
        "params"
    )

    payload = argument.get(
        "payload"
    )

    headers = argument.get(
        "headers"
    )

    timeout = argument.get(
        "timeout",
        DEFAULT_TIMEOUT
    )


    # --------------------------------------------------------
    # Validate method
    # --------------------------------------------------------

    if method not in (
        "GET",
        "POST"
    ):

        raise ValueError(
            "Only GET and POST requests are supported."
        )


    # --------------------------------------------------------
    # Validate optional fields
    # --------------------------------------------------------

    if params is not None and not isinstance(
        params,
        dict
    ):

        raise ValueError(
            "'params' must be a dictionary."
        )


    if headers is not None and not isinstance(
        headers,
        dict
    ):

        raise ValueError(
            "'headers' must be a dictionary."
        )


    if payload is not None and not isinstance(
        payload,
        (dict, list, str, int, float, bool)
    ):

        raise ValueError(
            "'payload' must contain JSON-compatible data."
        )


    try:

        timeout = float(timeout)

    except (TypeError, ValueError):

        raise ValueError(
            "'timeout' must be a number."
        )


    if timeout <= 0 or timeout > 120:

        raise ValueError(
            "Timeout must be between 1 and 120 seconds."
        )


    # --------------------------------------------------------
    # Prepare headers
    # --------------------------------------------------------

    request_headers = dict(
        headers or {}
    )


    # --------------------------------------------------------
    # Execute request
    # --------------------------------------------------------

    start_time = time.perf_counter()


    try:

        if method == "GET":

            response = requests.get(

                url,

                params=params,

                headers=request_headers,

                timeout=timeout

            )

        else:

            response = requests.post(

                url,

                params=params,

                json=payload,

                headers=request_headers,

                timeout=timeout

            )


        latency_ms = (
            time.perf_counter() -
            start_time
        ) * 1000


        # ----------------------------------------------------
        # HTTP error handling
        # ----------------------------------------------------

        response.raise_for_status()


        # ----------------------------------------------------
        # Parse response
        # ----------------------------------------------------

        data = parse_response(
            response
        )


        return {

            "success":
                True,

            "status_code":
                response.status_code,

            "method":
                method,

            "url":
                url,

            "data":
                data,

            "latency_ms":
                round(
                    latency_ms,
                    2
                )

        }


    except requests.exceptions.Timeout as error:

        return {

            "success":
                False,

            "method":
                method,

            "url":
                url,

            "error":
                f"API request timed out: {error}"

        }


    except requests.exceptions.ConnectionError as error:

        return {

            "success":
                False,

            "method":
                method,

            "url":
                url,

            "error":
                f"Could not connect to API: {error}"

        }


    except requests.exceptions.HTTPError as error:

        status_code = None

        if error.response is not None:

            status_code = (
                error.response.status_code
            )

        return {

            "success":
                False,

            "status_code":
                status_code,

            "method":
                method,

            "url":
                url,

            "error":
                str(error)

        }


    except requests.exceptions.RequestException as error:

        return {

            "success":
                False,

            "method":
                method,

            "url":
                url,

            "error":
                f"API request failed: {error}"

        }


# ============================================================
# SIMPLE API HEALTH TEST
# ============================================================

def test_api():

    return call_api({

        "url":
            "https://jsonplaceholder.typicode.com/todos/1",

        "method":
            "GET"

    })