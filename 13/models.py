from sqlalchemy import Column, Integer, String, Enum
from database import Base
import enum

class UserRole(enum.Enum):
    USER = 'user'
    ADMIN = 'admin'


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)