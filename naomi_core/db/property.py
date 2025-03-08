from sqlalchemy import Column, String, Text

from naomi_core.db.core import Base


class PropertyModel(Base):
    __tablename__ = "property"
    key = Column(String, primary_key=True, nullable=False)
    value = Column(Text, nullable=False)
