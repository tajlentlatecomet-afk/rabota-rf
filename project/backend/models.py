from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Polzovatel(Base):
    __tablename__ = "polzovateli"
    id = Column(Integer, primary_key=True, index=True)
    imya = Column(String(100))
    familiya = Column(String(100))
    email = Column(String(200), unique=True, index=True)
    telefon = Column(String(20), nullable=True)
    parol_hesh = Column(String(200))
    tip = Column(String(20), default="iskatel")
    data_reg = Column(DateTime, default=datetime.utcnow)

class Vakansiya(Base):
    __tablename__ = "vakansii"
    id = Column(Integer, primary_key=True, index=True)
    nazvanie = Column(String(200))
    kompaniya = Column(String(200))
    logo = Column(String(10))
    zarplata = Column(String(100))
    rezhim = Column(String(50))
    opisanie = Column(Text)
    trebovaniya = Column(Text)
    tegi = Column(String(300))

class Kompaniya(Base):
    __tablename__ = "kompanii"
    id = Column(Integer, primary_key=True, index=True)
    nazvanie = Column(String(200))
    logo = Column(String(10))
    opisanie = Column(Text)
    vakansij_count = Column(Integer, default=0)

class Otklik(Base):
    __tablename__ = "otkliki"
    id = Column(Integer, primary_key=True, index=True)
    polzovatel_id = Column(Integer, ForeignKey("polzovateli.id"))
    vakansiya_id = Column(Integer, ForeignKey("vakansii.id"))
    status = Column(String(50), default="Ожидание")
    data_sozdaniya = Column(DateTime, default=datetime.utcnow)

class Rezyume(Base):
    __tablename__ = "rezyume"
    id = Column(Integer, primary_key=True, index=True)
    polzovatel_id = Column(Integer, ForeignKey("polzovateli.id"), unique=True)
    dolzhnost = Column(String(200), nullable=True)
    gorod = Column(String(100), nullable=True)
    zarplata = Column(String(100), nullable=True)
    o_sebe = Column(Text, nullable=True)
    opyt = Column(Text, nullable=True)
    obrazovanie = Column(Text, nullable=True)
    navyki = Column(String(500), nullable=True)

class Otzyv(Base):
    __tablename__ = "otzyvy"
    id = Column(Integer, primary_key=True, index=True)
    polzovatel_id = Column(Integer, ForeignKey("polzovateli.id"))
    kompaniya = Column(String(200))
    tekst = Column(Text)
    zvezdy = Column(Integer)
    data = Column(DateTime, default=datetime.utcnow)
