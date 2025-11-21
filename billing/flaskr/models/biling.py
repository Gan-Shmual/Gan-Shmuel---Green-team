from datetime import datetime, date, time
from sqlalchemy import Integer, String, Date, Time, Text
from sqlalchemy.orm import Mapped, mapped_column
from flaskr.db import db

class Provider(db.Model):
    __tablename__ = 'Provider'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))