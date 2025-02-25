from naomi_core.db import Message, MessageModel


def message_data_1() -> Message:
    return Message(content="Hello, NAOMI!", role="user")


def message_data_2() -> Message:
    return Message(content="How are you?", role="assistant")


def message_data_3() -> Message:
    return Message(content="I'm good!", role="user")


def message_model_1() -> MessageModel:
    return MessageModel(conversation_id=1, id=1, content=message_data_1().to_json())


def message_model_2() -> MessageModel:
    return MessageModel(conversation_id=1, id=2, content=message_data_2().to_json())


def message_model_3() -> MessageModel:
    return MessageModel(conversation_id=1, id=3, content=message_data_3().to_json())
