from contextlib import contextmanager
import os
from typing import Iterator
from unittest.mock import patch
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from naomi_core.db.chat import (
    Base,
    Message,
    MessageModel,
)
from naomi_core.db.agent import AgentModel, AgentResponsibilityModel
from naomi_core.db.core import get_all_tables
from tests.data import (
    message_data_1,
    message_data_2,
    message_model_1,
    message_model_2,
    agent_model_1,
    agent_model_2,
    lead_agent_model,
    agent_responsibility_1,
    agent_responsibility_2,
)

os.environ["OPENAI_BASE_URL"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_MODEL"] = ""


TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def in_memory_session():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    InMemorySession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield InMemorySession()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Creates a new database for each test case."""

    with patch("naomi_core.db.core.engine", new_callable=lambda: engine):
        Base.metadata.drop_all(bind=engine)
        assert get_all_tables() == []

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

    with patch("naomi_core.db.core.engine", new_callable=lambda: engine):
        assert get_all_tables() == []


@pytest.fixture(scope="function")
def db_session(test_db):
    session = TestingSessionLocal()

    @contextmanager
    def mock_session_scope():
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    with patch("naomi_core.db.core.session_scope", side_effect=mock_session_scope):
        yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def message_data() -> Message:
    return message_data_1()


@pytest.fixture(scope="function")
def message_data2() -> Message:
    return message_data_2()


@pytest.fixture(scope="function")
def message1() -> MessageModel:
    return message_model_1()


@pytest.fixture(scope="function")
def message2() -> MessageModel:
    return message_model_2()


@pytest.fixture(scope="function")
def persist_messages(db_session, message1: MessageModel, message2: MessageModel):
    db_session.add(message1)
    db_session.add(message2)
    db_session.commit()
    return message1, message2


@pytest.fixture(scope="function")
def test_agent() -> AgentModel:
    return agent_model_1()


@pytest.fixture(scope="function")
def another_agent() -> AgentModel:
    return agent_model_2()


@pytest.fixture(scope="function")
def test_lead_agent() -> AgentModel:
    return lead_agent_model()


@pytest.fixture(scope="function")
def test_responsibility() -> AgentResponsibilityModel:
    return agent_responsibility_1()


@pytest.fixture(scope="function")
def another_responsibility() -> AgentResponsibilityModel:
    return agent_responsibility_2()


@pytest.fixture(scope="function")
def persist_agent(db_session, test_agent):
    db_session.add(test_agent)
    db_session.commit()
    return test_agent


@pytest.fixture(scope="function")
def persist_agents(db_session, test_agent, another_agent):
    db_session.add(test_agent)
    db_session.add(another_agent)
    db_session.commit()
    return test_agent, another_agent


@pytest.fixture(scope="function")
def persist_responsibilities(
    db_session, persist_agent, test_responsibility, another_responsibility
):
    db_session.add(test_responsibility)
    db_session.add(another_responsibility)
    db_session.commit()
    return test_responsibility, another_responsibility


@pytest.fixture
def mock_llm_client():
    with patch("naomi_core.assistant.agent.llm_client") as mock:
        yield mock


def pass_thru_process_llm_response(chunks: Iterator[str]) -> Iterator[str]:
    return chunks


@pytest.fixture(scope="function", autouse=True)
def patch_process_llm_response():
    with patch(
        "naomi_core.assistant.persistence.process_llm_response",
        side_effect=pass_thru_process_llm_response,
    ):
        yield
