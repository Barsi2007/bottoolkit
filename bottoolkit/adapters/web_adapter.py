from datetime import datetime
from typing import Awaitable
from typing import Callable

from aiohttp.web import Request
from botbuilder.core import BotAdapter
from botbuilder.core import TurnContext
from botbuilder.schema import Activity
from botbuilder.schema import ActivityTypes
from botbuilder.schema import ConversationReference
from botbuilder.schema import ResourceResponse
from loguru import logger

from bottoolkit.core import BotMessage


class WebAdapter(BotAdapter):
    """Connects PyBot to websocket or webhook"""

    def __init__(self, on_turn_error: Callable[[TurnContext, Exception], Awaitable] = None):
        super().__init__(on_turn_error)

    async def activity_to_message(self, activity: Activity) -> BotMessage:
        """ """
        message = BotMessage(
            type=activity.type,
            text=activity.text,
        )

        if activity.channel_data:
            message.__dict__ = activity.channel_data.__dict__

        return message

    async def send_activities(
        self, context: TurnContext, activities: list[Activity]
    ) -> ResourceResponse:
        """ """

        responses = list()

        for i in range(len(activities)):
            activity = activities[i]
            message = self.activity_to_message(activity=activity)
            channel = context.activity.channel_id

            if channel == "websocket":
                raise NotImplementedError("Web socket not implemented")
            elif channel == "webhook":
                outbound = context.turn_state.get("httpBody")

                if not outbound:
                    outbound = []

                outbound.append(message)
                context.turn_state["httpBody"] = outbound

        return responses

    async def update_activity(self, context: TurnContext, activity: Activity) -> None:
        """ """
        raise NotImplementedError()

    async def delete_activity(self, context: TurnContext, reference: ConversationReference) -> None:
        """ """
        raise NotImplementedError()

    async def process_activity(self, request: Request, logic: callable):
        body = await request.json()
        message = BotMessage(**body)

        activity = Activity(
            timestamp=datetime.now(),
            channel_id="webhook",
            conversation={"id": message.user},
            from_property={"id": message.user},
            recipient={"id": "bot"},
            channel_data=message,
            text=message.text,
            type=message.type,
        )

        context = TurnContext(self, activity)

        context.turn_state["httpStatus"] = 200

        await self.run_pipeline(context=context, callback=logic)

        return context.turn_state.get("httpBody")
