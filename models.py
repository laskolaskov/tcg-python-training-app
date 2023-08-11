import json
from sqlalchemy_serializer import SerializerMixin
from typing import List
from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase, SerializerMixin):
    pass


""" book_user_association = Table(
    "student_discipline",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("user_id", Integer, ForeignKey("user.id")),
) """


""" class BookModel(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(Integer)
    count: Mapped[int] = mapped_column(Integer)
    borrowed_by: Mapped[List["UserModel"]] = relationship(
        back_populates="books", secondary=book_user_association
    )

    def __repr__(self) -> str:
        return (
            f"Book(id={self.id!r}, title={self.title!r}, author={self.author!r},"
            f" rating={self.rating!r}, count={self.count!r}, borrowed_by={self.borrowed_by!r})"
        )

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__) """


#    def as_dict(self):
#        return {c.name: getattr(self, c.name) for c in self.__tablename__.columns


#    def __str__(self) -> str:
#        return f"ID: {self.id}\nBook: {self.title}\nAuthor: {self.author}\nISBN: {self.isbn}\n" \
#               f"Available: {self.count}\nRating: {self.rating} stars\n"


class UserModel(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    """ books: Mapped[List["BookModel"]] = relationship(
        back_populates="borrowed_by", secondary=book_user_association
    ) """

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, books={self.books!r})"


class TestModel(Base):
    __tablename__ = "test_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str] = mapped_column(String(255))
    """ books: Mapped[List["BookModel"]] = relationship(
        back_populates="borrowed_by", secondary=book_user_association
    ) """

    def __repr__(self) -> str:
        return f"Test(id={self.id!r}, data={self.data!r})"
