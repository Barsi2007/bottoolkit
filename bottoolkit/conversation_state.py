from botbuilder.core import ConversationState
from botbuilder.core import TurnContext
from botbuilder.schema import Activity


class BotConversationState(ConversationState):
    def get_storage_key(self, turn_context: TurnContext) -> str:
        """ """

        activity = turn_context.activity
        channel_id = turn_context.channel_id

        if not activity.conversation or activity.conversation.id:
            raise Exception("missing activity.conversation")

        return f"{channel_id}/conversations/{activity.conversation.id}"
