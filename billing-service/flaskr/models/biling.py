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
    __tablename__ = "Rates"

    product_id: Mapped[int] = mapped_column(String(50), primary_key=True)
    rate: Mapped[int] = mapped_column(Integer)  # stored in agorot (int)
    scope: Mapped[str] = mapped_column(String(50))  # "ALL" or provider.id


class Truck(db.Model):
    __tablename__ = "Trucks"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)  # License plate
    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"))