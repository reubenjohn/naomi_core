from unittest.mock import patch
from contextlib import contextmanager

from naomi_core.db.agent import (
    AgentModel,
    get_all_agents,
    get_lead_agent,
    save_responsibility,
    load_responsibilities_from_db,
    LEAD_DEFAULT_PROMPT,
)


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
