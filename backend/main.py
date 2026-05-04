import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

import models
from database import SessionLocal, baza, engine
from seed_data import seed_if_empty

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="РаботаРФ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

class PolzovatelReg(BaseModel):
    imya: str
    familiya: str
    email: str
    telefon: Optional[str] = None
    parol: str
    tip: str = "iskatel"

class PolzovatelVhod(BaseModel):
    email: str
    parol: str

class RezyumeSozdanie(BaseModel):
    dolzhnost: Optional[str] = None
    gorod: Optional[str] = None
    zarplata: Optional[str] = None
    o_sebe: Optional[str] = None
    opyt: Optional[str] = None
    obrazovanie: Optional[str] = None
    navyki: Optional[str] = None

class OtklikSozdanie(BaseModel):
    vakansiya_id: int

class OtzyvSozdanie(BaseModel):
    kompaniya: str
    tekst: str
    zvezdy: int

class VakansiyaSozdanie(BaseModel):
    nazvanie: str
    kompaniya: Optional[str] = None
    zarplata: Optional[str] = None
    rezhim: Optional[str] = None
    opisanie: Optional[str] = None
    trebovaniya: Optional[str] = None
    tegi: Optional[str] = None

class ChatSoobshchenieSozdanie(BaseModel):
    komu_kompaniya: str
    tekst: str

class ProfilObnovlenie(BaseModel):
    telefon: Optional[str] = None
    data_rozhdeniya: Optional[str] = None
    o_sebe: Optional[str] = None

@app.on_event("startup")
def startup_seed():
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()

def sozdat_token(polzovatel_id: int):
    data = {"sub": str(polzovatel_id), "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def tekushchij_polzovatel(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(baza)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        data = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        pol_id = int(data["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Неверный токен")
    pol = db.query(models.Polzovatel).filter(models.Polzovatel.id == pol_id).first()
    if not pol:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return pol

@app.get("/")
def koren():
    return {"status": "ok", "soobshchenie": "РаботаРФ API работает"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/registratsiya")
def registratsiya(data: PolzovatelReg, db=Depends(baza)):
    if data.tip not in ["iskatel", "rabotodatel"]:
        raise HTTPException(status_code=400, detail="Неверный тип аккаунта")
    exists = db.query(models.Polzovatel).filter(models.Polzovatel.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email уже занят")
    hesh = bcrypt.hashpw(data.parol.encode(), bcrypt.gensalt()).decode()
    pol = models.Polzovatel(
        imya=data.imya,
        familiya=data.familiya,
        email=data.email,
        telefon=data.telefon,
        parol_hesh=hesh,
        tip=data.tip,
    )
    db.add(pol)
    db.commit()
    db.refresh(pol)
    return {"token": sozdat_token(pol.id), "imya": pol.imya, "email": pol.email, "telefon": pol.telefon, "tip": pol.tip}

@app.post("/vhod")
def vhod(data: PolzovatelVhod, db=Depends(baza)):
    pol = db.query(models.Polzovatel).filter(models.Polzovatel.email == data.email).first()
    if not pol or not bcrypt.checkpw(data.parol.encode(), pol.parol_hesh.encode()):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    return {"token": sozdat_token(pol.id), "imya": pol.imya, "email": pol.email, "telefon": pol.telefon, "tip": pol.tip}

@app.get("/vakansii")
def poluchit_vakansii(
    poisk: Optional[str] = None,
    stranitsa: int = Query(1, ge=1),
    razmer: int = Query(9, ge=1, le=50),
    db=Depends(baza),
):
    query = db.query(models.Vakansiya)
    if poisk:
        query = query.filter(
            models.Vakansiya.nazvanie.ilike(f"%{poisk}%") |
            models.Vakansiya.kompaniya.ilike(f"%{poisk}%") |
            models.Vakansiya.tegi.ilike(f"%{poisk}%")
        )
    vsego = query.count()
    items = query.order_by(models.Vakansiya.id.desc()).offset((stranitsa - 1) * razmer).limit(razmer).all()
    vsego_stranits = max(1, (vsego + razmer - 1) // razmer)
    return {"vakansii": items, "vsego": vsego, "stranitsa": stranitsa, "razmer": razmer, "vsego_stranits": vsego_stranits}

@app.get("/vakansii/{vakansiya_id}")
def odna_vakansiya(vakansiya_id: int, db=Depends(baza)):
    v = db.query(models.Vakansiya).filter(models.Vakansiya.id == vakansiya_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return v

@app.post("/vakansii")
def dobavit_vakansiyu(data: VakansiyaSozdanie, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    if pol.tip != "rabotodatel":
        raise HTTPException(status_code=403, detail="Только для работодателей")
    kompaniya = data.kompaniya or f"{pol.imya} {pol.familiya}".strip()
    v = models.Vakansiya(
        nazvanie=data.nazvanie,
        kompaniya=kompaniya,
        logo="🏢",
        zarplata=data.zarplata or "по договорённости",
        rezhim=data.rezhim or "Офис",
        opisanie=data.opisanie or "",
        trebovaniya=data.trebovaniya or "",
        tegi=data.tegi or "",
        avtor_id=pol.id,
    )
    db.add(v)
    if not db.query(models.Kompaniya).filter(models.Kompaniya.nazvanie == kompaniya).first():
        db.add(models.Kompaniya(nazvanie=kompaniya, logo="🏢", opisanie="Компания работодателя", vakansij_count=1))
    db.commit()
    db.refresh(v)
    return v

@app.delete("/vakansii/{vakansiya_id}")
def udalit_vakansiyu(vakansiya_id: int, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    v = db.query(models.Vakansiya).filter(models.Vakansiya.id == vakansiya_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    if pol.tip != "rabotodatel" or v.avtor_id != pol.id:
        raise HTTPException(status_code=403, detail="Можно удалять только свои вакансии")
    db.delete(v)
    db.commit()
    return {"ok": True}

@app.get("/moi_vakansii")
def moi_vakansii(pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    if pol.tip != "rabotodatel":
        raise HTTPException(status_code=403, detail="Только для работодателей")
    return db.query(models.Vakansiya).filter(models.Vakansiya.avtor_id == pol.id).order_by(models.Vakansiya.id.desc()).all()

@app.get("/kompanii")
def kompanii(db=Depends(baza)):
    return db.query(models.Kompaniya).order_by(models.Kompaniya.nazvanie).all()

@app.post("/otkliki")
def sozdat_otklik(data: OtklikSozdanie, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    if not db.query(models.Vakansiya).filter(models.Vakansiya.id == data.vakansiya_id).first():
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    exists = db.query(models.Otklik).filter(models.Otklik.polzovatel_id == pol.id, models.Otklik.vakansiya_id == data.vakansiya_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Вы уже откликались на эту вакансию")
    o = models.Otklik(polzovatel_id=pol.id, vakansiya_id=data.vakansiya_id)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o

@app.get("/otkliki/moi")
def moi_otkliki(pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    otkliki = db.query(models.Otklik).filter(models.Otklik.polzovatel_id == pol.id).order_by(models.Otklik.id.desc()).all()
    result = []
    for o in otkliki:
        v = db.query(models.Vakansiya).filter(models.Vakansiya.id == o.vakansiya_id).first()
        result.append({"id": o.id, "vakansiya_id": o.vakansiya_id, "nazvanie": v.nazvanie if v else "—", "kompaniya": v.kompaniya if v else "—", "status": o.status, "data": o.data_sozdaniya})
    return result

@app.get("/rezyume/moe")
def moe_rezyume(pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    return db.query(models.Rezyume).filter(models.Rezyume.polzovatel_id == pol.id).first() or {}

@app.post("/rezyume")
def sohranit_rezyume(data: RezyumeSozdanie, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    rez = db.query(models.Rezyume).filter(models.Rezyume.polzovatel_id == pol.id).first()
    if not rez:
        rez = models.Rezyume(polzovatel_id=pol.id)
        db.add(rez)
    for field, value in data.dict().items():
        setattr(rez, field, value)
    db.commit()
    return {"soobshchenie": "Резюме сохранено"}

@app.post("/otzyvy")
def dobavit_otzyv(data: OtzyvSozdanie, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    if data.zvezdy < 1 or data.zvezdy > 5:
        raise HTTPException(status_code=400, detail="Оценка от 1 до 5")
    db.add(models.Otzyv(polzovatel_id=pol.id, kompaniya=data.kompaniya, tekst=data.tekst, zvezdy=data.zvezdy))
    db.commit()
    return {"soobshchenie": "Отзыв добавлен"}

@app.post("/lajki/{vakansiya_id}")
def toggle_lajk(vakansiya_id: int, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    item = db.query(models.Lajk).filter(models.Lajk.polzovatel_id == pol.id, models.Lajk.vakansiya_id == vakansiya_id).first()
    if item:
        db.delete(item)
        db.commit()
        return {"lajk": False}
    db.add(models.Lajk(polzovatel_id=pol.id, vakansiya_id=vakansiya_id))
    db.commit()
    return {"lajk": True}

@app.get("/lajki/moi")
def moi_lajki(pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    return [x.vakansiya_id for x in db.query(models.Lajk).filter(models.Lajk.polzovatel_id == pol.id).all()]

@app.post("/izbrannye/{vakansiya_id}")
def toggle_izbrannoe(vakansiya_id: int, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    item = db.query(models.Izbrannoe).filter(models.Izbrannoe.polzovatel_id == pol.id, models.Izbrannoe.vakansiya_id == vakansiya_id).first()
    if item:
        db.delete(item)
        db.commit()
        return {"izbrannoe": False}
    db.add(models.Izbrannoe(polzovatel_id=pol.id, vakansiya_id=vakansiya_id))
    db.commit()
    return {"izbrannoe": True}

@app.get("/izbrannye/moi")
def moi_izbrannye(pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    return [x.vakansiya_id for x in db.query(models.Izbrannoe).filter(models.Izbrannoe.polzovatel_id == pol.id).all()]

@app.get("/chat/soobshcheniya")
def chat_messages(komu_kompaniya: str, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    return db.query(models.ChatSoobshchenie).filter(models.ChatSoobshchenie.ot_polzovatel_id == pol.id, models.ChatSoobshchenie.komu_kompaniya == komu_kompaniya).order_by(models.ChatSoobshchenie.data).all()

@app.post("/chat/otpravit")
def chat_send(data: ChatSoobshchenieSozdanie, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    msg = models.ChatSoobshchenie(ot_polzovatel_id=pol.id, komu_kompaniya=data.komu_kompaniya, tekst=data.tekst, ot_kogo="user")
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@app.get("/profil")
def profil(pol=Depends(tekushchij_polzovatel)):
    return {"id": pol.id, "imya": pol.imya, "familiya": pol.familiya, "email": pol.email, "telefon": pol.telefon, "tip": pol.tip, "data_rozhdeniya": pol.data_rozhdeniya, "o_sebe": pol.o_sebe}

@app.put("/profil")
def profil_update(data: ProfilObnovlenie, pol=Depends(tekushchij_polzovatel), db=Depends(baza)):
    p = db.query(models.Polzovatel).filter(models.Polzovatel.id == pol.id).first()
    for field, value in data.dict().items():
        if value is not None:
            setattr(p, field, value)
    db.commit()
    return {"soobshchenie": "Профиль обновлён"}
