from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

metadata = MetaData()

Base = declarative_base(metadata=metadata)


class Model(Base):
    __tablename__ = "models"
    uid = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    key = Column(String)
    value = Column(String)
