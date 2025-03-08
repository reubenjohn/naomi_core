import logging
from typing import Iterator, Optional

from llm.llm import handle_base_model_arg, llm_client
from llm.stream_processing import MessageStream, ToolStream, parse_streaming_response
from swarm import Agent  # type: ignore[import]

from naomi_core.db import Message


def generate_llm_response(messages: list[Message], model: Optional[str] = None) -> Iterator[str]:
    model = handle_base_model_arg(model)
    agent = Agent(
        name="Creative Assistant",
        model=model,
        instructions="You are a helpful assistant.",
        stream=True,
    )
    return llm_client().run(agent, messages, stream=True)


def process_llm_response(chunks) -> Iterator[str]:
    for stream in parse_streaming_response(chunks):
        if isinstance(stream, MessageStream):
            for chunk in stream.content_stream:
                yield chunk
        elif isinstance(stream, ToolStream):
            logging.debug(f"Tool Use: {stream}")
    logging.info("Response generation complete")
