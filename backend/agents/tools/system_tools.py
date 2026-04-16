import datetime
from typing import Dict, Any
from backend.agents.base import AgentTool

class ClockTool(AgentTool):
    """
    Providing real-time date and time information.
    """
    def __init__(self):
        super().__init__(
            name="get_current_time",
            description="Returns the current date, time, and day of the week."
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        now = datetime.datetime.now()
        return {
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": "Local"
        }
