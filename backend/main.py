from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import jwt
import bcrypt
from datetime import datetime, timedelta
from database import baza, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

SEKRETNYJ_KLYUCH = "supersecretkey123"

class PolzovatelReg(BaseModel):
    imya: str
    familiya: str
    email: str
    telefon: Optional[str] = None
    parol: str
    tip: str

class PolzovatelVhod(BaseModel):
    email: str
    parol: str

class OtklikSozdanie(BaseModel):
    vakansiya_id: int

class OtzyvSozdanie(BaseModel):
    kompaniya: str
    tekst: str
    zvezdy: int

class RezyumeSozdanie(BaseModel):
    dolzhnost: Optional[str] = None
    gorod: Optional[str] = None
    zarplata: Optional[str] = None
    o_sebe: Optional[str] = None
    opyt: Optional[str] = None
    obrazovanie: Optional[str] = None
    navyki: Optional[str] = None


def sozdat_token(polzovatel_id: int):
    danye = {"sub": str(polzovatel_id), "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(danye, SEKRETNYJ_KLYUCH, algorithm="HS256")

def poluchit_tekushchego(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(baza)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        danye = jwt.decode(credentials.credentials, SEKRETNYJ_KLYUCH, algorithms=["HS256"])
        pol_id = int(danye["sub"])
    except:
        raise HTTPException(status_code=401, detail="Неверный токен")
    pol = db.query(models.Polzovatel).filter(models.Polzovatel.id == pol_id).first()
    if not pol:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return pol


@app.get("/")
def koren():
    return {"status": "ok", "soobshchenie": "РаботаРФ API работает"}


@app.post("/registratsiya")
def registratsiya(danye: PolzovatelReg, db=Depends(baza)):
    sushchestvuet = db.query(models.Polzovatel).filter(models.Polzovatel.email == danye.email).first()
    if sushchestvuet:
        raise HTTPException(status_code=400, detail="Email уже занят")
    hesh = bcrypt.hashpw(danye.parol.encode(), bcrypt.gensalt()).decode()
    pol = models.Polzovatel(
        imya=danye.imya,
        familiya=danye.familiya,
        email=danye.email,
        telefon=danye.telefon,
        parol_hesh=hesh,
        tip=danye.tip
    )
    db.add(pol)
    db.commit()
    db.refresh(pol)
    token = sozdat_token(pol.id)
    return {"token": token, "imya": pol.imya, "email": pol.email, "tip": pol.tip}


@app.post("/vhod")
def vhod(danye: PolzovatelVhod, db=Depends(baza)):
    pol = db.query(models.Polzovatel).filter(models.Polzovatel.email == danye.email).first()
    if not pol or not bcrypt.checkpw(danye.parol.encode(), pol.parol_hesh.encode()):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    token = sozdat_token(pol.id)
    return {"token": token, "imya": pol.imya, "email": pol.email, "tip": pol.tip}


@app.get("/vakansii")
def poluchit_vakansii(poisk: Optional[str] = None, db=Depends(baza)):
    zapros = db.query(models.Vakansiya)
    if poisk:
        zapros = zapros.filter(
            models.Vakansiya.nazvanie.ilike(f"%{poisk}%") |
            models.Vakansiya.kompaniya.ilike(f"%{poisk}%")
        )
    return zapros.all()


@app.get("/vakansii/{vakansiya_id}")
def poluchit_vakansiyu(vakansiya_id: int, db=Depends(baza)):
    v = db.query(models.Vakansiya).filter(models.Vakansiya.id == vakansiya_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return v


@app.get("/kompanii")
def poluchit_kompanii(db=Depends(baza)):
    return db.query(models.Kompaniya).all()


@app.post("/otkliki")
def sozdat_otklik(danye: OtklikSozdanie, pol=Depends(poluchit_tekushchego), db=Depends(baza)):
    sushchestvuet = db.query(models.Otklik).filter(
        models.Otklik.polzovatel_id == pol.id,
        models.Otklik.vakansiya_id == danye.vakansiya_id
    ).first()
    if sushchestvuet:
        raise HTTPException(status_code=400, detail="Вы уже откликались на эту вакансию")
    otklik = models.Otklik(polzovatel_id=pol.id, vakansiya_id=danye.vakansiya_id, status="Ожидание")
    db.add(otklik)
    db.commit()
    db.refresh(otklik)
    return otklik


@app.get("/otkliki/moi")
def moi_otkliki(pol=Depends(poluchit_tekushchego), db=Depends(baza)):
    otkliki = db.query(models.Otklik).filter(models.Otklik.polzovatel_id == pol.id).all()
    rezultat = []
    for o in otkliki:
        v = db.query(models.Vakansiya).filter(models.Vakansiya.id == o.vakansiya_id).first()
        rezultat.append({
            "id": o.id,
            "vakansiya_id": o.vakansiya_id,
            "nazvanie": v.nazvanie if v else "—",
            "kompaniya": v.kompaniya if v else "—",
            "status": o.status,
            "data": o.data_sozdaniya
        })
    return rezultat


@app.get("/rezyume/moe")
def moe_rezyume(pol=Depends(poluchit_tekushchego), db=Depends(baza)):
    rez = db.query(models.Rezyume).filter(models.Rezyume.polzovatel_id == pol.id).first()
    if not rez:
        return {}
    return rez


@app.post("/rezyume")
def sohranit_rezyume(danye: RezyumeSozdanie, pol=Depends(poluchit_tekushchego), db=Depends(baza)):
    rez = db.query(models.Rezyume).filter(models.Rezyume.polzovatel_id == pol.id).first()
    if rez:
        rez.dolzhnost = danye.dolzhnost
        rez.gorod = danye.gorod
        rez.zarplata = danye.zarplata
        rez.o_sebe = danye.o_sebe
        rez.opyt = danye.opyt
        rez.obrazovanie = danye.obrazovanie
        rez.navyki = danye.navyki
    else:
        rez = models.Rezyume(
            polzovatel_id=pol.id,
            dolzhnost=danye.dolzhnost,
            gorod=danye.gorod,
            zarplata=danye.zarplata,
            o_sebe=danye.o_sebe,
            opyt=danye.opyt,
            obrazovanie=danye.obrazovanie,
            navyki=danye.navyki
        )
        db.add(rez)
    db.commit()
    return {"soobshchenie": "Резюме сохранено"}


@app.post("/otzyvy")
def dobavit_otzyv(danye: OtzyvSozdanie, pol=Depends(poluchit_tekushchego), db=Depends(baza)):
    if danye.zvezdy < 1 or danye.zvezdy > 5:
        raise HTTPException(status_code=400, detail="Оценка от 1 до 5")
    otzyv = models.Otzyv(
        polzovatel_id=pol.id,
        kompaniya=danye.kompaniya,
        tekst=danye.tekst,
        zvezdy=danye.zvezdy
    )
    db.add(otzyv)
    db.commit()
    return {"soobshchenie": "Отзыв добавлен"}


@app.get("/otzyvy/{kompaniya}")
def otzyvy_kompanii(kompaniya: str, db=Depends(baza)):
    return db.query(models.Otzyv).filter(models.Otzyv.kompaniya == kompaniya).all()


@app.get("/profil")
def moj_profil(pol=Depends(poluchit_tekushchego)):
    return {"id": pol.id, "imya": pol.imya, "familiya": pol.familiya, "email": pol.email, "telefon": pol.telefon, "tip": pol.tip}
