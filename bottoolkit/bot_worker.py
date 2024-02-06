from botbuilder.schema import Activity

from .core import Bot
from .core import BotMessage


class BotWorker:
    """
    A base class for a `bot` instance, an object that contains the information and functionality for taking action in response to an incoming message.
    Note that adapters are likely to extend this class with additional platform-specific methods - refer to the adapter documentation for these extensions.
    """

    def __init__(self, controller: Bot, config: any) -> None:
        self._controller = controller
        self._config = config

    def get_controller(self):
        return self._controller

    def get_config(self):
        return self._config

    async def say(self, message: BotMessage):
        """ """

        activity = await self.ensure_message_format(message=message)

    async def ensure_message_format(self, message: BotMessage | str) -> Activity:
        """"""
        if isinstance(message, str):
            return Activity(type="message", text=message.text, channel_data={})

        return Activity(**message.__dict__)
