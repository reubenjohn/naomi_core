from contextlib import contextmanager
import json
import os
from typing import Any
from sqlalchemy import DateTime, create_engine, Column, Integer, String, Text, Boolean, func, text
from sqlalchemy.orm import sessionmaker, declarative_base


DB_PATH = os.environ.get("DB_PATH", "sqlite:///db.sqlite")

Base: Any = declarative_base()
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)


class Message(dict[str, str]):
    @staticmethod
    def from_llm_response(assistant_message: str) -> "Message":
        return Message(role="assistant", content=assistant_message)

    @staticmethod
    def from_user_input(prompt: str) -> "Message":
        return Message(role="user", content=prompt)

    @staticmethod
    def from_json(json_str: str) -> "Message":
        return Message(**json.loads(json_str))

    def to_json(self) -> str:
        return json.dumps(self)

    @property
    def body(self) -> str:
        return self["content"]

    @body.setter
    def body(self, value: str) -> None:
        self["content"] = value


DEFAULT_CONVERSATION_ID = 0


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)


class MessageModel(Base):
    __tablename__ = "message"
    conversation_id = Column(Integer, primary_key=True, nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(Text, nullable=False)

    @property
    def payload(self) -> Message:
        return Message.from_json(str(self.content))

    @staticmethod
    def from_llm_response(conversation_id: int, assistant_message: str) -> "MessageModel":
        return MessageModel(
            conversation_id=conversation_id,
            content=Message.from_llm_response(assistant_message).to_json(),
        )


class SummaryModel(Base):
    __tablename__ = "summary"
    conversation_id = Column(Integer, primary_key=True, nullable=False)
    summary_until_id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)


class AgentGoalModel(Base):
    __tablename__ = "agent_goal"
    name = Column(String, primary_key=True, nullable=False)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, nullable=False)
    persistence = Column(Text, nullable=False)


class PropertyModel(Base):
    __tablename__ = "property"
    key = Column(String, primary_key=True, nullable=False)
    value = Column(Text, nullable=False)


class WebhookEvent(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False, server_default="NEW")


# Database setup
def initialize_db():
    Base.metadata.create_all(engine)


# Save message to database
def add_message_to_db(message: Message, session, conversation_id: int) -> MessageModel:
    max_id = (
        session.query(func.max(MessageModel.id))
        .where(MessageModel.conversation_id == conversation_id)
        .scalar()
    )
    if max_id is None:
        max_id = 0
    message_model = MessageModel(
        conversation_id=conversation_id,
        id=max_id + 1,
        content=json.dumps(message),
    )
    session.add(message_model)
    return message_model


def fetch_messages(session, conversation_id) -> list[MessageModel]:
    return (
        session.query(MessageModel)
        .where(MessageModel.conversation_id == conversation_id)
        .order_by(MessageModel.id)
        .all()
    )


def delete_messages_after(session, message: MessageModel):
    session.query(MessageModel).where(
        MessageModel.conversation_id == message.conversation_id
    ).where(MessageModel.id >= message.id).delete()
    session.commit()


def save_agent_goal(goal: AgentGoalModel):
    with session_scope() as session:
        session.add(goal)


def load_goals_from_db() -> list[AgentGoalModel]:
    with session_scope() as session:
        return session.query(AgentGoalModel).order_by(AgentGoalModel.name).all()


def get_all_tables():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table';"))
        return [(name, sql) for name, sql in result]
