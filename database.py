from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sandelis.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Lakstai(Base):
    __tablename__ = "lakstai"
    id = Column(Integer, primary_key=True, index=True)
    kodas = Column(String(100), unique=True, index=True)
    registruota = Column(DateTime, default=datetime.utcnow)
    surinkta = Column(Boolean, default=False)
    surinkta_kada = Column(DateTime, nullable=True)
    perduota = Column(Boolean, default=False)
    perduota_kada = Column(DateTime, nullable=True)
    etapas = Column(String(100), nullable=True, index=True)

class AktyvusEtapas(Base):
    __tablename__ = "aktyvus_etapas"
    id = Column(Integer, primary_key=True)
    pavadinimas = Column(String(200), unique=True, nullable=False)
    sukurta = Column(DateTime, default=datetime.utcnow)

class Etapas(Base):
    __tablename__ = "etapai"
    id = Column(Integer, primary_key=True)
    pavadinimas = Column(String(200), unique=True)
    sukurta = Column(DateTime, default=datetime.utcnow)
    is_viso = Column(Integer, default=0)
    surinkta_sk = Column(Integer, default=0)
    perduota_sk = Column(Integer, default=0)

class Uzsakymas(Base):
    __tablename__ = "uzsakymai"
    id = Column(Integer, primary_key=True)
    uzs_id = Column(String(50), unique=True, index=True)
    klientas = Column(String(200))
    aprasymas = Column(String(500), nullable=True)
    pastabos = Column(Text, nullable=True)
    statusas = Column(String(50), default="Naujas")
    bendras_svoris = Column(Float, default=0)
    bendra_suma = Column(Float, default=0)
    detaliu_sk = Column(Integer, default=0)
    sukurta = Column(DateTime, default=datetime.utcnow)
    detales = relationship("Detale", back_populates="uzsakymas", cascade="all, delete-orphan")

class Detale(Base):
    __tablename__ = "detales"
    id = Column(Integer, primary_key=True)
    det_id = Column(String(50), unique=True, index=True)
    uzsakymo_id = Column(String(50), ForeignKey("uzsakymai.uzs_id"))
    pavadinimas = Column(String(300))
    storis = Column(Float)
    plotas = Column(Float)
    kiekis = Column(Integer, default=1)
    svoris = Column(Float)
    konturas = Column(Text, nullable=True)
    kaina_kg = Column(Float, default=1.45)
    suma = Column(Float, default=0)
    prideta = Column(DateTime, default=datetime.utcnow)
    uzsakymas = relationship("Uzsakymas", back_populates="detales")

class Sandelis(Base):
    __tablename__ = "sandelis"
    id = Column(Integer, primary_key=True)
    stk_id = Column(String(50), unique=True, index=True)
    storis = Column(Float)
    matmenys = Column(String(100))
    svoris_vnt = Column(Float)
    gauta_vnt = Column(Integer)
    sunaudota_vnt = Column(Integer, default=0)
    liko_vnt = Column(Integer)
    liko_kg = Column(Float)
    liko_t = Column(Float)
    kaina_kg = Column(Float, default=0)
    verte = Column(Float, default=0)
    prideta = Column(DateTime, default=datetime.utcnow)
    pastabos = Column(String(500), nullable=True)

class SandelioIstorijia(Base):
    __tablename__ = "sandelio_istorija"
    id = Column(Integer, primary_key=True)
    data = Column(DateTime, default=datetime.utcnow)
    veiksmas = Column(String(50))
    storis = Column(Float)
    matmenys = Column(String(100))
    kiekis = Column(Integer)
    svoris_vnt = Column(Float)
    svoris_is_viso = Column(Float)
    kaina_kg = Column(Float, default=0)
    verte = Column(Float, default=0)
    pastabos = Column(String(500), nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Prideti trukstamus stulpelius jei ju nera (migracija)
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE detales ADD COLUMN IF NOT EXISTS kaina_kg FLOAT DEFAULT 1.45"))
            conn.execute(text("ALTER TABLE detales ADD COLUMN IF NOT EXISTS suma FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE uzsakymai ADD COLUMN IF NOT EXISTS bendra_suma FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS kaina_kg FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS verte FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS pastabos VARCHAR(500)"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS svoris_is_viso FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS svoris_vnt FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS kiekis INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS storis FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS matmenys VARCHAR(100)"))
            conn.execute(text("ALTER TABLE sandelio_istorija ADD COLUMN IF NOT EXISTS veiksmas VARCHAR(50)"))
            conn.execute(text("ALTER TABLE sandelis ADD COLUMN IF NOT EXISTS kaina_kg FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelis ADD COLUMN IF NOT EXISTS verte FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE sandelis ADD COLUMN IF NOT EXISTS pastabos VARCHAR(500)"))
            conn.execute(text("ALTER TABLE sandelis ADD COLUMN IF NOT EXISTS sunaudota_vnt INTEGER DEFAULT 0"))
            conn.commit()
        except Exception:
            pass
