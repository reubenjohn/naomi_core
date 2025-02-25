from typing import Iterator
import pytest
from naomi_core.assistant.persistence import (
    persist_llm_response,
    generate_and_persist_llm_response,
)
from naomi_core.db import Message, MessageModel
from tests.matchers import assert_message_persisted


@pytest.fixture(scope="function", autouse=True)
def test_db2(test_db):
    _ = test_db


def test_persist_llm_response_without_id(db_session, message1, message2):
    db_session.add(message1)
    db_session.commit()

    # Make sure message.id is None
    message2.id = None
    persist_llm_response(message2, db_session)

    message2.id = message1.id + 1
    assert_message_persisted(message1, db_session)
    assert_message_persisted(message2, db_session)


def test_persist_llm_response_with_id(db_session, persist_messages):
    message1, message2 = persist_messages

    message2.content = Message.from_user_input("ASD").to_json()
    persist_llm_response(message2, db_session)

    assert_message_persisted(message1, db_session)
    assert_message_persisted(message2, db_session)


def collector(chunks: Iterator[str]) -> str:
    return "".join(chunks)


def test_generate_and_persist_llm_response_without_id(db_session, mock_llm_client):
    mock_llm_client.return_value.run.side_effect = lambda *_, **__: iter(["fake_chunk"])
    generate_and_persist_llm_response(
        MessageModel(conversation_id=1, content="{}"), collector, db_session
    )

    saved = db_session.query(MessageModel).first()
    assert saved.payload.body == "fake_chunk", "message is persisted with the updated body"


def test_generate_and_persist_llm_response_with_id(db_session, persist_messages, mock_llm_client):
    mock_llm_client.return_value.run.return_value = iter(["chunk1", "chunk2"])
    message1, _ = persist_messages
    generate_and_persist_llm_response(message1, collector, db_session)

    # Assert that older messages after message1 are deleted and message1 updated
    assert db_session.query(type(message1)).count() == 1
    saved = db_session.query(type(message1)).first()
    assert saved.payload.body is not None
