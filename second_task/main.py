import csv
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from second_task.models import Base, Level, LevelPrize, Player, PlayerLevel, Prize


def assign_prizes_to_player(session: Session, player_id: str, level_id: int, prize_ids: list[int]) -> list[LevelPrize]:
    """
    Присваивает призы игроку за прохождение уровня.

    :param session: Активная сессия SQLAlchemy
    :param player_id: Идентификатор игрока
    :param level_id: Идентификатор уровня
    :param prize_ids: Список идентификаторов призов

    :raise ValueError: Если игрок или уровень не найдены

    :return: Список присвоенных призов
    """
    # Получаем запись о прохождении уровня игроком
    player_level = session.execute(
        select(PlayerLevel)
        .where(
            PlayerLevel.player_id == player_id,
            PlayerLevel.level_id == level_id
        )
    ).scalar_one_or_none()

    if player_level is None:
        raise ValueError("PlayerLevel не найден")

    # Проверяем, что уровень уже пройден
    if not player_level.is_completed:
        raise ValueError("Игрок ещё не прошёл уровень")

    level_prizes = list()
    for i, prize_id in enumerate(prize_ids, start=1):
        # Создаём запись о призе за уровень
        level_prize = LevelPrize(
            id=i,
            prize_id=prize_id,
            player_level_id=player_level.id,
            received_at=datetime.utcnow()
        )
        level_prizes.append(level_prize)

    session.add_all(level_prizes)

    # Сохраняем изменения в базе данных
    session.commit()

    return level_prizes


def test_flow(session: Session):
    # У нас есть уровень
    level = Level(id=1, title='Level 1')
    session.add(level)

    # Появляется пользователь
    player = Player(id='super_unique_id')
    session.add(player)

    # Пользователь начинает проходить уровень
    player_level = PlayerLevel(
        id=1,
        player_id=player.id,
        level_id=level.id,
    )
    session.add(player_level)

    session.commit()

    # Пользователь проходит уровень
    player_level.complete()

    session.commit()

    # Для него генерируются классные призы за этот уровень
    prize_1 = Prize(id=1, title='Prize 1')
    prize_2 = Prize(id=2, title='Prize 2')

    session.add_all((prize_1, prize_2))

    # Призы присваиваются игроку
    prizes =assign_prizes_to_player(
        session=session,
        player_id=player.id,
        level_id=level.id,
        prize_ids=[prize_1.id, prize_2.id],
    )

    # Пользователь забирает свои призы
    for prize in prizes:
        prize.receive()

    session.commit()

    # Пользователь рад своим призам)


def export_player_levels_to_csv(session: Session, file_path: str, chunk_size: int = 1000) -> str:
    """
    Функция для экспорта данных игроков, уровней и призов в CSV.

    :param session: Активная сессия SQLAlchemy
    :param file_path: Путь к CSV файлу
    :param chunk_size: Размер чанка данных

    :return: Путь к CSV файлу
    """
    # Открываем файл для записи
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Записываем заголовки CSV
        csv_writer.writerow(['player_id', 'level_title', 'is_completed', 'prize_title'])

        # В запросе получаем только нужные столбцы
        stmt = (
            select(
                Player.id,
                Level.title,
                PlayerLevel.is_completed,
                Prize.title,
            )
            .join(PlayerLevel, Player.id == PlayerLevel.player_id)
            .join(Level, PlayerLevel.level_id == Level.id)
            .outerjoin(LevelPrize, PlayerLevel.id == LevelPrize.player_level_id)
            .outerjoin(Prize, LevelPrize.prize_id == Prize.id)
            .order_by(Player.id)
        )

        # Загружаем данные по частям
        for row in session.execute(stmt).yield_per(chunk_size):
            player_id, level_title, is_completed, prize_title = row
            csv_writer.writerow([player_id, level_title, is_completed, prize_title or 'No Prize'])

    return file_path


def main():
    engine = create_engine("sqlite:///test.db")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        test_flow(session)
        export_player_levels_to_csv(session, 'player_levels.csv')


if __name__ == '__main__':
    main()
