from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Car(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    url: str = Field(unique=True, index=True)
    price: str = Field()
    post_id: int = Field(unique=True)
    images: list["CarImage"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"}, back_populates="car"
    )


class CarImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    path: str = Field(unique=True)
    car_id: Optional[int] = Field(default=None, foreign_key="car.id")
    car: Optional[Car] = Relationship(back_populates="images")
