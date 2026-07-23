from sqlalchemy import  Column, Integer, String, ForeignKey, Text, DateTime,Boolean
from sqlalchemy.orm import relationship
import datetime

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    email = Column(String)
    password = Column(String)
    type = Column(String, default="user")
    profile_pic = Column(
        String, 
        nullable=True, 
    default="",
    server_default=""
    )
    
    phone = Column(String, nullable=True, default="Not set")
    address = Column(String, nullable=True, default="Not set")
    # "July 21, 2026"
    member_since = Column(String, default=lambda: datetime.datetime.now().strftime("%B %d, %Y")) 
    is_active = Column(Boolean, default=False)


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(Text)
    filename = Column(String)
    likes = Column(Integer, default=0)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    uploader = relationship("User")


class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")
