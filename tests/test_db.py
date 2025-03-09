import json
from contextlib import contextmanager
from unittest.mock import patch
from naomi_core.db.core import Base, initialize_db, session_scope, get_all_tables, wipe_db
from naomi_core.db.chat import (
    Message,
    MessageModel,
    delete_messages_after,
    fetch_messages,
    add_message_to_db,
    Conversation,
    SummaryModel,
)
from naomi_core.db.agent import (
    AgentModel,
    AgentResponsibilityModel,
    get_all_agents,
    get_lead_agent,
    save_responsibility,
    load_responsibilities_from_db,
    LEAD_DEFAULT_PROMPT,
)
from naomi_core.db.property import PropertyModel

from tests.conftest import engine, TestingSessionLocal
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


@patch("naomi_core.db.core.engine", new_callable=lambda: engine)
def test_initialize_db_and_get_all_tables(_):
    Base.metadata.drop_all(bind=engine)
    assert [] == get_all_tables()
    initialize_db()
    assert {
        "conversation",
        "message",
        "summary",
        "agent",
        "agent_responsibility",
        "property",
        "event",
    } == {t[0] for t in get_all_tables()}


def test_wipe_db(db_session):
    # First initialize the database with patched engine
    with patch("naomi_core.db.core.engine", new_callable=lambda: engine):
        # Initialize
        initialize_db()
        assert len(get_all_tables()) > 0

        # Add some data
        agent = AgentModel(name="TestAgent", prompt="Test prompt")
        db_session.add(agent)
        db_session.commit()

        # Now wipe the database and check it reinitializes correctly
        wipe_db()

        # Verify tables exist but previous data is gone
        agent_count = db_session.query(AgentModel).count()
        assert agent_count == 0

        # Verify all tables still exist
        tables = {t[0] for t in get_all_tables()}
        assert "agent" in tables
        assert "agent_responsibility" in tables


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


def test_agent_model_and_get_lead_agent(db_session):
    # Test get_lead_agent with empty DB
    lead_agent = get_lead_agent(db_session)
    assert lead_agent.name == "👑Lead"
    assert lead_agent.prompt == LEAD_DEFAULT_PROMPT

    # Verify that lead agent was saved to DB
    saved_agent = db_session.query(AgentModel).filter_by(name="👑Lead").one()
    assert saved_agent.name == "👑Lead"
    assert saved_agent.prompt == LEAD_DEFAULT_PROMPT

    # Update lead agent prompt
    lead_agent.prompt = "Updated prompt"
    db_session.commit()

    # Verify updated prompt is retrieved
    updated_lead = get_lead_agent(db_session)
    assert updated_lead.prompt == "Updated prompt"


def test_get_all_agents_empty_db(db_session):
    # Test with empty DB - should create lead agent
    agents = get_all_agents(db_session)
    assert len(agents) == 1
    assert agents[0].name == "👑Lead"


def test_get_all_agents_with_existing_agents(db_session, persist_agents):
    test_agent, another_agent = persist_agents

    # Add lead agent explicitly
    lead_agent = AgentModel(name="👑Lead", prompt="I am the lead")
    db_session.add(lead_agent)
    db_session.commit()

    # Test with existing agents
    agents = get_all_agents(db_session)
    assert len(agents) == 3
    agent_names = {agent.name for agent in agents}
    assert "👑Lead" in agent_names
    assert test_agent.name in agent_names
    assert another_agent.name in agent_names


def test_save_and_load_responsibilities_empty(db_session, persist_agent):
    # Test load with empty DB
    responsibilities = load_responsibilities_from_db(persist_agent, db_session)
    assert len(responsibilities) == 0


def test_save_responsibility(db_session, test_agent, test_responsibility):
    # Add the agent directly to the session
    db_session.add(test_agent)
    db_session.commit()

    # Use mocked session scope for save_responsibility
    with patch("naomi_core.db.core.session_scope") as mock_scope:

        @contextmanager
        def mock_session_fn():
            try:
                yield db_session
                db_session.commit()
            except Exception:
                db_session.rollback()
                raise

        mock_scope.side_effect = mock_session_fn

        # Add a responsibility
        save_responsibility(test_responsibility)

    # Verify responsibility was saved
    responsibilities = load_responsibilities_from_db(test_agent, db_session)
    assert len(responsibilities) == 1
    assert responsibilities[0].name == test_responsibility.name
    assert responsibilities[0].description == test_responsibility.description


def test_load_responsibilities_ordering(db_session, persist_agent, persist_responsibilities):
    test_responsibility, another_responsibility = persist_responsibilities

    # Verify both responsibilities are returned in correct order
    responsibilities = load_responsibilities_from_db(persist_agent, db_session)
    assert len(responsibilities) == 2

    # In alphabetical order
    assert responsibilities[0].name == another_responsibility.name
    assert responsibilities[1].name == test_responsibility.name


def test_create_and_query_models(db_session):
    convo = Conversation(name="TestConvo", description="A test conversation")
    db_session.add(convo)
    summary = SummaryModel(conversation_id=42, summary_until_id=1, content="Summarized content")
    db_session.add(summary)
    prop = PropertyModel(key="testKey", value="testValue")
    db_session.add(prop)
    db_session.commit()

    saved_convo = db_session.query(Conversation).filter_by(name="TestConvo").one()
    assert saved_convo.description == "A test conversation"
    saved_summary = db_session.query(SummaryModel).filter_by(conversation_id=42).one()
    assert saved_summary.content == "Summarized content"
    saved_prop = db_session.query(PropertyModel).filter_by(key="testKey").one()
    assert saved_prop.value == "testValue"


@patch("naomi_core.db.core.Session", new_callable=lambda: TestingSessionLocal)
def test_session_scope(mock_session):
    with session_scope() as session:
        assert session is not None
        assert isinstance(session, type(mock_session()))
        # Perform some operations to ensure session is working
        convo = Conversation(name="TestConvo", description="A test conversation")
        session.add(convo)
        session.commit()
        saved_convo = session.query(Conversation).filter_by(name="TestConvo").one()
        assert saved_convo.description == "A test conversation"


@patch("naomi_core.db.core.Session", new_callable=lambda: TestingSessionLocal)
def test_session_scope_commit(mock_session, db_session):
    with session_scope() as session:
        assert session is not None
        assert isinstance(session, type(mock_session()))
        convo = Conversation(name="TestConvo", description="A test conversation")
        session.add(convo)
    saved_convo = db_session.query(Conversation).filter_by(name="TestConvo").one()
    assert saved_convo.description == "A test conversation"


@patch("naomi_core.db.core.Session", new_callable=lambda: TestingSessionLocal)
def test_session_scope_rollback(mock_session):
    try:
        with session_scope() as session:
            assert session is not None
            assert isinstance(session, type(mock_session()))
            convo = Conversation(name="TestConvo", description="A test conversation")
            session.add(convo)
            raise Exception("Force rollback")
    except Exception:
        pass
    # assert session.is_active is False  # Ensure session is closed
    with session_scope() as session:
        saved_convo = session.query(Conversation).filter_by(name="TestConvo").first()
        assert saved_convo is None  # Ensure rollback occurred
