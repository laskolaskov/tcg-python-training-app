import json
from sqlalchemy_serializer import SerializerMixin
from typing import List
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase, SerializerMixin):
    pass


class UserModel(Base):
    __tablename__ = "myusers"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(70), unique=True)
    password: Mapped[str] = mapped_column(String())
    is_admin: Mapped[bool] = mapped_column(Boolean())
    credits: Mapped[int] = mapped_column(Integer())
    collections: Mapped[List["CollectionModel"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, credits={self.credits}, is_admin={self.is_admin!r}), collections={self.collections}"


class CardModel(Base):
    __tablename__ = "card"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    url: Mapped[str] = mapped_column(Text())
    data: Mapped[str] = mapped_column(Text())
    collections: Mapped[List["CollectionModel"]] = relationship(back_populates="card")

    def __repr__(self) -> str:
        return f"Card(id={self.id!r}, name={self.name}, url={self.url!r})"


class CollectionModel(Base):
    __tablename__ = "collection"
    user_id: Mapped[int] = mapped_column(ForeignKey("myusers.id"), primary_key=True)
    user: Mapped["UserModel"] = relationship(back_populates="collections")
    card_id: Mapped[int] = mapped_column(ForeignKey("card.id"), primary_key=True)
    card: Mapped["CardModel"] = relationship(back_populates="collections")
    count: Mapped[int] = mapped_column(Integer())
    price: Mapped[int] = mapped_column(Integer())
    is_marketed: Mapped[bool] = mapped_column(Boolean())

    def __repr__(self) -> str:
        return f"Collection(user={self.user.username}, card={self.card.name!r}, count={self.count!r}, price={self.price!r}, is_marketed={self.is_marketed!r})"
