from sqlalchemy.orm import selectinload
from sqlmodel import Session, SQLModel, create_engine, select

from db.models import Car, CarImage


sqlite_filename = "database.db"
sqlite_url = f"sqlite:///{sqlite_filename}"

engine = create_engine(sqlite_url)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def insert_car(json_data: dict[str, str | list]) -> None:
    with Session(engine) as session:
        statement = select(Car).where(Car.url == json_data["url"])
        car_in_db = session.exec(statement).first()
        if car_in_db:
            return

        car = Car(
            name=json_data["name"],
            url=json_data["url"],
            price=json_data["price"],
            post_id=json_data["post_id"],
        )

        for path in json_data["images"]:
            car_image = CarImage(path=path, car=car)
            session.add(car_image)
        session.commit()


def insert_cars(cars: list[dict[str, str | list]]) -> None:
    for car in cars:
        insert_car(car)


def get_all_cars() -> list[Car]:
    with Session(engine) as session:
        statement = select(Car).options(selectinload(Car.images))
        return session.exec(statement).all()


def get_all_urls() -> list[str]:
    with Session(engine) as session:
        statement = select(Car.url)
        return session.exec(statement).all()


def get_car_by_url(url: str) -> Car:
    with Session(engine) as session:
        statement = select(Car).where(Car.url == url).options(selectinload(Car.images))
        return session.exec(statement).first()


def update_price_by_url(url: str, new_price: str) -> None:
    with Session(engine) as session:
        statement = select(Car).where(Car.url == url)
        car = session.exec(statement).first()
        if car:
            car.price = new_price
            session.add(car)
            session.commit()


def delete_car_by_url(url: str) -> None:
    with Session(engine) as session:
        statement = select(Car).where(Car.url == url)
        car = session.exec(statement).first()
        if car:
            session.delete(car)
            session.commit()
