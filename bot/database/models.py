"""ORM модели приложения."""

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'user_vk'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=False)
    name = sq.Column(sq.String(length=100), nullable=False)

    status = relationship('Status', back_populates='user_vk')
    favorite = relationship('Favorite', back_populates='user_vk')


class Status(Base):
    __tablename__ = 'status'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_vk_id = sq.Column(sq.Integer, sq.ForeignKey('user_vk.id', ondelete='CASCADE'), nullable=False, unique=True)
    step = sq.Column(sq.String, nullable=False, default='start')
    search_criteria = sq.Column(sq.JSON, nullable=True)
    list_applicants = sq.Column(sq.JSON, nullable=True)
    step_datetime = sq.Column(sq.DateTime, nullable=False)

    user_vk = relationship('Users', back_populates='status', uselist=False)


class Favorite(Base):
    __tablename__ = 'favorite'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_vk_id = sq.Column(sq.Integer, sq.ForeignKey('user_vk.id', ondelete='CASCADE'), nullable=False)
    favorite_user_vk_id = sq.Column(sq.Integer, nullable=False)
    name = sq.Column(sq.String(length=100), nullable=False)
    surname = sq.Column(sq.String(length=100), nullable=True)
    gender = sq.Column(sq.String(length=1), nullable=False)
    photos = sq.Column(sq.JSON, nullable=True)
    datetime_update = sq.Column(sq.DateTime, nullable=False)

    __table_args__ = (
        sq.UniqueConstraint('user_vk_id', 'favorite_user_vk_id', name='unique_favorite'),
    )

    user_vk = relationship('Users', back_populates='favorite')
