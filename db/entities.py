from sqlalchemy.orm import relationship, backref, joinedload
from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey, func, UniqueConstraint

from db.base import Base, inverse_relationship, create_tables 

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Show(Base):
    __tablename__ = 'shows'
    id = Column(Integer, primary_key=True)

    title = Column(String)
    image_url = Column(String)
    api_id = Column(String, unique=True)

    created_at = Column(DateTime, default=func.now())
    update_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key = True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, backref=inverse_relationship('likes_shows'))

    show_id = Column(Integer, ForeignKey('shows.id'))
    show = relationship(Show, backref=inverse_relationship('has_followers'))

    uid_to_sid = Column(String, unique=True)    

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
