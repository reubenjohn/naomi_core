from sqlalchemy import Column, DateTime, Integer, String, Text, func

from naomi_core.db.core import Base


class WebhookEvent(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False, server_default="NEW")
