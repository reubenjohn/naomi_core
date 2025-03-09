from unittest.mock import patch

from naomi_core.db.core import Base, initialize_db, session_scope, get_all_tables, wipe_db
from naomi_core.db.chat import Conversation
from naomi_core.db.agent import AgentModel

from tests.conftest import engine, TestingSessionLocal


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
