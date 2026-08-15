# ============================================================
# ALEPHZERO SYSTEM TOOLS
# ============================================================

import platform
import socket
import os


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def get_system_info():

    try:

        processor = platform.processor()

        if not processor:

            processor = platform.machine()

        return {

            "operating_system":
                platform.system(),

            "os_version":
                platform.version(),

            "architecture":
                platform.machine(),

            "processor":
                processor,

            "hostname":
                socket.gethostname(),

            "python_version":
                platform.python_version(),

            "cpu_count":
                os.cpu_count()
        }

    except Exception as error:

        return {

            "error":
                str(error)
        }