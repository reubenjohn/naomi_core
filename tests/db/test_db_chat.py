import json

from naomi_core.db.chat import (
    Message,
    MessageModel,
    delete_messages_after,
    fetch_messages,
    add_message_to_db,
    Conversation,
    SummaryModel,
)

from tests.matchers import assert_message_model


def test_message_from_llm_response():
    assistant_message = "Hello, how can I assist you today?"
    message = Message.from_llm_response(assistant_message)
    assert message["role"] == "assistant"
    assert message["content"] == assistant_message


def test_message_from_user_input():
    user_prompt = "What is the weather like today?"
    message = Message.from_user_input(user_prompt)
    assert message["role"] == "user"
    assert message["content"] == user_prompt


def test_message_from_json():
    json_str = '{"role": "user", "content": "What is the weather like today?"}'
    message = Message.from_json(json_str)
    assert message["role"] == "user"
    assert message["content"] == "What is the weather like today?"


def test_message_to_json():
    message = Message(role="assistant", content="Hello, how can I assist you today?")
    json_str = message.to_json()
    expected_json_str = '{"role": "assistant", "content": "Hello, how can I assist you today?"}'
    assert json.loads(json_str) == json.loads(expected_json_str)


def test_message_body_property():
    message = Message(role="assistant", content="Hello, how can I assist you today?")
    assert message.body == "Hello, how can I assist you today?"
    message.body = "New content"
    assert message.body == "New content"
    assert message["content"] == "New content"


def test_add_message(db_session, message_data: Message):
    result = add_message_to_db(message_data, db_session, conversation_id=1)
    db_session.commit()
    assert result.id == 1
    assert result.payload == message_data
    saved_message = db_session.query(MessageModel).filter_by(id=1).one()
    assert saved_message.payload == message_data


def test_message_content_functions(db_session, message_data: Message):
    message = MessageModel(conversation_id=1, id=1, content=json.dumps(message_data))
    db_session.add(message)
    db_session.commit()
    saved_message = db_session.query(MessageModel).filter_by(id=1).one()
    assert saved_message.payload == message_data


def test_message_model_from_llm_response(db_session):
    assistant_message = "Hello, how can I assist you today?"
    actual = MessageModel.from_llm_response(conversation_id=1, assistant_message=assistant_message)
    expected = MessageModel(
        conversation_id=1,
        content=Message.from_llm_response(assistant_message).to_json(),
    )

    assert_message_model(actual, expected)


def test_fetch_messages(db_session, persist_messages):
    message1, message2 = persist_messages
    messages = fetch_messages(db_session, conversation_id=1)
    assert len(messages) == 2
    assert messages[0] == message1
    assert messages[1] == message2


def test_delete_messages(
    db_session, persist_messages, message2: MessageModel, message_data: Message
):
    delete_messages_after(db_session, message2)
    messages = fetch_messages(db_session, conversation_id=1)
    assert len(messages) == 1
    assert messages[0].payload == message_data


def test_create_conversation_model(db_session):
    convo = Conversation(name="TestConvo", description="A test conversation")
    db_session.add(convo)
    db_session.commit()

    saved_convo = db_session.query(Conversation).filter_by(name="TestConvo").one()
    assert saved_convo.description == "A test conversation"


def test_create_summary_model(db_session):
    summary = SummaryModel(conversation_id=42, summary_until_id=1, content="Summarized content")
    db_session.add(summary)
    db_session.commit()

    saved_summary = db_session.query(SummaryModel).filter_by(conversation_id=42).one()
    assert saved_summary.content == "Summarized content"
