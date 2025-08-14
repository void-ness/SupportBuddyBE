from datetime import datetime, timezone, timedelta

from .notion_manager import NotionManager


class NotionManagerV2(NotionManager):
    def get_filter_payload(self):
        # Calculate timestamp for 24 hours ago
        last_24_hours = datetime.now(timezone.utc) - timedelta(hours=24)
        last_24_hours_iso = last_24_hours.isoformat()

        return {
            "and": [
                {"property": "Ignore Entry", "checkbox": {"equals": False}},
                {
                    "timestamp": "last_edited_time",
                    "last_edited_time": {"on_or_after": last_24_hours_iso},
                },
            ]
        }
