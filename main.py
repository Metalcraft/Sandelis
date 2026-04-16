from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os

from database import get_db, init_db, Lakstai, Etapas, Uzsakymas, Detale, Sandelis, SandelioIstorijia

app = FastAPI(title="Sandelio Sistema")
TANKIS = 8000

import pathlib
pathlib.Path("static/css").mkdir(parents=True, exist_ok=True)
pathlib.Path("static/js").mkdir(parents=True, exist_ok=True)
pathlib.Path("templates").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({"name":"Sandelio Sistema","short_name":"Sandelis","start_url":"/","display":"standalone","background_color":"#f6f8fa","theme_color":"#0969da"})

@app.get("/sw.js")
async def sw():
    from fastapi.responses import Response
    return Response(content="// sw", media_type="application/javascript")

@app.get("/icon.png")
async def icon():
    from fastapi.responses import Response
    import base64
    return Response(content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="), media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# LAKSTAI API
@app.get("/api/lakstai")
def get_lakstai(etapas: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lakstai)
    if etapas:
        q = q.filter(Lakstai.etapas == etapas)
    else:
        q = q.filter(Lakstai.etapas == None)
    return {"orders": [_lk(l) for l in q.all()]}

@app.post("/api/lakstai/register")
def register_lakstas(data: dict, db: Session = Depends(get_db)):
    existing = db.query(Lakstai).filter(Lakstai.kodas == data["kodas"]).first()
    if existing:
        return {"success": False, "alreadyExists": True, "order": _lk(existing)}
    l = Lakstai(kodas=data["kodas"])
    db.add(l); db.commit(); db.refresh(l)
    return {"success": True, "kodas": l.kodas}

@app.post("/api/lakstai/next")
def next_step(data: dict, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == data["kodas"]).first()
    if not l:
        return {"success": False, "message": "Nerastas"}
    if l.perduota:
        return {"success": False, "alreadyDelivered": True}
    now = datetime.utcnow()
    if l.surinkta:
        l.perduota = True; l.perduota_kada = now
        db.commit()
        return {"success": True, "step": "delivered", "deliveredAt": now.strftime("%Y-%m-%d %H:%M:%S")}
    else:
        l.surinkta = True; l.surinkta_kada = now
        db.commit()
        return {"success": True, "step": "collected", "collectedAt": now.strftime("%Y-%m-%d %H:%M:%S")}

@app.delete("/api/lakstai/{kodas}")
def delete_lakstas(kodas: str, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == kodas).first()
    if not l:
        raise HTTPException(404)
    db.delete(l); db.commit()
    return {"success": True}

@app.post("/api/lakstai/archive")
def archive_stage(data: dict, db: Session = Depends(get_db)):
    name = data.get("pavadinimas", "Etapas " + datetime.utcnow().strftime("%Y-%m-%d"))
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    if not items:
        return {"success": False, "message": "Nera uzsakymu"}
    total = len(items)
    collected = sum(1 for l in items if l.surinkta)
    delivered = sum(1 for l in items if l.perduota)
    for l in items:
        l.etapas = name
    e = Etapas(pavadinimas=name, iš_viso=total, surinkta=collected, perduota=delivered)
    db.add(e); db.commit()
    return {"success": True, "archiveName": name, "total": total, "collected": collected, "delivered": delivered}

@app.get("/api/etapai")
def get_etapai(db: Session = Depends(get_db)):
    etapai = db.query(Etapas).order_by(Etapas.sukurta.desc()).all()
    return {"stages": [{"name": e.pavadinimas, "total": e.iš_viso, "collected": e.surinkta, "delivered": e.perduota, "pending": e.iš_viso - e.surinkta} for e in etapai]}

@app.get("/api/etapai/{name}")
def get_etapas(name: str, db: Session = Depends(get_db)):
    items = db.query(Lakstai).filter(Lakstai.etapas == name).all()
    return {"orders": [_lk(l) for l in items]}

# DXF API
@app.get("/api/uzsakymai")
def get_uzsakymai(db: Session = Depends(get_db)):
    items = db.query(Uzsakymas).order_by(Uzsakymas.sukurta.desc()).all()
    return {"orders": [_uzs(u) for u in items]}

@app.post("/api/uzsakymai")
def create_uzsakymas(data: dict, db: Session = Depends(get_db)):
    uzs_id = "UZS-" + str(int(datetime.utcnow().timestamp() * 1000))
    u = Uzsakymas(uzs_id=uzs_id, klientas=data.get("klientas", ""), aprasymas=data.get("aprasymas", ""), pastabos=data.get("pastabos", ""))
    db.add(u); db.commit()
    return {"success": True, "id": uzs_id}

@app.put("/api/uzsakymai/{uzs_id}/statusas")
def update_statusas(uzs_id: str, data: dict, db: Session = Depends(get_db)):
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if not u: raise HTTPException(404)
    u.statusas = data["statusas"]; db.commit()
    return {"success": True}

@app.delete("/api/uzsakymai/{uzs_id}")
def delete_uzsakymas(uzs_id: str, db: Session = Depends(get_db)):
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if not u: raise HTTPException(404)
    db.delete(u); db.commit()
    return {"success": True}

@app.get("/api/uzsakymai/{uzs_id}/detales")
def get_detales(uzs_id: str, db: Session = Depends(get_db)):
    items = db.query(Detale).filter(Detale.uzsakymo_id == uzs_id).order_by(Detale.storis, Detale.pavadinimas).all()
    return {"details": [_det(d) for d in items]}

@app.post("/api/detales")
def add_detale(data: dict, db: Session = Depends(get_db)):
    det_id = "DET-" + str(int(datetime.utcnow().timestamp() * 1000))
    storis = float(data.get("storis", 0))
    plotas = float(data.get("plotas", 0))
    kiekis = int(data.get("kiekis", 1))
    svoris = round(plotas * (storis / 10) * (TANKIS / 1000) * kiekis / 1000, 3)
    d = Detale(det_id=det_id, uzsakymo_id=data["uzsakymoId"], pavadinimas=data.get("pavadinimas", "Detale"),
               storis=storis, plotas=plotas, kiekis=kiekis, svoris=svoris, konturas=data.get("konturas", ""))
    db.add(d); db.commit()
    _recalc(data["uzsakymoId"], db)
    return {"success": True, "detId": det_id, "svoris": svoris}

@app.put("/api/detales/{det_id}")
def update_detale(det_id: str, data: dict, db: Session = Depends(get_db)):
    d = db.query(Detale).filter(Detale.det_id == det_id).first()
    if not d: raise HTTPException(404)
    if "storis" in data: d.storis = float(data["storis"])
    if "kiekis" in data: d.kiekis = int(data["kiekis"])
    if "svoris" in data:
        d.svoris = float(data["svoris"])
    else:
        d.svoris = round(d.plotas * (d.storis / 10) * (TANKIS / 1000) * d.kiekis / 1000, 3)
    db.commit()
    _recalc(d.uzsakymo_id, db)
    return {"success": True, "svoris": d.svoris}

@app.delete("/api/detales/{det_id}")
def delete_detale(det_id: str, db: Session = Depends(get_db)):
    d = db.query(Detale).filter(Detale.det_id == det_id).first()
    if not d: raise HTTPException(404)
    uzs_id = d.uzsakymo_id; db.delete(d); db.commit()
    _recalc(uzs_id, db)
    return {"success": True}

# SANDELIS API
@app.get("/api/sandelis")
def get_sandelis(db: Session = Depends(get_db)):
    items = db.query(Sandelis).order_by(Sandelis.storis).all()
    return {"stock": [_stk(s) for s in items]}

@app.post("/api/sandelis/gauti")
def gauti(data: dict, db: Session = Depends(get_db)):
    storis = float(data["storis"])
    w = float(data["plotis"])
    l = float(data["ilgis"])
    qty = int(data["kiekis"])
    kaina = float(data.get("kaina", 0))
    svoris_vnt = round((w/1000) * (l/1000) * (storis/1000) * TANKIS, 2)
    liko_kg = round(svoris_vnt * qty, 2)
    liko_t = round(liko_kg / 1000, 3)
    verte = round(liko_t * kaina, 2)
    stk_id = "STK-" + str(int(datetime.utcnow().timestamp() * 1000))
    s = Sandelis(stk_id=stk_id, storis=storis, matmenys=f"{int(w)}x{int(l)}", svoris_vnt=svoris_vnt,
                 gauta_vnt=qty, liko_vnt=qty, liko_kg=liko_kg, liko_t=liko_t, kaina_kg=kaina, verte=verte,
                 pastabos=data.get("pastabos", ""))
    db.add(s)
    hist = SandelioIstorijia(veiksmas="Gauta", storis=storis, matmenys=f"{int(w)}x{int(l)}", kiekis=qty,
                              svoris_vnt=svoris_vnt, svoris_iš_viso=liko_kg, kaina_kg=kaina, verte=verte,
                              pastabos=data.get("pastabos", ""))
    db.add(hist); db.commit()
    return {"success": True, "id": stk_id, "svorisVnt": svoris_vnt, "likoT": liko_t, "verte": verte}

@app.post("/api/sandelis/{stk_id}/naudoti")
def naudoti(stk_id: str, data: dict, db: Session = Depends(get_db)):
    s = db.query(Sandelis).filter(Sandelis.stk_id == stk_id).first()
    if not s: raise HTTPException(404)
    qty = int(data["kiekis"])
    s.sunaudota_vnt += qty
    s.liko_vnt = max(0, s.gauta_vnt - s.sunaudota_vnt)
    s.liko_kg = round(s.liko_vnt * s.svoris_vnt, 2)
    s.liko_t = round(s.liko_kg / 1000, 3)
    s.verte = round(s.liko_t * s.kaina_kg, 2)
    hist = SandelioIstorijia(veiksmas="Sunaudota", storis=s.storis, matmenys=s.matmenys, kiekis=qty,
                              svoris_vnt=s.svoris_vnt, svoris_iš_viso=round(qty*s.svoris_vnt, 2),
                              kaina_kg=s.kaina_kg, verte=round((qty*s.svoris_vnt/1000)*s.kaina_kg, 2),
                              pastabos=data.get("pastabos", ""))
    db.add(hist); db.commit()
    return {"success": True, "likoVnt": s.liko_vnt, "likoKg": s.liko_kg}

@app.delete("/api/sandelis/{stk_id}")
def delete_stk(stk_id: str, db: Session = Depends(get_db)):
    s = db.query(Sandelis).filter(Sandelis.stk_id == stk_id).first()
    if not s: raise HTTPException(404)
    db.delete(s); db.commit()
    return {"success": True}

@app.get("/api/sandelis/istorija")
def get_istorija(db: Session = Depends(get_db)):
    items = db.query(SandelioIstorijia).order_by(SandelioIstorijia.data.desc()).limit(100).all()
    return {"history": [{"data": h.data.strftime("%Y-%m-%d %H:%M"), "veiksmas": h.veiksmas,
                          "storis": h.storis, "matmenys": h.matmenys, "kiekis": h.kiekis,
                          "svorisVnt": h.svoris_vnt, "svorisIsViso": h.svoris_iš_viso,
                          "kainaKg": h.kaina_kg, "verte": h.verte} for h in items]}

# ATASKAITA
@app.get("/api/ataskaita")
def ataskaita(nuo: str, iki: str, db: Session = Depends(get_db)):
    from_dt = datetime.strptime(nuo, "%Y-%m-%d")
    to_dt = datetime.strptime(iki, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    lk_gauta = db.query(Lakstai).filter(Lakstai.registruota.between(from_dt, to_dt)).count()
    lk_surinkta = db.query(Lakstai).filter(Lakstai.surinkta_kada.between(from_dt, to_dt)).count()
    lk_perduota = db.query(Lakstai).filter(Lakstai.perduota_kada.between(from_dt, to_dt)).count()
    uzs = db.query(Uzsakymas).filter(Uzsakymas.sukurta.between(from_dt, to_dt)).all()
    hist = db.query(SandelioIstorijia).filter(SandelioIstorijia.data.between(from_dt, to_dt)).all()
    gauta_hist = [h for h in hist if h.veiksmas == "Gauta"]
    sun_hist = [h for h in hist if h.veiksmas == "Sunaudota"]
    stock = db.query(Sandelis).all()
    return {
        "lakstai": {"gauta": lk_gauta, "surinkta": lk_surinkta, "perduota": lk_perduota},
        "dxf": {"sk": len(uzs), "svoris": round(sum(u.bendras_svoris for u in uzs), 3)},
        "sandelis": {
            "gautaKg": round(sum(h.svoris_iš_viso for h in gauta_hist), 2),
            "sunaudotaKg": round(sum(h.svoris_iš_viso for h in sun_hist), 2),
            "gautaVerte": round(sum(h.verte for h in gauta_hist), 2),
            "sunaudotaVerte": round(sum(h.verte for h in sun_hist), 2),
        },
        "likutis": {
            "vnt": sum(s.liko_vnt for s in stock),
            "t": round(sum(s.liko_kg for s in stock) / 1000, 3),
            "verte": round(sum(s.verte for s in stock), 2),
        }
    }

# EMAIL
@app.post("/api/email/siusti")
async def siusti_email(db: Session = Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    smtp_host = os.getenv("SMTP_HOST", "vytis.serveriai.lt")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "info@metalcraft.lt")
    smtp_pass = os.getenv("SMTP_PASS", "")
    gaivejas = os.getenv("EMAIL_TO", "gintaras@metalikalt.eu")
    if not smtp_pass:
        raise HTTPException(400, "SMTP_PASS nenurodytas")
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti = [l for l in items if l.surinkta and not l.perduota]
    perduoti = [l for l in items if l.perduota]
    laukia = [l for l in items if not l.surinkta]
    def rows(lst, color):
        if not lst:
            return "<tr><td colspan='2' style='color:#aaa;padding:4px 8px'>Tuscia</td></tr>"
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else '-'}</td></tr>" for l in lst)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    html_body = f"""<html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>
    <div style='background:#0969da;padding:16px;border-radius:8px 8px 0 0'>
      <h2 style='color:white;margin:0'>Sandelio ataskaita {now}</h2>
    </div>
    <div style='padding:16px;background:#f6f8fa'>
      <p>Viso: <strong>{len(items)}</strong> | Surinkta: <strong style='color:#1a7f37'>{len(surinkti)}</strong> | Perduota: <strong style='color:#0969da'>{len(perduoti)}</strong> | Laukia: <strong style='color:#9a6700'>{len(laukia)}</strong></p>
      <h3 style='color:#1a7f37;margin-top:12px'>Surinkta ({len(surinkti)})</h3>
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#e6f4ea'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#e6f4ea'>Laikas</th></tr>{rows(surinkti,'#1a7f37')}</table>
      <h3 style='color:#0969da;margin-top:12px'>Perduota ({len(perduoti)})</h3>
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#ddf4ff'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#ddf4ff'>Laikas</th></tr>{rows(perduoti,'#0969da')}</table>
      <h3 style='color:#9a6700;margin-top:12px'>Laukia ({len(laukia)})</h3>
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Laikas</th></tr>{rows(laukia,'#9a6700')}</table>
      <p style='color:#57606a;font-size:11px;margin-top:16px'>Issiusta is Sandelio sistemos</p>
    </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandelio ataskaita {now}"
        msg["From"] = f"Metalcraft <{smtp_user}>"
        msg["To"] = gaivejas
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, gaivejas, msg.as_string())
        return {"success": True, "message": f"Issiusta i {gaivejas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")

# PAGALBINES FUNKCIJOS
def _lk(l):
    return {"kodas": l.kodas,
            "registered": l.registruota.strftime("%Y-%m-%d %H:%M:%S") if l.registruota else "",
            "collected": l.surinkta,
            "collectedAt": l.surinkta_kada.strftime("%Y-%m-%d %H:%M:%S") if l.surinkta_kada else "",
            "delivered": l.perduota,
            "deliveredAt": l.perduota_kada.strftime("%Y-%m-%d %H:%M:%S") if l.perduota_kada else ""}

def _uzs(u):
    return {"id": u.uzs_id, "klientas": u.klientas, "aprasymas": u.aprasymas or "",
            "pastabos": u.pastabos or "", "statusas": u.statusas,
            "bendraSvoris": u.bendras_svoris, "detaliuSk": u.detaliu_sk,
            "sukurta": u.sukurta.strftime("%Y-%m-%d %H:%M:%S") if u.sukurta else ""}

def _det(d):
    return {"detId": d.det_id, "uzsakymoId": d.uzsakymo_id, "pavadinimas": d.pavadinimas,
            "storis": d.storis, "plotas": d.plotas, "kiekis": d.kiekis, "svoris": d.svoris,
            "konturas": d.konturas or "",
            "prideta": d.prideta.strftime("%Y-%m-%d %H:%M:%S") if d.prideta else ""}

def _stk(s):
    return {"id": s.stk_id, "storis": s.storis, "matmenys": s.matmenys,
            "svorisVnt": s.svoris_vnt, "gautaVnt": s.gauta_vnt, "sunaudotaVnt": s.sunaudota_vnt,
            "likoVnt": s.liko_vnt, "likoKg": s.liko_kg, "likoT": s.liko_t,
            "kainaKg": s.kaina_kg, "verte": s.verte,
            "prideta": s.prideta.strftime("%Y-%m-%d %H:%M:%S") if s.prideta else "",
            "pastabos": s.pastabos or ""}

def _recalc(uzs_id, db):
    dets = db.query(Detale).filter(Detale.uzsakymo_id == uzs_id).all()
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if u:
        u.bendras_svoris = round(sum(d.svoris for d in dets), 3)
        u.detaliu_sk = len(dets)
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
