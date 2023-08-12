from models import Base, UserModel
from sqlalchemy import (
    create_engine,
    select,
    insert,
    Select,
    Result,
    ScalarResult,
    Engine,
    Insert,
)
from sqlalchemy.orm import Session


class Database:
    session: Session
    engine: Engine

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.session = Session(self.engine)

    def __del__(self):
        self.session.close()
        self.engine.dispose()

    def db_test(self):
        return self.engine.connect()

    def init_db(self):
        """data = [
            BookModel(
                title="Test Book 1", author="John Doe", rating=10, isbn=111234, count=2
            ),
            BookModel(
                title="Test Book 2", author="John Doe", rating=7, isbn=22255, count=15
            ),
            BookModel(
                title="Test Book 6", author="Jane Doe", rating=9, isbn=666, count=6
            ),
            UserModel(username="lasko.laskov"),
            UserModel(username="test.user"),
        ]"""

        Base.metadata.create_all(self.engine)
        # self.session.add_all(data)
        # self.session.commit()

    def getUserByName(self, name: str) -> UserModel:
        stmt: Select = select(UserModel).where(UserModel.username == name)
        result: Result = self.session.execute(stmt)
        return result.scalar()

    def getAllUsers(self) -> ScalarResult[UserModel]:
        stmt: Select = select(UserModel)
        result: Result = self.session.execute(stmt)
        return result.scalars()

    def insertUser(self, username: str, password: str, is_admin: bool):
        user = UserModel(username=username, password=password, is_admin=is_admin)
        self.session.add(user)
        self.session.commit()

    """ def get_all_books(self) -> ScalarResult[BookModel]:
        stmt: Select = select(BookModel)
        books: ScalarResult[BookModel] = self.session.scalars(stmt)
        return books

    def get_all_users(self) -> ScalarResult[UserModel]:
        stmt: Select = select(UserModel)
        users: ScalarResult[UserModel] = self.session.scalars(stmt)
        return users

    def get_book_by_isbn(self, isbn: int) -> BookModel:
        stmt: Select = select(BookModel).where(BookModel.isbn.is_(int(isbn)))
        book: BookModel = self.session.scalar(stmt)
        return book

    def get_user_by_name(self, name: str) -> UserModel:
        stmt: Select = select(UserModel).where(UserModel.username.is_(str(name)))
        user: UserModel = self.session.scalar(stmt)
        return user """
