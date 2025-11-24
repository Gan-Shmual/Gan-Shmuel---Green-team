from datetime import datetime, date, time
from sqlalchemy import Integer, String, Date, Time, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import ForeignKey
from flaskr.db import db

class Provider(db.Model):
    __tablename__ = "Provider"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class Rate(db.Model):
    __tablename__ = 'Rates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.String(50), nullable=False)
    rate = db.Column(db.Integer, default=0)
    scope = db.Column(db.String(50))


class Truck(db.Model):
    __tablename__ = "Trucks"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)  # License plate
    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"))

    