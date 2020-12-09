from sqlalchemy import Column, Integer, String, Date, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app import db


"""
movies_actors join table
"""
# this is an association table for actors and movies... capturing 'roles' that actors have held in specific movies
movies_actors = db.Table(
    "movies_actors",
    db.Column(
        "movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True
    ),
    db.Column(
        "actor_id", db.Integer, db.ForeignKey("actors.id"), primary_key=True
    ),
)

"""
Actors
"""


class Actor(db.Model):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(80), nullable=False)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
        }


"""
Movies
"""


class Movie(db.Model):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    release_date = Column(Date)
    actors = db.relationship(
        "Actor",
        secondary=movies_actors,
        backref=db.backref("movies", lazy="dynamic"),
        lazy="dynamic",
    )

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit(self)

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "release_date": self.release_date,
        }
