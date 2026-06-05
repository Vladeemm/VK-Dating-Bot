import sqlalchemy as sq
from sqlalchemy import JSON
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Users(Base):
    __tablename__ = 'user_vk'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=False)
    name = sq.Column(sq.String(length=100), nullable=False, unique=False)

    status = relationship('Status', back_populates='user_vk')
    favorite = relationship('Favorite', back_populates='user_vk')


class Status(Base):
    __tablename__ = 'status'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_vk_id = sq.Column(sq.Integer, sq.ForeignKey('user_vk.id',
                                                  ondelete='CASCADE'
                                                  ), nullable=False)
    step = sq.Column(sq.Integer, nullable=False)
    search_criteria = sq.Column(sq.JSON, nullable=False)
    step_datetime = sq.Column(sq.DateTime, nullable=False)

    user_vk = relationship('Users', back_populates='status')


class Favorite(Base):
    __tablename__ = 'favorite'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_vk_id = sq.Column(sq.Integer, sq.ForeignKey('user_vk.id',
                                                     ondelete='CASCADE'
                                                     ), nullable=False)
    name = sq.Column(sq.String(length=100), nullable=False, unique=False)
    surname = sq.Column(sq.String(length=100), nullable=True)
    gender = sq.Column(sq.String(length=1), nullable=False)
    photos = sq.Column(JSON, nullable=True)
    datetime_update = sq.Column(sq.DateTime, nullable=False)

    user_vk = relationship('Users', back_populates='favorite')
