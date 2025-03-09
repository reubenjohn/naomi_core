from sqlalchemy import Column, ForeignKey, String, Text

from naomi_core.db.core import Base


class AgentModel(Base):
    __tablename__ = "agent"
    name = Column(String, primary_key=True, nullable=False)
    prompt = Column(Text, nullable=False)


class AgentResponsibilityModel(Base):
    __tablename__ = "agent_responsibility"
    agent_name = Column(String, ForeignKey("agent.name"), primary_key=True, nullable=False)
    name = Column(String, primary_key=True, nullable=False)
    description = Column(Text, nullable=False)


LEAD_DEFAULT_PROMPT = "You are a helpful assistant."


def get_all_agents(session) -> list[AgentModel]:
    agents = session.query(AgentModel).all()
    agent_names = {agent.name for agent in agents}
    if "👑Lead" not in agent_names:
        lead_agent = get_lead_agent(session)
        agents.append(lead_agent)
    return agents


def get_lead_agent(session) -> AgentModel:
    lead_agent = session.query(AgentModel).first()
    if not lead_agent:
        lead_agent = AgentModel(name="👑Lead", prompt=LEAD_DEFAULT_PROMPT)
        session.add(lead_agent)
        session.commit()
    return lead_agent


def save_responsibility(goal: AgentResponsibilityModel):
    from naomi_core.db.core import session_scope

    with session_scope() as session:
        session.add(goal)


def load_responsibilities_from_db(agent: AgentModel, session) -> list[AgentResponsibilityModel]:
    return (
        session.query(AgentResponsibilityModel)
        .filter_by(agent_name=agent.name)
        .order_by(AgentResponsibilityModel.name)
        .all()
    )
