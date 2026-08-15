from datetime import datetime, timezone, timedelta


# Nigeria / West Africa Time
WAT = timezone(
    timedelta(hours=1),
    name="WAT"
)


def get_current_time():
    """
    Retrieve the actual current time in Nigeria.
    """

    try:

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

    except Exception as error:

        return {
            "error": str(error)
        }