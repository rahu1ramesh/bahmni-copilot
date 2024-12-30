from app.config.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Providers(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=True, default="General Medicine")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("Users", back_populates="providers")
    department = relationship("Departments", back_populates="providers")
