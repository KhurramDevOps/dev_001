from sqlalchemy import Column, String, Integer
from ..db.database import Base, engine
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    class config:
        orm_mode = True
Base.metadata.create_all(bind=engine)