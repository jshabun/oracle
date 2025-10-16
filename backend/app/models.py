from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    yahoo_sub = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tokens = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan")

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, default="yahoo")
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    extra = Column(JSON, default={})
    user = relationship("User", back_populates="tokens")

class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True)
    yahoo_league_key = Column(String, unique=True, index=True)
    name = Column(String)
    season = Column(String)
    scoring_type = Column(String)
    roster_positions = Column(JSON, default={})

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    yahoo_player_key = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    positions = Column(JSON, default=list)
    nba_team = Column(String)
    status = Column(String)

class PlayerStats(Base):
    __tablename__ = "player_stats"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), index=True)
    period = Column(String)  # ros|weekly|daily
    stats = Column(JSON, default={})
    source = Column(String, default="yahoo")
    as_of = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('player_id','period','as_of', name='uq_player_period_asof'),)