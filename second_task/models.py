from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'

    id: Mapped[str] = mapped_column(String(length=100), primary_key=True)

    levels: Mapped[list['PlayerLevel']] = relationship(back_populates='player')


class Level(Base):
    __tablename__ = 'level'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(length=100))
    order: Mapped[int] = mapped_column(default=0)

    players: Mapped[list['PlayerLevel']] = relationship(back_populates='level')


class Prize(Base):
    __tablename__ = 'prize'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()

    levels: Mapped[list['LevelPrize']] = relationship(back_populates='prize')


class PlayerLevel(Base):
    __tablename__ = 'player_level'

    id: Mapped[int] = mapped_column(primary_key=True)

    player_id: Mapped[str] = mapped_column(ForeignKey('player.id', ondelete='CASCADE'))
    level_id: Mapped[int] = mapped_column(ForeignKey('level.id', ondelete='CASCADE'))
    completed_at: Mapped[datetime | None] = mapped_column(default=None)
    is_completed: Mapped[bool] = mapped_column(default=False)
    score: Mapped[int] = mapped_column(default=0)

    player: Mapped['Player'] = relationship(back_populates='levels')
    level: Mapped['Level'] = relationship(back_populates='players')
    prizes: Mapped[list['LevelPrize']] = relationship(back_populates='level')

    def complete(self):
        self.completed_at = datetime.utcnow()
        self.is_completed = True


class LevelPrize(Base):
    __tablename__ = 'level_prize'

    id: Mapped[int] = mapped_column(primary_key=True)

    prize_id: Mapped[int] = mapped_column(ForeignKey('prize.id', ondelete='CASCADE'))
    player_level_id: Mapped[int] = mapped_column(ForeignKey('player_level.id', ondelete='CASCADE'))
    received_at: Mapped[datetime | None] = mapped_column()
    is_received: Mapped[bool] = mapped_column(default=False)

    prize: Mapped['Prize'] = relationship(back_populates='levels')
    level: Mapped['PlayerLevel'] = relationship(back_populates='prizes')

    def receive(self):
        self.received_at = datetime.utcnow()
        self.is_received = True
