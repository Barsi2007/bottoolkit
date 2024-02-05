from abc import ABC
from dataclasses import dataclass
from typing import Optional

from botbuilder.core import BotAdapter
from botbuilder.core import Storage
from botbuilder.core import TurnContext
from botbuilder.dialogs import Dialog
from botbuilder.dialogs import DialogContext
from botbuilder.dialogs import DialogSet
from botbuilder.dialogs import DialogTurnStatus
from botbuilder.dialogs import WaterfallDialog
from botbuilder.schema import Activity
from botbuilder.schema import ConversationReference


@dataclass
class BotMessage:
    type: Optional[str] = None
    text: Optional[str] = None
    value: Optional[str] = None
    user: Optional[str] = None
    channel: Optional[str] = None
    reference: Optional[ConversationReference] = None
    incoming_message: Optional[Activity] = None


class BotPlugin(ABC):
    name: str
    middlewares: dict


@dataclass
class BotTrigger:
    type: str
    pattern: str | BotMessage
    handler: callable


class PyBot:
    _events: dict
    _triggers: dict
    _interrupts: dict
    _conversation_state: any  # TODO: class BotConversationState
    _dependencies: dict
    _boot_complete_handlers: list[callable]

    version: str
    plugins: list
    storage: Storage
    webserver: any  # TODO: Select a default python web framework
    http: any
    adapter: BotAdapter
    dialog_set: DialogSet
    path: str
    booted: bool

    def __init__(
        self,
        webhook_uri: str = "/api/messages",
        dialog_state_property: str = "dialogState",
        adapter: any = None,
        adapter_config: dict = None,
        webserver: any = None,
        webserver_middlewares: str = None,
        storage: Storage = None,
        disable_webserver: bool = None,
        disable_console: bool = None,
        json_limit: str = "100kb",
        url_encoded_limit: str = "100kb",
    ) -> None:

        self.webhook_uri = webhook_uri
        self.dialog_state_property = dialog_state_property
        self.adapter = adapter
        self.adapter_config = adapter_config
        self.webserver = webserver
        self.webserver_middlewares = webserver_middlewares
        self.storage = storage
        self.disable_webserver = disable_webserver
        self.disable_console = disable_console
        self.json_limit = json_limit
        self.url_encoded_limit = url_encoded_limit

        self.booted = False

    def ready(self, handler: callable) -> None:
        """ """

        if self.booted:
            handler(self)
        else:
            self._boot_complete_handlers.append(handler)

    def hears(self, pattern: str, event: str, handler: callable) -> None:

        bot_trigger = BotTrigger(type=None, pattern=pattern, handler=handler)

        if not event in self._triggers:
            self._triggers = []

        self._triggers[event].append(bot_trigger)
