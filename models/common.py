#models/common.py
from datetime import datetime, timezone
from sqlalchemy import TIMESTAMP

TimestampTZ = TIMESTAMP(timezone=True)
utcnow_aware = lambda: datetime.now(timezone.utc)