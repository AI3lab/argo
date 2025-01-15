from datetime import datetime, timezone, timedelta
import time
from typing import Optional

def get_now_ms() -> int:
    return int(time.time_ns() // 1_000_000)

def datetime_to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def get_time_delta(days: int = 0, hours: int = 0, minutes: int = 0) -> timedelta:
    return timedelta(days=days, hours=hours, minutes=minutes)