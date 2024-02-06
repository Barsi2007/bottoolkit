from abc import ABC
from dataclasses import dataclass
from typing import Optional

from aiohttp import web
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
from loguru import logger

from bottoolkit.bot_worker import BotWorker
from bottoolkit.conversation_state import BotConversationState


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


@dataclass
class Middleware:
    spawn: callable
    ingest: callable
    send: callable
    receive: callable
    interpret: callable


class Bot:
    _events: dict[list]
    _triggers: dict[list[BotTrigger]]
    _interrupts: dict[list[BotTrigger]]
    _conversation_state: BotConversationState
    _dependencies: dict
    _boot_complete_handlers: list[callable]

    version: str
    middleware = Middleware
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

        self.webserver = web.Application()

        if self.webserver:
            self.configure_webhook()

    async def process_incoming_message(self, request: web.Request):
        """ """
        self.adapter.process_activity(request, await self.handle_turn(self))
        return web.Response(status=200)

    def configure_webhook(self):
        """ """
        self.webserver.add_routes([web.post(self.webhook_uri, self.process_incoming_message)])

    async def handle_turn(self, turn_context: TurnContext):
        """ """

        message = BotMessage(
            type=None,
            user=turn_context.activity.from_dict["id"],
            text=turn_context.activity.from_dict["text"],
            channel=turn_context.activity.conversation.id,
            value=turn_context.activity.value,
            reference=TurnContext.get_conversation_reference(turn_context.activity),
            incoming_message=turn_context.activity,
        )

        turn_context.turn_state["botKitMessage", message]

        dialog_context = await self.dialog_set.create_context(turn_context=turn_context)

        bot_worker = await self.spawn(dialog_context)

        return ...

    async def _process_trigger_and_events(self, bot_worker: BotWorker, message: BotMessage):
        """ """
        listen_results = await self._listen_for_triggers()

        if listen_results:
            trigger_results = await self.trigger(message.type, bot_worker, message)

    async def trigger(self, event: str, bot_worker: BotWorker, message: BotMessage):
        """ """
        if event in self._events:
            for ev in self._events[event]:
                handler_result = await ev(bot_worker, bot_worker, message)

                if handler_result:
                    break

    async def _listen_for_triggers(self, bot_worker: BotWorker, message: BotMessage):
        """ """
        if message.type in self._triggers:
            triggers = self._triggers[message.type]

            for trigger in triggers:
                test_results = await self._test_trigger(trigger)

                if test_results:
                    trigger_results = await trigger.handler(self, bot_worker, message)
                    return trigger_results

        return False

    async def _test_trigger(self, trigger: BotTrigger, message: BotMessage):
        """ """
        return True

    def run(self):
        web.run_app(self.webserver)

    async def ready(self, handler: callable) -> None:
        """ """

        if self.booted:
            handler(self)
        else:
            self._boot_complete_handlers.append(handler)

    async def hears(self, pattern: str, event: str, handler: callable) -> None:

        bot_trigger = BotTrigger(type=None, pattern=pattern, handler=handler)

        if not event in self._triggers:
            self._triggers = []

        self._triggers[event].append(bot_trigger)

    async def on(self, event: str, handler: callable):

        if not event in self._events:
            self._events[event] = []

        self._events[event] = handler

    async def spawn(
        self, config: TurnContext | DialogContext, custom_adapter: BotAdapter
    ) -> BotWorker:
        """ """
        _config = dict()

        if isinstance(config, TurnContext):
            config
