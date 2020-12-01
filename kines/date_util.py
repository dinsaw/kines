from datetime import datetime
from datetime import timedelta
import time


def utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp
    )
    return utc_datetime + offset


def to_iterator_timestamp(timestamp_input):
    if "h" in timestamp_input or "m" in timestamp_input:
        hours = 0
        minutes = 0

        h_split = timestamp_input.split("h")
        if len(h_split) > 1:
            hours = int(h_split[0])

        m_split = h_split[-1].split("m")
        if len(m_split) > 1:
            minutes = int(m_split[0])

        delta = timedelta(hours=hours, minutes=minutes)
        timestamp = datetime.now() - delta
        return datetime.utcfromtimestamp(time.mktime(timestamp.timetuple()))

    return timestamp_input
