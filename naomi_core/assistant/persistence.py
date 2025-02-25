import logging
from typing import Callable, Iterator

from sqlalchemy import Column

from naomi_core.assistant.agent import generate_llm_response, process_llm_response
from naomi_core.db import (
    MessageModel,
    add_message_to_db,
    delete_messages_after,
    fetch_messages,
)


def persist_llm_response(message: MessageModel, session):
    """
    Persists an LLM response, optionally deleting messages after the current ID if it exists.
    """
    payload = message.payload
    logging.debug(f"Persisting AI response: {payload.body}")
    if message.id is not None:
        delete_messages_after(session, message)
    add_message_to_db(message.payload, session, int(message.conversation_id))
    session.commit()


def generate_and_persist_llm_response(
    message: MessageModel,
    stream_collector: Callable[[Iterator[str]], str],
    session,
):
    """
    Generates an LLM response, processes it, and persists the updated message.
    """
    messages = [msg.payload for msg in fetch_messages(session, int(message.conversation_id))]
    response = generate_llm_response(messages)
    chunks = process_llm_response(response)
    payload = message.payload
    response_text = stream_collector(chunks)
    payload.body = response_text
    message.content = Column[str](payload.to_json())
    persist_llm_response(message, session)
