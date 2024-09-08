from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    username: Mapped[str] = mapped_column(unique=True)
    daily_points: Mapped[int] = mapped_column(default=0)

    first_login: Mapped[datetime | None] = mapped_column()
    next_accrual_available: Mapped[datetime | None] = mapped_column()

    boosts: Mapped[list['PlayerBoost']] = relationship(back_populates='player')
    logins: Mapped[list['PlayerLogin']] = relationship(back_populates='player')


class PlayerLogin(Base):
    __tablename__ = 'user_login'

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey('player.id', ondelete='CASCADE'))
    login_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Boost(Base):
    __tablename__ = 'boost'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None] = mapped_column()
    type: Mapped[str] = mapped_column()

    players: Mapped[list['PlayerBoost']] = relationship(back_populates='boost')


class PlayerBoost(Base):
    __tablename__ = 'player_boost'

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id', ondelete='CASCADE'))
    boost_id: Mapped[int] = mapped_column(ForeignKey('boosts.id', ondelete='CASCADE'))
    value: Mapped[float] = mapped_column()
    received_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    player: Mapped['Player'] = relationship(back_populates='boosts')
    boost: Mapped['Boost'] = relationship(back_populates='players')
