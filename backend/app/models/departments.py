from app.config.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Departments(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

    users = relationship("Users", back_populates="department", cascade="all, delete-orphan")
