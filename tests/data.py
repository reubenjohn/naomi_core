from naomi_core.db.chat import Message, MessageModel
from naomi_core.db.agent import AgentModel, AgentResponsibilityModel


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


def agent_model_1() -> AgentModel:
    return AgentModel(name="TestAgent", prompt="I am a test agent")


def agent_model_2() -> AgentModel:
    return AgentModel(name="AnotherAgent", prompt="I am another agent")


def lead_agent_model() -> AgentModel:
    return AgentModel(name="👑Lead", prompt="You are a helpful assistant.")


def agent_responsibility_1() -> AgentResponsibilityModel:
    return AgentResponsibilityModel(
        agent_name="TestAgent",
        name="TestResponsibility",
        description="This is a test responsibility",
    )


def agent_responsibility_2() -> AgentResponsibilityModel:
    return AgentResponsibilityModel(
        agent_name="TestAgent",
        name="AnotherResponsibility",
        description="This is another test responsibility",
    )
