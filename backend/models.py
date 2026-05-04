from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Polzovatel(Base):
    __tablename__ = "polzovateli"
    id = Column(Integer, primary_key=True, index=True)
    imya = Column(String(100), nullable=False)
    familiya = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    telefon = Column(String(40), nullable=True)
    parol_hesh = Column(String(200), nullable=False)
    tip = Column(String(20), default="iskatel")
    data_rozhdeniya = Column(String(20), nullable=True)
    o_sebe = Column(Text, nullable=True)
    data_reg = Column(DateTime, default=datetime.utcnow)

class Vakansiya(Base):
    __tablename__ = "vakansii"
    id = Column(Integer, primary_key=True, index=True)
    nazvanie = Column(String(200), nullable=False)
    kompaniya = Column(String(200), nullable=False)
    logo = Column(String(20), default="🏢")
    zarplata = Column(String(100), default="по договорённости")
    rezhim = Column(String(50), default="Офис")
    opisanie = Column(Text, default="")
    trebovaniya = Column(Text, default="")
    tegi = Column(String(300), default="")
    avtor_id = Column(Integer, ForeignKey("polzovateli.id"), nullable=True)
    data_sozdaniya = Column(DateTime, default=datetime.utcnow)

class Kompaniya(Base):
    __tablename__ = "kompanii"
    id = Column(Integer, primary_key=True, index=True)
    nazvanie = Column(String(200), unique=True, nullable=False)
    logo = Column(String(20), default="🏢")
    opisanie = Column(Text, default="")
    vakansij_count = Column(Integer, default=0)

class Otklik(Base):
    __tablename__ = "otkliki"
    id = Column(Integer, primary_key=True, index=True)
    polzovatel_id = Column(Integer, ForeignKey("polzovateli.id"))
    vakansiya_id = Column(Integer, ForeignKey("vakansii.id"))
    status = Column(String(50), default="Ожидание")
    data_sozdaniya = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("polzovatel_id", "vakansiya_id", name="uq_otklik"),)

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

class Lajk(Base):
    __tablename__ = "lajki"
    id = Column(Integer, primary_key=True, index=True)
    polzovatel_id = Column(Integer, ForeignKey("polzovateli.id"))
    vakansiya_id = Column(Integer, ForeignKey("vakansii.id"))
    __table_args__ = (UniqueConstraint("polzovatel_id", "vakansiya_id", name="uq_lajk"),)

class Izbrannoe(Base):
    __tablename__ = "izbrannye"
    id = Column(Integer, primary_key=True, index=True)
    polzovatel_id = Column(Integer, ForeignKey("polzovateli.id"))
    vakansiya_id = Column(Integer, ForeignKey("vakansii.id"))
    __table_args__ = (UniqueConstraint("polzovatel_id", "vakansiya_id", name="uq_izbrannoe"),)

class ChatSoobshchenie(Base):
    __tablename__ = "chat_soobshcheniya"
    id = Column(Integer, primary_key=True, index=True)
    ot_polzovatel_id = Column(Integer, ForeignKey("polzovateli.id"))
    komu_kompaniya = Column(String(200), nullable=False)
    tekst = Column(Text, nullable=False)
    ot_kogo = Column(String(20), default="user")
    data = Column(DateTime, default=datetime.utcnow)
