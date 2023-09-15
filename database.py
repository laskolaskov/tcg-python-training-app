from models import Base, UserModel, CardModel, CollectionModel
from sqlalchemy import (
    create_engine,
    select,
    Select,
    Result,
    ScalarResult,
    Engine,
)
from sqlalchemy.orm import Session
from mtg import get_k_cards
import json


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
        user = UserModel(
            username=username, password=password, is_admin=is_admin, credits=9000
        )
        self.session.add(user)
        self.session.commit()
        self.draftCardsForUser(user)

    def getCardByName(self, name: str) -> CardModel:
        stmt: Select = select(CardModel).where(CardModel.name == name)
        result: Result = self.session.execute(stmt)
        return result.scalar()

    def getAllCards(self) -> ScalarResult[CardModel]:
        stmt: Select = select(CardModel)
        result: Result = self.session.execute(stmt)
        return result.scalars()

    def getCollection(self, user: UserModel, card: CardModel) -> CollectionModel:
        stmt: Select = (
            select(CollectionModel)
            .where(CollectionModel.user == user)
            .where(CollectionModel.card == card)
        )
        result: Result = self.session.execute(stmt)
        return result.scalar()

    def draftCardsForUser(self, user: UserModel):
        mtg_cards = get_k_cards(5)
        cards = []
        new_cards = []

        for c in mtg_cards:
            # load user
            cm: CardModel = self.getCardByName(c.get("name"))

            if not cm:
                cm = CardModel()
                cm.name = c.get("name")
                cm.url = c.get("imageUrl", "n/a")
                cm.data = json.dumps(c)
                new_cards.append(cm)

            cards.append(cm)

        # add cards
        self.session.add_all(new_cards)
        """ self.session.execute(insert(CardModel)
                .values(cards)
                .on_conflict_do_nothing()) """
        self.session.commit()

        # add to user collection
        for card in cards:
            collection = self.getCollection(user, card)
            if collection:
                collection.count += 1
            else:
                collection = CollectionModel(count=1, price=100)
                collection.card = card
                collection.is_marketed = False

            user.collections.append(collection)

        self.session.commit()


"""     # create parent, append a child via association
p = Parent()
a = Association(extra_data="some data")
a.child = Child()
p.children.append(a)

# iterate through child objects via association, including association
# attributes
for assoc in p.children:
    print(assoc.extra_data)
    print(assoc.child) 
"""
