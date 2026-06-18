from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import os

class PushNotification(BaseModel):
    """ A message to be sent to the user. """
    message: str = Field(..., description="The message to be sent to the user.")

class PushNotificationTool(BaseTool):
    name: str = "Send a push notification"
    description: str = (
        "This tool is used to send a push notification to the user."
    )
    args_schema: Type[BaseModel] = PushNotification

    def _run(self, message: str) -> str:
        ntfy_url = os.getenv("NTFY_URL")
        response = requests.post(
            ntfy_url,
            data=message.encode('utf-8')
        )
        if response.status_code == 200:
            return {"message": "Notification sent successfully!"}
        else:
            return {"message": f"Failed to send: {response.status_code}"}
