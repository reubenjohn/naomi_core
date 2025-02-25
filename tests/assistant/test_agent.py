from unittest.mock import patch
from llm.stream_processing import MessageStream, ToolStream
from swarm import Agent  # type: ignore[import]

from naomi_core.assistant.agent import generate_llm_response, process_llm_response
from tests.matchers import InstanceOf


def test_generate_llm_response(mock_llm_client):
    mock_llm_client_instance = mock_llm_client.return_value
    mock_llm_client_instance.run.return_value = iter(["response_chunk_1", "response_chunk_2"])

    messages = [{"role": "user", "content": "Hello"}]
    response = list(generate_llm_response(messages, model="test-model"))

    assert response == ["response_chunk_1", "response_chunk_2"]
    mock_llm_client_instance.run.assert_called_once_with(InstanceOf(Agent), messages, stream=True)


@patch("naomi_core.assistant.agent.parse_streaming_response")
def test_process_llm_response(mock_parse_streaming_response):
    chunks = [
        MessageStream(
            sender="assistant",
            role="assistant",
            content_stream=iter(["message_chunk_1", "message_chunk_2"]),
        ),
        ToolStream(sender="system", tool_name="search"),
    ]
    mock_parse_streaming_response.return_value = chunks

    processed_chunks = list(process_llm_response(chunks))

    assert processed_chunks == ["message_chunk_1", "message_chunk_2"]
    mock_parse_streaming_response.assert_called_once_with(chunks)
