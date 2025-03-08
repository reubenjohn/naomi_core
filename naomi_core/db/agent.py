from naomi_core.db.core import Base


from sqlalchemy import Boolean, Column, String, Text


class AgentGoalModel(Base):
    __tablename__ = "agent_goal"
    name = Column(String, primary_key=True, nullable=False)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, nullable=False)
    persistence = Column(Text, nullable=False)


def save_agent_goal(goal: AgentGoalModel):
    from naomi_core.db.core import session_scope

    with session_scope() as session:
        session.add(goal)


def load_goals_from_db(session) -> list[AgentGoalModel]:
    return session.query(AgentGoalModel).order_by(AgentGoalModel.name).all()
