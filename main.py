from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os

from database import get_db, init_db, Lakstai, Etapas, Uzsakymas, Detale, Sandelis, SandelioIstorijia

app = FastAPI(title="Sandelio Sistema")
TANKIS = 8000

_CSS = """*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#f6f8fa;--s1:#ffffff;--s2:#f0f2f4;--s3:#e1e4e8;
  --bd:#d0d7de;--bd2:#afb8c1;
  --tx:#1f2328;--tx2:#57606a;--tx3:#848d97;
  --ac:#0969da;--ac2:#0550ae;--ac-bg:rgba(9,105,218,.08);
  --gn:#1a7f37;--gn-bg:rgba(26,127,55,.08);--gn-bd:rgba(26,127,55,.3);
  --yw:#9a6700;--yw-bg:rgba(154,103,0,.08);--yw-bd:rgba(154,103,0,.3);
  --rd:#cf222e;--rd-bg:rgba(207,34,46,.08);--rd-bd:rgba(207,34,46,.3);
  --pp:#6639ba;--pp-bg:rgba(102,57,186,.08);
  --or:#953800;
}
body{background:var(--bg);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;min-height:100vh;font-size:14px}

nav{background:var(--s1);border-bottom:1px solid var(--bd);padding:0 16px;height:52px;display:flex;align-items:center;gap:8px;position:sticky;top:0;z-index:50}
.brand{font-size:15px;font-weight:800;display:flex;align-items:center;gap:8px;flex-shrink:0}
.brand-ico{width:26px;height:26px;background:linear-gradient(135deg,#0969da,#6639ba);border-radius:6px}
.tabs{display:flex;height:100%;overflow-x:auto;flex:1;justify-content:center}
.tab{padding:0 13px;height:100%;display:flex;align-items:center;gap:4px;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;border:none;background:none;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}
.tab:hover{color:var(--tx)}.tab.active{color:var(--ac);border-bottom-color:var(--ac)}
.bdg{background:var(--ac);color:#fff;font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px}
.bdg.y{background:var(--yw)}.bdg.gray{background:var(--s3);color:var(--tx2)}.bdg.r{background:var(--rd)}
.nav-r{margin-left:auto;display:flex;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--bd2)}.dot.ok{background:var(--gn)}.dot.err{background:var(--rd)}

.view{display:none}.view.active{display:block}
.page-wrap{padding:16px;max-width:1000px;margin:0 auto}
.ph{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ph-t{font-size:18px;font-weight:800}.ph-s{font-size:11px;color:var(--tx2);margin-top:2px}

.btn{padding:7px 14px;border:none;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:12px;cursor:pointer;border-radius:6px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;white-space:nowrap}
.btn-p{background:var(--ac);color:#fff}.btn-p:hover{background:var(--ac2)}
.btn-s{background:transparent;border:1px solid var(--bd);color:var(--tx2)}.btn-s:hover{border-color:var(--tx);color:var(--tx)}
.btn-g{background:var(--gn-bg);border:1px solid var(--gn-bd);color:var(--gn)}.btn-g:hover{background:var(--gn);color:#fff}
.btn-d{background:transparent;border:1px solid transparent;color:var(--tx3)}.btn-d:hover{border-color:var(--rd-bd);color:var(--rd);background:var(--rd-bg)}
.btn-y{background:var(--yw-bg);border:1px solid var(--yw-bd);color:var(--yw)}.btn-y:hover{background:var(--yw);color:#fff}
.btn-sm{padding:4px 9px;font-size:11px}

.fl{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:4px}
input[type=text],input[type=number],input[type=date],input[type=email],textarea,select{width:100%;padding:7px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;outline:none;border-radius:6px;transition:border-color .15s;-webkit-appearance:none}
input:focus,textarea:focus,select:focus{border-color:var(--ac)}
textarea{resize:vertical;min-height:60px}
option{background:var(--s1)}

.card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;margin-bottom:12px}
.card-h{padding:12px 16px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.card-t{font-weight:700;font-size:14px}
.ct{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.ct::after{content:'';flex:1;height:1px;background:var(--bd)}

.mbg{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:24px;max-width:440px;width:100%;margin:auto}
.mh{font-size:17px;font-weight:800;margin-bottom:16px}
.mf{display:flex;flex-direction:column;gap:12px}
.mb{display:flex;gap:8px;justify-content:flex-end;margin-top:6px}

.toast{position:fixed;bottom:14px;right:14px;left:14px;max-width:340px;margin:0 auto;padding:11px 14px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;background:var(--s1);border:1px solid var(--bd);border-left:3px solid var(--gn);box-shadow:0 8px 24px rgba(0,0,0,.15);transform:translateY(70px);opacity:0;transition:all .25s;z-index:300;border-radius:6px}
.toast.w{border-left-color:var(--rd)}.toast.b{border-left-color:var(--ac)}.toast.p{border-left-color:var(--pp)}
.toast.show{transform:translateY(0);opacity:1}
.sp{display:inline-block;width:11px;height:11px;border:2px solid var(--bd2);border-top-color:var(--ac);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:4px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.empty-s{padding:40px;text-align:center;color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:12px}

/* LAKŠTAI */
.lk-wrap{display:grid;grid-template-columns:1fr 290px;min-height:calc(100vh - 52px)}
@media(max-width:680px){.lk-wrap{grid-template-columns:1fr}}
.lk-main{padding:16px;display:flex;flex-direction:column;gap:10px}
.lk-sb{border-left:1px solid var(--bd);background:var(--s1);display:flex;flex-direction:column}
.scan-f{position:relative}.scan-ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:16px;pointer-events:none;color:var(--tx3)}
.scan-inp{padding:11px 14px 11px 40px!important;font-size:17px!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important}
.scan-inp:focus{border-color:var(--ac)!important;box-shadow:0 0 0 3px var(--ac-bg)}
.hint{margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3)}
.steps{display:flex;gap:4px;margin-top:10px}
.step{flex:1;height:3px;background:var(--bd);border-radius:2px}
.s1{background:var(--yw)}.s2{background:var(--gn)}.s3{background:var(--ac)}
.step-lbl{display:flex;justify-content:space-between;margin-top:4px;font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.res{border:1px solid var(--bd);border-radius:8px;padding:12px 14px;animation:fadeUp .2s ease}
.res.rn{background:var(--yw-bg);border-color:var(--yw-bd)}.res.rc{background:var(--gn-bg);border-color:var(--gn-bd)}
.res.rd{background:var(--ac-bg);border-color:rgba(9,105,218,.3)}.res.re{background:var(--rd-bg);border-color:var(--rd-bd)}
.res.rp{background:var(--pp-bg);border-color:rgba(102,57,186,.3)}.res.ra{background:var(--gn-bg);border-color:var(--gn-bd)}
.rt{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}
.res.rn .rt{color:var(--yw)}.res.rc .rt{color:var(--gn)}.res.rd .rt{color:var(--ac)}.res.re .rt{color:var(--rd)}.res.rp .rt{color:var(--pp)}.res.ra .rt{color:var(--gn)}
.rc{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace}.rs{font-size:11px;color:var(--tx2);margin-top:2px}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
@media(max-width:480px){.stats-row{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.sn{font-size:22px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace}
.sn.a{color:var(--ac)}.sn.g{color:var(--gn)}.sn.b{color:var(--ac)}.sn.y{color:var(--yw)}
.sl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.prog-card{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px}
.pt{display:flex;justify-content:space-between;margin-bottom:6px;font-size:10px;color:var(--tx2);font-family:'JetBrains Mono',monospace}
.pct{color:var(--gn);font-weight:700}
.ptr{height:6px;background:var(--s2);border-radius:3px;overflow:hidden;position:relative}
.pfc{height:100%;background:var(--gn);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px}
.pfd{height:100%;background:var(--ac);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px;opacity:.4}
.stbar{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:12px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.stbar-lbl{font-weight:700;font-size:13px;white-space:nowrap}.stbar input{flex:1;min-width:130px}
.stbar-hint{font-size:9px;color:var(--tx3);width:100%;font-family:'JetBrains Mono',monospace}
.sbh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}
.sbt{font-weight:700;font-size:12px}.sbsr{position:relative;width:100%}
.sbsr input{padding:5px 10px 5px 26px;font-size:11px}.sbs-i{position:absolute;left:8px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--tx3);pointer-events:none}
.frow{padding:6px 14px;border-bottom:1px solid var(--bd);display:flex;gap:4px;flex-wrap:wrap}
.fb{padding:3px 8px;background:transparent;border:1px solid var(--bd);color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:9px;cursor:pointer;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;transition:all .15s}
.fb.active{background:var(--tx);color:var(--bg);border-color:var(--tx);font-weight:700}
.olist{flex:1;overflow-y:auto}
.oi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:6px;transition:background .1s}
.oi:hover{background:var(--s2)}
.od{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.oi.sc .od{background:var(--gn)}.oi.sdd .od{background:var(--ac)}
.oc{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ost{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700;flex-shrink:0}
.ost.s0{background:var(--yw-bg);color:var(--yw)}.ost.s1{background:var(--gn-bg);color:var(--gn)}.ost.s2{background:var(--ac-bg);color:var(--ac)}
.otm{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);flex-shrink:0}

/* SANDĖLIS */
.stk-sum{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin-bottom:14px}
.stk-s{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.stk-n{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.stk-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.stk-row{padding:10px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.stk-row:last-child{border-bottom:none}.stk-row:hover{background:var(--s2)}
@media(max-width:600px){.stk-row{grid-template-columns:1fr 1fr;gap:6px}}
.stk-thick{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:var(--ac)}
.stk-thick span{font-size:10px;color:var(--tx3)}
.stk-dims{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.stk-num{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700}
.stk-num.ok{color:var(--gn)}.stk-num.warn{color:var(--yw)}.stk-num.empty{color:var(--rd)}
.stk-sub{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.stk-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--or)}
.stk-acts{display:flex;gap:4px}
.stk-tot{padding:10px 16px;background:var(--s2);border-top:2px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.hist-row{padding:8px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:130px 60px 90px 60px 80px 80px;align-items:center;gap:8px;font-size:12px}
.hist-row:last-child{border-bottom:none}.hist-row:hover{background:var(--s2)}
.hist-act{font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700}
.hist-act.G{background:var(--gn-bg);color:var(--gn)}.hist-act.S{background:var(--rd-bg);color:var(--rd)}
.rec-prev{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--tx2)}

/* DXF */
.sumr{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin-bottom:14px}
.smc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.smn{font-size:20px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.sml{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.fbar{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.si{padding:5px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:11px;outline:none;border-radius:6px;min-width:150px}
.si:focus{border-color:var(--ac)}
.og{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.ocard{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.ocard:hover{border-color:var(--ac);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.oct{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.oid{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3)}
.stb{font-family:'JetBrains Mono',monospace;font-size:9px;padding:2px 7px;border-radius:4px;font-weight:700}
.stb.Naujas{background:var(--yw-bg);color:var(--yw);border:1px solid var(--yw-bd)}
.stb.Vykdomas{background:var(--ac-bg);color:var(--ac);border:1px solid rgba(9,105,218,.3)}
.stb.Baigtas{background:var(--gn-bg);color:var(--gn);border:1px solid var(--gn-bd)}
.ocli{font-size:14px;font-weight:700;margin-bottom:2px}.ocdesc{font-size:11px;color:var(--tx2);margin-bottom:10px}
.ocm{display:flex;gap:10px;flex-wrap:wrap}
.ocmi{font-family:'JetBrains Mono',monospace;font-size:10px}
.ocmi .v{color:var(--ac);font-weight:700}.ocmi .l{color:var(--tx3)}
.back{display:flex;align-items:center;gap:5px;color:var(--tx2);font-size:12px;cursor:pointer;margin-bottom:14px;font-family:'JetBrains Mono',monospace;transition:color .15s}
.back:hover{color:var(--ac)}
.oi-top{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px}
.oi-t{font-size:18px;font-weight:800}.oi-s{font-size:11px;color:var(--tx2);margin-top:2px}
.wbig{font-size:28px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac);line-height:1}
.wlbl{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px}
.stsel{padding:5px 10px;background:var(--s2);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:10px;outline:none;border-radius:6px;width:auto}
.dropz{border:2px dashed var(--bd);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:all .2s;position:relative}
.dropz:hover,.dropz.drag{border-color:var(--ac);background:var(--ac-bg)}
.dropz input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer}
.dz-t{font-size:12px;color:var(--tx2)}.dz-s{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.cvw{background:var(--s2);border:1px solid var(--bd);border-radius:6px;margin-top:10px;overflow:hidden}
canvas{display:block;max-width:100%;height:150px}
.pf{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:14px;margin-top:10px;animation:fadeUp .2s ease}
.wp{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;margin-bottom:10px}
.wv{font-size:19px;font-weight:700;color:var(--ac);font-family:'JetBrains Mono',monospace}
.wl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-top:1px;font-family:'JetBrains Mono',monospace}
.wa{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.fgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:480px){.fgrid{grid-template-columns:1fr}}
.msec{margin-top:12px;border-top:1px solid var(--bd);padding-top:12px}
.mlbl{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.svor-d{padding:7px 10px;background:var(--s1);border:1px solid var(--bd);border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ac)}
table{width:100%;border-collapse:collapse}
th{padding:7px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;text-align:left;border-bottom:1px solid var(--bd);background:var(--s2)}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}tr:hover td{background:var(--s2)}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px}
.num{color:var(--ac);font-weight:700;font-family:'JetBrains Mono',monospace}
.dttot{padding:10px 12px;background:var(--s2);border-top:2px solid var(--bd);display:flex;justify-content:flex-end;gap:14px;font-family:'JetBrains Mono',monospace;font-size:11px}
.tot{color:var(--ac);font-weight:700;font-size:13px}
.det-grp-hdr{padding:6px 12px;background:var(--s2);border-top:2px solid var(--bd);border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:10px}
.det-grp-t{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800;color:var(--ac)}
.det-grp-s{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.det-inp{padding:3px 6px!important;font-size:11px!important;width:auto!important}

/* ARCHYVAI */
.sc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:14px}
.scc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.scc:hover{border-color:var(--ac);transform:translateY(-1px)}.scc.open{border-color:var(--ac)}
.scn{font-size:13px;font-weight:700;margin-bottom:8px}
.scst{display:flex;gap:10px}
.scst .n{font-size:15px;font-weight:700;display:block;line-height:1;font-family:'JetBrains Mono',monospace}
.scst .n.g{color:var(--gn)}.scst .n.b{color:var(--ac)}.scst .n.r{color:var(--rd)}
.scst .l{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase}
.scp{margin-top:8px;height:3px;background:var(--s2);border-radius:2px;overflow:hidden}
.scpf{height:100%;background:var(--gn);border-radius:2px}
.adbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;margin-top:10px}
.adh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.adt{font-weight:700;font-size:13px}
.adlist{max-height:320px;overflow-y:auto}
.adi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:7px}
.addot{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.adi.sc .addot{background:var(--gn)}.adi.sdd .addot{background:var(--ac)}
.adcode{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1}
.adtag{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700}
.adtag.r{background:var(--yw-bg);color:var(--yw)}.adtag.c{background:var(--gn-bg);color:var(--gn)}.adtag.d{background:var(--ac-bg);color:var(--ac)}
.adtime{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx3)}

/* ATASKAITA */
.rep-s{margin-bottom:14px}
.rep-st{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--bd)}
.rep-sr{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}
.rep-sc{background:var(--s2);border-radius:6px;padding:10px 12px}
.rep-sc .n{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.rep-sc .l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}

/* PRINT */
@media print{body *{visibility:hidden!important}#printArea,#printArea *{visibility:visible!important}#printArea{position:fixed!important;left:0;top:0;width:100%}@page{margin:6mm;size:A4}}
.pmb{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:flex-start;justify-content:center;padding:16px;overflow-y:auto}
.pm{background:white;color:#000;max-width:210mm;width:100%;border-radius:8px;overflow:hidden;margin:auto}
.pbr{display:flex;gap:8px;padding:10px 14px;background:#f5f5f5;border-bottom:1px solid #ddd}
#printArea{background:white;color:#000;font-family:Arial,sans-serif;padding:10mm 8mm}
.pph{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}
.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666;font-family:monospace}
.ppbc{text-align:right;margin:2mm 0}
.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}
.ppi-l{font-size:7pt;color:#888;text-transform:uppercase;margin-bottom:.5mm}.ppi-v{font-size:10pt;font-weight:700}
.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}
.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}
.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}
.pptable tr:nth-child(even) td{background:#f9f9f9}
.ppsign{display:flex;gap:10mm;margin-top:5mm}
.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}
.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}
"""

_DXFJS = """
// DXF PARSERIS
const TANKIS = 8000;

function thickFromName(name){
  const m=name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)[ ]*mm/)||name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)/)||name.match(/([0-9]+(?:[.][0-9]+)?)[ ]*mm/);
  if(!m)return null;
  const v=parseFloat(m[1]);
  return STORIAI.includes(v)?v:null;
}

function qtyFromName(name){
  const m=name.match(/[_\x2D\x20]([0-9]+)[ ]*vnt/i)||name.match(/^([0-9]+)[ ]*vnt/i);
  if(!m)return null;
  const v=parseInt(m[1]);
  return v>0&&v<=9999?v:null;
}

function pDxf(txt){
  const lines=txt.split(/\r?\n/);
  const segs=[];
  let inE=false,curType=null,curV={},sf=1;

  for(let j=0;j<lines.length-1;j++){
    if(lines[j].trim()==='70'&&j>=2&&lines[j-2].trim()==='$INSUNITS'){
      const u=parseInt(lines[j+1]);if(u===1)sf=25.4;else if(u===6)sf=10;else if(u===5)sf=.1;
    }
  }

  const r4=v=>Math.round(v*10000)/10000;

  function saveSeg(t,v){
    if(t==='LINE'&&v._x1!==undefined&&v._y1!==undefined&&v._x2!==undefined&&v._y2!==undefined){
      segs.push({type:'L',x1:r4(v._x1*sf),y1:r4(v._y1*sf),x2:r4(v._x2*sf),y2:r4(v._y2*sf)});
    } else if(t==='CIRCLE'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf)});
    } else if((t==='LWPOLYLINE'||t==='POLYLINE')&&v._xs&&v._xs.length>=3){
      segs.push({type:'P',pts:v._xs.map((x,i)=>({x:r4(x*sf),y:r4((v._ys[i]||0)*sf)})),closed:((v[70]||0)&1)===1});
    } else if(t==='ARC'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf),arc:true});
    }
  }

  let i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i++;continue;}
    const val=(lines[i+1]||'').trim();
    if(code===2&&val==='ENTITIES'){inE=true;i+=2;continue;}
    if(code===0&&val==='ENDSEC'&&inE){saveSeg(curType,curV);break;}
    if(!inE){i+=2;continue;}
    if(code===0){saveSeg(curType,curV);curType=val;curV={};}
    else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._x1=n;}
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._y1=n;}
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11){curV._x2=n;}
        else if(code===21){curV._y2=n;}
        else if(code===70){curV[70]=parseInt(val)||0;}
        else{curV[code]=n;}
      }
    }
    i+=2;
  }

  let area=0;
  segs.filter(s=>s.type==='C'&&!s.arc).forEach(s=>area+=Math.PI*s.r*s.r);
  segs.filter(s=>s.type==='P').forEach(s=>{
    const pts=s.pts,n=pts.length;let a=0;
    for(let i=0;i<n;i++){const j=(i+1)%n;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}
    area+=Math.abs(a)/2;
  });
  const lineSegs=segs.filter(s=>s.type==='L');
  if(lineSegs.length){
    const adj=new Map();
    const key=p=>Math.round(p.x*100)/100+','+Math.round(p.y*100)/100;
    lineSegs.forEach(s=>{
      const p1={x:s.x1,y:s.y1},p2={x:s.x2,y:s.y2};
      const k1=key(p1),k2=key(p2);
      if(!adj.has(k1))adj.set(k1,{pt:p1,nb:[]});
      if(!adj.has(k2))adj.set(k2,{pt:p2,nb:[]});
      adj.get(k1).nb.push(k2);adj.get(k2).nb.push(k1);
    });
    const visitedE=new Set(),visitedP=new Set();
    adj.forEach((v,startK)=>{
      if(visitedP.has(startK))return;
      const path=[v.pt];let curK=startK;
      for(let iter=0;iter<adj.size*2;iter++){
        visitedP.add(curK);
        const nb=adj.get(curK).nb;let nextK=null;
        for(const nk of nb){
          const ek=[curK,nk].sort().join('|');
          if(!visitedE.has(ek)){visitedE.add(ek);nextK=nk;break;}
        }
        if(!nextK)break;
        path.push(adj.get(nextK).pt);curK=nextK;
      }
      if(path.length>=3){
        let a=0;const n=path.length;
        for(let i=0;i<n;i++){const j=(i+1)%n;a+=path[i].x*path[j].y-path[j].x*path[i].y;}
        area+=Math.abs(a)/2;
      }
    });
  }

  // Matmenys
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  segs.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  const dimW=isFinite(minX)?Math.round(maxX-minX):0;
  const dimH=isFinite(minY)?Math.round(maxY-minY):0;

  return{entities:segs,areaCm2:area/100,dimW,dimH};
}

function serializeContour(ents,dimW,dimH){
  try{
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    ents.forEach(s=>{
      if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
      else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
      else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
    });
    if(!isFinite(minX))return'';
    const W=maxX-minX||1,H=maxY-minY||1,sc=100/Math.max(W,H);
    const nx=x=>Math.round((x-minX)*sc*10)/10;
    const ny=y=>Math.round((maxY-y)*sc*10)/10;
    const paths=[];
    ents.forEach(s=>{
      if(s.type==='C'&&!s.arc)paths.push('C'+nx(s.cx)+','+ny(s.cy)+','+Math.round(s.r*sc*10)/10);
      else if(s.type==='P'){const step=Math.max(1,Math.floor(s.pts.length/50));const pts=[];for(let i=0;i<s.pts.length;i+=step)pts.push(nx(s.pts[i].x)+','+ny(s.pts[i].y));paths.push('L'+pts.join(' '));}
      else if(s.type==='L')paths.push('L'+nx(s.x1)+','+ny(s.y1)+' '+nx(s.x2)+','+ny(s.y2));
    });
    return('D:'+dimW+'x'+dimH+'|'+paths.join('|')).slice(0,2000);
  }catch(e){return'';}
}

function calcDims(d){
  if(d.konturas){
    const m=d.konturas.match(/D:([0-9]+)x([0-9]+)/);
    if(m)return m[1]+'×'+m[2]+'mm';
    try{
      let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
      d.konturas.split('|').forEach(p=>{
        if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);if(!isNaN(cx)){minX=Math.min(minX,cx-r);maxX=Math.max(maxX,cx+r);minY=Math.min(minY,cy-r);maxY=Math.max(maxY,cy+r);}}
        else if(p.startsWith('L')){p.slice(1).trim().split(' ').forEach(pt=>{const[x,y]=pt.split(',').map(Number);if(!isNaN(x)&&!isNaN(y)){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}});}
      });
      if(isFinite(minX)&&maxX>minX&&maxY>minY){
        const ratio=(maxX-minX)/(maxY-minY);const area=parseFloat(d.plotas)||0;
        if(area>0){const Hmm=Math.round(Math.sqrt(area*100/ratio));return Math.round(ratio*Hmm)+'×'+Hmm+'mm';}
      }
    }catch(e){}
  }
  const area=parseFloat(d.plotas)||0;
  if(!area)return'—';
  return'~'+Math.round(Math.sqrt(area*100))+'mm';
}

function drawPrev(ents){
  const w=document.getElementById('cvW'),c=document.getElementById('dxfCv');
  w.style.display='block';
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  ents.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  if(!isFinite(minX))return;
  const W=w.clientWidth||400,H=150;c.width=W;c.height=H;
  const ctx=c.getContext('2d');ctx.fillStyle='#f0f2f4';ctx.fillRect(0,0,W,H);
  const rX=maxX-minX||1,rY=maxY-minY||1,sc=Math.min((W-30)/rX,(H-30)/rY)*.9;
  const oX=(W-rX*sc)/2-minX*sc,oY=(H+rY*sc)/2+minY*sc;
  ctx.strokeStyle='#0969da';ctx.lineWidth=1.5;
  ents.forEach(s=>{
    ctx.beginPath();
    if(s.type==='C')ctx.arc(s.cx*sc+oX,oY-s.cy*sc,s.r*sc,0,Math.PI*2);
    else if(s.type==='P'&&s.pts.length){ctx.moveTo(s.pts[0].x*sc+oX,oY-s.pts[0].y*sc);for(let i=1;i<s.pts.length;i++)ctx.lineTo(s.pts[i].x*sc+oX,oY-s.pts[i].y*sc);if(s.closed)ctx.closePath();}
    else if(s.type==='L'){ctx.moveTo(s.x1*sc+oX,oY-s.y1*sc);ctx.lineTo(s.x2*sc+oX,oY-s.y2*sc);}
    ctx.stroke();
  });
}

function drawContourSvg(konturas,sizeMm=14){
  if(!konturas)return'';
  try{
    const parts=konturas.replace(/^D:[0-9]+x[0-9]+[|]/,'').split('|');
    let paths='';
    parts.forEach(p=>{
      if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);paths+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#000" stroke-width="2"/>`;}
      else if(p.startsWith('L')){const pts=p.slice(1).trim().split(' ');if(pts.length<2)return;const d='M'+pts[0]+' '+pts.slice(1).map(pt=>'L'+pt).join(' ');paths+=`<path d="${d}" fill="none" stroke="#000" stroke-width="2"/>`;}
    });
    const s=sizeMm+'mm';
    return`<svg viewBox="-5 -5 110 110" width="${s}" height="${s}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">${paths}</svg>`;
  }catch(e){return'';}
}

"""

_MAINJS = """
// SANDĖLIO SISTEMA – main.js

let lkOrders=[],lkF='all',lkLC=null,lkLT=0;
let dxfOrders=[],dxfF='all',dxfDets=[],curOrd=null,curArea=0,curContour='';
let stock=[],history=[],stages=[],archOpen=null;
let pendingSt='',curStockId=null;
let settings={defaultPrice:0,lowAlert:2};

// GARSAS
let actx=null;
function ga(){if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();return actx;}
function beep(t){try{const c=ga();if(c.state==='suspended')c.resume();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;if(t==='new'){o.frequency.value=880;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.2);o.start(n);o.stop(n+.2);}else if(t==='col'){o.frequency.setValueAtTime(660,n);o.frequency.setValueAtTime(880,n+.12);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.3);o.start(n);o.stop(n+.3);}else if(t==='del'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(660,n+.1);o.frequency.setValueAtTime(880,n+.2);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='err'){o.type='sawtooth';o.frequency.value=220;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='dup'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(220,n+.15);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.35);o.start(n);o.stop(n+.35);}}catch(e){}}

// API
async function api(method,url,data){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(data)opts.body=JSON.stringify(data);
  const r=await fetch(url,opts);
  if(!r.ok)throw new Error(r.statusText);
  return r.json();
}

// INIT
window.onload=()=>{
  loadAll();
  const lt=localStorage.getItem('lastThick');
  if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}
  setPeriod(30);
  const dz=document.getElementById('dropZ');
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
};
document.addEventListener('click',e=>{if(actx&&actx.state==='suspended')actx.resume();if(document.getElementById('view-lk').classList.contains('active')&&!e.target.closest('input,button,select'))focusScan();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mbg').forEach(m=>m.style.display='none');});

async function loadAll(){await loadLk();await loadDxfOrds();await loadStock();await loadHist();await loadStages();}

// NAVIGACIJA
function SW(v){
  document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById('view-'+v).classList.add('active');
  const t=document.getElementById('tab-'+v);if(t)t.classList.add('active');
  if(v==='lk')focusScan();
  if(v==='dv'){const lt=localStorage.getItem('lastThick');if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}}
}
function CM(id){document.getElementById(id).style.display='none';}
function focusScan(){try{document.getElementById('scanInp').focus();}catch(e){}}
function toast(msg,w=false,t=''){const el=document.getElementById('toast');el.textContent=msg;el.className='toast '+(w?'w':t)+' show';clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),3000);}

// ════ LAKŠTAI ════
const scanInp=document.getElementById('scanInp');
scanInp.addEventListener('keydown',async e=>{if(e.key==='Enter'){const c=scanInp.value.trim();if(c){scanInp.value='';await handleScan(c);}}});

async function handleScan(kodas){
  const now=Date.now();
  if(kodas===lkLC&&now-lkLT<3000){lkRes('rp','DUBLIKATAS',kodas,'Tas pats kodas du kartus!');beep('dup');toast('Dublikatas: '+kodas,false,'p');lkLC=null;return;}
  lkLC=kodas;lkLT=now;
  const local=lkOrders.find(o=>o.kodas===kodas);
  if(local){
    if(local.delivered){lkRes('ra','JAU PERDUOTA',kodas,'Perduota: '+local.deliveredAt);beep('err');return;}
    if(local.collected){
      lkRes('rd','PERDUOTA',kodas,'3× — siunčiama...');beep('del');
      local.delivered=true;local.deliveredAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Perduota: '+kodas,false,'b');else{local.delivered=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }else{
      lkRes('rc','SURINKTA',kodas,'2× — siunčiama...');beep('col');
      local.collected=true;local.collectedAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Surinkta: '+kodas);else{local.collected=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }
    return;
  }
  lkRes('rn','NAUJAS',kodas,'1× — siunčiama...');beep('new');
  const newOrd={kodas,registered:nowS(),collected:false,collectedAt:'',delivered:false,deliveredAt:''};
  lkOrders.push(newOrd);lkStats();rlkList();
  api('POST','/api/lakstai/register',{kodas}).then(r=>{
    if(r.success)toast('Užregistruota: '+kodas);
    else if(r.alreadyExists){lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkAddL(r.order);lkStats();rlkList();handleScan(kodas);}
    else{lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkRes('re','KLAIDA',kodas,'Nepavyko');beep('err');lkStats();rlkList();}
  });
}

function lkRes(c,t,kodas,s){
  const b=document.getElementById('lkRes');
  b.className='res '+c;b.style.display='block';
  document.getElementById('lkRt').textContent=t;
  document.getElementById('lkRc').textContent=kodas;
  document.getElementById('lkRs').textContent=s;
}

async function loadLk(){
  try{const r=await api('GET','/api/lakstai');lkOrders=r.orders||[];lkStats();rlkList();document.getElementById('connDot').className='dot ok';}
  catch(e){document.getElementById('connDot').className='dot err';toast('Nepavyko prisijungti',true);}
}
function lkAddL(o){const i=lkOrders.findIndex(x=>x.kodas===o.kodas);if(i>=0)lkOrders[i]=o;else lkOrders.push(o);}
function lkStats(){
  const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length,p=lkOrders.filter(o=>!o.collected).length;
  const pc=t>0?Math.round(c/t*100):0,pd=t>0?Math.round(d/t*100):0;
  document.getElementById('lkT').textContent=t;document.getElementById('lkC').textContent=c;
  document.getElementById('lkD').textContent=d;document.getElementById('lkP').textContent=p;
  document.getElementById('lkPct').textContent=pc+'%';
  document.getElementById('lkPfc').style.width=pc+'%';document.getElementById('lkPfd').style.width=pd+'%';
  document.getElementById('lkBdg').textContent=p||t;
}
function lkFlt(f,b){lkF=f;document.querySelectorAll('.frow .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rlkList();}
function sortLk(l){return[...l].sort((a,b)=>{const n=s=>parseInt((s.match(/[0-9]+/)||[0])[0]);return n(a.kodas)-n(b.kodas);});}
function rlkList(){
  const el=document.getElementById('lkList'),q=(document.getElementById('lkSrch').value||'').toLowerCase();
  let l=sortLk(lkOrders);
  if(lkF==='p')l=l.filter(o=>!o.collected);if(lkF==='c')l=l.filter(o=>o.collected&&!o.delivered);if(lkF==='d')l=l.filter(o=>o.delivered);
  if(q)l=l.filter(o=>o.kodas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(lkOrders.length===0?'Nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>{
    const sc=o.delivered?'sdd':o.collected?'sc':'';
    const sl=o.delivered?'s2':o.collected?'s1':'s0';
    const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
    const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);
    return`<div class="oi ${sc}"><div class="od"></div><div class="oc">${o.kodas}</div><span class="ost ${sl}">${st}</span><div class="otm">${tm}</div><button class="btn btn-d btn-sm" onclick="lkDel('${o.kodas}')">✕</button></div>`;
  }).join('');
}
async function lkDel(k){if(!confirm('Ištrinti "'+k+'"?'))return;await api('DELETE','/api/lakstai/'+k);lkOrders=lkOrders.filter(o=>o.kodas!==k);lkStats();rlkList();toast('Ištrinta');}
function askStage(){
  const n=document.getElementById('stageInp').value.trim();
  if(!n){toast('Įvesk etapo pavadinimą!',true);return;}
  if(!lkOrders.length){toast('Nėra užsakymų',true);return;}
  pendingSt=n;const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length;
  document.getElementById('stMn').textContent='Etapas: "'+n+'"';
  document.getElementById('stMs').innerHTML='Iš viso: <strong>'+t+'</strong><br>Surinkta: <strong>'+c+'</strong><br>Perduota: <strong>'+d+'</strong><br>Laukia: <strong>'+(t-c)+'</strong>';
  document.getElementById('stModal').style.display='flex';
}
async function confirmStage(){
  CM('stModal');
  const r=await api('POST','/api/lakstai/archive',{pavadinimas:pendingSt});
  if(r.success){lkOrders=[];document.getElementById('stageInp').value='';lkStats();rlkList();await loadStages();beep('del');toast('Archyvuota: "'+r.archiveName+'"');lkRes('ra','ARCHYVUOTA',r.archiveName,r.collected+'/'+r.total+' surinkta');}
  else toast(r.message||'Klaida',true);
  focusScan();
}

// ════ SANDĖLIS ════
async function loadStock(){try{const r=await api('GET','/api/sandelis');stock=r.stock||[];rStock();document.getElementById('stkBdg').textContent=stock.length;}catch(e){}}
async function loadHist(){try{const r=await api('GET','/api/sandelis/istorija');history=r.history||[];rHist();}catch(e){}}

function rStock(){
  const el=document.getElementById('stkTbl'),su=document.getElementById('stkSum');
  if(!stock.length){el.innerHTML='<div class="empty-s">Sandėlis tuščias</div>';su.innerHTML='';return;}
  const totVnt=stock.reduce((s,r)=>s+r.likoVnt,0);
  const totKg=stock.reduce((s,r)=>s+r.likoKg,0);
  const totT=Math.round(totKg/10)/100;
  const totVal=stock.reduce((s,r)=>s+r.verte,0);
  const byT={};stock.forEach(r=>{if(!byT[r.storis])byT[r.storis]={vnt:0,kg:0};byT[r.storis].vnt+=r.likoVnt;byT[r.storis].kg+=r.likoKg;});
  su.innerHTML=`<div class="stk-s"><div class="stk-n">${totVnt}</div><div class="stk-l">Viso vnt.</div></div><div class="stk-s"><div class="stk-n">${totKg.toFixed(1)}</div><div class="stk-l">Viso kg</div></div><div class="stk-s"><div class="stk-n" style="color:var(--gn)">${totT}</div><div class="stk-l">Tonos</div></div><div class="stk-s"><div class="stk-n" style="color:var(--or)">${totVal.toFixed(2)}</div><div class="stk-l">Vertė €</div></div>`+
    Object.entries(byT).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).map(([t,v])=>`<div class="stk-s"><div class="stk-n" style="font-size:15px">${v.vnt}vnt</div><div class="stk-l">${t}mm · ${(Math.round(v.kg/10)/100).toFixed(2)}t</div></div>`).join('');
  const sorted=[...stock].sort((a,b)=>a.storis-b.storis);
  el.innerHTML=sorted.map(r=>{
    const nc=r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return`<div class="stk-row"><div><div class="stk-thick">${r.storis}<span>mm</span></div></div><div><div class="stk-dims">${r.matmenys}mm</div><div class="stk-sub">${r.pastabos||''}</div></div><div><div class="stk-num ${nc}">${r.likoVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:13px;color:var(--tx2)">${r.likoKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${r.likoT.toFixed(3)}</div><div class="stk-sub">t</div></div><div><div class="stk-val">${r.verte.toFixed(2)}€</div><div class="stk-sub">${r.kainaKg>0?r.kainaKg+'€/kg':''}</div></div><div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse('${r.id}','${r.storis}mm ${r.matmenys}',${r.likoVnt})">−</button><button class="btn btn-d btn-sm" onclick="delStk('${r.id}')">✕</button></div></div>`;
  }).join('')+`<div class="stk-tot"><div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);font-weight:700">VISO</div><div></div><div><div class="stk-num" style="font-size:13px;color:var(--ac)">${totVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${totKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">${totT}</div><div class="stk-sub">t</div></div><div><div class="stk-val" style="font-size:13px;font-weight:800">${totVal.toFixed(2)}€</div></div><div></div></div>`;
}

function rHist(){
  const el=document.getElementById('histTbl');
  if(!history.length){el.innerHTML='<div class="empty-s">Dar nėra istorijos</div>';return;}
  el.innerHTML=`<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>${history.slice(0,50).map(h=>`<tr><td class="mono" style="font-size:10px;color:var(--tx3)">${h.data}</td><td><span class="hist-act ${h.veiksmas[0]}">${h.veiksmas}</span></td><td class="mono">${h.storis}mm</td><td class="mono" style="color:var(--tx2)">${h.matmenys}</td><td class="mono">${h.kiekis}vnt.</td><td class="num">${h.svorisIšViso.toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

function showRecv(){
  if(settings.defaultPrice)document.getElementById('recP').value=settings.defaultPrice;
  document.getElementById('recvModal').style.display='flex';
}
function rcRecv(){
  const t=parseFloat(document.getElementById('recThk').value)||0,w=parseFloat(document.getElementById('recW').value)||0,l=parseFloat(document.getElementById('recL').value)||0,q=parseInt(document.getElementById('recQ').value)||1,p=parseFloat(document.getElementById('recP').value)||0;
  if(!w||!l){document.getElementById('recPrev').textContent='Įvesk matmenis...';return;}
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100,totT=Math.round(tot/10)/100,val=p>0?Math.round(tot*p*100)/100:0;
  document.getElementById('recPrev').innerHTML=`1 lakštas: <strong style="color:var(--ac)">${we}kg</strong> · ${q}vnt.: <strong style="color:var(--gn)">${tot}kg = ${totT}t</strong>${val>0?' · <strong style="color:var(--or)">'+val+'€</strong>':''}`;
}
async function doRecv(){
  const t=document.getElementById('recThk').value,w=document.getElementById('recW').value,l=document.getElementById('recL').value,q=document.getElementById('recQ').value,p=document.getElementById('recP').value,n=document.getElementById('recN').value;
  if(!w||!l){toast('Įvesk matmenis!',true);return;}
  const r=await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if(r.success){CM('recvModal');await loadStock();await loadHist();toast('Pridėta: '+q+'vnt. × '+t+'mm ('+r.likoT+'t)');}
}
function showUse(id,label,rem){curStockId=id;document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';document.getElementById('useQ').value=1;document.getElementById('useNote').value='';document.getElementById('useModal').style.display='flex';}
async function doUse(){
  const q=parseInt(document.getElementById('useQ').value)||1,n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if(r.success){CM('useModal');await loadStock();await loadHist();toast('Sunaudota: '+q+'vnt. Liko: '+r.likoVnt+'vnt.');}
  else toast('Klaida',true);
}
async function delStk(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/sandelis/'+id);await loadStock();toast('Ištrinta');}
function showSett(){document.getElementById('settP').value=settings.defaultPrice||'';document.getElementById('settL').value=settings.lowAlert||2;document.getElementById('settModal').style.display='flex';}
function saveSett(){settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;settings.lowAlert=parseInt(document.getElementById('settL').value)||2;CM('settModal');localStorage.setItem('sandSettings',JSON.stringify(settings));toast('Nustatymai išsaugoti');}

// ════ ARCHYVAI ════
async function loadStages(){try{const r=await api('GET','/api/etapai');stages=r.stages||[];document.getElementById('archBdg').textContent=stages.length;rStages();}catch(e){}}
function rStages(){
  const el=document.getElementById('stageCards');
  if(!stages.length){el.innerHTML='<div class="empty-s">Dar nėra archyvų</div>';return;}
  el.innerHTML=stages.map(s=>{
    const t=s.total||0,c=s.collected||0,d=s.delivered||0,p=s.pending||(t-c),pct=t>0?Math.round(c/t*100):0;
    return`<div class="scc ${archOpen===s.name?'open':''}" onclick="toggleArch('${s.name.replace(/'/g,"\\'")}')"><div class="scn">${s.name}</div><div class="scst"><div><span class="n">${t}</span><span class="l">Viso</span></div><div><span class="n g">${c}</span><span class="l">Surinkta</span></div><div><span class="n b">${d}</span><span class="l">Perduota</span></div><div><span class="n ${p>0?'r':'g'}">${p}</span><span class="l">Liko</span></div></div><div class="scp"><div class="scpf" style="width:${pct}%"></div></div></div>`;
  }).join('');
}
async function toggleArch(name){
  if(archOpen===name){archOpen=null;closeAd();rStages();return;}
  archOpen=name;rStages();
  document.getElementById('adTitle').textContent=name;
  document.getElementById('adList').innerHTML='<div class="empty-s"><span class="sp"></span> Kraunama...</div>';
  document.getElementById('adBox').style.display='block';
  try{
    const r=await api('GET','/api/etapai/'+encodeURIComponent(name));
    const items=sortLk(r.orders||[]);
    if(!items.length){document.getElementById('adList').innerHTML='<div class="empty-s">Tuščias</div>';return;}
    document.getElementById('adList').innerHTML=items.map(o=>{
      const sc=o.delivered?'sdd':o.collected?'sc':'';const tc=o.delivered?'d':o.collected?'c':'r';const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
      const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(0,16);
      return`<div class="adi ${sc}"><div class="addot"></div><div class="adcode">${o.kodas}</div><span class="adtag ${tc}">${st}</span><div class="adtime">${tm}</div></div>`;
    }).join('');
  }catch(e){}
}
function closeAd(){document.getElementById('adBox').style.display='none';archOpen=null;rStages();}

// ════ DXF ════
async function loadDxfOrds(){try{const r=await api('GET','/api/uzsakymai');dxfOrders=r.orders||[];dxfSum();rOrds();document.getElementById('dxfBdg').textContent=dxfOrders.length;}catch(e){}}
function dxfSum(){
  const t=dxfOrders.length,n=dxfOrders.filter(o=>o.statusas==='Naujas').length,a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length,d=dxfOrders.filter(o=>o.statusas==='Baigtas').length,w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML=`<div class="smc"><div class="smn a">${t}</div><div class="sml">Iš viso</div></div><div class="smc"><div class="smn" style="color:var(--yw)">${n}</div><div class="sml">Nauji</div></div><div class="smc"><div class="smn a">${a}</div><div class="sml">Vykdomi</div></div><div class="smc"><div class="smn" style="color:var(--gn)">${d}</div><div class="sml">Baigti</div></div><div class="smc"><div class="smn a">${w.toFixed(2)}</div><div class="sml">Svoris kg</div></div>`;
}
function dxfFlt(f,b){dxfF=f;document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rOrds();}
function rOrds(){
  const el=document.getElementById('ordsGrid'),q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all')l=l.filter(o=>o.statusas===dxfF);if(q)l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>`<div class="ocard" onclick="openOrd('${o.id}')"><div class="oct"><div class="oid">${o.id}</div><div style="display:flex;gap:4px"><span class="stb ${o.statusas}">${o.statusas}</span><button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd('${o.id}','${o.klientas.replace(/'/g,"\\'")}')">✕</button></div></div><div class="ocli">${o.klientas}</div><div class="ocdesc">${o.aprasymas||'—'}</div><div class="ocm"><div class="ocmi"><span class="v">${o.bendraSvoris.toFixed(3)}</span><span class="l"> kg</span></div><div class="ocmi"><span class="v">${o.detaliuSk}</span><span class="l"> det.</span></div><div class="ocmi"><span class="l">${(o.sukurta||'').slice(0,10)}</span></div></div></div>`).join('');
}
async function quickDelOrd(id,klientas){if(!confirm('Ištrinti "'+klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+id);dxfOrders=dxfOrders.filter(o=>o.id!==id);dxfSum();rOrds();toast('Ištrinta');}
function showNewOrd(){document.getElementById('noModal').style.display='flex';setTimeout(()=>document.getElementById('noC').focus(),100);}
async function createOrd(){
  const c=document.getElementById('noC').value.trim();if(!c){toast('Įvesk klientą!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id){
  const o=dxfOrders.find(x=>x.id===id);if(!o)return;curOrd=o;
  document.getElementById('dvId').textContent=o.id;document.getElementById('dvCli').textContent=o.klientas;document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' · '+o.pastabos:'');
  SW('dv');await loadDets();
}
function back2Ords(){SW('dxf');loadDxfOrds();curArea=0;curContour='';document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';}
async function chSt(){if(!curOrd)return;await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value});toast('Statusas atnaujintas');}
async function delOrd(){if(!curOrd)return;if(!confirm('Ištrinti "'+curOrd.klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+curOrd.id);toast('Ištrinta');back2Ords();}
async function loadDets(){
  if(!curOrd)return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[];rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
}

function rDets(){
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nėra detalių</div>';return;}
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const groups={};
  dxfDets.forEach(d=>{const t=String(d.storis);if(!groups[t])groups[t]={t,dets:[],w:0,q:0};groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;});
  let rows='';let idx=0;
  Object.values(groups).forEach(g=>{
    rows+=`<tr class="det-grp-hdr"><td colspan="2"></td><td colspan="2"><span class="det-grp-t">${g.t}mm</span></td><td><span class="det-grp-s">${g.dets.length}det.</span></td><td><span class="det-grp-s">${g.q}vnt.</span></td><td><span class="det-grp-s" style="color:var(--ac)">${g.w.toFixed(3)}kg</span></td><td></td></tr>`;
    g.dets.forEach(d=>{
      idx++;
      rows+=`<tr><td class="mono" style="color:var(--tx3);font-size:10px">${idx}</td><td style="font-weight:600">${d.pavadinimas}</td><td><select class="det-inp" onchange="updDet('${d.detId}','storis',this.value)">${STORIAI.map(t=>`<option value="${t}"${d.storis===t?' selected':''}>${t}mm</option>`).join('')}</select></td><td class="mono" style="font-size:11px;color:var(--tx2)">${calcDims(d)}</td><td><input type="number" class="det-inp" value="${d.kiekis}" min="1" style="width:50px" onchange="updDet('${d.detId}','kiekis',this.value)"></td><td><input type="number" class="det-inp num" value="${d.svoris.toFixed(3)}" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-${d.detId}" onchange="updDetW('${d.detId}',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td><td><button class="btn btn-d btn-sm" onclick="delDet('${d.detId}')">✕</button></td></tr>`;
    });
  });
  w.innerHTML=`<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">${tq}vnt.</strong></span><span>Bendras svoris: <span class="tot">${tw.toFixed(3)}kg</span></span></div>`;
}

async function updDet(detId,field,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  if(field==='storis')d.storis=parseFloat(value);else if(field==='kiekis')d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  const wEl=document.getElementById('w-'+detId);if(wEl)wEl.value=d.svoris.toFixed(3);
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas});
}
async function updDetW(detId,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
function _updateTotals(){
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  document.getElementById('dvWt').textContent=tw.toFixed(3);
}
async function delDet(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/detales/'+id);dxfDets=dxfDets.filter(d=>d.detId!==id);rDets();_updateTotals();toast('Ištrinta');}

// DXF ĮKĖLIMAS
function handleDxf(e){if(e.target.files.length)handleMultiDxf(Array.from(e.target.files));}
function handleFolder(e){
  if(!e.target.files.length)return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failų!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' → '+ft+'mm, '+files.length+' failų',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files){
  if(!curOrd){toast('Pirma atidaryk užsakymą!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Įkeliama '+files.length+' failų...';
  for(const file of files){
    await new Promise(resolve=>{
      const r=new FileReader();
      r.onload=async e2=>{
        try{
          const res=pDxf(e2.target.result);
          if(res.areaCm2<=0){fail++;resolve();return;}
          const at=thickFromName(file.name)||defThick;
          const aq=qtyFromName(file.name)||defQty;
          const ctour=serializeContour(res.entities,res.dimW,res.dimH);
          const resp=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:file.name.replace(/[.]dxf$/i,''),storis:at,plotas:res.areaCm2,kiekis:aq,konturas:ctour});
          if(resp.success)ok++;else fail++;
        }catch(ex){fail++;}
        resolve();
      };
      r.readAsText(file);
    });
  }
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Tempk DXF failus čia arba spusk';
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?`Įkelta: ${ok}, nepavyko: ${fail}`:`Sėkmingai įkeltos ${ok} detalės!`);
}
function procDxf(file){
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2;
      curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name);const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq)document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
      toast('DXF: '+res.areaCm2.toFixed(2)+'cm²'+(at?' · '+at+'mm':''));
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm² · '+t+'mm × '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd)return;if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd)return;const a=parseFloat(document.getElementById('mArea').value)||0;if(a<=0){toast('Įvesk plotą!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:''});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}

// ATASKAITA
function setPeriod(days){
  const to=new Date(),from=new Date();
  if(days===0)from.setDate(1);else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep(){
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpį!',true);return;}
  const r=await api('GET',`/api/ataskaita?nuo=${from}&iki=${to}`);
  const el=document.getElementById('repOut');
  el.style.display='block';
  el.innerHTML=`<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: ${from} — ${to}</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.lakstai.gauta}</div><div class="l">Lakštų gauta</div></div><div class="rep-sc"><div class="n">${r.lakstai.surinkta}</div><div class="l">Surinkta</div></div><div class="rep-sc"><div class="n">${r.lakstai.perduota}</div><div class="l">Perduota</div></div><div class="rep-sc"><div class="n">${r.dxf.sk}</div><div class="l">DXF užsakymų</div></div><div class="rep-sc"><div class="n">${r.dxf.svoris.toFixed(1)}</div><div class="l">DXF svoris kg</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio judėjimas</div><div class="rep-sr"><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.sandelis.gautaKg.toFixed(1)}</div><div class="l">Gauta kg</div></div><div class="rep-sc"><div class="n" style="color:var(--rd)">${r.sandelis.sunaudotaKg.toFixed(1)}</div><div class="l">Sunaudota kg</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.gautaVerte.toFixed(2)}</div><div class="l">Gauta vertė €</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.sunaudotaVerte.toFixed(2)}</div><div class="l">Sunaudota €</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio likutis dabar</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.likutis.vnt}</div><div class="l">Viso vnt.</div></div><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.likutis.t}</div><div class="l">Tonos</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.likutis.verte.toFixed(2)}</div><div class="l">Vertė €</div></div></div></div></div>`;
}

// SPAUSDINIMAS
function printOrd(){
  if(!curOrd)return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return`<tr><td style="font-weight:700;color:#1e3a5f">${t}mm</td><td style="text-align:center">${dets.length}</td><td style="text-align:center">${gq}</td><td style="text-align:right;font-weight:700">${gw.toFixed(3)}</td></tr>`;}).join('');
  let html=`<div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div><div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">${totW.toFixed(3)} kg</div></div><div><div class="ppi-l">Viso detalių</div><div class="ppi-v">${totQ} vnt.</div></div><div><div class="ppi-l">Storių sk.</div><div class="ppi-v">${groups.size} storiai</div></div></div><table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>${sumRows}<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">${sorted.length}</td><td style="text-align:center">${totQ}</td><td style="text-align:right">${totW.toFixed(3)}</td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>Išspausdinta: ${now}</span><span>${curOrd.id}</span></div>`;
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>`<tr><td>${i+1}</td><td><strong>${d.pavadinimas}</strong></td><td style="text-align:center">${calcDims(d)}</td><td style="text-align:center">${d.kiekis}</td><td style="text-align:right"><strong>${d.svoris.toFixed(3)}</strong></td><td style="text-align:center;vertical-align:middle">${drawContourSvg(d.konturas,12)}</td></tr>`).join('');
    html+=`<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">${thick}mm</div></div><div class="ppinfo"><div><div class="ppi-l">Svoris (${thick}mm)</div><div class="ppi-v">${gw.toFixed(3)} kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">${gq}vnt. (${dets.length}poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">${now}</div></div></div><table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>${rows}<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">${gq}vnt.</td><td style="text-align:right">${gw.toFixed(3)}kg</td><td></td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>${thick}mm · ${dets.length}poz. · ${gq}vnt. · ${gw.toFixed(3)}kg</span><span>${curOrd.id}</span></div></div>`;
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}

function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  const s='<style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style>';
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'+s+'</head><body>'+c+'</body>');
  w.document.close();
  setTimeout(function(){w.print();},500);
}

function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}

// Nustatymų įkėlimas
const savedSett=localStorage.getItem('sandSettings');
if(savedSett)try{settings=JSON.parse(savedSett);}catch(e){}

async function siustiEmail(){
  const btn=document.getElementById('emailBtn');
  btn.textContent='Siunčiama...';btn.disabled=true;
  try{
    const r=await fetch('/api/email/siusti',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const d=await r.json();
    if(d.success){alert('✓ '+d.message);}
    else{alert('Klaida: '+(d.detail||d.message));}
  }catch(e){alert('Klaida: '+e.message);}
  btn.textContent='✉ Siųsti ataskaitą';btn.disabled=false;
}

"""

_HTML = """<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0969da">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sandelis">
<link rel="manifest" href="/manifest.json">
<title>Sandelio Sistema</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
<nav>
  <div class="brand"><div class="brand-ico"></div>SANDELIS</div>
  <div class="tabs">
    <button class="tab active" onclick="SW('lk')" id="tab-lk">Lakstai <span class="bdg" id="lkBdg">0</span></button>
    <button class="tab" onclick="SW('stk')" id="tab-stk">Sandelis <span class="bdg y" id="stkBdg">0</span></button>
    <button class="tab" onclick="SW('dxf')" id="tab-dxf">DXF <span class="bdg gray" id="dxfBdg">0</span></button>
    <button class="tab" onclick="SW('arch')" id="tab-arch">Archyvai <span class="bdg gray" id="archBdg">0</span></button>
    <button class="tab" onclick="SW('rep')" id="tab-rep">Ataskaita</button>
  </div>
  <div class="nav-r"><div class="dot ok" id="connDot"></div></div>
</nav>

<div class="view active" id="view-lk">
  <div class="lk-wrap">
    <div class="lk-main">
      <div class="card">
        <div class="ct">Skanavimas</div>
        <div class="scan-f"><span class="scan-ico">▦</span><input class="scan-inp" id="scanInp" placeholder="Skanuok arba ivesk koda..." autocomplete="off" spellcheck="false"></div>
        <div class="hint" id="scanHint">Laukiama skanavimo...</div>
        <div class="steps"><div class="step s1"></div><div class="step s2"></div><div class="step s3"></div></div>
        <div class="step-lbl"><span>1x Registruota</span><span>2x Surinkta</span><span>3x Perduota</span></div>
      </div>
      <div class="res" id="lkRes" style="display:none"><div class="rt" id="lkRt"></div><div class="rc" id="lkRc"></div><div class="rs" id="lkRs"></div></div>
      <div class="stats-row">
        <div class="stat"><div class="sn a" id="lkT">0</div><div class="sl">Is viso</div></div>
        <div class="stat"><div class="sn g" id="lkC">0</div><div class="sl">Surinkta</div></div>
        <div class="stat"><div class="sn b" id="lkD">0</div><div class="sl">Perduota</div></div>
        <div class="stat"><div class="sn y" id="lkP">0</div><div class="sl">Laukia</div></div>
      </div>
      <div class="prog-card">
        <div class="pt"><span>Progresas</span><span class="pct" id="lkPct">0%</span></div>
        <div class="ptr"><div class="pfd" id="lkPfd" style="width:0%"></div><div class="pfc" id="lkPfc" style="width:0%"></div></div>
      </div>
      <div class="stbar">
        <span class="stbar-lbl">Naujas etapas:</span>
        <input type="text" id="stageInp" placeholder="pvz. Etapas 221">
        <button class="btn btn-p btn-sm" onclick="askStage()">Archyvuoti</button>
      </div>
    </div>
    <div class="lk-sb">
      <div class="sbh">
        <div class="sbt">Uzsakymai</div>
        <button class="btn btn-g btn-sm" onclick="loadLk()">&#x21BB;</button>
        <button id="pdfBtn" class="btn btn-s btn-sm" onclick="genPdfReport()">&#x22C6; Atsisiusti PDF</button>
        <div class="sbsr"><span class="sbs-i">&#x2315;</span><input type="text" id="lkSrch" placeholder="Ieskoti..." oninput="rlkList()"></div>
      </div>
      <div class="frow">
        <button class="fb active" onclick="lkFlt('all',this)">Visi</button>
        <button class="fb" onclick="lkFlt('p',this)">Laukia</button>
        <button class="fb" onclick="lkFlt('c',this)">Surinkti</button>
        <button class="fb" onclick="lkFlt('d',this)">Perduoti</button>
      </div>
      <div class="olist" id="lkList"><div class="empty-s">Jungiamasi...</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-stk">
  <div class="page-wrap">
    <div class="ph"><div><div class="ph-t">Metalo sandelis</div><div class="ph-s">Lakstu likuciai pagal stori</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-s btn-sm" onclick="showSett()">Nustatymai</button>
        <button class="btn btn-p" onclick="showRecv()">+ Gauti lakstus</button>
      </div>
    </div>
    <div class="stk-sum" id="stkSum"></div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Likutis</span><button class="btn btn-s btn-sm" onclick="loadStock()">&#x21BB;</button></div>
      <div id="stkTbl"><div class="empty-s">Sandelis tuscias</div></div>
    </div>
    <div class="card" style="overflow:hidden;padding:0;margin-top:12px">
      <div class="card-h"><span class="card-t">Istorija</span><button class="btn btn-s btn-sm" onclick="loadHist()">&#x21BB;</button></div>
      <div id="histTbl"><div class="empty-s">Dar nera istorijos</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-dxf">
  <div class="page-wrap">
    <div class="ph"><div class="ph-t">DXF Uzsakymai</div><button class="btn btn-p" onclick="showNewOrd()">+ Naujas</button></div>
    <div class="sumr" id="dxfSum"></div>
    <div class="fbar">
      <button class="fb active" onclick="dxfFlt('all',this)">Visi</button>
      <button class="fb" onclick="dxfFlt('Naujas',this)">Nauji</button>
      <button class="fb" onclick="dxfFlt('Vykdomas',this)">Vykdomi</button>
      <button class="fb" onclick="dxfFlt('Baigtas',this)">Baigti</button>
      <input class="si" id="dxfSrch" placeholder="Ieskoti..." oninput="rOrds()">
    </div>
    <div class="og" id="ordsGrid"><div class="empty-s">Jungiamasi...</div></div>
  </div>
</div>

<div class="view" id="view-dv">
  <div class="page-wrap">
    <div class="back" onclick="back2Ords()">&#x2190; Grizti</div>
    <div class="card" style="margin-bottom:12px">
      <div class="oi-top">
        <div><div class="oid" id="dvId"></div><div class="oi-t" id="dvCli"></div><div class="oi-s" id="dvDsc"></div></div>
        <div style="text-align:right">
          <div class="wbig" id="dvWt">0</div><div class="wlbl">kg bendras svoris</div>
          <div style="margin-top:8px;display:flex;gap:5px;justify-content:flex-end;flex-wrap:wrap">
            <select class="stsel" id="dvSt" onchange="chSt()"><option>Naujas</option><option>Vykdomas</option><option>Baigtas</option></select>
            <button class="btn btn-p btn-sm" onclick="printOrd()">Spausdinti</button>
            <button class="btn btn-d btn-sm" onclick="delOrd()">Trinti</button>
          </div>
        </div>
      </div>
      <div id="dvMeta" style="font-size:11px;color:#57606a;font-family:'JetBrains Mono',monospace;margin-top:6px"></div>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Prideti detale is DXF</div>
      <div class="dropz" id="dropZ">
        <input type="file" id="dxfFile" accept=".dxf" multiple onchange="handleDxf(event)">
        <div class="dz-t">Tempk DXF failus cia arba spusk</div>
        <div class="dz-s">.dxf - galima ikelti kelis failus</div>
      </div>
      <div style="margin-top:8px">
        <label class="btn btn-s btn-sm" style="cursor:pointer">Ikelti aplanka<input type="file" id="dxfFolder" webkitdirectory multiple accept=".dxf" style="display:none" onchange="handleFolder(event)"></label>
      </div>
      <div class="cvw" id="cvW" style="display:none"><canvas id="dxfCv"></canvas></div>
      <div class="pf" id="pForm" style="display:none">
        <div class="wp"><div class="wv" id="wPv">0.000</div><div class="wl">kg (vieno vnt.)</div><div class="wa" id="wAr"></div></div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="dName"></div>
          <div><label class="fl">Storis (mm)</label><select id="dThk" onchange="rcW();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Kiekis</label><input type="number" id="dQty" value="1" min="1" oninput="rcW()"></div>
        </div>
        <button class="btn btn-p" style="width:100%" onclick="addDet()">+ Prideti detale</button>
      </div>
      <div class="msec">
        <div class="mlbl">arba ivesk rankiniu budu</div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="mName"></div>
          <div><label class="fl">Storis (mm)</label><select id="mThk" onchange="rcM();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Plotas (cm2)</label><input type="number" id="mArea" step="0.01" oninput="rcM()"></div>
        </div>
        <div class="fgrid">
          <div><label class="fl">Kiekis</label><input type="number" id="mQty" value="1" min="1" oninput="rcM()"></div>
          <div><label class="fl">Svoris</label><div class="svor-d" id="mWp">0.000 kg</div></div>
          <div style="display:flex;align-items:flex-end"><button class="btn btn-p" style="width:100%" onclick="addMDet()">+ Prideti</button></div>
        </div>
      </div>
    </div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Detaliu sarasas</span><button class="btn btn-s btn-sm" onclick="loadDets()">&#x21BB;</button></div>
      <div id="dtWrap"><div class="empty-s">Dar nera detaliu</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-arch">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Archyvai</div>
    <div class="sc-grid" id="stageCards"><div class="empty-s">Dar nera archivu</div></div>
    <div class="adbox" id="adBox" style="display:none">
      <div class="adh"><div class="adt" id="adTitle"></div><button class="btn btn-s btn-sm" onclick="closeAd()">X</button></div>
      <div class="adlist" id="adList"></div>
    </div>
  </div>
</div>

<div class="view" id="view-rep">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Ataskaita</div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Laikotarpis</div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr;margin-bottom:10px">
        <div><label class="fl">Nuo</label><input type="date" id="repFrom"></div>
        <div><label class="fl">Iki</label><input type="date" id="repTo"></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
        <button class="btn btn-s btn-sm" onclick="setPeriod(7)">7 dienos</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(30)">30 dienu</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(0)">Sis menuo</button>
      </div>
      <button class="btn btn-p" onclick="genRep()">Generuoti</button>
    </div>
    <div id="repOut" style="display:none"></div>
  </div>
</div>

<div class="mbg" id="noModal" style="display:none">
  <div class="modal">
    <div class="mh">Naujas DXF uzsakymas</div>
    <div class="mf">
      <div><label class="fl">Klientas *</label><input type="text" id="noC"></div>
      <div><label class="fl">Aprasymas</label><input type="text" id="noD"></div>
      <div><label class="fl">Pastabos</label><textarea id="noN"></textarea></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('noModal')">Atsaukti</button><button class="btn btn-p" onclick="createOrd()">Sukurti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="recvModal" style="display:none">
  <div class="modal">
    <div class="mh">Gauti lakstus</div>
    <div class="mf">
      <div><label class="fl">Storis (mm)</label><select id="recThk"><option value="3">3 mm</option><option value="4">4 mm</option><option value="5">5 mm</option><option value="6">6 mm</option><option value="8">8 mm</option><option value="10">10 mm</option><option value="12">12 mm</option><option value="14">14 mm</option><option value="15">15 mm</option><option value="16">16 mm</option><option value="18">18 mm</option><option value="20">20 mm</option><option value="25">25 mm</option></select></div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Plotis (mm)</label><input type="number" id="recW" oninput="rcRecv()"></div>
        <div><label class="fl">Ilgis (mm)</label><input type="number" id="recL" oninput="rcRecv()"></div>
      </div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Kiekis (vnt.)</label><input type="number" id="recQ" value="1" oninput="rcRecv()"></div>
        <div><label class="fl">Kaina / t (EUR)</label><input type="number" id="recP" step="0.01" oninput="rcRecv()"></div>
      </div>
      <div class="rec-prev" id="recPrev">Ivesk matmenis...</div>
      <div><label class="fl">Pastabos (SF nr.)</label><input type="text" id="recN"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('recvModal')">Atsaukti</button><button class="btn btn-p" onclick="doRecv()">Prideti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="useModal" style="display:none">
  <div class="modal">
    <div class="mh">Sunaudoti lakstus</div>
    <div class="mf">
      <div id="useInfo" class="rec-prev"></div>
      <div><label class="fl">Kiek vnt.?</label><input type="number" id="useQ" value="1" min="1"></div>
      <div><label class="fl">Pastabos</label><input type="text" id="useNote"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('useModal')">Atsaukti</button><button class="btn btn-y" onclick="doUse()">Sunaudoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="settModal" style="display:none">
  <div class="modal">
    <div class="mh">Nustatymai</div>
    <div class="mf">
      <div><label class="fl">Numatyta kaina / kg (EUR)</label><input type="number" id="settP" step="0.01"></div>
      <div><label class="fl">Zemos atsargos ispejimas</label><input type="number" id="settL" value="2" min="0"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('settModal')">Atsaukti</button><button class="btn btn-p" onclick="saveSett()">Issaugoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="stModal" style="display:none">
  <div class="modal">
    <div class="mh">Archyvuoti etapa?</div>
    <div id="stMn" style="font-size:11px;color:#57606a;margin-bottom:10px"></div>
    <div id="stMs" class="rec-prev" style="margin-bottom:12px;line-height:2"></div>
    <div class="mb"><button class="btn btn-s" onclick="CM('stModal')">Atsaukti</button><button class="btn btn-p" onclick="confirmStage()">Archyvuoti</button></div>
  </div>
</div>

<div class="pmb" id="printMod" style="display:none">
  <div class="pm">
    <div class="pbr">
      <button class="btn btn-p btn-sm" onclick="window.print()">Spausdinti</button>
      <button class="btn btn-s btn-sm" onclick="dlPdf()">PDF</button>
      <button class="btn btn-s btn-sm" onclick="CM('printMod')">Uzdaryti</button>
    </div>
    <div id="printArea"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const STORIAI=[3,4,5,6,8,10,12,14,15,16,18,20,25];
const TANKIS=8000;
</script>
<script src="/static/js/dxf.js"></script>
<script src="/static/js/main.js"></script>
</body>
</html>"""

@app.on_event("startup")
def startup():
    init_db()

@app.get("/static/css/main.css")
async def serve_css():
    return Response(content=_CSS, media_type="text/css")

@app.get("/static/js/dxf.js")
async def serve_dxfjs():
    return Response(content=_DXFJS, media_type="application/javascript")

@app.get("/static/js/main.js")
async def serve_mainjs():
    return Response(content=_MAINJS, media_type="application/javascript")

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({"name":"Sandelio Sistema","short_name":"Sandelis","start_url":"/","display":"standalone","background_color":"#f6f8fa","theme_color":"#0969da"})

@app.get("/sw.js")
async def sw():
    return Response(content="// sw", media_type="application/javascript")

@app.get("/icon.png")
async def icon():
    import base64
    return Response(content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="), media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=_HTML)


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
        raise HTTPException(400, "SMTP_PASS nenurodytas Railway Variables")
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti = [l for l in items if l.surinkta and not l.perduota]
    perduoti = [l for l in items if l.perduota]
    laukia = [l for l in items if not l.surinkta]
    def rows(lst, color):
        if not lst: return "<tr><td colspan=2 style='color:#aaa;padding:4px 8px'>Tuscia</td></tr>"
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else '-'}</td></tr>" for l in lst)
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
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
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th></tr>{rows(laukia,'#9a6700')}</table>
      <p style='color:#57606a;font-size:11px;margin-top:16px'>Issiusta is Sandelio sistemos - metalcraft.lt</p>
    </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandelio ataskaita {now}"
        msg["From"] = f"Metalcraft <{smtp_user}>"
        msg["To"] = gaivejas
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        # Bandome 587 su STARTTLS
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        except Exception as e1:
            # Bandome 465 su SSL
            with smtplib.SMTP_SSL(smtp_host, 465, timeout=30) as s:
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        return {"success": True, "message": f"Issiusta i {gaivejas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# LAKŠTAI API
# ══════════════════════════════════════════════════

@app.get("/api/lakstai")
def get_lakstai(etapas: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lakstai)
    if etapas:
        q = q.filter(Lakstai.etapas == etapas)
    else:
        q = q.filter(Lakstai.etapas == None)
    items = q.all()
    return {"orders": [_lk(l) for l in items]}

@app.get("/api/lakstai/find/{kodas}")
def find_lakstas(kodas: str, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == kodas).first()
    if not l:
        return {"found": False}
    return {"found": True, **_lk(l)}

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
        return {"success": False, "message": "Nėra užsakymų"}
    total = len(items); collected = sum(1 for l in items if l.surinkta); delivered = sum(1 for l in items if l.perduota)
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

# ══════════════════════════════════════════════════
# DXF API
# ══════════════════════════════════════════════════

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
    d = Detale(det_id=det_id, uzsakymo_id=data["uzsakymoId"], pavadinimas=data.get("pavadinimas", "Detalė"),
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

# ══════════════════════════════════════════════════
# SANDĖLIS API
# ══════════════════════════════════════════════════

@app.get("/api/sandelis")
def get_sandelis(db: Session = Depends(get_db)):
    items = db.query(Sandelis).order_by(Sandelis.storis).all()
    return {"stock": [_stk(s) for s in items]}

@app.post("/api/sandelis/gauti")
def gauti(data: dict, db: Session = Depends(get_db)):
    storis = float(data["storis"]); w = float(data["plotis"]); l = float(data["ilgis"]); qty = int(data["kiekis"])
    kaina = float(data.get("kaina", 0))
    svoris_vnt = round((w/1000) * (l/1000) * (storis/1000) * TANKIS, 2)
    liko_kg = round(svoris_vnt * qty, 2)
    liko_t = round(liko_kg / 1000, 3)
    verte = round(liko_t * kaina, 2)  # kaina uz tona
    stk_id = "STK-" + str(int(datetime.utcnow().timestamp() * 1000))
    s = Sandelis(stk_id=stk_id, storis=storis, matmenys=f"{int(w)}×{int(l)}", svoris_vnt=svoris_vnt,
                 gauta_vnt=qty, liko_vnt=qty, liko_kg=liko_kg, liko_t=liko_t, kaina_kg=kaina, verte=verte,
                 pastabos=data.get("pastabos", ""))
    db.add(s)
    hist = SandelioIstorijia(veiksmas="Gauta", storis=storis, matmenys=f"{int(w)}×{int(l)}", kiekis=qty,
                              svoris_vnt=svoris_vnt, svoris_iš_viso=liko_kg, kaina_kg=kaina, verte=verte, pastabos=data.get("pastabos", ""))
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
    s.verte = round(s.liko_t * s.kaina_kg, 2)  # kaina uz tona
    hist = SandelioIstorijia(veiksmas="Sunaudota", storis=s.storis, matmenys=s.matmenys, kiekis=qty,
                              svoris_vnt=s.svoris_vnt, svoris_iš_viso=round(qty*s.svoris_vnt, 2),
                              kaina_kg=s.kaina_kg, verte=round((qty*s.svoris_vnt/1000)*s.kaina_kg, 2), pastabos=data.get("pastabos", ""))
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
    return {"history": [{"data": h.data.strftime("%Y-%m-%d %H:%M"), "veiksmas": h.veiksmas, "storis": h.storis,
                          "matmenys": h.matmenys, "kiekis": h.kiekis, "svorisVnt": h.svoris_vnt,
                          "svorisIšViso": h.svoris_iš_viso, "kainaKg": h.kaina_kg, "verte": h.verte} for h in items]}

# ══════════════════════════════════════════════════
# ATASKAITA
# ══════════════════════════════════════════════════

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
            "pagalStori": [{"storis": s.storis, "vnt": s.liko_vnt, "kg": round(s.liko_kg, 1), "t": s.liko_t} for s in sorted(stock, key=lambda x: x.storis)]
        }
    }


# ══════════════════════════════════════════════════
# EL. PAŠTAS
# ══════════════════════════════════════════════════

@app.post("/api/email/siusti")
async def siusti_email(data: dict, db: Session = Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    smtp_host = os.getenv("SMTP_HOST", "vytis.serveriai.lt")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "info@metalcraft.lt")
    smtp_pass = os.getenv("SMTP_PASS", "")
    gavėjas   = os.getenv("EMAIL_TO", "gintaras@metalikalt.eu")
    
    if not smtp_pass:
        raise HTTPException(400, "SMTP slaptažodis nenurodytas")
    
    # Gauti lakštus
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti  = [l for l in items if l.surinkta and not l.perduota]
    perduoti  = [l for l in items if l.perduota]
    laukia    = [l for l in items if not l.surinkta]
    
    # HTML laiškas
    def rows(lst, color):
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else ''}</td></tr>" for l in lst)
    
    html = f"""
    <html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>
    <div style='background:#0969da;padding:16px;border-radius:8px 8px 0 0'>
      <h2 style='color:white;margin:0'>Sandėlio ataskaita – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</h2>
    </div>
    <div style='padding:16px;background:#f6f8fa;border-radius:0 0 8px 8px'>
      <p>Iš viso: <strong>{len(items)}</strong> | Surinkta: <strong style='color:#1a7f37'>{len(surinkti)}</strong> | Perduota: <strong style='color:#0969da'>{len(perduoti)}</strong> | Laukia: <strong style='color:#9a6700'>{len(laukia)}</strong></p>
      
      {'<h3 style="color:#1a7f37">✓ Surinkta</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Kodas</th><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Laikas</th></tr>' + rows(surinkti, '#1a7f37') + '</table>' if surinkti else ''}
      
      {'<h3 style="color:#0969da">→ Perduota</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Kodas</th><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Laikas</th></tr>' + rows(perduoti, '#0969da') + '</table>' if perduoti else ''}
      
      {'<h3 style="color:#9a6700">⏳ Laukia</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#fff8c5">Kodas</th><th style="text-align:left;padding:4px 8px;background:#fff8c5">Laikas</th></tr>' + rows(laukia, '#9a6700') + '</table>' if laukia else ''}
      
      <p style='color:#57606a;font-size:12px;margin-top:16px'>Išsiųsta iš Sandėlio sistemos – metalcraft.lt</p>
    </div>
    </body></html>
    """
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandėlio ataskaita {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        msg["From"]    = f"Metalcraft <{smtp_user}>"
        msg["To"]      = gavėjas
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, gavėjas, msg.as_string())
        
        return {"success": True, "message": f"Išsiųsta į {gavėjas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# ══════════════════════════════════════════════════
# PAGALBINĖS FUNKCIJOS
# ══════════════════════════════════════════════════

def _lk(l):
    return {"kodas": l.kodas, "registered": l.registruota.strftime("%Y-%m-%d %H:%M:%S") if l.registruota else "",
            "collected": l.surinkta, "collectedAt": l.surinkta_kada.strftime("%Y-%m-%d %H:%M:%S") if l.surinkta_kada else "",
            "delivered": l.perduota, "deliveredAt": l.perduota_kada.strftime("%Y-%m-%d %H:%M:%S") if l.perduota_kada else ""}

def _uzs(u):
    return {"id": u.uzs_id, "klientas": u.klientas, "aprasymas": u.aprasymas or "", "pastabos": u.pastabos or "",
            "statusas": u.statusas, "bendraSvoris": u.bendras_svoris, "detaliuSk": u.detaliu_sk,
            "sukurta": u.sukurta.strftime("%Y-%m-%d %H:%M:%S") if u.sukurta else ""}

def _det(d):
    return {"detId": d.det_id, "uzsakymoId": d.uzsakymo_id, "pavadinimas": d.pavadinimas,
            "storis": d.storis, "plotas": d.plotas, "kiekis": d.kiekis, "svoris": d.svoris,
            "konturas": d.konturas or "", "prideta": d.prideta.strftime("%Y-%m-%d %H:%M:%S") if d.prideta else ""}

def _stk(s):
    return {"id": s.stk_id, "storis": s.storis, "matmenys": s.matmenys, "svorisVnt": s.svoris_vnt,
            "gautaVnt": s.gauta_vnt, "sunaudotaVnt": s.sunaudota_vnt, "likoVnt": s.liko_vnt,
            "likoKg": s.liko_kg, "likoT": s.liko_t, "kainaKg": s.kaina_kg, "verte": s.verte,
            "prideta": s.prideta.strftime("%Y-%m-%d %H:%M:%S") if s.prideta else "", "pastabos": s.pastabos or ""}

def _recalc(uzs_id, db):
    dets = db.query(Detale).filter(Detale.uzsakymo_id == uzs_id).all()
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if u:
        u.bendras_svoris = round(sum(d.svoris for d in dets), 3)
        u.detaliu_sk = len(dets)
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os

from database import get_db, init_db, Lakstai, Etapas, Uzsakymas, Detale, Sandelis, SandelioIstorijia

app = FastAPI(title="Sandelio Sistema")
TANKIS = 8000

_CSS = """*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#f6f8fa;--s1:#ffffff;--s2:#f0f2f4;--s3:#e1e4e8;
  --bd:#d0d7de;--bd2:#afb8c1;
  --tx:#1f2328;--tx2:#57606a;--tx3:#848d97;
  --ac:#0969da;--ac2:#0550ae;--ac-bg:rgba(9,105,218,.08);
  --gn:#1a7f37;--gn-bg:rgba(26,127,55,.08);--gn-bd:rgba(26,127,55,.3);
  --yw:#9a6700;--yw-bg:rgba(154,103,0,.08);--yw-bd:rgba(154,103,0,.3);
  --rd:#cf222e;--rd-bg:rgba(207,34,46,.08);--rd-bd:rgba(207,34,46,.3);
  --pp:#6639ba;--pp-bg:rgba(102,57,186,.08);
  --or:#953800;
}
body{background:var(--bg);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;min-height:100vh;font-size:14px}

nav{background:var(--s1);border-bottom:1px solid var(--bd);padding:0 16px;height:52px;display:flex;align-items:center;gap:8px;position:sticky;top:0;z-index:50}
.brand{font-size:15px;font-weight:800;display:flex;align-items:center;gap:8px;flex-shrink:0}
.brand-ico{width:26px;height:26px;background:linear-gradient(135deg,#0969da,#6639ba);border-radius:6px}
.tabs{display:flex;height:100%;overflow-x:auto;flex:1;justify-content:center}
.tab{padding:0 13px;height:100%;display:flex;align-items:center;gap:4px;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;border:none;background:none;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}
.tab:hover{color:var(--tx)}.tab.active{color:var(--ac);border-bottom-color:var(--ac)}
.bdg{background:var(--ac);color:#fff;font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px}
.bdg.y{background:var(--yw)}.bdg.gray{background:var(--s3);color:var(--tx2)}.bdg.r{background:var(--rd)}
.nav-r{margin-left:auto;display:flex;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--bd2)}.dot.ok{background:var(--gn)}.dot.err{background:var(--rd)}

.view{display:none}.view.active{display:block}
.page-wrap{padding:16px;max-width:1000px;margin:0 auto}
.ph{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ph-t{font-size:18px;font-weight:800}.ph-s{font-size:11px;color:var(--tx2);margin-top:2px}

.btn{padding:7px 14px;border:none;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:12px;cursor:pointer;border-radius:6px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;white-space:nowrap}
.btn-p{background:var(--ac);color:#fff}.btn-p:hover{background:var(--ac2)}
.btn-s{background:transparent;border:1px solid var(--bd);color:var(--tx2)}.btn-s:hover{border-color:var(--tx);color:var(--tx)}
.btn-g{background:var(--gn-bg);border:1px solid var(--gn-bd);color:var(--gn)}.btn-g:hover{background:var(--gn);color:#fff}
.btn-d{background:transparent;border:1px solid transparent;color:var(--tx3)}.btn-d:hover{border-color:var(--rd-bd);color:var(--rd);background:var(--rd-bg)}
.btn-y{background:var(--yw-bg);border:1px solid var(--yw-bd);color:var(--yw)}.btn-y:hover{background:var(--yw);color:#fff}
.btn-sm{padding:4px 9px;font-size:11px}

.fl{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:4px}
input[type=text],input[type=number],input[type=date],input[type=email],textarea,select{width:100%;padding:7px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;outline:none;border-radius:6px;transition:border-color .15s;-webkit-appearance:none}
input:focus,textarea:focus,select:focus{border-color:var(--ac)}
textarea{resize:vertical;min-height:60px}
option{background:var(--s1)}

.card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;margin-bottom:12px}
.card-h{padding:12px 16px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.card-t{font-weight:700;font-size:14px}
.ct{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.ct::after{content:'';flex:1;height:1px;background:var(--bd)}

.mbg{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:24px;max-width:440px;width:100%;margin:auto}
.mh{font-size:17px;font-weight:800;margin-bottom:16px}
.mf{display:flex;flex-direction:column;gap:12px}
.mb{display:flex;gap:8px;justify-content:flex-end;margin-top:6px}

.toast{position:fixed;bottom:14px;right:14px;left:14px;max-width:340px;margin:0 auto;padding:11px 14px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;background:var(--s1);border:1px solid var(--bd);border-left:3px solid var(--gn);box-shadow:0 8px 24px rgba(0,0,0,.15);transform:translateY(70px);opacity:0;transition:all .25s;z-index:300;border-radius:6px}
.toast.w{border-left-color:var(--rd)}.toast.b{border-left-color:var(--ac)}.toast.p{border-left-color:var(--pp)}
.toast.show{transform:translateY(0);opacity:1}
.sp{display:inline-block;width:11px;height:11px;border:2px solid var(--bd2);border-top-color:var(--ac);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:4px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.empty-s{padding:40px;text-align:center;color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:12px}

/* LAKŠTAI */
.lk-wrap{display:grid;grid-template-columns:1fr 290px;min-height:calc(100vh - 52px)}
@media(max-width:680px){.lk-wrap{grid-template-columns:1fr}}
.lk-main{padding:16px;display:flex;flex-direction:column;gap:10px}
.lk-sb{border-left:1px solid var(--bd);background:var(--s1);display:flex;flex-direction:column}
.scan-f{position:relative}.scan-ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:16px;pointer-events:none;color:var(--tx3)}
.scan-inp{padding:11px 14px 11px 40px!important;font-size:17px!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important}
.scan-inp:focus{border-color:var(--ac)!important;box-shadow:0 0 0 3px var(--ac-bg)}
.hint{margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3)}
.steps{display:flex;gap:4px;margin-top:10px}
.step{flex:1;height:3px;background:var(--bd);border-radius:2px}
.s1{background:var(--yw)}.s2{background:var(--gn)}.s3{background:var(--ac)}
.step-lbl{display:flex;justify-content:space-between;margin-top:4px;font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.res{border:1px solid var(--bd);border-radius:8px;padding:12px 14px;animation:fadeUp .2s ease}
.res.rn{background:var(--yw-bg);border-color:var(--yw-bd)}.res.rc{background:var(--gn-bg);border-color:var(--gn-bd)}
.res.rd{background:var(--ac-bg);border-color:rgba(9,105,218,.3)}.res.re{background:var(--rd-bg);border-color:var(--rd-bd)}
.res.rp{background:var(--pp-bg);border-color:rgba(102,57,186,.3)}.res.ra{background:var(--gn-bg);border-color:var(--gn-bd)}
.rt{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}
.res.rn .rt{color:var(--yw)}.res.rc .rt{color:var(--gn)}.res.rd .rt{color:var(--ac)}.res.re .rt{color:var(--rd)}.res.rp .rt{color:var(--pp)}.res.ra .rt{color:var(--gn)}
.rc{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace}.rs{font-size:11px;color:var(--tx2);margin-top:2px}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
@media(max-width:480px){.stats-row{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.sn{font-size:22px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace}
.sn.a{color:var(--ac)}.sn.g{color:var(--gn)}.sn.b{color:var(--ac)}.sn.y{color:var(--yw)}
.sl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.prog-card{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px}
.pt{display:flex;justify-content:space-between;margin-bottom:6px;font-size:10px;color:var(--tx2);font-family:'JetBrains Mono',monospace}
.pct{color:var(--gn);font-weight:700}
.ptr{height:6px;background:var(--s2);border-radius:3px;overflow:hidden;position:relative}
.pfc{height:100%;background:var(--gn);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px}
.pfd{height:100%;background:var(--ac);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px;opacity:.4}
.stbar{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:12px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.stbar-lbl{font-weight:700;font-size:13px;white-space:nowrap}.stbar input{flex:1;min-width:130px}
.stbar-hint{font-size:9px;color:var(--tx3);width:100%;font-family:'JetBrains Mono',monospace}
.sbh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}
.sbt{font-weight:700;font-size:12px}.sbsr{position:relative;width:100%}
.sbsr input{padding:5px 10px 5px 26px;font-size:11px}.sbs-i{position:absolute;left:8px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--tx3);pointer-events:none}
.frow{padding:6px 14px;border-bottom:1px solid var(--bd);display:flex;gap:4px;flex-wrap:wrap}
.fb{padding:3px 8px;background:transparent;border:1px solid var(--bd);color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:9px;cursor:pointer;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;transition:all .15s}
.fb.active{background:var(--tx);color:var(--bg);border-color:var(--tx);font-weight:700}
.olist{flex:1;overflow-y:auto}
.oi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:6px;transition:background .1s}
.oi:hover{background:var(--s2)}
.od{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.oi.sc .od{background:var(--gn)}.oi.sdd .od{background:var(--ac)}
.oc{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ost{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700;flex-shrink:0}
.ost.s0{background:var(--yw-bg);color:var(--yw)}.ost.s1{background:var(--gn-bg);color:var(--gn)}.ost.s2{background:var(--ac-bg);color:var(--ac)}
.otm{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);flex-shrink:0}

/* SANDĖLIS */
.stk-sum{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin-bottom:14px}
.stk-s{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.stk-n{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.stk-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.stk-row{padding:10px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.stk-row:last-child{border-bottom:none}.stk-row:hover{background:var(--s2)}
@media(max-width:600px){.stk-row{grid-template-columns:1fr 1fr;gap:6px}}
.stk-thick{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:var(--ac)}
.stk-thick span{font-size:10px;color:var(--tx3)}
.stk-dims{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.stk-num{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700}
.stk-num.ok{color:var(--gn)}.stk-num.warn{color:var(--yw)}.stk-num.empty{color:var(--rd)}
.stk-sub{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.stk-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--or)}
.stk-acts{display:flex;gap:4px}
.stk-tot{padding:10px 16px;background:var(--s2);border-top:2px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.hist-row{padding:8px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:130px 60px 90px 60px 80px 80px;align-items:center;gap:8px;font-size:12px}
.hist-row:last-child{border-bottom:none}.hist-row:hover{background:var(--s2)}
.hist-act{font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700}
.hist-act.G{background:var(--gn-bg);color:var(--gn)}.hist-act.S{background:var(--rd-bg);color:var(--rd)}
.rec-prev{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--tx2)}

/* DXF */
.sumr{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin-bottom:14px}
.smc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.smn{font-size:20px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.sml{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.fbar{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.si{padding:5px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:11px;outline:none;border-radius:6px;min-width:150px}
.si:focus{border-color:var(--ac)}
.og{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.ocard{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.ocard:hover{border-color:var(--ac);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.oct{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.oid{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3)}
.stb{font-family:'JetBrains Mono',monospace;font-size:9px;padding:2px 7px;border-radius:4px;font-weight:700}
.stb.Naujas{background:var(--yw-bg);color:var(--yw);border:1px solid var(--yw-bd)}
.stb.Vykdomas{background:var(--ac-bg);color:var(--ac);border:1px solid rgba(9,105,218,.3)}
.stb.Baigtas{background:var(--gn-bg);color:var(--gn);border:1px solid var(--gn-bd)}
.ocli{font-size:14px;font-weight:700;margin-bottom:2px}.ocdesc{font-size:11px;color:var(--tx2);margin-bottom:10px}
.ocm{display:flex;gap:10px;flex-wrap:wrap}
.ocmi{font-family:'JetBrains Mono',monospace;font-size:10px}
.ocmi .v{color:var(--ac);font-weight:700}.ocmi .l{color:var(--tx3)}
.back{display:flex;align-items:center;gap:5px;color:var(--tx2);font-size:12px;cursor:pointer;margin-bottom:14px;font-family:'JetBrains Mono',monospace;transition:color .15s}
.back:hover{color:var(--ac)}
.oi-top{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px}
.oi-t{font-size:18px;font-weight:800}.oi-s{font-size:11px;color:var(--tx2);margin-top:2px}
.wbig{font-size:28px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac);line-height:1}
.wlbl{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px}
.stsel{padding:5px 10px;background:var(--s2);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:10px;outline:none;border-radius:6px;width:auto}
.dropz{border:2px dashed var(--bd);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:all .2s;position:relative}
.dropz:hover,.dropz.drag{border-color:var(--ac);background:var(--ac-bg)}
.dropz input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer}
.dz-t{font-size:12px;color:var(--tx2)}.dz-s{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.cvw{background:var(--s2);border:1px solid var(--bd);border-radius:6px;margin-top:10px;overflow:hidden}
canvas{display:block;max-width:100%;height:150px}
.pf{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:14px;margin-top:10px;animation:fadeUp .2s ease}
.wp{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;margin-bottom:10px}
.wv{font-size:19px;font-weight:700;color:var(--ac);font-family:'JetBrains Mono',monospace}
.wl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-top:1px;font-family:'JetBrains Mono',monospace}
.wa{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.fgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:480px){.fgrid{grid-template-columns:1fr}}
.msec{margin-top:12px;border-top:1px solid var(--bd);padding-top:12px}
.mlbl{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.svor-d{padding:7px 10px;background:var(--s1);border:1px solid var(--bd);border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ac)}
table{width:100%;border-collapse:collapse}
th{padding:7px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;text-align:left;border-bottom:1px solid var(--bd);background:var(--s2)}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}tr:hover td{background:var(--s2)}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px}
.num{color:var(--ac);font-weight:700;font-family:'JetBrains Mono',monospace}
.dttot{padding:10px 12px;background:var(--s2);border-top:2px solid var(--bd);display:flex;justify-content:flex-end;gap:14px;font-family:'JetBrains Mono',monospace;font-size:11px}
.tot{color:var(--ac);font-weight:700;font-size:13px}
.det-grp-hdr{padding:6px 12px;background:var(--s2);border-top:2px solid var(--bd);border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:10px}
.det-grp-t{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800;color:var(--ac)}
.det-grp-s{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.det-inp{padding:3px 6px!important;font-size:11px!important;width:auto!important}

/* ARCHYVAI */
.sc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:14px}
.scc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.scc:hover{border-color:var(--ac);transform:translateY(-1px)}.scc.open{border-color:var(--ac)}
.scn{font-size:13px;font-weight:700;margin-bottom:8px}
.scst{display:flex;gap:10px}
.scst .n{font-size:15px;font-weight:700;display:block;line-height:1;font-family:'JetBrains Mono',monospace}
.scst .n.g{color:var(--gn)}.scst .n.b{color:var(--ac)}.scst .n.r{color:var(--rd)}
.scst .l{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase}
.scp{margin-top:8px;height:3px;background:var(--s2);border-radius:2px;overflow:hidden}
.scpf{height:100%;background:var(--gn);border-radius:2px}
.adbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;margin-top:10px}
.adh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.adt{font-weight:700;font-size:13px}
.adlist{max-height:320px;overflow-y:auto}
.adi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:7px}
.addot{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.adi.sc .addot{background:var(--gn)}.adi.sdd .addot{background:var(--ac)}
.adcode{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1}
.adtag{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700}
.adtag.r{background:var(--yw-bg);color:var(--yw)}.adtag.c{background:var(--gn-bg);color:var(--gn)}.adtag.d{background:var(--ac-bg);color:var(--ac)}
.adtime{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx3)}

/* ATASKAITA */
.rep-s{margin-bottom:14px}
.rep-st{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--bd)}
.rep-sr{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}
.rep-sc{background:var(--s2);border-radius:6px;padding:10px 12px}
.rep-sc .n{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.rep-sc .l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}

/* PRINT */
@media print{body *{visibility:hidden!important}#printArea,#printArea *{visibility:visible!important}#printArea{position:fixed!important;left:0;top:0;width:100%}@page{margin:6mm;size:A4}}
.pmb{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:flex-start;justify-content:center;padding:16px;overflow-y:auto}
.pm{background:white;color:#000;max-width:210mm;width:100%;border-radius:8px;overflow:hidden;margin:auto}
.pbr{display:flex;gap:8px;padding:10px 14px;background:#f5f5f5;border-bottom:1px solid #ddd}
#printArea{background:white;color:#000;font-family:Arial,sans-serif;padding:10mm 8mm}
.pph{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}
.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666;font-family:monospace}
.ppbc{text-align:right;margin:2mm 0}
.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}
.ppi-l{font-size:7pt;color:#888;text-transform:uppercase;margin-bottom:.5mm}.ppi-v{font-size:10pt;font-weight:700}
.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}
.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}
.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}
.pptable tr:nth-child(even) td{background:#f9f9f9}
.ppsign{display:flex;gap:10mm;margin-top:5mm}
.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}
.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}
"""

_DXFJS = """
// DXF PARSERIS
const TANKIS = 8000;

function thickFromName(name){
  const m=name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)[ ]*mm/)||name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)/)||name.match(/([0-9]+(?:[.][0-9]+)?)[ ]*mm/);
  if(!m)return null;
  const v=parseFloat(m[1]);
  return STORIAI.includes(v)?v:null;
}

function qtyFromName(name){
  const m=name.match(/[_\x2D\x20]([0-9]+)[ ]*vnt/i)||name.match(/^([0-9]+)[ ]*vnt/i);
  if(!m)return null;
  const v=parseInt(m[1]);
  return v>0&&v<=9999?v:null;
}

function pDxf(txt){
  const lines=txt.split(/\r?\n/);
  const segs=[];
  let inE=false,curType=null,curV={},sf=1;

  for(let j=0;j<lines.length-1;j++){
    if(lines[j].trim()==='70'&&j>=2&&lines[j-2].trim()==='$INSUNITS'){
      const u=parseInt(lines[j+1]);if(u===1)sf=25.4;else if(u===6)sf=10;else if(u===5)sf=.1;
    }
  }

  const r4=v=>Math.round(v*10000)/10000;

  function saveSeg(t,v){
    if(t==='LINE'&&v._x1!==undefined&&v._y1!==undefined&&v._x2!==undefined&&v._y2!==undefined){
      segs.push({type:'L',x1:r4(v._x1*sf),y1:r4(v._y1*sf),x2:r4(v._x2*sf),y2:r4(v._y2*sf)});
    } else if(t==='CIRCLE'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf)});
    } else if((t==='LWPOLYLINE'||t==='POLYLINE')&&v._xs&&v._xs.length>=3){
      segs.push({type:'P',pts:v._xs.map((x,i)=>({x:r4(x*sf),y:r4((v._ys[i]||0)*sf)})),closed:((v[70]||0)&1)===1});
    } else if(t==='ARC'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf),arc:true});
    }
  }

  let i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i++;continue;}
    const val=(lines[i+1]||'').trim();
    if(code===2&&val==='ENTITIES'){inE=true;i+=2;continue;}
    if(code===0&&val==='ENDSEC'&&inE){saveSeg(curType,curV);break;}
    if(!inE){i+=2;continue;}
    if(code===0){saveSeg(curType,curV);curType=val;curV={};}
    else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._x1=n;}
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._y1=n;}
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11){curV._x2=n;}
        else if(code===21){curV._y2=n;}
        else if(code===70){curV[70]=parseInt(val)||0;}
        else{curV[code]=n;}
      }
    }
    i+=2;
  }

  let area=0;
  segs.filter(s=>s.type==='C'&&!s.arc).forEach(s=>area+=Math.PI*s.r*s.r);
  segs.filter(s=>s.type==='P').forEach(s=>{
    const pts=s.pts,n=pts.length;let a=0;
    for(let i=0;i<n;i++){const j=(i+1)%n;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}
    area+=Math.abs(a)/2;
  });
  const lineSegs=segs.filter(s=>s.type==='L');
  if(lineSegs.length){
    const adj=new Map();
    const key=p=>Math.round(p.x*100)/100+','+Math.round(p.y*100)/100;
    lineSegs.forEach(s=>{
      const p1={x:s.x1,y:s.y1},p2={x:s.x2,y:s.y2};
      const k1=key(p1),k2=key(p2);
      if(!adj.has(k1))adj.set(k1,{pt:p1,nb:[]});
      if(!adj.has(k2))adj.set(k2,{pt:p2,nb:[]});
      adj.get(k1).nb.push(k2);adj.get(k2).nb.push(k1);
    });
    const visitedE=new Set(),visitedP=new Set();
    adj.forEach((v,startK)=>{
      if(visitedP.has(startK))return;
      const path=[v.pt];let curK=startK;
      for(let iter=0;iter<adj.size*2;iter++){
        visitedP.add(curK);
        const nb=adj.get(curK).nb;let nextK=null;
        for(const nk of nb){
          const ek=[curK,nk].sort().join('|');
          if(!visitedE.has(ek)){visitedE.add(ek);nextK=nk;break;}
        }
        if(!nextK)break;
        path.push(adj.get(nextK).pt);curK=nextK;
      }
      if(path.length>=3){
        let a=0;const n=path.length;
        for(let i=0;i<n;i++){const j=(i+1)%n;a+=path[i].x*path[j].y-path[j].x*path[i].y;}
        area+=Math.abs(a)/2;
      }
    });
  }

  // Matmenys
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  segs.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  const dimW=isFinite(minX)?Math.round(maxX-minX):0;
  const dimH=isFinite(minY)?Math.round(maxY-minY):0;

  return{entities:segs,areaCm2:area/100,dimW,dimH};
}

function serializeContour(ents,dimW,dimH){
  try{
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    ents.forEach(s=>{
      if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
      else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
      else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
    });
    if(!isFinite(minX))return'';
    const W=maxX-minX||1,H=maxY-minY||1,sc=100/Math.max(W,H);
    const nx=x=>Math.round((x-minX)*sc*10)/10;
    const ny=y=>Math.round((maxY-y)*sc*10)/10;
    const paths=[];
    ents.forEach(s=>{
      if(s.type==='C'&&!s.arc)paths.push('C'+nx(s.cx)+','+ny(s.cy)+','+Math.round(s.r*sc*10)/10);
      else if(s.type==='P'){const step=Math.max(1,Math.floor(s.pts.length/50));const pts=[];for(let i=0;i<s.pts.length;i+=step)pts.push(nx(s.pts[i].x)+','+ny(s.pts[i].y));paths.push('L'+pts.join(' '));}
      else if(s.type==='L')paths.push('L'+nx(s.x1)+','+ny(s.y1)+' '+nx(s.x2)+','+ny(s.y2));
    });
    return('D:'+dimW+'x'+dimH+'|'+paths.join('|')).slice(0,2000);
  }catch(e){return'';}
}

function calcDims(d){
  if(d.konturas){
    const m=d.konturas.match(/D:([0-9]+)x([0-9]+)/);
    if(m)return m[1]+'×'+m[2]+'mm';
    try{
      let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
      d.konturas.split('|').forEach(p=>{
        if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);if(!isNaN(cx)){minX=Math.min(minX,cx-r);maxX=Math.max(maxX,cx+r);minY=Math.min(minY,cy-r);maxY=Math.max(maxY,cy+r);}}
        else if(p.startsWith('L')){p.slice(1).trim().split(' ').forEach(pt=>{const[x,y]=pt.split(',').map(Number);if(!isNaN(x)&&!isNaN(y)){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}});}
      });
      if(isFinite(minX)&&maxX>minX&&maxY>minY){
        const ratio=(maxX-minX)/(maxY-minY);const area=parseFloat(d.plotas)||0;
        if(area>0){const Hmm=Math.round(Math.sqrt(area*100/ratio));return Math.round(ratio*Hmm)+'×'+Hmm+'mm';}
      }
    }catch(e){}
  }
  const area=parseFloat(d.plotas)||0;
  if(!area)return'—';
  return'~'+Math.round(Math.sqrt(area*100))+'mm';
}

function drawPrev(ents){
  const w=document.getElementById('cvW'),c=document.getElementById('dxfCv');
  w.style.display='block';
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  ents.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  if(!isFinite(minX))return;
  const W=w.clientWidth||400,H=150;c.width=W;c.height=H;
  const ctx=c.getContext('2d');ctx.fillStyle='#f0f2f4';ctx.fillRect(0,0,W,H);
  const rX=maxX-minX||1,rY=maxY-minY||1,sc=Math.min((W-30)/rX,(H-30)/rY)*.9;
  const oX=(W-rX*sc)/2-minX*sc,oY=(H+rY*sc)/2+minY*sc;
  ctx.strokeStyle='#0969da';ctx.lineWidth=1.5;
  ents.forEach(s=>{
    ctx.beginPath();
    if(s.type==='C')ctx.arc(s.cx*sc+oX,oY-s.cy*sc,s.r*sc,0,Math.PI*2);
    else if(s.type==='P'&&s.pts.length){ctx.moveTo(s.pts[0].x*sc+oX,oY-s.pts[0].y*sc);for(let i=1;i<s.pts.length;i++)ctx.lineTo(s.pts[i].x*sc+oX,oY-s.pts[i].y*sc);if(s.closed)ctx.closePath();}
    else if(s.type==='L'){ctx.moveTo(s.x1*sc+oX,oY-s.y1*sc);ctx.lineTo(s.x2*sc+oX,oY-s.y2*sc);}
    ctx.stroke();
  });
}

function drawContourSvg(konturas,sizeMm=14){
  if(!konturas)return'';
  try{
    const parts=konturas.replace(/^D:[0-9]+x[0-9]+[|]/,'').split('|');
    let paths='';
    parts.forEach(p=>{
      if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);paths+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#000" stroke-width="2"/>`;}
      else if(p.startsWith('L')){const pts=p.slice(1).trim().split(' ');if(pts.length<2)return;const d='M'+pts[0]+' '+pts.slice(1).map(pt=>'L'+pt).join(' ');paths+=`<path d="${d}" fill="none" stroke="#000" stroke-width="2"/>`;}
    });
    const s=sizeMm+'mm';
    return`<svg viewBox="-5 -5 110 110" width="${s}" height="${s}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">${paths}</svg>`;
  }catch(e){return'';}
}

"""

_MAINJS = """
// SANDĖLIO SISTEMA – main.js

let lkOrders=[],lkF='all',lkLC=null,lkLT=0;
let dxfOrders=[],dxfF='all',dxfDets=[],curOrd=null,curArea=0,curContour='';
let stock=[],history=[],stages=[],archOpen=null;
let pendingSt='',curStockId=null;
let settings={defaultPrice:0,lowAlert:2};

// GARSAS
let actx=null;
function ga(){if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();return actx;}
function beep(t){try{const c=ga();if(c.state==='suspended')c.resume();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;if(t==='new'){o.frequency.value=880;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.2);o.start(n);o.stop(n+.2);}else if(t==='col'){o.frequency.setValueAtTime(660,n);o.frequency.setValueAtTime(880,n+.12);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.3);o.start(n);o.stop(n+.3);}else if(t==='del'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(660,n+.1);o.frequency.setValueAtTime(880,n+.2);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='err'){o.type='sawtooth';o.frequency.value=220;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='dup'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(220,n+.15);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.35);o.start(n);o.stop(n+.35);}}catch(e){}}

// API
async function api(method,url,data){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(data)opts.body=JSON.stringify(data);
  const r=await fetch(url,opts);
  if(!r.ok)throw new Error(r.statusText);
  return r.json();
}

// INIT
window.onload=()=>{
  loadAll();
  const lt=localStorage.getItem('lastThick');
  if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}
  setPeriod(30);
  const dz=document.getElementById('dropZ');
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
};
document.addEventListener('click',e=>{if(actx&&actx.state==='suspended')actx.resume();if(document.getElementById('view-lk').classList.contains('active')&&!e.target.closest('input,button,select'))focusScan();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mbg').forEach(m=>m.style.display='none');});

async function loadAll(){await loadLk();await loadDxfOrds();await loadStock();await loadHist();await loadStages();}

// NAVIGACIJA
function SW(v){
  document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById('view-'+v).classList.add('active');
  const t=document.getElementById('tab-'+v);if(t)t.classList.add('active');
  if(v==='lk')focusScan();
  if(v==='dv'){const lt=localStorage.getItem('lastThick');if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}}
}
function CM(id){document.getElementById(id).style.display='none';}
function focusScan(){try{document.getElementById('scanInp').focus();}catch(e){}}
function toast(msg,w=false,t=''){const el=document.getElementById('toast');el.textContent=msg;el.className='toast '+(w?'w':t)+' show';clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),3000);}

// ════ LAKŠTAI ════
const scanInp=document.getElementById('scanInp');
scanInp.addEventListener('keydown',async e=>{if(e.key==='Enter'){const c=scanInp.value.trim();if(c){scanInp.value='';await handleScan(c);}}});

async function handleScan(kodas){
  const now=Date.now();
  if(kodas===lkLC&&now-lkLT<3000){lkRes('rp','DUBLIKATAS',kodas,'Tas pats kodas du kartus!');beep('dup');toast('Dublikatas: '+kodas,false,'p');lkLC=null;return;}
  lkLC=kodas;lkLT=now;
  const local=lkOrders.find(o=>o.kodas===kodas);
  if(local){
    if(local.delivered){lkRes('ra','JAU PERDUOTA',kodas,'Perduota: '+local.deliveredAt);beep('err');return;}
    if(local.collected){
      lkRes('rd','PERDUOTA',kodas,'3× — siunčiama...');beep('del');
      local.delivered=true;local.deliveredAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Perduota: '+kodas,false,'b');else{local.delivered=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }else{
      lkRes('rc','SURINKTA',kodas,'2× — siunčiama...');beep('col');
      local.collected=true;local.collectedAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Surinkta: '+kodas);else{local.collected=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }
    return;
  }
  lkRes('rn','NAUJAS',kodas,'1× — siunčiama...');beep('new');
  const newOrd={kodas,registered:nowS(),collected:false,collectedAt:'',delivered:false,deliveredAt:''};
  lkOrders.push(newOrd);lkStats();rlkList();
  api('POST','/api/lakstai/register',{kodas}).then(r=>{
    if(r.success)toast('Užregistruota: '+kodas);
    else if(r.alreadyExists){lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkAddL(r.order);lkStats();rlkList();handleScan(kodas);}
    else{lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkRes('re','KLAIDA',kodas,'Nepavyko');beep('err');lkStats();rlkList();}
  });
}

function lkRes(c,t,kodas,s){
  const b=document.getElementById('lkRes');
  b.className='res '+c;b.style.display='block';
  document.getElementById('lkRt').textContent=t;
  document.getElementById('lkRc').textContent=kodas;
  document.getElementById('lkRs').textContent=s;
}

async function loadLk(){
  try{const r=await api('GET','/api/lakstai');lkOrders=r.orders||[];lkStats();rlkList();document.getElementById('connDot').className='dot ok';}
  catch(e){document.getElementById('connDot').className='dot err';toast('Nepavyko prisijungti',true);}
}
function lkAddL(o){const i=lkOrders.findIndex(x=>x.kodas===o.kodas);if(i>=0)lkOrders[i]=o;else lkOrders.push(o);}
function lkStats(){
  const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length,p=lkOrders.filter(o=>!o.collected).length;
  const pc=t>0?Math.round(c/t*100):0,pd=t>0?Math.round(d/t*100):0;
  document.getElementById('lkT').textContent=t;document.getElementById('lkC').textContent=c;
  document.getElementById('lkD').textContent=d;document.getElementById('lkP').textContent=p;
  document.getElementById('lkPct').textContent=pc+'%';
  document.getElementById('lkPfc').style.width=pc+'%';document.getElementById('lkPfd').style.width=pd+'%';
  document.getElementById('lkBdg').textContent=p||t;
}
function lkFlt(f,b){lkF=f;document.querySelectorAll('.frow .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rlkList();}
function sortLk(l){return[...l].sort((a,b)=>{const n=s=>parseInt((s.match(/[0-9]+/)||[0])[0]);return n(a.kodas)-n(b.kodas);});}
function rlkList(){
  const el=document.getElementById('lkList'),q=(document.getElementById('lkSrch').value||'').toLowerCase();
  let l=sortLk(lkOrders);
  if(lkF==='p')l=l.filter(o=>!o.collected);if(lkF==='c')l=l.filter(o=>o.collected&&!o.delivered);if(lkF==='d')l=l.filter(o=>o.delivered);
  if(q)l=l.filter(o=>o.kodas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(lkOrders.length===0?'Nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>{
    const sc=o.delivered?'sdd':o.collected?'sc':'';
    const sl=o.delivered?'s2':o.collected?'s1':'s0';
    const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
    const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);
    return`<div class="oi ${sc}"><div class="od"></div><div class="oc">${o.kodas}</div><span class="ost ${sl}">${st}</span><div class="otm">${tm}</div><button class="btn btn-d btn-sm" onclick="lkDel('${o.kodas}')">✕</button></div>`;
  }).join('');
}
async function lkDel(k){if(!confirm('Ištrinti "'+k+'"?'))return;await api('DELETE','/api/lakstai/'+k);lkOrders=lkOrders.filter(o=>o.kodas!==k);lkStats();rlkList();toast('Ištrinta');}
function askStage(){
  const n=document.getElementById('stageInp').value.trim();
  if(!n){toast('Įvesk etapo pavadinimą!',true);return;}
  if(!lkOrders.length){toast('Nėra užsakymų',true);return;}
  pendingSt=n;const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length;
  document.getElementById('stMn').textContent='Etapas: "'+n+'"';
  document.getElementById('stMs').innerHTML='Iš viso: <strong>'+t+'</strong><br>Surinkta: <strong>'+c+'</strong><br>Perduota: <strong>'+d+'</strong><br>Laukia: <strong>'+(t-c)+'</strong>';
  document.getElementById('stModal').style.display='flex';
}
async function confirmStage(){
  CM('stModal');
  const r=await api('POST','/api/lakstai/archive',{pavadinimas:pendingSt});
  if(r.success){lkOrders=[];document.getElementById('stageInp').value='';lkStats();rlkList();await loadStages();beep('del');toast('Archyvuota: "'+r.archiveName+'"');lkRes('ra','ARCHYVUOTA',r.archiveName,r.collected+'/'+r.total+' surinkta');}
  else toast(r.message||'Klaida',true);
  focusScan();
}

// ════ SANDĖLIS ════
async function loadStock(){try{const r=await api('GET','/api/sandelis');stock=r.stock||[];rStock();document.getElementById('stkBdg').textContent=stock.length;}catch(e){}}
async function loadHist(){try{const r=await api('GET','/api/sandelis/istorija');history=r.history||[];rHist();}catch(e){}}

function rStock(){
  const el=document.getElementById('stkTbl'),su=document.getElementById('stkSum');
  if(!stock.length){el.innerHTML='<div class="empty-s">Sandėlis tuščias</div>';su.innerHTML='';return;}
  const totVnt=stock.reduce((s,r)=>s+r.likoVnt,0);
  const totKg=stock.reduce((s,r)=>s+r.likoKg,0);
  const totT=Math.round(totKg/10)/100;
  const totVal=stock.reduce((s,r)=>s+r.verte,0);
  const byT={};stock.forEach(r=>{if(!byT[r.storis])byT[r.storis]={vnt:0,kg:0};byT[r.storis].vnt+=r.likoVnt;byT[r.storis].kg+=r.likoKg;});
  su.innerHTML=`<div class="stk-s"><div class="stk-n">${totVnt}</div><div class="stk-l">Viso vnt.</div></div><div class="stk-s"><div class="stk-n">${totKg.toFixed(1)}</div><div class="stk-l">Viso kg</div></div><div class="stk-s"><div class="stk-n" style="color:var(--gn)">${totT}</div><div class="stk-l">Tonos</div></div><div class="stk-s"><div class="stk-n" style="color:var(--or)">${totVal.toFixed(2)}</div><div class="stk-l">Vertė €</div></div>`+
    Object.entries(byT).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).map(([t,v])=>`<div class="stk-s"><div class="stk-n" style="font-size:15px">${v.vnt}vnt</div><div class="stk-l">${t}mm · ${(Math.round(v.kg/10)/100).toFixed(2)}t</div></div>`).join('');
  const sorted=[...stock].sort((a,b)=>a.storis-b.storis);
  el.innerHTML=sorted.map(r=>{
    const nc=r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return`<div class="stk-row"><div><div class="stk-thick">${r.storis}<span>mm</span></div></div><div><div class="stk-dims">${r.matmenys}mm</div><div class="stk-sub">${r.pastabos||''}</div></div><div><div class="stk-num ${nc}">${r.likoVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:13px;color:var(--tx2)">${r.likoKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${r.likoT.toFixed(3)}</div><div class="stk-sub">t</div></div><div><div class="stk-val">${r.verte.toFixed(2)}€</div><div class="stk-sub">${r.kainaKg>0?r.kainaKg+'€/kg':''}</div></div><div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse('${r.id}','${r.storis}mm ${r.matmenys}',${r.likoVnt})">−</button><button class="btn btn-d btn-sm" onclick="delStk('${r.id}')">✕</button></div></div>`;
  }).join('')+`<div class="stk-tot"><div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);font-weight:700">VISO</div><div></div><div><div class="stk-num" style="font-size:13px;color:var(--ac)">${totVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${totKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">${totT}</div><div class="stk-sub">t</div></div><div><div class="stk-val" style="font-size:13px;font-weight:800">${totVal.toFixed(2)}€</div></div><div></div></div>`;
}

function rHist(){
  const el=document.getElementById('histTbl');
  if(!history.length){el.innerHTML='<div class="empty-s">Dar nėra istorijos</div>';return;}
  el.innerHTML=`<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>${history.slice(0,50).map(h=>`<tr><td class="mono" style="font-size:10px;color:var(--tx3)">${h.data}</td><td><span class="hist-act ${h.veiksmas[0]}">${h.veiksmas}</span></td><td class="mono">${h.storis}mm</td><td class="mono" style="color:var(--tx2)">${h.matmenys}</td><td class="mono">${h.kiekis}vnt.</td><td class="num">${h.svorisIšViso.toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

function showRecv(){
  if(settings.defaultPrice)document.getElementById('recP').value=settings.defaultPrice;
  document.getElementById('recvModal').style.display='flex';
}
function rcRecv(){
  const t=parseFloat(document.getElementById('recThk').value)||0,w=parseFloat(document.getElementById('recW').value)||0,l=parseFloat(document.getElementById('recL').value)||0,q=parseInt(document.getElementById('recQ').value)||1,p=parseFloat(document.getElementById('recP').value)||0;
  if(!w||!l){document.getElementById('recPrev').textContent='Įvesk matmenis...';return;}
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100,totT=Math.round(tot/10)/100,val=p>0?Math.round(tot*p*100)/100:0;
  document.getElementById('recPrev').innerHTML=`1 lakštas: <strong style="color:var(--ac)">${we}kg</strong> · ${q}vnt.: <strong style="color:var(--gn)">${tot}kg = ${totT}t</strong>${val>0?' · <strong style="color:var(--or)">'+val+'€</strong>':''}`;
}
async function doRecv(){
  const t=document.getElementById('recThk').value,w=document.getElementById('recW').value,l=document.getElementById('recL').value,q=document.getElementById('recQ').value,p=document.getElementById('recP').value,n=document.getElementById('recN').value;
  if(!w||!l){toast('Įvesk matmenis!',true);return;}
  const r=await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if(r.success){CM('recvModal');await loadStock();await loadHist();toast('Pridėta: '+q+'vnt. × '+t+'mm ('+r.likoT+'t)');}
}
function showUse(id,label,rem){curStockId=id;document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';document.getElementById('useQ').value=1;document.getElementById('useNote').value='';document.getElementById('useModal').style.display='flex';}
async function doUse(){
  const q=parseInt(document.getElementById('useQ').value)||1,n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if(r.success){CM('useModal');await loadStock();await loadHist();toast('Sunaudota: '+q+'vnt. Liko: '+r.likoVnt+'vnt.');}
  else toast('Klaida',true);
}
async function delStk(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/sandelis/'+id);await loadStock();toast('Ištrinta');}
function showSett(){document.getElementById('settP').value=settings.defaultPrice||'';document.getElementById('settL').value=settings.lowAlert||2;document.getElementById('settModal').style.display='flex';}
function saveSett(){settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;settings.lowAlert=parseInt(document.getElementById('settL').value)||2;CM('settModal');localStorage.setItem('sandSettings',JSON.stringify(settings));toast('Nustatymai išsaugoti');}

// ════ ARCHYVAI ════
async function loadStages(){try{const r=await api('GET','/api/etapai');stages=r.stages||[];document.getElementById('archBdg').textContent=stages.length;rStages();}catch(e){}}
function rStages(){
  const el=document.getElementById('stageCards');
  if(!stages.length){el.innerHTML='<div class="empty-s">Dar nėra archyvų</div>';return;}
  el.innerHTML=stages.map(s=>{
    const t=s.total||0,c=s.collected||0,d=s.delivered||0,p=s.pending||(t-c),pct=t>0?Math.round(c/t*100):0;
    return`<div class="scc ${archOpen===s.name?'open':''}" onclick="toggleArch('${s.name.replace(/'/g,"\\'")}')"><div class="scn">${s.name}</div><div class="scst"><div><span class="n">${t}</span><span class="l">Viso</span></div><div><span class="n g">${c}</span><span class="l">Surinkta</span></div><div><span class="n b">${d}</span><span class="l">Perduota</span></div><div><span class="n ${p>0?'r':'g'}">${p}</span><span class="l">Liko</span></div></div><div class="scp"><div class="scpf" style="width:${pct}%"></div></div></div>`;
  }).join('');
}
async function toggleArch(name){
  if(archOpen===name){archOpen=null;closeAd();rStages();return;}
  archOpen=name;rStages();
  document.getElementById('adTitle').textContent=name;
  document.getElementById('adList').innerHTML='<div class="empty-s"><span class="sp"></span> Kraunama...</div>';
  document.getElementById('adBox').style.display='block';
  try{
    const r=await api('GET','/api/etapai/'+encodeURIComponent(name));
    const items=sortLk(r.orders||[]);
    if(!items.length){document.getElementById('adList').innerHTML='<div class="empty-s">Tuščias</div>';return;}
    document.getElementById('adList').innerHTML=items.map(o=>{
      const sc=o.delivered?'sdd':o.collected?'sc':'';const tc=o.delivered?'d':o.collected?'c':'r';const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
      const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(0,16);
      return`<div class="adi ${sc}"><div class="addot"></div><div class="adcode">${o.kodas}</div><span class="adtag ${tc}">${st}</span><div class="adtime">${tm}</div></div>`;
    }).join('');
  }catch(e){}
}
function closeAd(){document.getElementById('adBox').style.display='none';archOpen=null;rStages();}

// ════ DXF ════
async function loadDxfOrds(){try{const r=await api('GET','/api/uzsakymai');dxfOrders=r.orders||[];dxfSum();rOrds();document.getElementById('dxfBdg').textContent=dxfOrders.length;}catch(e){}}
function dxfSum(){
  const t=dxfOrders.length,n=dxfOrders.filter(o=>o.statusas==='Naujas').length,a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length,d=dxfOrders.filter(o=>o.statusas==='Baigtas').length,w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML=`<div class="smc"><div class="smn a">${t}</div><div class="sml">Iš viso</div></div><div class="smc"><div class="smn" style="color:var(--yw)">${n}</div><div class="sml">Nauji</div></div><div class="smc"><div class="smn a">${a}</div><div class="sml">Vykdomi</div></div><div class="smc"><div class="smn" style="color:var(--gn)">${d}</div><div class="sml">Baigti</div></div><div class="smc"><div class="smn a">${w.toFixed(2)}</div><div class="sml">Svoris kg</div></div>`;
}
function dxfFlt(f,b){dxfF=f;document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rOrds();}
function rOrds(){
  const el=document.getElementById('ordsGrid'),q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all')l=l.filter(o=>o.statusas===dxfF);if(q)l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>`<div class="ocard" onclick="openOrd('${o.id}')"><div class="oct"><div class="oid">${o.id}</div><div style="display:flex;gap:4px"><span class="stb ${o.statusas}">${o.statusas}</span><button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd('${o.id}','${o.klientas.replace(/'/g,"\\'")}')">✕</button></div></div><div class="ocli">${o.klientas}</div><div class="ocdesc">${o.aprasymas||'—'}</div><div class="ocm"><div class="ocmi"><span class="v">${o.bendraSvoris.toFixed(3)}</span><span class="l"> kg</span></div><div class="ocmi"><span class="v">${o.detaliuSk}</span><span class="l"> det.</span></div><div class="ocmi"><span class="l">${(o.sukurta||'').slice(0,10)}</span></div></div></div>`).join('');
}
async function quickDelOrd(id,klientas){if(!confirm('Ištrinti "'+klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+id);dxfOrders=dxfOrders.filter(o=>o.id!==id);dxfSum();rOrds();toast('Ištrinta');}
function showNewOrd(){document.getElementById('noModal').style.display='flex';setTimeout(()=>document.getElementById('noC').focus(),100);}
async function createOrd(){
  const c=document.getElementById('noC').value.trim();if(!c){toast('Įvesk klientą!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id){
  const o=dxfOrders.find(x=>x.id===id);if(!o)return;curOrd=o;
  document.getElementById('dvId').textContent=o.id;document.getElementById('dvCli').textContent=o.klientas;document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' · '+o.pastabos:'');
  SW('dv');await loadDets();
}
function back2Ords(){SW('dxf');loadDxfOrds();curArea=0;curContour='';document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';}
async function chSt(){if(!curOrd)return;await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value});toast('Statusas atnaujintas');}
async function delOrd(){if(!curOrd)return;if(!confirm('Ištrinti "'+curOrd.klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+curOrd.id);toast('Ištrinta');back2Ords();}
async function loadDets(){
  if(!curOrd)return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[];rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
}

function rDets(){
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nėra detalių</div>';return;}
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const groups={};
  dxfDets.forEach(d=>{const t=String(d.storis);if(!groups[t])groups[t]={t,dets:[],w:0,q:0};groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;});
  let rows='';let idx=0;
  Object.values(groups).forEach(g=>{
    rows+=`<tr class="det-grp-hdr"><td colspan="2"></td><td colspan="2"><span class="det-grp-t">${g.t}mm</span></td><td><span class="det-grp-s">${g.dets.length}det.</span></td><td><span class="det-grp-s">${g.q}vnt.</span></td><td><span class="det-grp-s" style="color:var(--ac)">${g.w.toFixed(3)}kg</span></td><td></td></tr>`;
    g.dets.forEach(d=>{
      idx++;
      rows+=`<tr><td class="mono" style="color:var(--tx3);font-size:10px">${idx}</td><td style="font-weight:600">${d.pavadinimas}</td><td><select class="det-inp" onchange="updDet('${d.detId}','storis',this.value)">${STORIAI.map(t=>`<option value="${t}"${d.storis===t?' selected':''}>${t}mm</option>`).join('')}</select></td><td class="mono" style="font-size:11px;color:var(--tx2)">${calcDims(d)}</td><td><input type="number" class="det-inp" value="${d.kiekis}" min="1" style="width:50px" onchange="updDet('${d.detId}','kiekis',this.value)"></td><td><input type="number" class="det-inp num" value="${d.svoris.toFixed(3)}" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-${d.detId}" onchange="updDetW('${d.detId}',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td><td><button class="btn btn-d btn-sm" onclick="delDet('${d.detId}')">✕</button></td></tr>`;
    });
  });
  w.innerHTML=`<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">${tq}vnt.</strong></span><span>Bendras svoris: <span class="tot">${tw.toFixed(3)}kg</span></span></div>`;
}

async function updDet(detId,field,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  if(field==='storis')d.storis=parseFloat(value);else if(field==='kiekis')d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  const wEl=document.getElementById('w-'+detId);if(wEl)wEl.value=d.svoris.toFixed(3);
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas});
}
async function updDetW(detId,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
function _updateTotals(){
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  document.getElementById('dvWt').textContent=tw.toFixed(3);
}
async function delDet(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/detales/'+id);dxfDets=dxfDets.filter(d=>d.detId!==id);rDets();_updateTotals();toast('Ištrinta');}

// DXF ĮKĖLIMAS
function handleDxf(e){if(e.target.files.length)handleMultiDxf(Array.from(e.target.files));}
function handleFolder(e){
  if(!e.target.files.length)return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failų!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' → '+ft+'mm, '+files.length+' failų',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files){
  if(!curOrd){toast('Pirma atidaryk užsakymą!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Įkeliama '+files.length+' failų...';
  for(const file of files){
    await new Promise(resolve=>{
      const r=new FileReader();
      r.onload=async e2=>{
        try{
          const res=pDxf(e2.target.result);
          if(res.areaCm2<=0){fail++;resolve();return;}
          const at=thickFromName(file.name)||defThick;
          const aq=qtyFromName(file.name)||defQty;
          const ctour=serializeContour(res.entities,res.dimW,res.dimH);
          const resp=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:file.name.replace(/[.]dxf$/i,''),storis:at,plotas:res.areaCm2,kiekis:aq,konturas:ctour});
          if(resp.success)ok++;else fail++;
        }catch(ex){fail++;}
        resolve();
      };
      r.readAsText(file);
    });
  }
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Tempk DXF failus čia arba spusk';
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?`Įkelta: ${ok}, nepavyko: ${fail}`:`Sėkmingai įkeltos ${ok} detalės!`);
}
function procDxf(file){
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2;
      curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name);const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq)document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
      toast('DXF: '+res.areaCm2.toFixed(2)+'cm²'+(at?' · '+at+'mm':''));
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm² · '+t+'mm × '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd)return;if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd)return;const a=parseFloat(document.getElementById('mArea').value)||0;if(a<=0){toast('Įvesk plotą!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:''});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}

// ATASKAITA
function setPeriod(days){
  const to=new Date(),from=new Date();
  if(days===0)from.setDate(1);else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep(){
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpį!',true);return;}
  const r=await api('GET',`/api/ataskaita?nuo=${from}&iki=${to}`);
  const el=document.getElementById('repOut');
  el.style.display='block';
  el.innerHTML=`<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: ${from} — ${to}</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.lakstai.gauta}</div><div class="l">Lakštų gauta</div></div><div class="rep-sc"><div class="n">${r.lakstai.surinkta}</div><div class="l">Surinkta</div></div><div class="rep-sc"><div class="n">${r.lakstai.perduota}</div><div class="l">Perduota</div></div><div class="rep-sc"><div class="n">${r.dxf.sk}</div><div class="l">DXF užsakymų</div></div><div class="rep-sc"><div class="n">${r.dxf.svoris.toFixed(1)}</div><div class="l">DXF svoris kg</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio judėjimas</div><div class="rep-sr"><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.sandelis.gautaKg.toFixed(1)}</div><div class="l">Gauta kg</div></div><div class="rep-sc"><div class="n" style="color:var(--rd)">${r.sandelis.sunaudotaKg.toFixed(1)}</div><div class="l">Sunaudota kg</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.gautaVerte.toFixed(2)}</div><div class="l">Gauta vertė €</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.sunaudotaVerte.toFixed(2)}</div><div class="l">Sunaudota €</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio likutis dabar</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.likutis.vnt}</div><div class="l">Viso vnt.</div></div><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.likutis.t}</div><div class="l">Tonos</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.likutis.verte.toFixed(2)}</div><div class="l">Vertė €</div></div></div></div></div>`;
}

// SPAUSDINIMAS
function printOrd(){
  if(!curOrd)return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return`<tr><td style="font-weight:700;color:#1e3a5f">${t}mm</td><td style="text-align:center">${dets.length}</td><td style="text-align:center">${gq}</td><td style="text-align:right;font-weight:700">${gw.toFixed(3)}</td></tr>`;}).join('');
  let html=`<div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div><div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">${totW.toFixed(3)} kg</div></div><div><div class="ppi-l">Viso detalių</div><div class="ppi-v">${totQ} vnt.</div></div><div><div class="ppi-l">Storių sk.</div><div class="ppi-v">${groups.size} storiai</div></div></div><table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>${sumRows}<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">${sorted.length}</td><td style="text-align:center">${totQ}</td><td style="text-align:right">${totW.toFixed(3)}</td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>Išspausdinta: ${now}</span><span>${curOrd.id}</span></div>`;
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>`<tr><td>${i+1}</td><td><strong>${d.pavadinimas}</strong></td><td style="text-align:center">${calcDims(d)}</td><td style="text-align:center">${d.kiekis}</td><td style="text-align:right"><strong>${d.svoris.toFixed(3)}</strong></td><td style="text-align:center;vertical-align:middle">${drawContourSvg(d.konturas,12)}</td></tr>`).join('');
    html+=`<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">${thick}mm</div></div><div class="ppinfo"><div><div class="ppi-l">Svoris (${thick}mm)</div><div class="ppi-v">${gw.toFixed(3)} kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">${gq}vnt. (${dets.length}poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">${now}</div></div></div><table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>${rows}<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">${gq}vnt.</td><td style="text-align:right">${gw.toFixed(3)}kg</td><td></td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>${thick}mm · ${dets.length}poz. · ${gq}vnt. · ${gw.toFixed(3)}kg</span><span>${curOrd.id}</span></div></div>`;
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}

function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  const s='<style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style>';
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'+s+'</head><body>'+c+'</body>');
  w.document.close();
  setTimeout(function(){w.print();},500);
}

function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}

// Nustatymų įkėlimas
const savedSett=localStorage.getItem('sandSettings');
if(savedSett)try{settings=JSON.parse(savedSett);}catch(e){}

async function siustiEmail(){
  const btn=document.getElementById('emailBtn');
  btn.textContent='Siunčiama...';btn.disabled=true;
  try{
    const r=await fetch('/api/email/siusti',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const d=await r.json();
    if(d.success){alert('✓ '+d.message);}
    else{alert('Klaida: '+(d.detail||d.message));}
  }catch(e){alert('Klaida: '+e.message);}
  btn.textContent='✉ Siųsti ataskaitą';btn.disabled=false;
}

"""

_HTML = """<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0969da">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sandelis">
<link rel="manifest" href="/manifest.json">
<title>Sandelio Sistema</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
<nav>
  <div class="brand"><div class="brand-ico"></div>SANDELIS</div>
  <div class="tabs">
    <button class="tab active" onclick="SW('lk')" id="tab-lk">Lakstai <span class="bdg" id="lkBdg">0</span></button>
    <button class="tab" onclick="SW('stk')" id="tab-stk">Sandelis <span class="bdg y" id="stkBdg">0</span></button>
    <button class="tab" onclick="SW('dxf')" id="tab-dxf">DXF <span class="bdg gray" id="dxfBdg">0</span></button>
    <button class="tab" onclick="SW('arch')" id="tab-arch">Archyvai <span class="bdg gray" id="archBdg">0</span></button>
    <button class="tab" onclick="SW('rep')" id="tab-rep">Ataskaita</button>
  </div>
  <div class="nav-r"><div class="dot ok" id="connDot"></div></div>
</nav>

<div class="view active" id="view-lk">
  <div class="lk-wrap">
    <div class="lk-main">
      <div class="card">
        <div class="ct">Skanavimas</div>
        <div class="scan-f"><span class="scan-ico">▦</span><input class="scan-inp" id="scanInp" placeholder="Skanuok arba ivesk koda..." autocomplete="off" spellcheck="false"></div>
        <div class="hint" id="scanHint">Laukiama skanavimo...</div>
        <div class="steps"><div class="step s1"></div><div class="step s2"></div><div class="step s3"></div></div>
        <div class="step-lbl"><span>1x Registruota</span><span>2x Surinkta</span><span>3x Perduota</span></div>
      </div>
      <div class="res" id="lkRes" style="display:none"><div class="rt" id="lkRt"></div><div class="rc" id="lkRc"></div><div class="rs" id="lkRs"></div></div>
      <div class="stats-row">
        <div class="stat"><div class="sn a" id="lkT">0</div><div class="sl">Is viso</div></div>
        <div class="stat"><div class="sn g" id="lkC">0</div><div class="sl">Surinkta</div></div>
        <div class="stat"><div class="sn b" id="lkD">0</div><div class="sl">Perduota</div></div>
        <div class="stat"><div class="sn y" id="lkP">0</div><div class="sl">Laukia</div></div>
      </div>
      <div class="prog-card">
        <div class="pt"><span>Progresas</span><span class="pct" id="lkPct">0%</span></div>
        <div class="ptr"><div class="pfd" id="lkPfd" style="width:0%"></div><div class="pfc" id="lkPfc" style="width:0%"></div></div>
      </div>
      <div class="stbar">
        <span class="stbar-lbl">Naujas etapas:</span>
        <input type="text" id="stageInp" placeholder="pvz. Etapas 221">
        <button class="btn btn-p btn-sm" onclick="askStage()">Archyvuoti</button>
      </div>
    </div>
    <div class="lk-sb">
      <div class="sbh">
        <div class="sbt">Uzsakymai</div>
        <button class="btn btn-g btn-sm" onclick="loadLk()">&#x21BB;</button>
        <button id="pdfBtn" class="btn btn-s btn-sm" onclick="genPdfReport()">&#x22C6; Atsisiusti PDF</button>
        <div class="sbsr"><span class="sbs-i">&#x2315;</span><input type="text" id="lkSrch" placeholder="Ieskoti..." oninput="rlkList()"></div>
      </div>
      <div class="frow">
        <button class="fb active" onclick="lkFlt('all',this)">Visi</button>
        <button class="fb" onclick="lkFlt('p',this)">Laukia</button>
        <button class="fb" onclick="lkFlt('c',this)">Surinkti</button>
        <button class="fb" onclick="lkFlt('d',this)">Perduoti</button>
      </div>
      <div class="olist" id="lkList"><div class="empty-s">Jungiamasi...</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-stk">
  <div class="page-wrap">
    <div class="ph"><div><div class="ph-t">Metalo sandelis</div><div class="ph-s">Lakstu likuciai pagal stori</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-s btn-sm" onclick="showSett()">Nustatymai</button>
        <button class="btn btn-p" onclick="showRecv()">+ Gauti lakstus</button>
      </div>
    </div>
    <div class="stk-sum" id="stkSum"></div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Likutis</span><button class="btn btn-s btn-sm" onclick="loadStock()">&#x21BB;</button></div>
      <div id="stkTbl"><div class="empty-s">Sandelis tuscias</div></div>
    </div>
    <div class="card" style="overflow:hidden;padding:0;margin-top:12px">
      <div class="card-h"><span class="card-t">Istorija</span><button class="btn btn-s btn-sm" onclick="loadHist()">&#x21BB;</button></div>
      <div id="histTbl"><div class="empty-s">Dar nera istorijos</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-dxf">
  <div class="page-wrap">
    <div class="ph"><div class="ph-t">DXF Uzsakymai</div><button class="btn btn-p" onclick="showNewOrd()">+ Naujas</button></div>
    <div class="sumr" id="dxfSum"></div>
    <div class="fbar">
      <button class="fb active" onclick="dxfFlt('all',this)">Visi</button>
      <button class="fb" onclick="dxfFlt('Naujas',this)">Nauji</button>
      <button class="fb" onclick="dxfFlt('Vykdomas',this)">Vykdomi</button>
      <button class="fb" onclick="dxfFlt('Baigtas',this)">Baigti</button>
      <input class="si" id="dxfSrch" placeholder="Ieskoti..." oninput="rOrds()">
    </div>
    <div class="og" id="ordsGrid"><div class="empty-s">Jungiamasi...</div></div>
  </div>
</div>

<div class="view" id="view-dv">
  <div class="page-wrap">
    <div class="back" onclick="back2Ords()">&#x2190; Grizti</div>
    <div class="card" style="margin-bottom:12px">
      <div class="oi-top">
        <div><div class="oid" id="dvId"></div><div class="oi-t" id="dvCli"></div><div class="oi-s" id="dvDsc"></div></div>
        <div style="text-align:right">
          <div class="wbig" id="dvWt">0</div><div class="wlbl">kg bendras svoris</div>
          <div style="margin-top:8px;display:flex;gap:5px;justify-content:flex-end;flex-wrap:wrap">
            <select class="stsel" id="dvSt" onchange="chSt()"><option>Naujas</option><option>Vykdomas</option><option>Baigtas</option></select>
            <button class="btn btn-p btn-sm" onclick="printOrd()">Spausdinti</button>
            <button class="btn btn-d btn-sm" onclick="delOrd()">Trinti</button>
          </div>
        </div>
      </div>
      <div id="dvMeta" style="font-size:11px;color:#57606a;font-family:'JetBrains Mono',monospace;margin-top:6px"></div>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Prideti detale is DXF</div>
      <div class="dropz" id="dropZ">
        <input type="file" id="dxfFile" accept=".dxf" multiple onchange="handleDxf(event)">
        <div class="dz-t">Tempk DXF failus cia arba spusk</div>
        <div class="dz-s">.dxf - galima ikelti kelis failus</div>
      </div>
      <div style="margin-top:8px">
        <label class="btn btn-s btn-sm" style="cursor:pointer">Ikelti aplanka<input type="file" id="dxfFolder" webkitdirectory multiple accept=".dxf" style="display:none" onchange="handleFolder(event)"></label>
      </div>
      <div class="cvw" id="cvW" style="display:none"><canvas id="dxfCv"></canvas></div>
      <div class="pf" id="pForm" style="display:none">
        <div class="wp"><div class="wv" id="wPv">0.000</div><div class="wl">kg (vieno vnt.)</div><div class="wa" id="wAr"></div></div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="dName"></div>
          <div><label class="fl">Storis (mm)</label><select id="dThk" onchange="rcW();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Kiekis</label><input type="number" id="dQty" value="1" min="1" oninput="rcW()"></div>
        </div>
        <button class="btn btn-p" style="width:100%" onclick="addDet()">+ Prideti detale</button>
      </div>
      <div class="msec">
        <div class="mlbl">arba ivesk rankiniu budu</div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="mName"></div>
          <div><label class="fl">Storis (mm)</label><select id="mThk" onchange="rcM();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Plotas (cm2)</label><input type="number" id="mArea" step="0.01" oninput="rcM()"></div>
        </div>
        <div class="fgrid">
          <div><label class="fl">Kiekis</label><input type="number" id="mQty" value="1" min="1" oninput="rcM()"></div>
          <div><label class="fl">Svoris</label><div class="svor-d" id="mWp">0.000 kg</div></div>
          <div style="display:flex;align-items:flex-end"><button class="btn btn-p" style="width:100%" onclick="addMDet()">+ Prideti</button></div>
        </div>
      </div>
    </div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Detaliu sarasas</span><button class="btn btn-s btn-sm" onclick="loadDets()">&#x21BB;</button></div>
      <div id="dtWrap"><div class="empty-s">Dar nera detaliu</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-arch">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Archyvai</div>
    <div class="sc-grid" id="stageCards"><div class="empty-s">Dar nera archivu</div></div>
    <div class="adbox" id="adBox" style="display:none">
      <div class="adh"><div class="adt" id="adTitle"></div><button class="btn btn-s btn-sm" onclick="closeAd()">X</button></div>
      <div class="adlist" id="adList"></div>
    </div>
  </div>
</div>

<div class="view" id="view-rep">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Ataskaita</div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Laikotarpis</div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr;margin-bottom:10px">
        <div><label class="fl">Nuo</label><input type="date" id="repFrom"></div>
        <div><label class="fl">Iki</label><input type="date" id="repTo"></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
        <button class="btn btn-s btn-sm" onclick="setPeriod(7)">7 dienos</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(30)">30 dienu</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(0)">Sis menuo</button>
      </div>
      <button class="btn btn-p" onclick="genRep()">Generuoti</button>
    </div>
    <div id="repOut" style="display:none"></div>
  </div>
</div>

<div class="mbg" id="noModal" style="display:none">
  <div class="modal">
    <div class="mh">Naujas DXF uzsakymas</div>
    <div class="mf">
      <div><label class="fl">Klientas *</label><input type="text" id="noC"></div>
      <div><label class="fl">Aprasymas</label><input type="text" id="noD"></div>
      <div><label class="fl">Pastabos</label><textarea id="noN"></textarea></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('noModal')">Atsaukti</button><button class="btn btn-p" onclick="createOrd()">Sukurti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="recvModal" style="display:none">
  <div class="modal">
    <div class="mh">Gauti lakstus</div>
    <div class="mf">
      <div><label class="fl">Storis (mm)</label><select id="recThk"><option value="3">3 mm</option><option value="4">4 mm</option><option value="5">5 mm</option><option value="6">6 mm</option><option value="8">8 mm</option><option value="10">10 mm</option><option value="12">12 mm</option><option value="14">14 mm</option><option value="15">15 mm</option><option value="16">16 mm</option><option value="18">18 mm</option><option value="20">20 mm</option><option value="25">25 mm</option></select></div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Plotis (mm)</label><input type="number" id="recW" oninput="rcRecv()"></div>
        <div><label class="fl">Ilgis (mm)</label><input type="number" id="recL" oninput="rcRecv()"></div>
      </div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Kiekis (vnt.)</label><input type="number" id="recQ" value="1" oninput="rcRecv()"></div>
        <div><label class="fl">Kaina / t (EUR)</label><input type="number" id="recP" step="0.01" oninput="rcRecv()"></div>
      </div>
      <div class="rec-prev" id="recPrev">Ivesk matmenis...</div>
      <div><label class="fl">Pastabos (SF nr.)</label><input type="text" id="recN"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('recvModal')">Atsaukti</button><button class="btn btn-p" onclick="doRecv()">Prideti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="useModal" style="display:none">
  <div class="modal">
    <div class="mh">Sunaudoti lakstus</div>
    <div class="mf">
      <div id="useInfo" class="rec-prev"></div>
      <div><label class="fl">Kiek vnt.?</label><input type="number" id="useQ" value="1" min="1"></div>
      <div><label class="fl">Pastabos</label><input type="text" id="useNote"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('useModal')">Atsaukti</button><button class="btn btn-y" onclick="doUse()">Sunaudoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="settModal" style="display:none">
  <div class="modal">
    <div class="mh">Nustatymai</div>
    <div class="mf">
      <div><label class="fl">Numatyta kaina / kg (EUR)</label><input type="number" id="settP" step="0.01"></div>
      <div><label class="fl">Zemos atsargos ispejimas</label><input type="number" id="settL" value="2" min="0"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('settModal')">Atsaukti</button><button class="btn btn-p" onclick="saveSett()">Issaugoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="stModal" style="display:none">
  <div class="modal">
    <div class="mh">Archyvuoti etapa?</div>
    <div id="stMn" style="font-size:11px;color:#57606a;margin-bottom:10px"></div>
    <div id="stMs" class="rec-prev" style="margin-bottom:12px;line-height:2"></div>
    <div class="mb"><button class="btn btn-s" onclick="CM('stModal')">Atsaukti</button><button class="btn btn-p" onclick="confirmStage()">Archyvuoti</button></div>
  </div>
</div>

<div class="pmb" id="printMod" style="display:none">
  <div class="pm">
    <div class="pbr">
      <button class="btn btn-p btn-sm" onclick="window.print()">Spausdinti</button>
      <button class="btn btn-s btn-sm" onclick="dlPdf()">PDF</button>
      <button class="btn btn-s btn-sm" onclick="CM('printMod')">Uzdaryti</button>
    </div>
    <div id="printArea"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const STORIAI=[3,4,5,6,8,10,12,14,15,16,18,20,25];
const TANKIS=8000;
</script>
<script src="/static/js/dxf.js"></script>
<script src="/static/js/main.js"></script>
</body>
</html>"""

@app.on_event("startup")
def startup():
    init_db()

@app.get("/static/css/main.css")
async def serve_css():
    return Response(content=_CSS, media_type="text/css")

@app.get("/static/js/dxf.js")
async def serve_dxfjs():
    return Response(content=_DXFJS, media_type="application/javascript")

@app.get("/static/js/main.js")
async def serve_mainjs():
    return Response(content=_MAINJS, media_type="application/javascript")

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({"name":"Sandelio Sistema","short_name":"Sandelis","start_url":"/","display":"standalone","background_color":"#f6f8fa","theme_color":"#0969da"})

@app.get("/sw.js")
async def sw():
    return Response(content="// sw", media_type="application/javascript")

@app.get("/icon.png")
async def icon():
    import base64
    return Response(content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="), media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=_HTML)


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
        raise HTTPException(400, "SMTP_PASS nenurodytas Railway Variables")
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti = [l for l in items if l.surinkta and not l.perduota]
    perduoti = [l for l in items if l.perduota]
    laukia = [l for l in items if not l.surinkta]
    def rows(lst, color):
        if not lst: return "<tr><td colspan=2 style='color:#aaa;padding:4px 8px'>Tuscia</td></tr>"
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else '-'}</td></tr>" for l in lst)
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
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
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th></tr>{rows(laukia,'#9a6700')}</table>
      <p style='color:#57606a;font-size:11px;margin-top:16px'>Issiusta is Sandelio sistemos - metalcraft.lt</p>
    </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandelio ataskaita {now}"
        msg["From"] = f"Metalcraft <{smtp_user}>"
        msg["To"] = gaivejas
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        # Bandome 587 su STARTTLS
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        except Exception as e1:
            # Bandome 465 su SSL
            with smtplib.SMTP_SSL(smtp_host, 465, timeout=30) as s:
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        return {"success": True, "message": f"Issiusta i {gaivejas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# LAKŠTAI API
# ══════════════════════════════════════════════════

@app.get("/api/lakstai")
def get_lakstai(etapas: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lakstai)
    if etapas:
        q = q.filter(Lakstai.etapas == etapas)
    else:
        q = q.filter(Lakstai.etapas == None)
    items = q.all()
    return {"orders": [_lk(l) for l in items]}

@app.get("/api/lakstai/find/{kodas}")
def find_lakstas(kodas: str, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == kodas).first()
    if not l:
        return {"found": False}
    return {"found": True, **_lk(l)}

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
        return {"success": False, "message": "Nėra užsakymų"}
    total = len(items); collected = sum(1 for l in items if l.surinkta); delivered = sum(1 for l in items if l.perduota)
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

# ══════════════════════════════════════════════════
# DXF API
# ══════════════════════════════════════════════════

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
    d = Detale(det_id=det_id, uzsakymo_id=data["uzsakymoId"], pavadinimas=data.get("pavadinimas", "Detalė"),
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

# ══════════════════════════════════════════════════
# SANDĖLIS API
# ══════════════════════════════════════════════════

@app.get("/api/sandelis")
def get_sandelis(db: Session = Depends(get_db)):
    items = db.query(Sandelis).order_by(Sandelis.storis).all()
    return {"stock": [_stk(s) for s in items]}

@app.post("/api/sandelis/gauti")
def gauti(data: dict, db: Session = Depends(get_db)):
    storis = float(data["storis"]); w = float(data["plotis"]); l = float(data["ilgis"]); qty = int(data["kiekis"])
    kaina = float(data.get("kaina", 0))
    svoris_vnt = round((w/1000) * (l/1000) * (storis/1000) * TANKIS, 2)
    liko_kg = round(svoris_vnt * qty, 2)
    liko_t = round(liko_kg / 1000, 3)
    verte = round(liko_t * kaina, 2)  # kaina uz tona
    stk_id = "STK-" + str(int(datetime.utcnow().timestamp() * 1000))
    s = Sandelis(stk_id=stk_id, storis=storis, matmenys=f"{int(w)}×{int(l)}", svoris_vnt=svoris_vnt,
                 gauta_vnt=qty, liko_vnt=qty, liko_kg=liko_kg, liko_t=liko_t, kaina_kg=kaina, verte=verte,
                 pastabos=data.get("pastabos", ""))
    db.add(s)
    hist = SandelioIstorijia(veiksmas="Gauta", storis=storis, matmenys=f"{int(w)}×{int(l)}", kiekis=qty,
                              svoris_vnt=svoris_vnt, svoris_iš_viso=liko_kg, kaina_kg=kaina, verte=verte, pastabos=data.get("pastabos", ""))
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
    s.verte = round(s.liko_t * s.kaina_kg, 2)  # kaina uz tona
    hist = SandelioIstorijia(veiksmas="Sunaudota", storis=s.storis, matmenys=s.matmenys, kiekis=qty,
                              svoris_vnt=s.svoris_vnt, svoris_iš_viso=round(qty*s.svoris_vnt, 2),
                              kaina_kg=s.kaina_kg, verte=round((qty*s.svoris_vnt/1000)*s.kaina_kg, 2), pastabos=data.get("pastabos", ""))
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
    return {"history": [{"data": h.data.strftime("%Y-%m-%d %H:%M"), "veiksmas": h.veiksmas, "storis": h.storis,
                          "matmenys": h.matmenys, "kiekis": h.kiekis, "svorisVnt": h.svoris_vnt,
                          "svorisIšViso": h.svoris_iš_viso, "kainaKg": h.kaina_kg, "verte": h.verte} for h in items]}

# ══════════════════════════════════════════════════
# ATASKAITA
# ══════════════════════════════════════════════════

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
            "pagalStori": [{"storis": s.storis, "vnt": s.liko_vnt, "kg": round(s.liko_kg, 1), "t": s.liko_t} for s in sorted(stock, key=lambda x: x.storis)]
        }
    }


# ══════════════════════════════════════════════════
# EL. PAŠTAS
# ══════════════════════════════════════════════════

@app.post("/api/email/siusti")
async def siusti_email(data: dict, db: Session = Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    smtp_host = os.getenv("SMTP_HOST", "vytis.serveriai.lt")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "info@metalcraft.lt")
    smtp_pass = os.getenv("SMTP_PASS", "")
    gavėjas   = os.getenv("EMAIL_TO", "gintaras@metalikalt.eu")
    
    if not smtp_pass:
        raise HTTPException(400, "SMTP slaptažodis nenurodytas")
    
    # Gauti lakštus
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti  = [l for l in items if l.surinkta and not l.perduota]
    perduoti  = [l for l in items if l.perduota]
    laukia    = [l for l in items if not l.surinkta]
    
    # HTML laiškas
    def rows(lst, color):
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else ''}</td></tr>" for l in lst)
    
    html = f"""
    <html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>
    <div style='background:#0969da;padding:16px;border-radius:8px 8px 0 0'>
      <h2 style='color:white;margin:0'>Sandėlio ataskaita – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</h2>
    </div>
    <div style='padding:16px;background:#f6f8fa;border-radius:0 0 8px 8px'>
      <p>Iš viso: <strong>{len(items)}</strong> | Surinkta: <strong style='color:#1a7f37'>{len(surinkti)}</strong> | Perduota: <strong style='color:#0969da'>{len(perduoti)}</strong> | Laukia: <strong style='color:#9a6700'>{len(laukia)}</strong></p>
      
      {'<h3 style="color:#1a7f37">✓ Surinkta</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Kodas</th><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Laikas</th></tr>' + rows(surinkti, '#1a7f37') + '</table>' if surinkti else ''}
      
      {'<h3 style="color:#0969da">→ Perduota</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Kodas</th><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Laikas</th></tr>' + rows(perduoti, '#0969da') + '</table>' if perduoti else ''}
      
      {'<h3 style="color:#9a6700">⏳ Laukia</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#fff8c5">Kodas</th><th style="text-align:left;padding:4px 8px;background:#fff8c5">Laikas</th></tr>' + rows(laukia, '#9a6700') + '</table>' if laukia else ''}
      
      <p style='color:#57606a;font-size:12px;margin-top:16px'>Išsiųsta iš Sandėlio sistemos – metalcraft.lt</p>
    </div>
    </body></html>
    """
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandėlio ataskaita {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        msg["From"]    = f"Metalcraft <{smtp_user}>"
        msg["To"]      = gavėjas
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, gavėjas, msg.as_string())
        
        return {"success": True, "message": f"Išsiųsta į {gavėjas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# ══════════════════════════════════════════════════
# PAGALBINĖS FUNKCIJOS
# ══════════════════════════════════════════════════

def _lk(l):
    return {"kodas": l.kodas, "registered": l.registruota.strftime("%Y-%m-%d %H:%M:%S") if l.registruota else "",
            "collected": l.surinkta, "collectedAt": l.surinkta_kada.strftime("%Y-%m-%d %H:%M:%S") if l.surinkta_kada else "",
            "delivered": l.perduota, "deliveredAt": l.perduota_kada.strftime("%Y-%m-%d %H:%M:%S") if l.perduota_kada else ""}

def _uzs(u):
    return {"id": u.uzs_id, "klientas": u.klientas, "aprasymas": u.aprasymas or "", "pastabos": u.pastabos or "",
            "statusas": u.statusas, "bendraSvoris": u.bendras_svoris, "detaliuSk": u.detaliu_sk,
            "sukurta": u.sukurta.strftime("%Y-%m-%d %H:%M:%S") if u.sukurta else ""}

def _det(d):
    return {"detId": d.det_id, "uzsakymoId": d.uzsakymo_id, "pavadinimas": d.pavadinimas,
            "storis": d.storis, "plotas": d.plotas, "kiekis": d.kiekis, "svoris": d.svoris,
            "konturas": d.konturas or "", "prideta": d.prideta.strftime("%Y-%m-%d %H:%M:%S") if d.prideta else ""}

def _stk(s):
    return {"id": s.stk_id, "storis": s.storis, "matmenys": s.matmenys, "svorisVnt": s.svoris_vnt,
            "gautaVnt": s.gauta_vnt, "sunaudotaVnt": s.sunaudota_vnt, "likoVnt": s.liko_vnt,
            "likoKg": s.liko_kg, "likoT": s.liko_t, "kainaKg": s.kaina_kg, "verte": s.verte,
            "prideta": s.prideta.strftime("%Y-%m-%d %H:%M:%S") if s.prideta else "", "pastabos": s.pastabos or ""}

def _recalc(uzs_id, db):
    dets = db.query(Detale).filter(Detale.uzsakymo_id == uzs_id).all()
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if u:
        u.bendras_svoris = round(sum(d.svoris for d in dets), 3)
        u.detaliu_sk = len(dets)
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os

from database import get_db, init_db, Lakstai, Etapas, Uzsakymas, Detale, Sandelis, SandelioIstorijia

app = FastAPI(title="Sandelio Sistema")
TANKIS = 8000

_CSS = """*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#f6f8fa;--s1:#ffffff;--s2:#f0f2f4;--s3:#e1e4e8;
  --bd:#d0d7de;--bd2:#afb8c1;
  --tx:#1f2328;--tx2:#57606a;--tx3:#848d97;
  --ac:#0969da;--ac2:#0550ae;--ac-bg:rgba(9,105,218,.08);
  --gn:#1a7f37;--gn-bg:rgba(26,127,55,.08);--gn-bd:rgba(26,127,55,.3);
  --yw:#9a6700;--yw-bg:rgba(154,103,0,.08);--yw-bd:rgba(154,103,0,.3);
  --rd:#cf222e;--rd-bg:rgba(207,34,46,.08);--rd-bd:rgba(207,34,46,.3);
  --pp:#6639ba;--pp-bg:rgba(102,57,186,.08);
  --or:#953800;
}
body{background:var(--bg);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;min-height:100vh;font-size:14px}

nav{background:var(--s1);border-bottom:1px solid var(--bd);padding:0 16px;height:52px;display:flex;align-items:center;gap:8px;position:sticky;top:0;z-index:50}
.brand{font-size:15px;font-weight:800;display:flex;align-items:center;gap:8px;flex-shrink:0}
.brand-ico{width:26px;height:26px;background:linear-gradient(135deg,#0969da,#6639ba);border-radius:6px}
.tabs{display:flex;height:100%;overflow-x:auto;flex:1;justify-content:center}
.tab{padding:0 13px;height:100%;display:flex;align-items:center;gap:4px;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;border:none;background:none;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}
.tab:hover{color:var(--tx)}.tab.active{color:var(--ac);border-bottom-color:var(--ac)}
.bdg{background:var(--ac);color:#fff;font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px}
.bdg.y{background:var(--yw)}.bdg.gray{background:var(--s3);color:var(--tx2)}.bdg.r{background:var(--rd)}
.nav-r{margin-left:auto;display:flex;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--bd2)}.dot.ok{background:var(--gn)}.dot.err{background:var(--rd)}

.view{display:none}.view.active{display:block}
.page-wrap{padding:16px;max-width:1000px;margin:0 auto}
.ph{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ph-t{font-size:18px;font-weight:800}.ph-s{font-size:11px;color:var(--tx2);margin-top:2px}

.btn{padding:7px 14px;border:none;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:12px;cursor:pointer;border-radius:6px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;white-space:nowrap}
.btn-p{background:var(--ac);color:#fff}.btn-p:hover{background:var(--ac2)}
.btn-s{background:transparent;border:1px solid var(--bd);color:var(--tx2)}.btn-s:hover{border-color:var(--tx);color:var(--tx)}
.btn-g{background:var(--gn-bg);border:1px solid var(--gn-bd);color:var(--gn)}.btn-g:hover{background:var(--gn);color:#fff}
.btn-d{background:transparent;border:1px solid transparent;color:var(--tx3)}.btn-d:hover{border-color:var(--rd-bd);color:var(--rd);background:var(--rd-bg)}
.btn-y{background:var(--yw-bg);border:1px solid var(--yw-bd);color:var(--yw)}.btn-y:hover{background:var(--yw);color:#fff}
.btn-sm{padding:4px 9px;font-size:11px}

.fl{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:4px}
input[type=text],input[type=number],input[type=date],input[type=email],textarea,select{width:100%;padding:7px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;outline:none;border-radius:6px;transition:border-color .15s;-webkit-appearance:none}
input:focus,textarea:focus,select:focus{border-color:var(--ac)}
textarea{resize:vertical;min-height:60px}
option{background:var(--s1)}

.card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;margin-bottom:12px}
.card-h{padding:12px 16px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.card-t{font-weight:700;font-size:14px}
.ct{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.ct::after{content:'';flex:1;height:1px;background:var(--bd)}

.mbg{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:24px;max-width:440px;width:100%;margin:auto}
.mh{font-size:17px;font-weight:800;margin-bottom:16px}
.mf{display:flex;flex-direction:column;gap:12px}
.mb{display:flex;gap:8px;justify-content:flex-end;margin-top:6px}

.toast{position:fixed;bottom:14px;right:14px;left:14px;max-width:340px;margin:0 auto;padding:11px 14px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;background:var(--s1);border:1px solid var(--bd);border-left:3px solid var(--gn);box-shadow:0 8px 24px rgba(0,0,0,.15);transform:translateY(70px);opacity:0;transition:all .25s;z-index:300;border-radius:6px}
.toast.w{border-left-color:var(--rd)}.toast.b{border-left-color:var(--ac)}.toast.p{border-left-color:var(--pp)}
.toast.show{transform:translateY(0);opacity:1}
.sp{display:inline-block;width:11px;height:11px;border:2px solid var(--bd2);border-top-color:var(--ac);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:4px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.empty-s{padding:40px;text-align:center;color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:12px}

/* LAKŠTAI */
.lk-wrap{display:grid;grid-template-columns:1fr 290px;min-height:calc(100vh - 52px)}
@media(max-width:680px){.lk-wrap{grid-template-columns:1fr}}
.lk-main{padding:16px;display:flex;flex-direction:column;gap:10px}
.lk-sb{border-left:1px solid var(--bd);background:var(--s1);display:flex;flex-direction:column}
.scan-f{position:relative}.scan-ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:16px;pointer-events:none;color:var(--tx3)}
.scan-inp{padding:11px 14px 11px 40px!important;font-size:17px!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important}
.scan-inp:focus{border-color:var(--ac)!important;box-shadow:0 0 0 3px var(--ac-bg)}
.hint{margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3)}
.steps{display:flex;gap:4px;margin-top:10px}
.step{flex:1;height:3px;background:var(--bd);border-radius:2px}
.s1{background:var(--yw)}.s2{background:var(--gn)}.s3{background:var(--ac)}
.step-lbl{display:flex;justify-content:space-between;margin-top:4px;font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.res{border:1px solid var(--bd);border-radius:8px;padding:12px 14px;animation:fadeUp .2s ease}
.res.rn{background:var(--yw-bg);border-color:var(--yw-bd)}.res.rc{background:var(--gn-bg);border-color:var(--gn-bd)}
.res.rd{background:var(--ac-bg);border-color:rgba(9,105,218,.3)}.res.re{background:var(--rd-bg);border-color:var(--rd-bd)}
.res.rp{background:var(--pp-bg);border-color:rgba(102,57,186,.3)}.res.ra{background:var(--gn-bg);border-color:var(--gn-bd)}
.rt{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}
.res.rn .rt{color:var(--yw)}.res.rc .rt{color:var(--gn)}.res.rd .rt{color:var(--ac)}.res.re .rt{color:var(--rd)}.res.rp .rt{color:var(--pp)}.res.ra .rt{color:var(--gn)}
.rc{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace}.rs{font-size:11px;color:var(--tx2);margin-top:2px}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
@media(max-width:480px){.stats-row{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.sn{font-size:22px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace}
.sn.a{color:var(--ac)}.sn.g{color:var(--gn)}.sn.b{color:var(--ac)}.sn.y{color:var(--yw)}
.sl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.prog-card{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px}
.pt{display:flex;justify-content:space-between;margin-bottom:6px;font-size:10px;color:var(--tx2);font-family:'JetBrains Mono',monospace}
.pct{color:var(--gn);font-weight:700}
.ptr{height:6px;background:var(--s2);border-radius:3px;overflow:hidden;position:relative}
.pfc{height:100%;background:var(--gn);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px}
.pfd{height:100%;background:var(--ac);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px;opacity:.4}
.stbar{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:12px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.stbar-lbl{font-weight:700;font-size:13px;white-space:nowrap}.stbar input{flex:1;min-width:130px}
.stbar-hint{font-size:9px;color:var(--tx3);width:100%;font-family:'JetBrains Mono',monospace}
.sbh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}
.sbt{font-weight:700;font-size:12px}.sbsr{position:relative;width:100%}
.sbsr input{padding:5px 10px 5px 26px;font-size:11px}.sbs-i{position:absolute;left:8px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--tx3);pointer-events:none}
.frow{padding:6px 14px;border-bottom:1px solid var(--bd);display:flex;gap:4px;flex-wrap:wrap}
.fb{padding:3px 8px;background:transparent;border:1px solid var(--bd);color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:9px;cursor:pointer;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;transition:all .15s}
.fb.active{background:var(--tx);color:var(--bg);border-color:var(--tx);font-weight:700}
.olist{flex:1;overflow-y:auto}
.oi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:6px;transition:background .1s}
.oi:hover{background:var(--s2)}
.od{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.oi.sc .od{background:var(--gn)}.oi.sdd .od{background:var(--ac)}
.oc{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ost{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700;flex-shrink:0}
.ost.s0{background:var(--yw-bg);color:var(--yw)}.ost.s1{background:var(--gn-bg);color:var(--gn)}.ost.s2{background:var(--ac-bg);color:var(--ac)}
.otm{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);flex-shrink:0}

/* SANDĖLIS */
.stk-sum{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin-bottom:14px}
.stk-s{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.stk-n{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.stk-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.stk-row{padding:10px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.stk-row:last-child{border-bottom:none}.stk-row:hover{background:var(--s2)}
@media(max-width:600px){.stk-row{grid-template-columns:1fr 1fr;gap:6px}}
.stk-thick{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:var(--ac)}
.stk-thick span{font-size:10px;color:var(--tx3)}
.stk-dims{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.stk-num{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700}
.stk-num.ok{color:var(--gn)}.stk-num.warn{color:var(--yw)}.stk-num.empty{color:var(--rd)}
.stk-sub{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.stk-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--or)}
.stk-acts{display:flex;gap:4px}
.stk-tot{padding:10px 16px;background:var(--s2);border-top:2px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.hist-row{padding:8px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:130px 60px 90px 60px 80px 80px;align-items:center;gap:8px;font-size:12px}
.hist-row:last-child{border-bottom:none}.hist-row:hover{background:var(--s2)}
.hist-act{font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700}
.hist-act.G{background:var(--gn-bg);color:var(--gn)}.hist-act.S{background:var(--rd-bg);color:var(--rd)}
.rec-prev{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--tx2)}

/* DXF */
.sumr{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin-bottom:14px}
.smc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.smn{font-size:20px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.sml{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.fbar{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.si{padding:5px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:11px;outline:none;border-radius:6px;min-width:150px}
.si:focus{border-color:var(--ac)}
.og{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.ocard{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.ocard:hover{border-color:var(--ac);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.oct{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.oid{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3)}
.stb{font-family:'JetBrains Mono',monospace;font-size:9px;padding:2px 7px;border-radius:4px;font-weight:700}
.stb.Naujas{background:var(--yw-bg);color:var(--yw);border:1px solid var(--yw-bd)}
.stb.Vykdomas{background:var(--ac-bg);color:var(--ac);border:1px solid rgba(9,105,218,.3)}
.stb.Baigtas{background:var(--gn-bg);color:var(--gn);border:1px solid var(--gn-bd)}
.ocli{font-size:14px;font-weight:700;margin-bottom:2px}.ocdesc{font-size:11px;color:var(--tx2);margin-bottom:10px}
.ocm{display:flex;gap:10px;flex-wrap:wrap}
.ocmi{font-family:'JetBrains Mono',monospace;font-size:10px}
.ocmi .v{color:var(--ac);font-weight:700}.ocmi .l{color:var(--tx3)}
.back{display:flex;align-items:center;gap:5px;color:var(--tx2);font-size:12px;cursor:pointer;margin-bottom:14px;font-family:'JetBrains Mono',monospace;transition:color .15s}
.back:hover{color:var(--ac)}
.oi-top{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px}
.oi-t{font-size:18px;font-weight:800}.oi-s{font-size:11px;color:var(--tx2);margin-top:2px}
.wbig{font-size:28px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac);line-height:1}
.wlbl{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px}
.stsel{padding:5px 10px;background:var(--s2);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:10px;outline:none;border-radius:6px;width:auto}
.dropz{border:2px dashed var(--bd);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:all .2s;position:relative}
.dropz:hover,.dropz.drag{border-color:var(--ac);background:var(--ac-bg)}
.dropz input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer}
.dz-t{font-size:12px;color:var(--tx2)}.dz-s{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.cvw{background:var(--s2);border:1px solid var(--bd);border-radius:6px;margin-top:10px;overflow:hidden}
canvas{display:block;max-width:100%;height:150px}
.pf{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:14px;margin-top:10px;animation:fadeUp .2s ease}
.wp{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;margin-bottom:10px}
.wv{font-size:19px;font-weight:700;color:var(--ac);font-family:'JetBrains Mono',monospace}
.wl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-top:1px;font-family:'JetBrains Mono',monospace}
.wa{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.fgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:480px){.fgrid{grid-template-columns:1fr}}
.msec{margin-top:12px;border-top:1px solid var(--bd);padding-top:12px}
.mlbl{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.svor-d{padding:7px 10px;background:var(--s1);border:1px solid var(--bd);border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ac)}
table{width:100%;border-collapse:collapse}
th{padding:7px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;text-align:left;border-bottom:1px solid var(--bd);background:var(--s2)}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}tr:hover td{background:var(--s2)}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px}
.num{color:var(--ac);font-weight:700;font-family:'JetBrains Mono',monospace}
.dttot{padding:10px 12px;background:var(--s2);border-top:2px solid var(--bd);display:flex;justify-content:flex-end;gap:14px;font-family:'JetBrains Mono',monospace;font-size:11px}
.tot{color:var(--ac);font-weight:700;font-size:13px}
.det-grp-hdr{padding:6px 12px;background:var(--s2);border-top:2px solid var(--bd);border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:10px}
.det-grp-t{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800;color:var(--ac)}
.det-grp-s{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.det-inp{padding:3px 6px!important;font-size:11px!important;width:auto!important}

/* ARCHYVAI */
.sc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:14px}
.scc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.scc:hover{border-color:var(--ac);transform:translateY(-1px)}.scc.open{border-color:var(--ac)}
.scn{font-size:13px;font-weight:700;margin-bottom:8px}
.scst{display:flex;gap:10px}
.scst .n{font-size:15px;font-weight:700;display:block;line-height:1;font-family:'JetBrains Mono',monospace}
.scst .n.g{color:var(--gn)}.scst .n.b{color:var(--ac)}.scst .n.r{color:var(--rd)}
.scst .l{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase}
.scp{margin-top:8px;height:3px;background:var(--s2);border-radius:2px;overflow:hidden}
.scpf{height:100%;background:var(--gn);border-radius:2px}
.adbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;margin-top:10px}
.adh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.adt{font-weight:700;font-size:13px}
.adlist{max-height:320px;overflow-y:auto}
.adi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:7px}
.addot{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.adi.sc .addot{background:var(--gn)}.adi.sdd .addot{background:var(--ac)}
.adcode{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1}
.adtag{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700}
.adtag.r{background:var(--yw-bg);color:var(--yw)}.adtag.c{background:var(--gn-bg);color:var(--gn)}.adtag.d{background:var(--ac-bg);color:var(--ac)}
.adtime{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx3)}

/* ATASKAITA */
.rep-s{margin-bottom:14px}
.rep-st{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--bd)}
.rep-sr{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}
.rep-sc{background:var(--s2);border-radius:6px;padding:10px 12px}
.rep-sc .n{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.rep-sc .l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}

/* PRINT */
@media print{body *{visibility:hidden!important}#printArea,#printArea *{visibility:visible!important}#printArea{position:fixed!important;left:0;top:0;width:100%}@page{margin:6mm;size:A4}}
.pmb{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:flex-start;justify-content:center;padding:16px;overflow-y:auto}
.pm{background:white;color:#000;max-width:210mm;width:100%;border-radius:8px;overflow:hidden;margin:auto}
.pbr{display:flex;gap:8px;padding:10px 14px;background:#f5f5f5;border-bottom:1px solid #ddd}
#printArea{background:white;color:#000;font-family:Arial,sans-serif;padding:10mm 8mm}
.pph{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}
.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666;font-family:monospace}
.ppbc{text-align:right;margin:2mm 0}
.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}
.ppi-l{font-size:7pt;color:#888;text-transform:uppercase;margin-bottom:.5mm}.ppi-v{font-size:10pt;font-weight:700}
.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}
.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}
.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}
.pptable tr:nth-child(even) td{background:#f9f9f9}
.ppsign{display:flex;gap:10mm;margin-top:5mm}
.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}
.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}
"""

_DXFJS = """
// DXF PARSERIS
const TANKIS = 8000;

function thickFromName(name){
  const m=name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)[ ]*mm/)||name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)/)||name.match(/([0-9]+(?:[.][0-9]+)?)[ ]*mm/);
  if(!m)return null;
  const v=parseFloat(m[1]);
  return STORIAI.includes(v)?v:null;
}

function qtyFromName(name){
  const m=name.match(/[_\x2D\x20]([0-9]+)[ ]*vnt/i)||name.match(/^([0-9]+)[ ]*vnt/i);
  if(!m)return null;
  const v=parseInt(m[1]);
  return v>0&&v<=9999?v:null;
}

function pDxf(txt){
  const lines=txt.split(/\r?\n/);
  const segs=[];
  let inE=false,curType=null,curV={},sf=1;

  for(let j=0;j<lines.length-1;j++){
    if(lines[j].trim()==='70'&&j>=2&&lines[j-2].trim()==='$INSUNITS'){
      const u=parseInt(lines[j+1]);if(u===1)sf=25.4;else if(u===6)sf=10;else if(u===5)sf=.1;
    }
  }

  const r4=v=>Math.round(v*10000)/10000;

  function saveSeg(t,v){
    if(t==='LINE'&&v._x1!==undefined&&v._y1!==undefined&&v._x2!==undefined&&v._y2!==undefined){
      segs.push({type:'L',x1:r4(v._x1*sf),y1:r4(v._y1*sf),x2:r4(v._x2*sf),y2:r4(v._y2*sf)});
    } else if(t==='CIRCLE'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf)});
    } else if((t==='LWPOLYLINE'||t==='POLYLINE')&&v._xs&&v._xs.length>=3){
      segs.push({type:'P',pts:v._xs.map((x,i)=>({x:r4(x*sf),y:r4((v._ys[i]||0)*sf)})),closed:((v[70]||0)&1)===1});
    } else if(t==='ARC'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf),arc:true});
    }
  }

  let i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i++;continue;}
    const val=(lines[i+1]||'').trim();
    if(code===2&&val==='ENTITIES'){inE=true;i+=2;continue;}
    if(code===0&&val==='ENDSEC'&&inE){saveSeg(curType,curV);break;}
    if(!inE){i+=2;continue;}
    if(code===0){saveSeg(curType,curV);curType=val;curV={};}
    else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._x1=n;}
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._y1=n;}
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11){curV._x2=n;}
        else if(code===21){curV._y2=n;}
        else if(code===70){curV[70]=parseInt(val)||0;}
        else{curV[code]=n;}
      }
    }
    i+=2;
  }

  let area=0;
  segs.filter(s=>s.type==='C'&&!s.arc).forEach(s=>area+=Math.PI*s.r*s.r);
  segs.filter(s=>s.type==='P').forEach(s=>{
    const pts=s.pts,n=pts.length;let a=0;
    for(let i=0;i<n;i++){const j=(i+1)%n;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}
    area+=Math.abs(a)/2;
  });
  const lineSegs=segs.filter(s=>s.type==='L');
  if(lineSegs.length){
    const adj=new Map();
    const key=p=>Math.round(p.x*100)/100+','+Math.round(p.y*100)/100;
    lineSegs.forEach(s=>{
      const p1={x:s.x1,y:s.y1},p2={x:s.x2,y:s.y2};
      const k1=key(p1),k2=key(p2);
      if(!adj.has(k1))adj.set(k1,{pt:p1,nb:[]});
      if(!adj.has(k2))adj.set(k2,{pt:p2,nb:[]});
      adj.get(k1).nb.push(k2);adj.get(k2).nb.push(k1);
    });
    const visitedE=new Set(),visitedP=new Set();
    adj.forEach((v,startK)=>{
      if(visitedP.has(startK))return;
      const path=[v.pt];let curK=startK;
      for(let iter=0;iter<adj.size*2;iter++){
        visitedP.add(curK);
        const nb=adj.get(curK).nb;let nextK=null;
        for(const nk of nb){
          const ek=[curK,nk].sort().join('|');
          if(!visitedE.has(ek)){visitedE.add(ek);nextK=nk;break;}
        }
        if(!nextK)break;
        path.push(adj.get(nextK).pt);curK=nextK;
      }
      if(path.length>=3){
        let a=0;const n=path.length;
        for(let i=0;i<n;i++){const j=(i+1)%n;a+=path[i].x*path[j].y-path[j].x*path[i].y;}
        area+=Math.abs(a)/2;
      }
    });
  }

  // Matmenys
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  segs.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  const dimW=isFinite(minX)?Math.round(maxX-minX):0;
  const dimH=isFinite(minY)?Math.round(maxY-minY):0;

  return{entities:segs,areaCm2:area/100,dimW,dimH};
}

function serializeContour(ents,dimW,dimH){
  try{
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    ents.forEach(s=>{
      if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
      else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
      else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
    });
    if(!isFinite(minX))return'';
    const W=maxX-minX||1,H=maxY-minY||1,sc=100/Math.max(W,H);
    const nx=x=>Math.round((x-minX)*sc*10)/10;
    const ny=y=>Math.round((maxY-y)*sc*10)/10;
    const paths=[];
    ents.forEach(s=>{
      if(s.type==='C'&&!s.arc)paths.push('C'+nx(s.cx)+','+ny(s.cy)+','+Math.round(s.r*sc*10)/10);
      else if(s.type==='P'){const step=Math.max(1,Math.floor(s.pts.length/50));const pts=[];for(let i=0;i<s.pts.length;i+=step)pts.push(nx(s.pts[i].x)+','+ny(s.pts[i].y));paths.push('L'+pts.join(' '));}
      else if(s.type==='L')paths.push('L'+nx(s.x1)+','+ny(s.y1)+' '+nx(s.x2)+','+ny(s.y2));
    });
    return('D:'+dimW+'x'+dimH+'|'+paths.join('|')).slice(0,2000);
  }catch(e){return'';}
}

function calcDims(d){
  if(d.konturas){
    const m=d.konturas.match(/D:([0-9]+)x([0-9]+)/);
    if(m)return m[1]+'×'+m[2]+'mm';
    try{
      let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
      d.konturas.split('|').forEach(p=>{
        if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);if(!isNaN(cx)){minX=Math.min(minX,cx-r);maxX=Math.max(maxX,cx+r);minY=Math.min(minY,cy-r);maxY=Math.max(maxY,cy+r);}}
        else if(p.startsWith('L')){p.slice(1).trim().split(' ').forEach(pt=>{const[x,y]=pt.split(',').map(Number);if(!isNaN(x)&&!isNaN(y)){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}});}
      });
      if(isFinite(minX)&&maxX>minX&&maxY>minY){
        const ratio=(maxX-minX)/(maxY-minY);const area=parseFloat(d.plotas)||0;
        if(area>0){const Hmm=Math.round(Math.sqrt(area*100/ratio));return Math.round(ratio*Hmm)+'×'+Hmm+'mm';}
      }
    }catch(e){}
  }
  const area=parseFloat(d.plotas)||0;
  if(!area)return'—';
  return'~'+Math.round(Math.sqrt(area*100))+'mm';
}

function drawPrev(ents){
  const w=document.getElementById('cvW'),c=document.getElementById('dxfCv');
  w.style.display='block';
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  ents.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  if(!isFinite(minX))return;
  const W=w.clientWidth||400,H=150;c.width=W;c.height=H;
  const ctx=c.getContext('2d');ctx.fillStyle='#f0f2f4';ctx.fillRect(0,0,W,H);
  const rX=maxX-minX||1,rY=maxY-minY||1,sc=Math.min((W-30)/rX,(H-30)/rY)*.9;
  const oX=(W-rX*sc)/2-minX*sc,oY=(H+rY*sc)/2+minY*sc;
  ctx.strokeStyle='#0969da';ctx.lineWidth=1.5;
  ents.forEach(s=>{
    ctx.beginPath();
    if(s.type==='C')ctx.arc(s.cx*sc+oX,oY-s.cy*sc,s.r*sc,0,Math.PI*2);
    else if(s.type==='P'&&s.pts.length){ctx.moveTo(s.pts[0].x*sc+oX,oY-s.pts[0].y*sc);for(let i=1;i<s.pts.length;i++)ctx.lineTo(s.pts[i].x*sc+oX,oY-s.pts[i].y*sc);if(s.closed)ctx.closePath();}
    else if(s.type==='L'){ctx.moveTo(s.x1*sc+oX,oY-s.y1*sc);ctx.lineTo(s.x2*sc+oX,oY-s.y2*sc);}
    ctx.stroke();
  });
}

function drawContourSvg(konturas,sizeMm=14){
  if(!konturas)return'';
  try{
    const parts=konturas.replace(/^D:[0-9]+x[0-9]+[|]/,'').split('|');
    let paths='';
    parts.forEach(p=>{
      if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);paths+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#000" stroke-width="2"/>`;}
      else if(p.startsWith('L')){const pts=p.slice(1).trim().split(' ');if(pts.length<2)return;const d='M'+pts[0]+' '+pts.slice(1).map(pt=>'L'+pt).join(' ');paths+=`<path d="${d}" fill="none" stroke="#000" stroke-width="2"/>`;}
    });
    const s=sizeMm+'mm';
    return`<svg viewBox="-5 -5 110 110" width="${s}" height="${s}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">${paths}</svg>`;
  }catch(e){return'';}
}

"""

_MAINJS = """
// SANDĖLIO SISTEMA – main.js

let lkOrders=[],lkF='all',lkLC=null,lkLT=0;
let dxfOrders=[],dxfF='all',dxfDets=[],curOrd=null,curArea=0,curContour='';
let stock=[],history=[],stages=[],archOpen=null;
let pendingSt='',curStockId=null;
let settings={defaultPrice:0,lowAlert:2};

// GARSAS
let actx=null;
function ga(){if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();return actx;}
function beep(t){try{const c=ga();if(c.state==='suspended')c.resume();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;if(t==='new'){o.frequency.value=880;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.2);o.start(n);o.stop(n+.2);}else if(t==='col'){o.frequency.setValueAtTime(660,n);o.frequency.setValueAtTime(880,n+.12);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.3);o.start(n);o.stop(n+.3);}else if(t==='del'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(660,n+.1);o.frequency.setValueAtTime(880,n+.2);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='err'){o.type='sawtooth';o.frequency.value=220;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='dup'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(220,n+.15);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.35);o.start(n);o.stop(n+.35);}}catch(e){}}

// API
async function api(method,url,data){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(data)opts.body=JSON.stringify(data);
  const r=await fetch(url,opts);
  if(!r.ok)throw new Error(r.statusText);
  return r.json();
}

// INIT
window.onload=()=>{
  loadAll();
  const lt=localStorage.getItem('lastThick');
  if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}
  setPeriod(30);
  const dz=document.getElementById('dropZ');
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
};
document.addEventListener('click',e=>{if(actx&&actx.state==='suspended')actx.resume();if(document.getElementById('view-lk').classList.contains('active')&&!e.target.closest('input,button,select'))focusScan();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mbg').forEach(m=>m.style.display='none');});

async function loadAll(){await loadLk();await loadDxfOrds();await loadStock();await loadHist();await loadStages();}

// NAVIGACIJA
function SW(v){
  document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById('view-'+v).classList.add('active');
  const t=document.getElementById('tab-'+v);if(t)t.classList.add('active');
  if(v==='lk')focusScan();
  if(v==='dv'){const lt=localStorage.getItem('lastThick');if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}}
}
function CM(id){document.getElementById(id).style.display='none';}
function focusScan(){try{document.getElementById('scanInp').focus();}catch(e){}}
function toast(msg,w=false,t=''){const el=document.getElementById('toast');el.textContent=msg;el.className='toast '+(w?'w':t)+' show';clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),3000);}

// ════ LAKŠTAI ════
const scanInp=document.getElementById('scanInp');
scanInp.addEventListener('keydown',async e=>{if(e.key==='Enter'){const c=scanInp.value.trim();if(c){scanInp.value='';await handleScan(c);}}});

async function handleScan(kodas){
  const now=Date.now();
  if(kodas===lkLC&&now-lkLT<3000){lkRes('rp','DUBLIKATAS',kodas,'Tas pats kodas du kartus!');beep('dup');toast('Dublikatas: '+kodas,false,'p');lkLC=null;return;}
  lkLC=kodas;lkLT=now;
  const local=lkOrders.find(o=>o.kodas===kodas);
  if(local){
    if(local.delivered){lkRes('ra','JAU PERDUOTA',kodas,'Perduota: '+local.deliveredAt);beep('err');return;}
    if(local.collected){
      lkRes('rd','PERDUOTA',kodas,'3× — siunčiama...');beep('del');
      local.delivered=true;local.deliveredAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Perduota: '+kodas,false,'b');else{local.delivered=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }else{
      lkRes('rc','SURINKTA',kodas,'2× — siunčiama...');beep('col');
      local.collected=true;local.collectedAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Surinkta: '+kodas);else{local.collected=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }
    return;
  }
  lkRes('rn','NAUJAS',kodas,'1× — siunčiama...');beep('new');
  const newOrd={kodas,registered:nowS(),collected:false,collectedAt:'',delivered:false,deliveredAt:''};
  lkOrders.push(newOrd);lkStats();rlkList();
  api('POST','/api/lakstai/register',{kodas}).then(r=>{
    if(r.success)toast('Užregistruota: '+kodas);
    else if(r.alreadyExists){lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkAddL(r.order);lkStats();rlkList();handleScan(kodas);}
    else{lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkRes('re','KLAIDA',kodas,'Nepavyko');beep('err');lkStats();rlkList();}
  });
}

function lkRes(c,t,kodas,s){
  const b=document.getElementById('lkRes');
  b.className='res '+c;b.style.display='block';
  document.getElementById('lkRt').textContent=t;
  document.getElementById('lkRc').textContent=kodas;
  document.getElementById('lkRs').textContent=s;
}

async function loadLk(){
  try{const r=await api('GET','/api/lakstai');lkOrders=r.orders||[];lkStats();rlkList();document.getElementById('connDot').className='dot ok';}
  catch(e){document.getElementById('connDot').className='dot err';toast('Nepavyko prisijungti',true);}
}
function lkAddL(o){const i=lkOrders.findIndex(x=>x.kodas===o.kodas);if(i>=0)lkOrders[i]=o;else lkOrders.push(o);}
function lkStats(){
  const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length,p=lkOrders.filter(o=>!o.collected).length;
  const pc=t>0?Math.round(c/t*100):0,pd=t>0?Math.round(d/t*100):0;
  document.getElementById('lkT').textContent=t;document.getElementById('lkC').textContent=c;
  document.getElementById('lkD').textContent=d;document.getElementById('lkP').textContent=p;
  document.getElementById('lkPct').textContent=pc+'%';
  document.getElementById('lkPfc').style.width=pc+'%';document.getElementById('lkPfd').style.width=pd+'%';
  document.getElementById('lkBdg').textContent=p||t;
}
function lkFlt(f,b){lkF=f;document.querySelectorAll('.frow .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rlkList();}
function sortLk(l){return[...l].sort((a,b)=>{const n=s=>parseInt((s.match(/[0-9]+/)||[0])[0]);return n(a.kodas)-n(b.kodas);});}
function rlkList(){
  const el=document.getElementById('lkList'),q=(document.getElementById('lkSrch').value||'').toLowerCase();
  let l=sortLk(lkOrders);
  if(lkF==='p')l=l.filter(o=>!o.collected);if(lkF==='c')l=l.filter(o=>o.collected&&!o.delivered);if(lkF==='d')l=l.filter(o=>o.delivered);
  if(q)l=l.filter(o=>o.kodas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(lkOrders.length===0?'Nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>{
    const sc=o.delivered?'sdd':o.collected?'sc':'';
    const sl=o.delivered?'s2':o.collected?'s1':'s0';
    const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
    const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);
    return`<div class="oi ${sc}"><div class="od"></div><div class="oc">${o.kodas}</div><span class="ost ${sl}">${st}</span><div class="otm">${tm}</div><button class="btn btn-d btn-sm" onclick="lkDel('${o.kodas}')">✕</button></div>`;
  }).join('');
}
async function lkDel(k){if(!confirm('Ištrinti "'+k+'"?'))return;await api('DELETE','/api/lakstai/'+k);lkOrders=lkOrders.filter(o=>o.kodas!==k);lkStats();rlkList();toast('Ištrinta');}
function askStage(){
  const n=document.getElementById('stageInp').value.trim();
  if(!n){toast('Įvesk etapo pavadinimą!',true);return;}
  if(!lkOrders.length){toast('Nėra užsakymų',true);return;}
  pendingSt=n;const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length;
  document.getElementById('stMn').textContent='Etapas: "'+n+'"';
  document.getElementById('stMs').innerHTML='Iš viso: <strong>'+t+'</strong><br>Surinkta: <strong>'+c+'</strong><br>Perduota: <strong>'+d+'</strong><br>Laukia: <strong>'+(t-c)+'</strong>';
  document.getElementById('stModal').style.display='flex';
}
async function confirmStage(){
  CM('stModal');
  const r=await api('POST','/api/lakstai/archive',{pavadinimas:pendingSt});
  if(r.success){lkOrders=[];document.getElementById('stageInp').value='';lkStats();rlkList();await loadStages();beep('del');toast('Archyvuota: "'+r.archiveName+'"');lkRes('ra','ARCHYVUOTA',r.archiveName,r.collected+'/'+r.total+' surinkta');}
  else toast(r.message||'Klaida',true);
  focusScan();
}

// ════ SANDĖLIS ════
async function loadStock(){try{const r=await api('GET','/api/sandelis');stock=r.stock||[];rStock();document.getElementById('stkBdg').textContent=stock.length;}catch(e){}}
async function loadHist(){try{const r=await api('GET','/api/sandelis/istorija');history=r.history||[];rHist();}catch(e){}}

function rStock(){
  const el=document.getElementById('stkTbl'),su=document.getElementById('stkSum');
  if(!stock.length){el.innerHTML='<div class="empty-s">Sandėlis tuščias</div>';su.innerHTML='';return;}
  const totVnt=stock.reduce((s,r)=>s+r.likoVnt,0);
  const totKg=stock.reduce((s,r)=>s+r.likoKg,0);
  const totT=Math.round(totKg/10)/100;
  const totVal=stock.reduce((s,r)=>s+r.verte,0);
  const byT={};stock.forEach(r=>{if(!byT[r.storis])byT[r.storis]={vnt:0,kg:0};byT[r.storis].vnt+=r.likoVnt;byT[r.storis].kg+=r.likoKg;});
  su.innerHTML=`<div class="stk-s"><div class="stk-n">${totVnt}</div><div class="stk-l">Viso vnt.</div></div><div class="stk-s"><div class="stk-n">${totKg.toFixed(1)}</div><div class="stk-l">Viso kg</div></div><div class="stk-s"><div class="stk-n" style="color:var(--gn)">${totT}</div><div class="stk-l">Tonos</div></div><div class="stk-s"><div class="stk-n" style="color:var(--or)">${totVal.toFixed(2)}</div><div class="stk-l">Vertė €</div></div>`+
    Object.entries(byT).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).map(([t,v])=>`<div class="stk-s"><div class="stk-n" style="font-size:15px">${v.vnt}vnt</div><div class="stk-l">${t}mm · ${(Math.round(v.kg/10)/100).toFixed(2)}t</div></div>`).join('');
  const sorted=[...stock].sort((a,b)=>a.storis-b.storis);
  el.innerHTML=sorted.map(r=>{
    const nc=r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return`<div class="stk-row"><div><div class="stk-thick">${r.storis}<span>mm</span></div></div><div><div class="stk-dims">${r.matmenys}mm</div><div class="stk-sub">${r.pastabos||''}</div></div><div><div class="stk-num ${nc}">${r.likoVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:13px;color:var(--tx2)">${r.likoKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${r.likoT.toFixed(3)}</div><div class="stk-sub">t</div></div><div><div class="stk-val">${r.verte.toFixed(2)}€</div><div class="stk-sub">${r.kainaKg>0?r.kainaKg+'€/kg':''}</div></div><div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse('${r.id}','${r.storis}mm ${r.matmenys}',${r.likoVnt})">−</button><button class="btn btn-d btn-sm" onclick="delStk('${r.id}')">✕</button></div></div>`;
  }).join('')+`<div class="stk-tot"><div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);font-weight:700">VISO</div><div></div><div><div class="stk-num" style="font-size:13px;color:var(--ac)">${totVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${totKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">${totT}</div><div class="stk-sub">t</div></div><div><div class="stk-val" style="font-size:13px;font-weight:800">${totVal.toFixed(2)}€</div></div><div></div></div>`;
}

function rHist(){
  const el=document.getElementById('histTbl');
  if(!history.length){el.innerHTML='<div class="empty-s">Dar nėra istorijos</div>';return;}
  el.innerHTML=`<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>${history.slice(0,50).map(h=>`<tr><td class="mono" style="font-size:10px;color:var(--tx3)">${h.data}</td><td><span class="hist-act ${h.veiksmas[0]}">${h.veiksmas}</span></td><td class="mono">${h.storis}mm</td><td class="mono" style="color:var(--tx2)">${h.matmenys}</td><td class="mono">${h.kiekis}vnt.</td><td class="num">${h.svorisIšViso.toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

function showRecv(){
  if(settings.defaultPrice)document.getElementById('recP').value=settings.defaultPrice;
  document.getElementById('recvModal').style.display='flex';
}
function rcRecv(){
  const t=parseFloat(document.getElementById('recThk').value)||0,w=parseFloat(document.getElementById('recW').value)||0,l=parseFloat(document.getElementById('recL').value)||0,q=parseInt(document.getElementById('recQ').value)||1,p=parseFloat(document.getElementById('recP').value)||0;
  if(!w||!l){document.getElementById('recPrev').textContent='Įvesk matmenis...';return;}
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100,totT=Math.round(tot/10)/100,val=p>0?Math.round(tot*p*100)/100:0;
  document.getElementById('recPrev').innerHTML=`1 lakštas: <strong style="color:var(--ac)">${we}kg</strong> · ${q}vnt.: <strong style="color:var(--gn)">${tot}kg = ${totT}t</strong>${val>0?' · <strong style="color:var(--or)">'+val+'€</strong>':''}`;
}
async function doRecv(){
  const t=document.getElementById('recThk').value,w=document.getElementById('recW').value,l=document.getElementById('recL').value,q=document.getElementById('recQ').value,p=document.getElementById('recP').value,n=document.getElementById('recN').value;
  if(!w||!l){toast('Įvesk matmenis!',true);return;}
  const r=await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if(r.success){CM('recvModal');await loadStock();await loadHist();toast('Pridėta: '+q+'vnt. × '+t+'mm ('+r.likoT+'t)');}
}
function showUse(id,label,rem){curStockId=id;document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';document.getElementById('useQ').value=1;document.getElementById('useNote').value='';document.getElementById('useModal').style.display='flex';}
async function doUse(){
  const q=parseInt(document.getElementById('useQ').value)||1,n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if(r.success){CM('useModal');await loadStock();await loadHist();toast('Sunaudota: '+q+'vnt. Liko: '+r.likoVnt+'vnt.');}
  else toast('Klaida',true);
}
async function delStk(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/sandelis/'+id);await loadStock();toast('Ištrinta');}
function showSett(){document.getElementById('settP').value=settings.defaultPrice||'';document.getElementById('settL').value=settings.lowAlert||2;document.getElementById('settModal').style.display='flex';}
function saveSett(){settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;settings.lowAlert=parseInt(document.getElementById('settL').value)||2;CM('settModal');localStorage.setItem('sandSettings',JSON.stringify(settings));toast('Nustatymai išsaugoti');}

// ════ ARCHYVAI ════
async function loadStages(){try{const r=await api('GET','/api/etapai');stages=r.stages||[];document.getElementById('archBdg').textContent=stages.length;rStages();}catch(e){}}
function rStages(){
  const el=document.getElementById('stageCards');
  if(!stages.length){el.innerHTML='<div class="empty-s">Dar nėra archyvų</div>';return;}
  el.innerHTML=stages.map(s=>{
    const t=s.total||0,c=s.collected||0,d=s.delivered||0,p=s.pending||(t-c),pct=t>0?Math.round(c/t*100):0;
    return`<div class="scc ${archOpen===s.name?'open':''}" onclick="toggleArch('${s.name.replace(/'/g,"\\'")}')"><div class="scn">${s.name}</div><div class="scst"><div><span class="n">${t}</span><span class="l">Viso</span></div><div><span class="n g">${c}</span><span class="l">Surinkta</span></div><div><span class="n b">${d}</span><span class="l">Perduota</span></div><div><span class="n ${p>0?'r':'g'}">${p}</span><span class="l">Liko</span></div></div><div class="scp"><div class="scpf" style="width:${pct}%"></div></div></div>`;
  }).join('');
}
async function toggleArch(name){
  if(archOpen===name){archOpen=null;closeAd();rStages();return;}
  archOpen=name;rStages();
  document.getElementById('adTitle').textContent=name;
  document.getElementById('adList').innerHTML='<div class="empty-s"><span class="sp"></span> Kraunama...</div>';
  document.getElementById('adBox').style.display='block';
  try{
    const r=await api('GET','/api/etapai/'+encodeURIComponent(name));
    const items=sortLk(r.orders||[]);
    if(!items.length){document.getElementById('adList').innerHTML='<div class="empty-s">Tuščias</div>';return;}
    document.getElementById('adList').innerHTML=items.map(o=>{
      const sc=o.delivered?'sdd':o.collected?'sc':'';const tc=o.delivered?'d':o.collected?'c':'r';const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
      const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(0,16);
      return`<div class="adi ${sc}"><div class="addot"></div><div class="adcode">${o.kodas}</div><span class="adtag ${tc}">${st}</span><div class="adtime">${tm}</div></div>`;
    }).join('');
  }catch(e){}
}
function closeAd(){document.getElementById('adBox').style.display='none';archOpen=null;rStages();}

// ════ DXF ════
async function loadDxfOrds(){try{const r=await api('GET','/api/uzsakymai');dxfOrders=r.orders||[];dxfSum();rOrds();document.getElementById('dxfBdg').textContent=dxfOrders.length;}catch(e){}}
function dxfSum(){
  const t=dxfOrders.length,n=dxfOrders.filter(o=>o.statusas==='Naujas').length,a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length,d=dxfOrders.filter(o=>o.statusas==='Baigtas').length,w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML=`<div class="smc"><div class="smn a">${t}</div><div class="sml">Iš viso</div></div><div class="smc"><div class="smn" style="color:var(--yw)">${n}</div><div class="sml">Nauji</div></div><div class="smc"><div class="smn a">${a}</div><div class="sml">Vykdomi</div></div><div class="smc"><div class="smn" style="color:var(--gn)">${d}</div><div class="sml">Baigti</div></div><div class="smc"><div class="smn a">${w.toFixed(2)}</div><div class="sml">Svoris kg</div></div>`;
}
function dxfFlt(f,b){dxfF=f;document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rOrds();}
function rOrds(){
  const el=document.getElementById('ordsGrid'),q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all')l=l.filter(o=>o.statusas===dxfF);if(q)l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>`<div class="ocard" onclick="openOrd('${o.id}')"><div class="oct"><div class="oid">${o.id}</div><div style="display:flex;gap:4px"><span class="stb ${o.statusas}">${o.statusas}</span><button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd('${o.id}','${o.klientas.replace(/'/g,"\\'")}')">✕</button></div></div><div class="ocli">${o.klientas}</div><div class="ocdesc">${o.aprasymas||'—'}</div><div class="ocm"><div class="ocmi"><span class="v">${o.bendraSvoris.toFixed(3)}</span><span class="l"> kg</span></div><div class="ocmi"><span class="v">${o.detaliuSk}</span><span class="l"> det.</span></div><div class="ocmi"><span class="l">${(o.sukurta||'').slice(0,10)}</span></div></div></div>`).join('');
}
async function quickDelOrd(id,klientas){if(!confirm('Ištrinti "'+klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+id);dxfOrders=dxfOrders.filter(o=>o.id!==id);dxfSum();rOrds();toast('Ištrinta');}
function showNewOrd(){document.getElementById('noModal').style.display='flex';setTimeout(()=>document.getElementById('noC').focus(),100);}
async function createOrd(){
  const c=document.getElementById('noC').value.trim();if(!c){toast('Įvesk klientą!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id){
  const o=dxfOrders.find(x=>x.id===id);if(!o)return;curOrd=o;
  document.getElementById('dvId').textContent=o.id;document.getElementById('dvCli').textContent=o.klientas;document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' · '+o.pastabos:'');
  SW('dv');await loadDets();
}
function back2Ords(){SW('dxf');loadDxfOrds();curArea=0;curContour='';document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';}
async function chSt(){if(!curOrd)return;await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value});toast('Statusas atnaujintas');}
async function delOrd(){if(!curOrd)return;if(!confirm('Ištrinti "'+curOrd.klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+curOrd.id);toast('Ištrinta');back2Ords();}
async function loadDets(){
  if(!curOrd)return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[];rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
}

function rDets(){
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nėra detalių</div>';return;}
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const groups={};
  dxfDets.forEach(d=>{const t=String(d.storis);if(!groups[t])groups[t]={t,dets:[],w:0,q:0};groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;});
  let rows='';let idx=0;
  Object.values(groups).forEach(g=>{
    rows+=`<tr class="det-grp-hdr"><td colspan="2"></td><td colspan="2"><span class="det-grp-t">${g.t}mm</span></td><td><span class="det-grp-s">${g.dets.length}det.</span></td><td><span class="det-grp-s">${g.q}vnt.</span></td><td><span class="det-grp-s" style="color:var(--ac)">${g.w.toFixed(3)}kg</span></td><td></td></tr>`;
    g.dets.forEach(d=>{
      idx++;
      rows+=`<tr><td class="mono" style="color:var(--tx3);font-size:10px">${idx}</td><td style="font-weight:600">${d.pavadinimas}</td><td><select class="det-inp" onchange="updDet('${d.detId}','storis',this.value)">${STORIAI.map(t=>`<option value="${t}"${d.storis===t?' selected':''}>${t}mm</option>`).join('')}</select></td><td class="mono" style="font-size:11px;color:var(--tx2)">${calcDims(d)}</td><td><input type="number" class="det-inp" value="${d.kiekis}" min="1" style="width:50px" onchange="updDet('${d.detId}','kiekis',this.value)"></td><td><input type="number" class="det-inp num" value="${d.svoris.toFixed(3)}" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-${d.detId}" onchange="updDetW('${d.detId}',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td><td><button class="btn btn-d btn-sm" onclick="delDet('${d.detId}')">✕</button></td></tr>`;
    });
  });
  w.innerHTML=`<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">${tq}vnt.</strong></span><span>Bendras svoris: <span class="tot">${tw.toFixed(3)}kg</span></span></div>`;
}

async function updDet(detId,field,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  if(field==='storis')d.storis=parseFloat(value);else if(field==='kiekis')d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  const wEl=document.getElementById('w-'+detId);if(wEl)wEl.value=d.svoris.toFixed(3);
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas});
}
async function updDetW(detId,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
function _updateTotals(){
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  document.getElementById('dvWt').textContent=tw.toFixed(3);
}
async function delDet(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/detales/'+id);dxfDets=dxfDets.filter(d=>d.detId!==id);rDets();_updateTotals();toast('Ištrinta');}

// DXF ĮKĖLIMAS
function handleDxf(e){if(e.target.files.length)handleMultiDxf(Array.from(e.target.files));}
function handleFolder(e){
  if(!e.target.files.length)return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failų!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' → '+ft+'mm, '+files.length+' failų',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files){
  if(!curOrd){toast('Pirma atidaryk užsakymą!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Įkeliama '+files.length+' failų...';
  for(const file of files){
    await new Promise(resolve=>{
      const r=new FileReader();
      r.onload=async e2=>{
        try{
          const res=pDxf(e2.target.result);
          if(res.areaCm2<=0){fail++;resolve();return;}
          const at=thickFromName(file.name)||defThick;
          const aq=qtyFromName(file.name)||defQty;
          const ctour=serializeContour(res.entities,res.dimW,res.dimH);
          const resp=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:file.name.replace(/[.]dxf$/i,''),storis:at,plotas:res.areaCm2,kiekis:aq,konturas:ctour});
          if(resp.success)ok++;else fail++;
        }catch(ex){fail++;}
        resolve();
      };
      r.readAsText(file);
    });
  }
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Tempk DXF failus čia arba spusk';
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?`Įkelta: ${ok}, nepavyko: ${fail}`:`Sėkmingai įkeltos ${ok} detalės!`);
}
function procDxf(file){
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2;
      curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name);const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq)document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
      toast('DXF: '+res.areaCm2.toFixed(2)+'cm²'+(at?' · '+at+'mm':''));
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm² · '+t+'mm × '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd)return;if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd)return;const a=parseFloat(document.getElementById('mArea').value)||0;if(a<=0){toast('Įvesk plotą!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:''});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}

// ATASKAITA
function setPeriod(days){
  const to=new Date(),from=new Date();
  if(days===0)from.setDate(1);else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep(){
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpį!',true);return;}
  const r=await api('GET',`/api/ataskaita?nuo=${from}&iki=${to}`);
  const el=document.getElementById('repOut');
  el.style.display='block';
  el.innerHTML=`<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: ${from} — ${to}</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.lakstai.gauta}</div><div class="l">Lakštų gauta</div></div><div class="rep-sc"><div class="n">${r.lakstai.surinkta}</div><div class="l">Surinkta</div></div><div class="rep-sc"><div class="n">${r.lakstai.perduota}</div><div class="l">Perduota</div></div><div class="rep-sc"><div class="n">${r.dxf.sk}</div><div class="l">DXF užsakymų</div></div><div class="rep-sc"><div class="n">${r.dxf.svoris.toFixed(1)}</div><div class="l">DXF svoris kg</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio judėjimas</div><div class="rep-sr"><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.sandelis.gautaKg.toFixed(1)}</div><div class="l">Gauta kg</div></div><div class="rep-sc"><div class="n" style="color:var(--rd)">${r.sandelis.sunaudotaKg.toFixed(1)}</div><div class="l">Sunaudota kg</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.gautaVerte.toFixed(2)}</div><div class="l">Gauta vertė €</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.sunaudotaVerte.toFixed(2)}</div><div class="l">Sunaudota €</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio likutis dabar</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.likutis.vnt}</div><div class="l">Viso vnt.</div></div><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.likutis.t}</div><div class="l">Tonos</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.likutis.verte.toFixed(2)}</div><div class="l">Vertė €</div></div></div></div></div>`;
}

// SPAUSDINIMAS
function printOrd(){
  if(!curOrd)return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return`<tr><td style="font-weight:700;color:#1e3a5f">${t}mm</td><td style="text-align:center">${dets.length}</td><td style="text-align:center">${gq}</td><td style="text-align:right;font-weight:700">${gw.toFixed(3)}</td></tr>`;}).join('');
  let html=`<div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div><div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">${totW.toFixed(3)} kg</div></div><div><div class="ppi-l">Viso detalių</div><div class="ppi-v">${totQ} vnt.</div></div><div><div class="ppi-l">Storių sk.</div><div class="ppi-v">${groups.size} storiai</div></div></div><table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>${sumRows}<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">${sorted.length}</td><td style="text-align:center">${totQ}</td><td style="text-align:right">${totW.toFixed(3)}</td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>Išspausdinta: ${now}</span><span>${curOrd.id}</span></div>`;
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>`<tr><td>${i+1}</td><td><strong>${d.pavadinimas}</strong></td><td style="text-align:center">${calcDims(d)}</td><td style="text-align:center">${d.kiekis}</td><td style="text-align:right"><strong>${d.svoris.toFixed(3)}</strong></td><td style="text-align:center;vertical-align:middle">${drawContourSvg(d.konturas,12)}</td></tr>`).join('');
    html+=`<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">${thick}mm</div></div><div class="ppinfo"><div><div class="ppi-l">Svoris (${thick}mm)</div><div class="ppi-v">${gw.toFixed(3)} kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">${gq}vnt. (${dets.length}poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">${now}</div></div></div><table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>${rows}<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">${gq}vnt.</td><td style="text-align:right">${gw.toFixed(3)}kg</td><td></td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>${thick}mm · ${dets.length}poz. · ${gq}vnt. · ${gw.toFixed(3)}kg</span><span>${curOrd.id}</span></div></div>`;
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}

function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  const s='<style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style>';
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'+s+'</head><body>'+c+'</body>');
  w.document.close();
  setTimeout(function(){w.print();},500);
}

function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}

// Nustatymų įkėlimas
const savedSett=localStorage.getItem('sandSettings');
if(savedSett)try{settings=JSON.parse(savedSett);}catch(e){}

async function siustiEmail(){
  const btn=document.getElementById('emailBtn');
  btn.textContent='Siunčiama...';btn.disabled=true;
  try{
    const r=await fetch('/api/email/siusti',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const d=await r.json();
    if(d.success){alert('✓ '+d.message);}
    else{alert('Klaida: '+(d.detail||d.message));}
  }catch(e){alert('Klaida: '+e.message);}
  btn.textContent='✉ Siųsti ataskaitą';btn.disabled=false;
}

"""

_HTML = """<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0969da">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sandelis">
<link rel="manifest" href="/manifest.json">
<title>Sandelio Sistema</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
<nav>
  <div class="brand"><div class="brand-ico"></div>SANDELIS</div>
  <div class="tabs">
    <button class="tab active" onclick="SW('lk')" id="tab-lk">Lakstai <span class="bdg" id="lkBdg">0</span></button>
    <button class="tab" onclick="SW('stk')" id="tab-stk">Sandelis <span class="bdg y" id="stkBdg">0</span></button>
    <button class="tab" onclick="SW('dxf')" id="tab-dxf">DXF <span class="bdg gray" id="dxfBdg">0</span></button>
    <button class="tab" onclick="SW('arch')" id="tab-arch">Archyvai <span class="bdg gray" id="archBdg">0</span></button>
    <button class="tab" onclick="SW('rep')" id="tab-rep">Ataskaita</button>
  </div>
  <div class="nav-r"><div class="dot ok" id="connDot"></div></div>
</nav>

<div class="view active" id="view-lk">
  <div class="lk-wrap">
    <div class="lk-main">
      <div class="card">
        <div class="ct">Skanavimas</div>
        <div class="scan-f"><span class="scan-ico">▦</span><input class="scan-inp" id="scanInp" placeholder="Skanuok arba ivesk koda..." autocomplete="off" spellcheck="false"></div>
        <div class="hint" id="scanHint">Laukiama skanavimo...</div>
        <div class="steps"><div class="step s1"></div><div class="step s2"></div><div class="step s3"></div></div>
        <div class="step-lbl"><span>1x Registruota</span><span>2x Surinkta</span><span>3x Perduota</span></div>
      </div>
      <div class="res" id="lkRes" style="display:none"><div class="rt" id="lkRt"></div><div class="rc" id="lkRc"></div><div class="rs" id="lkRs"></div></div>
      <div class="stats-row">
        <div class="stat"><div class="sn a" id="lkT">0</div><div class="sl">Is viso</div></div>
        <div class="stat"><div class="sn g" id="lkC">0</div><div class="sl">Surinkta</div></div>
        <div class="stat"><div class="sn b" id="lkD">0</div><div class="sl">Perduota</div></div>
        <div class="stat"><div class="sn y" id="lkP">0</div><div class="sl">Laukia</div></div>
      </div>
      <div class="prog-card">
        <div class="pt"><span>Progresas</span><span class="pct" id="lkPct">0%</span></div>
        <div class="ptr"><div class="pfd" id="lkPfd" style="width:0%"></div><div class="pfc" id="lkPfc" style="width:0%"></div></div>
      </div>
      <div class="stbar">
        <span class="stbar-lbl">Naujas etapas:</span>
        <input type="text" id="stageInp" placeholder="pvz. Etapas 221">
        <button class="btn btn-p btn-sm" onclick="askStage()">Archyvuoti</button>
      </div>
    </div>
    <div class="lk-sb">
      <div class="sbh">
        <div class="sbt">Uzsakymai</div>
        <button class="btn btn-g btn-sm" onclick="loadLk()">&#x21BB;</button>
        <button id="pdfBtn" class="btn btn-s btn-sm" onclick="genPdfReport()">&#x22C6; Atsisiusti PDF</button>
        <div class="sbsr"><span class="sbs-i">&#x2315;</span><input type="text" id="lkSrch" placeholder="Ieskoti..." oninput="rlkList()"></div>
      </div>
      <div class="frow">
        <button class="fb active" onclick="lkFlt('all',this)">Visi</button>
        <button class="fb" onclick="lkFlt('p',this)">Laukia</button>
        <button class="fb" onclick="lkFlt('c',this)">Surinkti</button>
        <button class="fb" onclick="lkFlt('d',this)">Perduoti</button>
      </div>
      <div class="olist" id="lkList"><div class="empty-s">Jungiamasi...</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-stk">
  <div class="page-wrap">
    <div class="ph"><div><div class="ph-t">Metalo sandelis</div><div class="ph-s">Lakstu likuciai pagal stori</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-s btn-sm" onclick="showSett()">Nustatymai</button>
        <button class="btn btn-p" onclick="showRecv()">+ Gauti lakstus</button>
      </div>
    </div>
    <div class="stk-sum" id="stkSum"></div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Likutis</span><button class="btn btn-s btn-sm" onclick="loadStock()">&#x21BB;</button></div>
      <div id="stkTbl"><div class="empty-s">Sandelis tuscias</div></div>
    </div>
    <div class="card" style="overflow:hidden;padding:0;margin-top:12px">
      <div class="card-h"><span class="card-t">Istorija</span><button class="btn btn-s btn-sm" onclick="loadHist()">&#x21BB;</button></div>
      <div id="histTbl"><div class="empty-s">Dar nera istorijos</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-dxf">
  <div class="page-wrap">
    <div class="ph"><div class="ph-t">DXF Uzsakymai</div><button class="btn btn-p" onclick="showNewOrd()">+ Naujas</button></div>
    <div class="sumr" id="dxfSum"></div>
    <div class="fbar">
      <button class="fb active" onclick="dxfFlt('all',this)">Visi</button>
      <button class="fb" onclick="dxfFlt('Naujas',this)">Nauji</button>
      <button class="fb" onclick="dxfFlt('Vykdomas',this)">Vykdomi</button>
      <button class="fb" onclick="dxfFlt('Baigtas',this)">Baigti</button>
      <input class="si" id="dxfSrch" placeholder="Ieskoti..." oninput="rOrds()">
    </div>
    <div class="og" id="ordsGrid"><div class="empty-s">Jungiamasi...</div></div>
  </div>
</div>

<div class="view" id="view-dv">
  <div class="page-wrap">
    <div class="back" onclick="back2Ords()">&#x2190; Grizti</div>
    <div class="card" style="margin-bottom:12px">
      <div class="oi-top">
        <div><div class="oid" id="dvId"></div><div class="oi-t" id="dvCli"></div><div class="oi-s" id="dvDsc"></div></div>
        <div style="text-align:right">
          <div class="wbig" id="dvWt">0</div><div class="wlbl">kg bendras svoris</div>
          <div style="margin-top:8px;display:flex;gap:5px;justify-content:flex-end;flex-wrap:wrap">
            <select class="stsel" id="dvSt" onchange="chSt()"><option>Naujas</option><option>Vykdomas</option><option>Baigtas</option></select>
            <button class="btn btn-p btn-sm" onclick="printOrd()">Spausdinti</button>
            <button class="btn btn-d btn-sm" onclick="delOrd()">Trinti</button>
          </div>
        </div>
      </div>
      <div id="dvMeta" style="font-size:11px;color:#57606a;font-family:'JetBrains Mono',monospace;margin-top:6px"></div>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Prideti detale is DXF</div>
      <div class="dropz" id="dropZ">
        <input type="file" id="dxfFile" accept=".dxf" multiple onchange="handleDxf(event)">
        <div class="dz-t">Tempk DXF failus cia arba spusk</div>
        <div class="dz-s">.dxf - galima ikelti kelis failus</div>
      </div>
      <div style="margin-top:8px">
        <label class="btn btn-s btn-sm" style="cursor:pointer">Ikelti aplanka<input type="file" id="dxfFolder" webkitdirectory multiple accept=".dxf" style="display:none" onchange="handleFolder(event)"></label>
      </div>
      <div class="cvw" id="cvW" style="display:none"><canvas id="dxfCv"></canvas></div>
      <div class="pf" id="pForm" style="display:none">
        <div class="wp"><div class="wv" id="wPv">0.000</div><div class="wl">kg (vieno vnt.)</div><div class="wa" id="wAr"></div></div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="dName"></div>
          <div><label class="fl">Storis (mm)</label><select id="dThk" onchange="rcW();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Kiekis</label><input type="number" id="dQty" value="1" min="1" oninput="rcW()"></div>
        </div>
        <button class="btn btn-p" style="width:100%" onclick="addDet()">+ Prideti detale</button>
      </div>
      <div class="msec">
        <div class="mlbl">arba ivesk rankiniu budu</div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="mName"></div>
          <div><label class="fl">Storis (mm)</label><select id="mThk" onchange="rcM();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Plotas (cm2)</label><input type="number" id="mArea" step="0.01" oninput="rcM()"></div>
        </div>
        <div class="fgrid">
          <div><label class="fl">Kiekis</label><input type="number" id="mQty" value="1" min="1" oninput="rcM()"></div>
          <div><label class="fl">Svoris</label><div class="svor-d" id="mWp">0.000 kg</div></div>
          <div style="display:flex;align-items:flex-end"><button class="btn btn-p" style="width:100%" onclick="addMDet()">+ Prideti</button></div>
        </div>
      </div>
    </div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Detaliu sarasas</span><button class="btn btn-s btn-sm" onclick="loadDets()">&#x21BB;</button></div>
      <div id="dtWrap"><div class="empty-s">Dar nera detaliu</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-arch">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Archyvai</div>
    <div class="sc-grid" id="stageCards"><div class="empty-s">Dar nera archivu</div></div>
    <div class="adbox" id="adBox" style="display:none">
      <div class="adh"><div class="adt" id="adTitle"></div><button class="btn btn-s btn-sm" onclick="closeAd()">X</button></div>
      <div class="adlist" id="adList"></div>
    </div>
  </div>
</div>

<div class="view" id="view-rep">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Ataskaita</div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Laikotarpis</div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr;margin-bottom:10px">
        <div><label class="fl">Nuo</label><input type="date" id="repFrom"></div>
        <div><label class="fl">Iki</label><input type="date" id="repTo"></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
        <button class="btn btn-s btn-sm" onclick="setPeriod(7)">7 dienos</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(30)">30 dienu</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(0)">Sis menuo</button>
      </div>
      <button class="btn btn-p" onclick="genRep()">Generuoti</button>
    </div>
    <div id="repOut" style="display:none"></div>
  </div>
</div>

<div class="mbg" id="noModal" style="display:none">
  <div class="modal">
    <div class="mh">Naujas DXF uzsakymas</div>
    <div class="mf">
      <div><label class="fl">Klientas *</label><input type="text" id="noC"></div>
      <div><label class="fl">Aprasymas</label><input type="text" id="noD"></div>
      <div><label class="fl">Pastabos</label><textarea id="noN"></textarea></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('noModal')">Atsaukti</button><button class="btn btn-p" onclick="createOrd()">Sukurti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="recvModal" style="display:none">
  <div class="modal">
    <div class="mh">Gauti lakstus</div>
    <div class="mf">
      <div><label class="fl">Storis (mm)</label><select id="recThk"><option value="3">3 mm</option><option value="4">4 mm</option><option value="5">5 mm</option><option value="6">6 mm</option><option value="8">8 mm</option><option value="10">10 mm</option><option value="12">12 mm</option><option value="14">14 mm</option><option value="15">15 mm</option><option value="16">16 mm</option><option value="18">18 mm</option><option value="20">20 mm</option><option value="25">25 mm</option></select></div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Plotis (mm)</label><input type="number" id="recW" oninput="rcRecv()"></div>
        <div><label class="fl">Ilgis (mm)</label><input type="number" id="recL" oninput="rcRecv()"></div>
      </div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Kiekis (vnt.)</label><input type="number" id="recQ" value="1" oninput="rcRecv()"></div>
        <div><label class="fl">Kaina / t (EUR)</label><input type="number" id="recP" step="0.01" oninput="rcRecv()"></div>
      </div>
      <div class="rec-prev" id="recPrev">Ivesk matmenis...</div>
      <div><label class="fl">Pastabos (SF nr.)</label><input type="text" id="recN"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('recvModal')">Atsaukti</button><button class="btn btn-p" onclick="doRecv()">Prideti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="useModal" style="display:none">
  <div class="modal">
    <div class="mh">Sunaudoti lakstus</div>
    <div class="mf">
      <div id="useInfo" class="rec-prev"></div>
      <div><label class="fl">Kiek vnt.?</label><input type="number" id="useQ" value="1" min="1"></div>
      <div><label class="fl">Pastabos</label><input type="text" id="useNote"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('useModal')">Atsaukti</button><button class="btn btn-y" onclick="doUse()">Sunaudoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="settModal" style="display:none">
  <div class="modal">
    <div class="mh">Nustatymai</div>
    <div class="mf">
      <div><label class="fl">Numatyta kaina / kg (EUR)</label><input type="number" id="settP" step="0.01"></div>
      <div><label class="fl">Zemos atsargos ispejimas</label><input type="number" id="settL" value="2" min="0"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('settModal')">Atsaukti</button><button class="btn btn-p" onclick="saveSett()">Issaugoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="stModal" style="display:none">
  <div class="modal">
    <div class="mh">Archyvuoti etapa?</div>
    <div id="stMn" style="font-size:11px;color:#57606a;margin-bottom:10px"></div>
    <div id="stMs" class="rec-prev" style="margin-bottom:12px;line-height:2"></div>
    <div class="mb"><button class="btn btn-s" onclick="CM('stModal')">Atsaukti</button><button class="btn btn-p" onclick="confirmStage()">Archyvuoti</button></div>
  </div>
</div>

<div class="pmb" id="printMod" style="display:none">
  <div class="pm">
    <div class="pbr">
      <button class="btn btn-p btn-sm" onclick="window.print()">Spausdinti</button>
      <button class="btn btn-s btn-sm" onclick="dlPdf()">PDF</button>
      <button class="btn btn-s btn-sm" onclick="CM('printMod')">Uzdaryti</button>
    </div>
    <div id="printArea"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const STORIAI=[3,4,5,6,8,10,12,14,15,16,18,20,25];
const TANKIS=8000;
</script>
<script src="/static/js/dxf.js"></script>
<script src="/static/js/main.js"></script>
</body>
</html>"""

@app.on_event("startup")
def startup():
    init_db()

@app.get("/static/css/main.css")
async def serve_css():
    return Response(content=_CSS, media_type="text/css")

@app.get("/static/js/dxf.js")
async def serve_dxfjs():
    return Response(content=_DXFJS, media_type="application/javascript")

@app.get("/static/js/main.js")
async def serve_mainjs():
    return Response(content=_MAINJS, media_type="application/javascript")

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({"name":"Sandelio Sistema","short_name":"Sandelis","start_url":"/","display":"standalone","background_color":"#f6f8fa","theme_color":"#0969da"})

@app.get("/sw.js")
async def sw():
    return Response(content="// sw", media_type="application/javascript")

@app.get("/icon.png")
async def icon():
    import base64
    return Response(content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="), media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=_HTML)


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
        raise HTTPException(400, "SMTP_PASS nenurodytas Railway Variables")
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti = [l for l in items if l.surinkta and not l.perduota]
    perduoti = [l for l in items if l.perduota]
    laukia = [l for l in items if not l.surinkta]
    def rows(lst, color):
        if not lst: return "<tr><td colspan=2 style='color:#aaa;padding:4px 8px'>Tuscia</td></tr>"
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else '-'}</td></tr>" for l in lst)
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
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
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th></tr>{rows(laukia,'#9a6700')}</table>
      <p style='color:#57606a;font-size:11px;margin-top:16px'>Issiusta is Sandelio sistemos - metalcraft.lt</p>
    </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandelio ataskaita {now}"
        msg["From"] = f"Metalcraft <{smtp_user}>"
        msg["To"] = gaivejas
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        # Bandome 587 su STARTTLS
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        except Exception as e1:
            # Bandome 465 su SSL
            with smtplib.SMTP_SSL(smtp_host, 465, timeout=30) as s:
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        return {"success": True, "message": f"Issiusta i {gaivejas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# LAKŠTAI API
# ══════════════════════════════════════════════════

@app.get("/api/lakstai")
def get_lakstai(etapas: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lakstai)
    if etapas:
        q = q.filter(Lakstai.etapas == etapas)
    else:
        q = q.filter(Lakstai.etapas == None)
    items = q.all()
    return {"orders": [_lk(l) for l in items]}

@app.get("/api/lakstai/find/{kodas}")
def find_lakstas(kodas: str, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == kodas).first()
    if not l:
        return {"found": False}
    return {"found": True, **_lk(l)}

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
        return {"success": False, "message": "Nėra užsakymų"}
    total = len(items); collected = sum(1 for l in items if l.surinkta); delivered = sum(1 for l in items if l.perduota)
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

# ══════════════════════════════════════════════════
# DXF API
# ══════════════════════════════════════════════════

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
    d = Detale(det_id=det_id, uzsakymo_id=data["uzsakymoId"], pavadinimas=data.get("pavadinimas", "Detalė"),
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

# ══════════════════════════════════════════════════
# SANDĖLIS API
# ══════════════════════════════════════════════════

@app.get("/api/sandelis")
def get_sandelis(db: Session = Depends(get_db)):
    items = db.query(Sandelis).order_by(Sandelis.storis).all()
    return {"stock": [_stk(s) for s in items]}

@app.post("/api/sandelis/gauti")
def gauti(data: dict, db: Session = Depends(get_db)):
    storis = float(data["storis"]); w = float(data["plotis"]); l = float(data["ilgis"]); qty = int(data["kiekis"])
    kaina = float(data.get("kaina", 0))
    svoris_vnt = round((w/1000) * (l/1000) * (storis/1000) * TANKIS, 2)
    liko_kg = round(svoris_vnt * qty, 2)
    liko_t = round(liko_kg / 1000, 3)
    verte = round(liko_t * kaina, 2)  # kaina uz tona
    stk_id = "STK-" + str(int(datetime.utcnow().timestamp() * 1000))
    s = Sandelis(stk_id=stk_id, storis=storis, matmenys=f"{int(w)}×{int(l)}", svoris_vnt=svoris_vnt,
                 gauta_vnt=qty, liko_vnt=qty, liko_kg=liko_kg, liko_t=liko_t, kaina_kg=kaina, verte=verte,
                 pastabos=data.get("pastabos", ""))
    db.add(s)
    hist = SandelioIstorijia(veiksmas="Gauta", storis=storis, matmenys=f"{int(w)}×{int(l)}", kiekis=qty,
                              svoris_vnt=svoris_vnt, svoris_iš_viso=liko_kg, kaina_kg=kaina, verte=verte, pastabos=data.get("pastabos", ""))
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
    s.verte = round(s.liko_t * s.kaina_kg, 2)  # kaina uz tona
    hist = SandelioIstorijia(veiksmas="Sunaudota", storis=s.storis, matmenys=s.matmenys, kiekis=qty,
                              svoris_vnt=s.svoris_vnt, svoris_iš_viso=round(qty*s.svoris_vnt, 2),
                              kaina_kg=s.kaina_kg, verte=round((qty*s.svoris_vnt/1000)*s.kaina_kg, 2), pastabos=data.get("pastabos", ""))
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
    return {"history": [{"data": h.data.strftime("%Y-%m-%d %H:%M"), "veiksmas": h.veiksmas, "storis": h.storis,
                          "matmenys": h.matmenys, "kiekis": h.kiekis, "svorisVnt": h.svoris_vnt,
                          "svorisIšViso": h.svoris_iš_viso, "kainaKg": h.kaina_kg, "verte": h.verte} for h in items]}

# ══════════════════════════════════════════════════
# ATASKAITA
# ══════════════════════════════════════════════════

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
            "pagalStori": [{"storis": s.storis, "vnt": s.liko_vnt, "kg": round(s.liko_kg, 1), "t": s.liko_t} for s in sorted(stock, key=lambda x: x.storis)]
        }
    }


# ══════════════════════════════════════════════════
# EL. PAŠTAS
# ══════════════════════════════════════════════════

@app.post("/api/email/siusti")
async def siusti_email(data: dict, db: Session = Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    smtp_host = os.getenv("SMTP_HOST", "vytis.serveriai.lt")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "info@metalcraft.lt")
    smtp_pass = os.getenv("SMTP_PASS", "")
    gavėjas   = os.getenv("EMAIL_TO", "gintaras@metalikalt.eu")
    
    if not smtp_pass:
        raise HTTPException(400, "SMTP slaptažodis nenurodytas")
    
    # Gauti lakštus
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti  = [l for l in items if l.surinkta and not l.perduota]
    perduoti  = [l for l in items if l.perduota]
    laukia    = [l for l in items if not l.surinkta]
    
    # HTML laiškas
    def rows(lst, color):
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else ''}</td></tr>" for l in lst)
    
    html = f"""
    <html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>
    <div style='background:#0969da;padding:16px;border-radius:8px 8px 0 0'>
      <h2 style='color:white;margin:0'>Sandėlio ataskaita – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</h2>
    </div>
    <div style='padding:16px;background:#f6f8fa;border-radius:0 0 8px 8px'>
      <p>Iš viso: <strong>{len(items)}</strong> | Surinkta: <strong style='color:#1a7f37'>{len(surinkti)}</strong> | Perduota: <strong style='color:#0969da'>{len(perduoti)}</strong> | Laukia: <strong style='color:#9a6700'>{len(laukia)}</strong></p>
      
      {'<h3 style="color:#1a7f37">✓ Surinkta</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Kodas</th><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Laikas</th></tr>' + rows(surinkti, '#1a7f37') + '</table>' if surinkti else ''}
      
      {'<h3 style="color:#0969da">→ Perduota</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Kodas</th><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Laikas</th></tr>' + rows(perduoti, '#0969da') + '</table>' if perduoti else ''}
      
      {'<h3 style="color:#9a6700">⏳ Laukia</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#fff8c5">Kodas</th><th style="text-align:left;padding:4px 8px;background:#fff8c5">Laikas</th></tr>' + rows(laukia, '#9a6700') + '</table>' if laukia else ''}
      
      <p style='color:#57606a;font-size:12px;margin-top:16px'>Išsiųsta iš Sandėlio sistemos – metalcraft.lt</p>
    </div>
    </body></html>
    """
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandėlio ataskaita {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        msg["From"]    = f"Metalcraft <{smtp_user}>"
        msg["To"]      = gavėjas
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, gavėjas, msg.as_string())
        
        return {"success": True, "message": f"Išsiųsta į {gavėjas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# ══════════════════════════════════════════════════
# PAGALBINĖS FUNKCIJOS
# ══════════════════════════════════════════════════

def _lk(l):
    return {"kodas": l.kodas, "registered": l.registruota.strftime("%Y-%m-%d %H:%M:%S") if l.registruota else "",
            "collected": l.surinkta, "collectedAt": l.surinkta_kada.strftime("%Y-%m-%d %H:%M:%S") if l.surinkta_kada else "",
            "delivered": l.perduota, "deliveredAt": l.perduota_kada.strftime("%Y-%m-%d %H:%M:%S") if l.perduota_kada else ""}

def _uzs(u):
    return {"id": u.uzs_id, "klientas": u.klientas, "aprasymas": u.aprasymas or "", "pastabos": u.pastabos or "",
            "statusas": u.statusas, "bendraSvoris": u.bendras_svoris, "detaliuSk": u.detaliu_sk,
            "sukurta": u.sukurta.strftime("%Y-%m-%d %H:%M:%S") if u.sukurta else ""}

def _det(d):
    return {"detId": d.det_id, "uzsakymoId": d.uzsakymo_id, "pavadinimas": d.pavadinimas,
            "storis": d.storis, "plotas": d.plotas, "kiekis": d.kiekis, "svoris": d.svoris,
            "konturas": d.konturas or "", "prideta": d.prideta.strftime("%Y-%m-%d %H:%M:%S") if d.prideta else ""}

def _stk(s):
    return {"id": s.stk_id, "storis": s.storis, "matmenys": s.matmenys, "svorisVnt": s.svoris_vnt,
            "gautaVnt": s.gauta_vnt, "sunaudotaVnt": s.sunaudota_vnt, "likoVnt": s.liko_vnt,
            "likoKg": s.liko_kg, "likoT": s.liko_t, "kainaKg": s.kaina_kg, "verte": s.verte,
            "prideta": s.prideta.strftime("%Y-%m-%d %H:%M:%S") if s.prideta else "", "pastabos": s.pastabos or ""}

def _recalc(uzs_id, db):
    dets = db.query(Detale).filter(Detale.uzsakymo_id == uzs_id).all()
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if u:
        u.bendras_svoris = round(sum(d.svoris for d in dets), 3)
        u.detaliu_sk = len(dets)
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os

from database import get_db, init_db, Lakstai, Etapas, Uzsakymas, Detale, Sandelis, SandelioIstorijia

app = FastAPI(title="Sandelio Sistema")
TANKIS = 8000

_CSS = """*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#f6f8fa;--s1:#ffffff;--s2:#f0f2f4;--s3:#e1e4e8;
  --bd:#d0d7de;--bd2:#afb8c1;
  --tx:#1f2328;--tx2:#57606a;--tx3:#848d97;
  --ac:#0969da;--ac2:#0550ae;--ac-bg:rgba(9,105,218,.08);
  --gn:#1a7f37;--gn-bg:rgba(26,127,55,.08);--gn-bd:rgba(26,127,55,.3);
  --yw:#9a6700;--yw-bg:rgba(154,103,0,.08);--yw-bd:rgba(154,103,0,.3);
  --rd:#cf222e;--rd-bg:rgba(207,34,46,.08);--rd-bd:rgba(207,34,46,.3);
  --pp:#6639ba;--pp-bg:rgba(102,57,186,.08);
  --or:#953800;
}
body{background:var(--bg);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;min-height:100vh;font-size:14px}

nav{background:var(--s1);border-bottom:1px solid var(--bd);padding:0 16px;height:52px;display:flex;align-items:center;gap:8px;position:sticky;top:0;z-index:50}
.brand{font-size:15px;font-weight:800;display:flex;align-items:center;gap:8px;flex-shrink:0}
.brand-ico{width:26px;height:26px;background:linear-gradient(135deg,#0969da,#6639ba);border-radius:6px}
.tabs{display:flex;height:100%;overflow-x:auto;flex:1;justify-content:center}
.tab{padding:0 13px;height:100%;display:flex;align-items:center;gap:4px;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;border:none;background:none;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}
.tab:hover{color:var(--tx)}.tab.active{color:var(--ac);border-bottom-color:var(--ac)}
.bdg{background:var(--ac);color:#fff;font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px}
.bdg.y{background:var(--yw)}.bdg.gray{background:var(--s3);color:var(--tx2)}.bdg.r{background:var(--rd)}
.nav-r{margin-left:auto;display:flex;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--bd2)}.dot.ok{background:var(--gn)}.dot.err{background:var(--rd)}

.view{display:none}.view.active{display:block}
.page-wrap{padding:16px;max-width:1000px;margin:0 auto}
.ph{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ph-t{font-size:18px;font-weight:800}.ph-s{font-size:11px;color:var(--tx2);margin-top:2px}

.btn{padding:7px 14px;border:none;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:12px;cursor:pointer;border-radius:6px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;white-space:nowrap}
.btn-p{background:var(--ac);color:#fff}.btn-p:hover{background:var(--ac2)}
.btn-s{background:transparent;border:1px solid var(--bd);color:var(--tx2)}.btn-s:hover{border-color:var(--tx);color:var(--tx)}
.btn-g{background:var(--gn-bg);border:1px solid var(--gn-bd);color:var(--gn)}.btn-g:hover{background:var(--gn);color:#fff}
.btn-d{background:transparent;border:1px solid transparent;color:var(--tx3)}.btn-d:hover{border-color:var(--rd-bd);color:var(--rd);background:var(--rd-bg)}
.btn-y{background:var(--yw-bg);border:1px solid var(--yw-bd);color:var(--yw)}.btn-y:hover{background:var(--yw);color:#fff}
.btn-sm{padding:4px 9px;font-size:11px}

.fl{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:4px}
input[type=text],input[type=number],input[type=date],input[type=email],textarea,select{width:100%;padding:7px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;outline:none;border-radius:6px;transition:border-color .15s;-webkit-appearance:none}
input:focus,textarea:focus,select:focus{border-color:var(--ac)}
textarea{resize:vertical;min-height:60px}
option{background:var(--s1)}

.card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;margin-bottom:12px}
.card-h{padding:12px 16px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.card-t{font-weight:700;font-size:14px}
.ct{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.ct::after{content:'';flex:1;height:1px;background:var(--bd)}

.mbg{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:24px;max-width:440px;width:100%;margin:auto}
.mh{font-size:17px;font-weight:800;margin-bottom:16px}
.mf{display:flex;flex-direction:column;gap:12px}
.mb{display:flex;gap:8px;justify-content:flex-end;margin-top:6px}

.toast{position:fixed;bottom:14px;right:14px;left:14px;max-width:340px;margin:0 auto;padding:11px 14px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;background:var(--s1);border:1px solid var(--bd);border-left:3px solid var(--gn);box-shadow:0 8px 24px rgba(0,0,0,.15);transform:translateY(70px);opacity:0;transition:all .25s;z-index:300;border-radius:6px}
.toast.w{border-left-color:var(--rd)}.toast.b{border-left-color:var(--ac)}.toast.p{border-left-color:var(--pp)}
.toast.show{transform:translateY(0);opacity:1}
.sp{display:inline-block;width:11px;height:11px;border:2px solid var(--bd2);border-top-color:var(--ac);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:4px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.empty-s{padding:40px;text-align:center;color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:12px}

/* LAKŠTAI */
.lk-wrap{display:grid;grid-template-columns:1fr 290px;min-height:calc(100vh - 52px)}
@media(max-width:680px){.lk-wrap{grid-template-columns:1fr}}
.lk-main{padding:16px;display:flex;flex-direction:column;gap:10px}
.lk-sb{border-left:1px solid var(--bd);background:var(--s1);display:flex;flex-direction:column}
.scan-f{position:relative}.scan-ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:16px;pointer-events:none;color:var(--tx3)}
.scan-inp{padding:11px 14px 11px 40px!important;font-size:17px!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important}
.scan-inp:focus{border-color:var(--ac)!important;box-shadow:0 0 0 3px var(--ac-bg)}
.hint{margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3)}
.steps{display:flex;gap:4px;margin-top:10px}
.step{flex:1;height:3px;background:var(--bd);border-radius:2px}
.s1{background:var(--yw)}.s2{background:var(--gn)}.s3{background:var(--ac)}
.step-lbl{display:flex;justify-content:space-between;margin-top:4px;font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.res{border:1px solid var(--bd);border-radius:8px;padding:12px 14px;animation:fadeUp .2s ease}
.res.rn{background:var(--yw-bg);border-color:var(--yw-bd)}.res.rc{background:var(--gn-bg);border-color:var(--gn-bd)}
.res.rd{background:var(--ac-bg);border-color:rgba(9,105,218,.3)}.res.re{background:var(--rd-bg);border-color:var(--rd-bd)}
.res.rp{background:var(--pp-bg);border-color:rgba(102,57,186,.3)}.res.ra{background:var(--gn-bg);border-color:var(--gn-bd)}
.rt{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}
.res.rn .rt{color:var(--yw)}.res.rc .rt{color:var(--gn)}.res.rd .rt{color:var(--ac)}.res.re .rt{color:var(--rd)}.res.rp .rt{color:var(--pp)}.res.ra .rt{color:var(--gn)}
.rc{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace}.rs{font-size:11px;color:var(--tx2);margin-top:2px}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
@media(max-width:480px){.stats-row{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.sn{font-size:22px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace}
.sn.a{color:var(--ac)}.sn.g{color:var(--gn)}.sn.b{color:var(--ac)}.sn.y{color:var(--yw)}
.sl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.prog-card{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px}
.pt{display:flex;justify-content:space-between;margin-bottom:6px;font-size:10px;color:var(--tx2);font-family:'JetBrains Mono',monospace}
.pct{color:var(--gn);font-weight:700}
.ptr{height:6px;background:var(--s2);border-radius:3px;overflow:hidden;position:relative}
.pfc{height:100%;background:var(--gn);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px}
.pfd{height:100%;background:var(--ac);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px;opacity:.4}
.stbar{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:12px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.stbar-lbl{font-weight:700;font-size:13px;white-space:nowrap}.stbar input{flex:1;min-width:130px}
.stbar-hint{font-size:9px;color:var(--tx3);width:100%;font-family:'JetBrains Mono',monospace}
.sbh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}
.sbt{font-weight:700;font-size:12px}.sbsr{position:relative;width:100%}
.sbsr input{padding:5px 10px 5px 26px;font-size:11px}.sbs-i{position:absolute;left:8px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--tx3);pointer-events:none}
.frow{padding:6px 14px;border-bottom:1px solid var(--bd);display:flex;gap:4px;flex-wrap:wrap}
.fb{padding:3px 8px;background:transparent;border:1px solid var(--bd);color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:9px;cursor:pointer;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;transition:all .15s}
.fb.active{background:var(--tx);color:var(--bg);border-color:var(--tx);font-weight:700}
.olist{flex:1;overflow-y:auto}
.oi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:6px;transition:background .1s}
.oi:hover{background:var(--s2)}
.od{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.oi.sc .od{background:var(--gn)}.oi.sdd .od{background:var(--ac)}
.oc{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ost{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700;flex-shrink:0}
.ost.s0{background:var(--yw-bg);color:var(--yw)}.ost.s1{background:var(--gn-bg);color:var(--gn)}.ost.s2{background:var(--ac-bg);color:var(--ac)}
.otm{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);flex-shrink:0}

/* SANDĖLIS */
.stk-sum{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin-bottom:14px}
.stk-s{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.stk-n{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.stk-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.stk-row{padding:10px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.stk-row:last-child{border-bottom:none}.stk-row:hover{background:var(--s2)}
@media(max-width:600px){.stk-row{grid-template-columns:1fr 1fr;gap:6px}}
.stk-thick{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:var(--ac)}
.stk-thick span{font-size:10px;color:var(--tx3)}
.stk-dims{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.stk-num{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700}
.stk-num.ok{color:var(--gn)}.stk-num.warn{color:var(--yw)}.stk-num.empty{color:var(--rd)}
.stk-sub{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.stk-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--or)}
.stk-acts{display:flex;gap:4px}
.stk-tot{padding:10px 16px;background:var(--s2);border-top:2px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.hist-row{padding:8px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:130px 60px 90px 60px 80px 80px;align-items:center;gap:8px;font-size:12px}
.hist-row:last-child{border-bottom:none}.hist-row:hover{background:var(--s2)}
.hist-act{font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700}
.hist-act.G{background:var(--gn-bg);color:var(--gn)}.hist-act.S{background:var(--rd-bg);color:var(--rd)}
.rec-prev{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--tx2)}

/* DXF */
.sumr{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin-bottom:14px}
.smc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.smn{font-size:20px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.sml{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.fbar{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.si{padding:5px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:11px;outline:none;border-radius:6px;min-width:150px}
.si:focus{border-color:var(--ac)}
.og{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.ocard{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.ocard:hover{border-color:var(--ac);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.oct{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.oid{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3)}
.stb{font-family:'JetBrains Mono',monospace;font-size:9px;padding:2px 7px;border-radius:4px;font-weight:700}
.stb.Naujas{background:var(--yw-bg);color:var(--yw);border:1px solid var(--yw-bd)}
.stb.Vykdomas{background:var(--ac-bg);color:var(--ac);border:1px solid rgba(9,105,218,.3)}
.stb.Baigtas{background:var(--gn-bg);color:var(--gn);border:1px solid var(--gn-bd)}
.ocli{font-size:14px;font-weight:700;margin-bottom:2px}.ocdesc{font-size:11px;color:var(--tx2);margin-bottom:10px}
.ocm{display:flex;gap:10px;flex-wrap:wrap}
.ocmi{font-family:'JetBrains Mono',monospace;font-size:10px}
.ocmi .v{color:var(--ac);font-weight:700}.ocmi .l{color:var(--tx3)}
.back{display:flex;align-items:center;gap:5px;color:var(--tx2);font-size:12px;cursor:pointer;margin-bottom:14px;font-family:'JetBrains Mono',monospace;transition:color .15s}
.back:hover{color:var(--ac)}
.oi-top{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px}
.oi-t{font-size:18px;font-weight:800}.oi-s{font-size:11px;color:var(--tx2);margin-top:2px}
.wbig{font-size:28px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac);line-height:1}
.wlbl{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px}
.stsel{padding:5px 10px;background:var(--s2);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:10px;outline:none;border-radius:6px;width:auto}
.dropz{border:2px dashed var(--bd);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:all .2s;position:relative}
.dropz:hover,.dropz.drag{border-color:var(--ac);background:var(--ac-bg)}
.dropz input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer}
.dz-t{font-size:12px;color:var(--tx2)}.dz-s{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.cvw{background:var(--s2);border:1px solid var(--bd);border-radius:6px;margin-top:10px;overflow:hidden}
canvas{display:block;max-width:100%;height:150px}
.pf{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:14px;margin-top:10px;animation:fadeUp .2s ease}
.wp{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;margin-bottom:10px}
.wv{font-size:19px;font-weight:700;color:var(--ac);font-family:'JetBrains Mono',monospace}
.wl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-top:1px;font-family:'JetBrains Mono',monospace}
.wa{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.fgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:480px){.fgrid{grid-template-columns:1fr}}
.msec{margin-top:12px;border-top:1px solid var(--bd);padding-top:12px}
.mlbl{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.svor-d{padding:7px 10px;background:var(--s1);border:1px solid var(--bd);border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ac)}
table{width:100%;border-collapse:collapse}
th{padding:7px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;text-align:left;border-bottom:1px solid var(--bd);background:var(--s2)}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}tr:hover td{background:var(--s2)}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px}
.num{color:var(--ac);font-weight:700;font-family:'JetBrains Mono',monospace}
.dttot{padding:10px 12px;background:var(--s2);border-top:2px solid var(--bd);display:flex;justify-content:flex-end;gap:14px;font-family:'JetBrains Mono',monospace;font-size:11px}
.tot{color:var(--ac);font-weight:700;font-size:13px}
.det-grp-hdr{padding:6px 12px;background:var(--s2);border-top:2px solid var(--bd);border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:10px}
.det-grp-t{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800;color:var(--ac)}
.det-grp-s{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.det-inp{padding:3px 6px!important;font-size:11px!important;width:auto!important}

/* ARCHYVAI */
.sc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:14px}
.scc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.scc:hover{border-color:var(--ac);transform:translateY(-1px)}.scc.open{border-color:var(--ac)}
.scn{font-size:13px;font-weight:700;margin-bottom:8px}
.scst{display:flex;gap:10px}
.scst .n{font-size:15px;font-weight:700;display:block;line-height:1;font-family:'JetBrains Mono',monospace}
.scst .n.g{color:var(--gn)}.scst .n.b{color:var(--ac)}.scst .n.r{color:var(--rd)}
.scst .l{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase}
.scp{margin-top:8px;height:3px;background:var(--s2);border-radius:2px;overflow:hidden}
.scpf{height:100%;background:var(--gn);border-radius:2px}
.adbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;margin-top:10px}
.adh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.adt{font-weight:700;font-size:13px}
.adlist{max-height:320px;overflow-y:auto}
.adi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:7px}
.addot{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.adi.sc .addot{background:var(--gn)}.adi.sdd .addot{background:var(--ac)}
.adcode{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1}
.adtag{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700}
.adtag.r{background:var(--yw-bg);color:var(--yw)}.adtag.c{background:var(--gn-bg);color:var(--gn)}.adtag.d{background:var(--ac-bg);color:var(--ac)}
.adtime{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx3)}

/* ATASKAITA */
.rep-s{margin-bottom:14px}
.rep-st{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--bd)}
.rep-sr{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}
.rep-sc{background:var(--s2);border-radius:6px;padding:10px 12px}
.rep-sc .n{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.rep-sc .l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}

/* PRINT */
@media print{body *{visibility:hidden!important}#printArea,#printArea *{visibility:visible!important}#printArea{position:fixed!important;left:0;top:0;width:100%}@page{margin:6mm;size:A4}}
.pmb{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:flex-start;justify-content:center;padding:16px;overflow-y:auto}
.pm{background:white;color:#000;max-width:210mm;width:100%;border-radius:8px;overflow:hidden;margin:auto}
.pbr{display:flex;gap:8px;padding:10px 14px;background:#f5f5f5;border-bottom:1px solid #ddd}
#printArea{background:white;color:#000;font-family:Arial,sans-serif;padding:10mm 8mm}
.pph{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}
.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666;font-family:monospace}
.ppbc{text-align:right;margin:2mm 0}
.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}
.ppi-l{font-size:7pt;color:#888;text-transform:uppercase;margin-bottom:.5mm}.ppi-v{font-size:10pt;font-weight:700}
.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}
.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}
.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}
.pptable tr:nth-child(even) td{background:#f9f9f9}
.ppsign{display:flex;gap:10mm;margin-top:5mm}
.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}
.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}
"""

_DXFJS = """
// DXF PARSERIS
const TANKIS = 8000;

function thickFromName(name){
  const m=name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)[ ]*mm/)||name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)/)||name.match(/([0-9]+(?:[.][0-9]+)?)[ ]*mm/);
  if(!m)return null;
  const v=parseFloat(m[1]);
  return STORIAI.includes(v)?v:null;
}

function qtyFromName(name){
  const m=name.match(/[_\x2D\x20]([0-9]+)[ ]*vnt/i)||name.match(/^([0-9]+)[ ]*vnt/i);
  if(!m)return null;
  const v=parseInt(m[1]);
  return v>0&&v<=9999?v:null;
}

function pDxf(txt){
  const lines=txt.split(/\r?\n/);
  const segs=[];
  let inE=false,curType=null,curV={},sf=1;

  for(let j=0;j<lines.length-1;j++){
    if(lines[j].trim()==='70'&&j>=2&&lines[j-2].trim()==='$INSUNITS'){
      const u=parseInt(lines[j+1]);if(u===1)sf=25.4;else if(u===6)sf=10;else if(u===5)sf=.1;
    }
  }

  const r4=v=>Math.round(v*10000)/10000;

  function saveSeg(t,v){
    if(t==='LINE'&&v._x1!==undefined&&v._y1!==undefined&&v._x2!==undefined&&v._y2!==undefined){
      segs.push({type:'L',x1:r4(v._x1*sf),y1:r4(v._y1*sf),x2:r4(v._x2*sf),y2:r4(v._y2*sf)});
    } else if(t==='CIRCLE'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf)});
    } else if((t==='LWPOLYLINE'||t==='POLYLINE')&&v._xs&&v._xs.length>=3){
      segs.push({type:'P',pts:v._xs.map((x,i)=>({x:r4(x*sf),y:r4((v._ys[i]||0)*sf)})),closed:((v[70]||0)&1)===1});
    } else if(t==='ARC'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf),arc:true});
    }
  }

  let i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i++;continue;}
    const val=(lines[i+1]||'').trim();
    if(code===2&&val==='ENTITIES'){inE=true;i+=2;continue;}
    if(code===0&&val==='ENDSEC'&&inE){saveSeg(curType,curV);break;}
    if(!inE){i+=2;continue;}
    if(code===0){saveSeg(curType,curV);curType=val;curV={};}
    else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._x1=n;}
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._y1=n;}
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11){curV._x2=n;}
        else if(code===21){curV._y2=n;}
        else if(code===70){curV[70]=parseInt(val)||0;}
        else{curV[code]=n;}
      }
    }
    i+=2;
  }

  let area=0;
  segs.filter(s=>s.type==='C'&&!s.arc).forEach(s=>area+=Math.PI*s.r*s.r);
  segs.filter(s=>s.type==='P').forEach(s=>{
    const pts=s.pts,n=pts.length;let a=0;
    for(let i=0;i<n;i++){const j=(i+1)%n;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}
    area+=Math.abs(a)/2;
  });
  const lineSegs=segs.filter(s=>s.type==='L');
  if(lineSegs.length){
    const adj=new Map();
    const key=p=>Math.round(p.x*100)/100+','+Math.round(p.y*100)/100;
    lineSegs.forEach(s=>{
      const p1={x:s.x1,y:s.y1},p2={x:s.x2,y:s.y2};
      const k1=key(p1),k2=key(p2);
      if(!adj.has(k1))adj.set(k1,{pt:p1,nb:[]});
      if(!adj.has(k2))adj.set(k2,{pt:p2,nb:[]});
      adj.get(k1).nb.push(k2);adj.get(k2).nb.push(k1);
    });
    const visitedE=new Set(),visitedP=new Set();
    adj.forEach((v,startK)=>{
      if(visitedP.has(startK))return;
      const path=[v.pt];let curK=startK;
      for(let iter=0;iter<adj.size*2;iter++){
        visitedP.add(curK);
        const nb=adj.get(curK).nb;let nextK=null;
        for(const nk of nb){
          const ek=[curK,nk].sort().join('|');
          if(!visitedE.has(ek)){visitedE.add(ek);nextK=nk;break;}
        }
        if(!nextK)break;
        path.push(adj.get(nextK).pt);curK=nextK;
      }
      if(path.length>=3){
        let a=0;const n=path.length;
        for(let i=0;i<n;i++){const j=(i+1)%n;a+=path[i].x*path[j].y-path[j].x*path[i].y;}
        area+=Math.abs(a)/2;
      }
    });
  }

  // Matmenys
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  segs.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  const dimW=isFinite(minX)?Math.round(maxX-minX):0;
  const dimH=isFinite(minY)?Math.round(maxY-minY):0;

  return{entities:segs,areaCm2:area/100,dimW,dimH};
}

function serializeContour(ents,dimW,dimH){
  try{
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    ents.forEach(s=>{
      if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
      else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
      else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
    });
    if(!isFinite(minX))return'';
    const W=maxX-minX||1,H=maxY-minY||1,sc=100/Math.max(W,H);
    const nx=x=>Math.round((x-minX)*sc*10)/10;
    const ny=y=>Math.round((maxY-y)*sc*10)/10;
    const paths=[];
    ents.forEach(s=>{
      if(s.type==='C'&&!s.arc)paths.push('C'+nx(s.cx)+','+ny(s.cy)+','+Math.round(s.r*sc*10)/10);
      else if(s.type==='P'){const step=Math.max(1,Math.floor(s.pts.length/50));const pts=[];for(let i=0;i<s.pts.length;i+=step)pts.push(nx(s.pts[i].x)+','+ny(s.pts[i].y));paths.push('L'+pts.join(' '));}
      else if(s.type==='L')paths.push('L'+nx(s.x1)+','+ny(s.y1)+' '+nx(s.x2)+','+ny(s.y2));
    });
    return('D:'+dimW+'x'+dimH+'|'+paths.join('|')).slice(0,2000);
  }catch(e){return'';}
}

function calcDims(d){
  if(d.konturas){
    const m=d.konturas.match(/D:([0-9]+)x([0-9]+)/);
    if(m)return m[1]+'×'+m[2]+'mm';
    try{
      let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
      d.konturas.split('|').forEach(p=>{
        if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);if(!isNaN(cx)){minX=Math.min(minX,cx-r);maxX=Math.max(maxX,cx+r);minY=Math.min(minY,cy-r);maxY=Math.max(maxY,cy+r);}}
        else if(p.startsWith('L')){p.slice(1).trim().split(' ').forEach(pt=>{const[x,y]=pt.split(',').map(Number);if(!isNaN(x)&&!isNaN(y)){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}});}
      });
      if(isFinite(minX)&&maxX>minX&&maxY>minY){
        const ratio=(maxX-minX)/(maxY-minY);const area=parseFloat(d.plotas)||0;
        if(area>0){const Hmm=Math.round(Math.sqrt(area*100/ratio));return Math.round(ratio*Hmm)+'×'+Hmm+'mm';}
      }
    }catch(e){}
  }
  const area=parseFloat(d.plotas)||0;
  if(!area)return'—';
  return'~'+Math.round(Math.sqrt(area*100))+'mm';
}

function drawPrev(ents){
  const w=document.getElementById('cvW'),c=document.getElementById('dxfCv');
  w.style.display='block';
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  ents.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  if(!isFinite(minX))return;
  const W=w.clientWidth||400,H=150;c.width=W;c.height=H;
  const ctx=c.getContext('2d');ctx.fillStyle='#f0f2f4';ctx.fillRect(0,0,W,H);
  const rX=maxX-minX||1,rY=maxY-minY||1,sc=Math.min((W-30)/rX,(H-30)/rY)*.9;
  const oX=(W-rX*sc)/2-minX*sc,oY=(H+rY*sc)/2+minY*sc;
  ctx.strokeStyle='#0969da';ctx.lineWidth=1.5;
  ents.forEach(s=>{
    ctx.beginPath();
    if(s.type==='C')ctx.arc(s.cx*sc+oX,oY-s.cy*sc,s.r*sc,0,Math.PI*2);
    else if(s.type==='P'&&s.pts.length){ctx.moveTo(s.pts[0].x*sc+oX,oY-s.pts[0].y*sc);for(let i=1;i<s.pts.length;i++)ctx.lineTo(s.pts[i].x*sc+oX,oY-s.pts[i].y*sc);if(s.closed)ctx.closePath();}
    else if(s.type==='L'){ctx.moveTo(s.x1*sc+oX,oY-s.y1*sc);ctx.lineTo(s.x2*sc+oX,oY-s.y2*sc);}
    ctx.stroke();
  });
}

function drawContourSvg(konturas,sizeMm=14){
  if(!konturas)return'';
  try{
    const parts=konturas.replace(/^D:[0-9]+x[0-9]+[|]/,'').split('|');
    let paths='';
    parts.forEach(p=>{
      if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);paths+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#000" stroke-width="2"/>`;}
      else if(p.startsWith('L')){const pts=p.slice(1).trim().split(' ');if(pts.length<2)return;const d='M'+pts[0]+' '+pts.slice(1).map(pt=>'L'+pt).join(' ');paths+=`<path d="${d}" fill="none" stroke="#000" stroke-width="2"/>`;}
    });
    const s=sizeMm+'mm';
    return`<svg viewBox="-5 -5 110 110" width="${s}" height="${s}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">${paths}</svg>`;
  }catch(e){return'';}
}

"""

_MAINJS = """
// SANDĖLIO SISTEMA – main.js

let lkOrders=[],lkF='all',lkLC=null,lkLT=0;
let dxfOrders=[],dxfF='all',dxfDets=[],curOrd=null,curArea=0,curContour='';
let stock=[],history=[],stages=[],archOpen=null;
let pendingSt='',curStockId=null;
let settings={defaultPrice:0,lowAlert:2};

// GARSAS
let actx=null;
function ga(){if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();return actx;}
function beep(t){try{const c=ga();if(c.state==='suspended')c.resume();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;if(t==='new'){o.frequency.value=880;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.2);o.start(n);o.stop(n+.2);}else if(t==='col'){o.frequency.setValueAtTime(660,n);o.frequency.setValueAtTime(880,n+.12);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.3);o.start(n);o.stop(n+.3);}else if(t==='del'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(660,n+.1);o.frequency.setValueAtTime(880,n+.2);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='err'){o.type='sawtooth';o.frequency.value=220;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='dup'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(220,n+.15);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.35);o.start(n);o.stop(n+.35);}}catch(e){}}

// API
async function api(method,url,data){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(data)opts.body=JSON.stringify(data);
  const r=await fetch(url,opts);
  if(!r.ok)throw new Error(r.statusText);
  return r.json();
}

// INIT
window.onload=()=>{
  loadAll();
  const lt=localStorage.getItem('lastThick');
  if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}
  setPeriod(30);
  const dz=document.getElementById('dropZ');
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
};
document.addEventListener('click',e=>{if(actx&&actx.state==='suspended')actx.resume();if(document.getElementById('view-lk').classList.contains('active')&&!e.target.closest('input,button,select'))focusScan();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mbg').forEach(m=>m.style.display='none');});

async function loadAll(){await loadLk();await loadDxfOrds();await loadStock();await loadHist();await loadStages();}

// NAVIGACIJA
function SW(v){
  document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById('view-'+v).classList.add('active');
  const t=document.getElementById('tab-'+v);if(t)t.classList.add('active');
  if(v==='lk')focusScan();
  if(v==='dv'){const lt=localStorage.getItem('lastThick');if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}}
}
function CM(id){document.getElementById(id).style.display='none';}
function focusScan(){try{document.getElementById('scanInp').focus();}catch(e){}}
function toast(msg,w=false,t=''){const el=document.getElementById('toast');el.textContent=msg;el.className='toast '+(w?'w':t)+' show';clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),3000);}

// ════ LAKŠTAI ════
const scanInp=document.getElementById('scanInp');
scanInp.addEventListener('keydown',async e=>{if(e.key==='Enter'){const c=scanInp.value.trim();if(c){scanInp.value='';await handleScan(c);}}});

async function handleScan(kodas){
  const now=Date.now();
  if(kodas===lkLC&&now-lkLT<3000){lkRes('rp','DUBLIKATAS',kodas,'Tas pats kodas du kartus!');beep('dup');toast('Dublikatas: '+kodas,false,'p');lkLC=null;return;}
  lkLC=kodas;lkLT=now;
  const local=lkOrders.find(o=>o.kodas===kodas);
  if(local){
    if(local.delivered){lkRes('ra','JAU PERDUOTA',kodas,'Perduota: '+local.deliveredAt);beep('err');return;}
    if(local.collected){
      lkRes('rd','PERDUOTA',kodas,'3× — siunčiama...');beep('del');
      local.delivered=true;local.deliveredAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Perduota: '+kodas,false,'b');else{local.delivered=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }else{
      lkRes('rc','SURINKTA',kodas,'2× — siunčiama...');beep('col');
      local.collected=true;local.collectedAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Surinkta: '+kodas);else{local.collected=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }
    return;
  }
  lkRes('rn','NAUJAS',kodas,'1× — siunčiama...');beep('new');
  const newOrd={kodas,registered:nowS(),collected:false,collectedAt:'',delivered:false,deliveredAt:''};
  lkOrders.push(newOrd);lkStats();rlkList();
  api('POST','/api/lakstai/register',{kodas}).then(r=>{
    if(r.success)toast('Užregistruota: '+kodas);
    else if(r.alreadyExists){lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkAddL(r.order);lkStats();rlkList();handleScan(kodas);}
    else{lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkRes('re','KLAIDA',kodas,'Nepavyko');beep('err');lkStats();rlkList();}
  });
}

function lkRes(c,t,kodas,s){
  const b=document.getElementById('lkRes');
  b.className='res '+c;b.style.display='block';
  document.getElementById('lkRt').textContent=t;
  document.getElementById('lkRc').textContent=kodas;
  document.getElementById('lkRs').textContent=s;
}

async function loadLk(){
  try{const r=await api('GET','/api/lakstai');lkOrders=r.orders||[];lkStats();rlkList();document.getElementById('connDot').className='dot ok';}
  catch(e){document.getElementById('connDot').className='dot err';toast('Nepavyko prisijungti',true);}
}
function lkAddL(o){const i=lkOrders.findIndex(x=>x.kodas===o.kodas);if(i>=0)lkOrders[i]=o;else lkOrders.push(o);}
function lkStats(){
  const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length,p=lkOrders.filter(o=>!o.collected).length;
  const pc=t>0?Math.round(c/t*100):0,pd=t>0?Math.round(d/t*100):0;
  document.getElementById('lkT').textContent=t;document.getElementById('lkC').textContent=c;
  document.getElementById('lkD').textContent=d;document.getElementById('lkP').textContent=p;
  document.getElementById('lkPct').textContent=pc+'%';
  document.getElementById('lkPfc').style.width=pc+'%';document.getElementById('lkPfd').style.width=pd+'%';
  document.getElementById('lkBdg').textContent=p||t;
}
function lkFlt(f,b){lkF=f;document.querySelectorAll('.frow .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rlkList();}
function sortLk(l){return[...l].sort((a,b)=>{const n=s=>parseInt((s.match(/[0-9]+/)||[0])[0]);return n(a.kodas)-n(b.kodas);});}
function rlkList(){
  const el=document.getElementById('lkList'),q=(document.getElementById('lkSrch').value||'').toLowerCase();
  let l=sortLk(lkOrders);
  if(lkF==='p')l=l.filter(o=>!o.collected);if(lkF==='c')l=l.filter(o=>o.collected&&!o.delivered);if(lkF==='d')l=l.filter(o=>o.delivered);
  if(q)l=l.filter(o=>o.kodas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(lkOrders.length===0?'Nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>{
    const sc=o.delivered?'sdd':o.collected?'sc':'';
    const sl=o.delivered?'s2':o.collected?'s1':'s0';
    const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
    const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);
    return`<div class="oi ${sc}"><div class="od"></div><div class="oc">${o.kodas}</div><span class="ost ${sl}">${st}</span><div class="otm">${tm}</div><button class="btn btn-d btn-sm" onclick="lkDel('${o.kodas}')">✕</button></div>`;
  }).join('');
}
async function lkDel(k){if(!confirm('Ištrinti "'+k+'"?'))return;await api('DELETE','/api/lakstai/'+k);lkOrders=lkOrders.filter(o=>o.kodas!==k);lkStats();rlkList();toast('Ištrinta');}
function askStage(){
  const n=document.getElementById('stageInp').value.trim();
  if(!n){toast('Įvesk etapo pavadinimą!',true);return;}
  if(!lkOrders.length){toast('Nėra užsakymų',true);return;}
  pendingSt=n;const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length;
  document.getElementById('stMn').textContent='Etapas: "'+n+'"';
  document.getElementById('stMs').innerHTML='Iš viso: <strong>'+t+'</strong><br>Surinkta: <strong>'+c+'</strong><br>Perduota: <strong>'+d+'</strong><br>Laukia: <strong>'+(t-c)+'</strong>';
  document.getElementById('stModal').style.display='flex';
}
async function confirmStage(){
  CM('stModal');
  const r=await api('POST','/api/lakstai/archive',{pavadinimas:pendingSt});
  if(r.success){lkOrders=[];document.getElementById('stageInp').value='';lkStats();rlkList();await loadStages();beep('del');toast('Archyvuota: "'+r.archiveName+'"');lkRes('ra','ARCHYVUOTA',r.archiveName,r.collected+'/'+r.total+' surinkta');}
  else toast(r.message||'Klaida',true);
  focusScan();
}

// ════ SANDĖLIS ════
async function loadStock(){try{const r=await api('GET','/api/sandelis');stock=r.stock||[];rStock();document.getElementById('stkBdg').textContent=stock.length;}catch(e){}}
async function loadHist(){try{const r=await api('GET','/api/sandelis/istorija');history=r.history||[];rHist();}catch(e){}}

function rStock(){
  const el=document.getElementById('stkTbl'),su=document.getElementById('stkSum');
  if(!stock.length){el.innerHTML='<div class="empty-s">Sandėlis tuščias</div>';su.innerHTML='';return;}
  const totVnt=stock.reduce((s,r)=>s+r.likoVnt,0);
  const totKg=stock.reduce((s,r)=>s+r.likoKg,0);
  const totT=Math.round(totKg/10)/100;
  const totVal=stock.reduce((s,r)=>s+r.verte,0);
  const byT={};stock.forEach(r=>{if(!byT[r.storis])byT[r.storis]={vnt:0,kg:0};byT[r.storis].vnt+=r.likoVnt;byT[r.storis].kg+=r.likoKg;});
  su.innerHTML=`<div class="stk-s"><div class="stk-n">${totVnt}</div><div class="stk-l">Viso vnt.</div></div><div class="stk-s"><div class="stk-n">${totKg.toFixed(1)}</div><div class="stk-l">Viso kg</div></div><div class="stk-s"><div class="stk-n" style="color:var(--gn)">${totT}</div><div class="stk-l">Tonos</div></div><div class="stk-s"><div class="stk-n" style="color:var(--or)">${totVal.toFixed(2)}</div><div class="stk-l">Vertė €</div></div>`+
    Object.entries(byT).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).map(([t,v])=>`<div class="stk-s"><div class="stk-n" style="font-size:15px">${v.vnt}vnt</div><div class="stk-l">${t}mm · ${(Math.round(v.kg/10)/100).toFixed(2)}t</div></div>`).join('');
  const sorted=[...stock].sort((a,b)=>a.storis-b.storis);
  el.innerHTML=sorted.map(r=>{
    const nc=r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return`<div class="stk-row"><div><div class="stk-thick">${r.storis}<span>mm</span></div></div><div><div class="stk-dims">${r.matmenys}mm</div><div class="stk-sub">${r.pastabos||''}</div></div><div><div class="stk-num ${nc}">${r.likoVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:13px;color:var(--tx2)">${r.likoKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${r.likoT.toFixed(3)}</div><div class="stk-sub">t</div></div><div><div class="stk-val">${r.verte.toFixed(2)}€</div><div class="stk-sub">${r.kainaKg>0?r.kainaKg+'€/kg':''}</div></div><div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse('${r.id}','${r.storis}mm ${r.matmenys}',${r.likoVnt})">−</button><button class="btn btn-d btn-sm" onclick="delStk('${r.id}')">✕</button></div></div>`;
  }).join('')+`<div class="stk-tot"><div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);font-weight:700">VISO</div><div></div><div><div class="stk-num" style="font-size:13px;color:var(--ac)">${totVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${totKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">${totT}</div><div class="stk-sub">t</div></div><div><div class="stk-val" style="font-size:13px;font-weight:800">${totVal.toFixed(2)}€</div></div><div></div></div>`;
}

function rHist(){
  const el=document.getElementById('histTbl');
  if(!history.length){el.innerHTML='<div class="empty-s">Dar nėra istorijos</div>';return;}
  el.innerHTML=`<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>${history.slice(0,50).map(h=>`<tr><td class="mono" style="font-size:10px;color:var(--tx3)">${h.data}</td><td><span class="hist-act ${h.veiksmas[0]}">${h.veiksmas}</span></td><td class="mono">${h.storis}mm</td><td class="mono" style="color:var(--tx2)">${h.matmenys}</td><td class="mono">${h.kiekis}vnt.</td><td class="num">${h.svorisIšViso.toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

function showRecv(){
  if(settings.defaultPrice)document.getElementById('recP').value=settings.defaultPrice;
  document.getElementById('recvModal').style.display='flex';
}
function rcRecv(){
  const t=parseFloat(document.getElementById('recThk').value)||0,w=parseFloat(document.getElementById('recW').value)||0,l=parseFloat(document.getElementById('recL').value)||0,q=parseInt(document.getElementById('recQ').value)||1,p=parseFloat(document.getElementById('recP').value)||0;
  if(!w||!l){document.getElementById('recPrev').textContent='Įvesk matmenis...';return;}
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100,totT=Math.round(tot/10)/100,val=p>0?Math.round(tot*p*100)/100:0;
  document.getElementById('recPrev').innerHTML=`1 lakštas: <strong style="color:var(--ac)">${we}kg</strong> · ${q}vnt.: <strong style="color:var(--gn)">${tot}kg = ${totT}t</strong>${val>0?' · <strong style="color:var(--or)">'+val+'€</strong>':''}`;
}
async function doRecv(){
  const t=document.getElementById('recThk').value,w=document.getElementById('recW').value,l=document.getElementById('recL').value,q=document.getElementById('recQ').value,p=document.getElementById('recP').value,n=document.getElementById('recN').value;
  if(!w||!l){toast('Įvesk matmenis!',true);return;}
  const r=await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if(r.success){CM('recvModal');await loadStock();await loadHist();toast('Pridėta: '+q+'vnt. × '+t+'mm ('+r.likoT+'t)');}
}
function showUse(id,label,rem){curStockId=id;document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';document.getElementById('useQ').value=1;document.getElementById('useNote').value='';document.getElementById('useModal').style.display='flex';}
async function doUse(){
  const q=parseInt(document.getElementById('useQ').value)||1,n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if(r.success){CM('useModal');await loadStock();await loadHist();toast('Sunaudota: '+q+'vnt. Liko: '+r.likoVnt+'vnt.');}
  else toast('Klaida',true);
}
async function delStk(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/sandelis/'+id);await loadStock();toast('Ištrinta');}
function showSett(){document.getElementById('settP').value=settings.defaultPrice||'';document.getElementById('settL').value=settings.lowAlert||2;document.getElementById('settModal').style.display='flex';}
function saveSett(){settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;settings.lowAlert=parseInt(document.getElementById('settL').value)||2;CM('settModal');localStorage.setItem('sandSettings',JSON.stringify(settings));toast('Nustatymai išsaugoti');}

// ════ ARCHYVAI ════
async function loadStages(){try{const r=await api('GET','/api/etapai');stages=r.stages||[];document.getElementById('archBdg').textContent=stages.length;rStages();}catch(e){}}
function rStages(){
  const el=document.getElementById('stageCards');
  if(!stages.length){el.innerHTML='<div class="empty-s">Dar nėra archyvų</div>';return;}
  el.innerHTML=stages.map(s=>{
    const t=s.total||0,c=s.collected||0,d=s.delivered||0,p=s.pending||(t-c),pct=t>0?Math.round(c/t*100):0;
    return`<div class="scc ${archOpen===s.name?'open':''}" onclick="toggleArch('${s.name.replace(/'/g,"\\'")}')"><div class="scn">${s.name}</div><div class="scst"><div><span class="n">${t}</span><span class="l">Viso</span></div><div><span class="n g">${c}</span><span class="l">Surinkta</span></div><div><span class="n b">${d}</span><span class="l">Perduota</span></div><div><span class="n ${p>0?'r':'g'}">${p}</span><span class="l">Liko</span></div></div><div class="scp"><div class="scpf" style="width:${pct}%"></div></div></div>`;
  }).join('');
}
async function toggleArch(name){
  if(archOpen===name){archOpen=null;closeAd();rStages();return;}
  archOpen=name;rStages();
  document.getElementById('adTitle').textContent=name;
  document.getElementById('adList').innerHTML='<div class="empty-s"><span class="sp"></span> Kraunama...</div>';
  document.getElementById('adBox').style.display='block';
  try{
    const r=await api('GET','/api/etapai/'+encodeURIComponent(name));
    const items=sortLk(r.orders||[]);
    if(!items.length){document.getElementById('adList').innerHTML='<div class="empty-s">Tuščias</div>';return;}
    document.getElementById('adList').innerHTML=items.map(o=>{
      const sc=o.delivered?'sdd':o.collected?'sc':'';const tc=o.delivered?'d':o.collected?'c':'r';const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
      const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(0,16);
      return`<div class="adi ${sc}"><div class="addot"></div><div class="adcode">${o.kodas}</div><span class="adtag ${tc}">${st}</span><div class="adtime">${tm}</div></div>`;
    }).join('');
  }catch(e){}
}
function closeAd(){document.getElementById('adBox').style.display='none';archOpen=null;rStages();}

// ════ DXF ════
async function loadDxfOrds(){try{const r=await api('GET','/api/uzsakymai');dxfOrders=r.orders||[];dxfSum();rOrds();document.getElementById('dxfBdg').textContent=dxfOrders.length;}catch(e){}}
function dxfSum(){
  const t=dxfOrders.length,n=dxfOrders.filter(o=>o.statusas==='Naujas').length,a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length,d=dxfOrders.filter(o=>o.statusas==='Baigtas').length,w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML=`<div class="smc"><div class="smn a">${t}</div><div class="sml">Iš viso</div></div><div class="smc"><div class="smn" style="color:var(--yw)">${n}</div><div class="sml">Nauji</div></div><div class="smc"><div class="smn a">${a}</div><div class="sml">Vykdomi</div></div><div class="smc"><div class="smn" style="color:var(--gn)">${d}</div><div class="sml">Baigti</div></div><div class="smc"><div class="smn a">${w.toFixed(2)}</div><div class="sml">Svoris kg</div></div>`;
}
function dxfFlt(f,b){dxfF=f;document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rOrds();}
function rOrds(){
  const el=document.getElementById('ordsGrid'),q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all')l=l.filter(o=>o.statusas===dxfF);if(q)l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>`<div class="ocard" onclick="openOrd('${o.id}')"><div class="oct"><div class="oid">${o.id}</div><div style="display:flex;gap:4px"><span class="stb ${o.statusas}">${o.statusas}</span><button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd('${o.id}','${o.klientas.replace(/'/g,"\\'")}')">✕</button></div></div><div class="ocli">${o.klientas}</div><div class="ocdesc">${o.aprasymas||'—'}</div><div class="ocm"><div class="ocmi"><span class="v">${o.bendraSvoris.toFixed(3)}</span><span class="l"> kg</span></div><div class="ocmi"><span class="v">${o.detaliuSk}</span><span class="l"> det.</span></div><div class="ocmi"><span class="l">${(o.sukurta||'').slice(0,10)}</span></div></div></div>`).join('');
}
async function quickDelOrd(id,klientas){if(!confirm('Ištrinti "'+klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+id);dxfOrders=dxfOrders.filter(o=>o.id!==id);dxfSum();rOrds();toast('Ištrinta');}
function showNewOrd(){document.getElementById('noModal').style.display='flex';setTimeout(()=>document.getElementById('noC').focus(),100);}
async function createOrd(){
  const c=document.getElementById('noC').value.trim();if(!c){toast('Įvesk klientą!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id){
  const o=dxfOrders.find(x=>x.id===id);if(!o)return;curOrd=o;
  document.getElementById('dvId').textContent=o.id;document.getElementById('dvCli').textContent=o.klientas;document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' · '+o.pastabos:'');
  SW('dv');await loadDets();
}
function back2Ords(){SW('dxf');loadDxfOrds();curArea=0;curContour='';document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';}
async function chSt(){if(!curOrd)return;await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value});toast('Statusas atnaujintas');}
async function delOrd(){if(!curOrd)return;if(!confirm('Ištrinti "'+curOrd.klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+curOrd.id);toast('Ištrinta');back2Ords();}
async function loadDets(){
  if(!curOrd)return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[];rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
}

function rDets(){
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nėra detalių</div>';return;}
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const groups={};
  dxfDets.forEach(d=>{const t=String(d.storis);if(!groups[t])groups[t]={t,dets:[],w:0,q:0};groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;});
  let rows='';let idx=0;
  Object.values(groups).forEach(g=>{
    rows+=`<tr class="det-grp-hdr"><td colspan="2"></td><td colspan="2"><span class="det-grp-t">${g.t}mm</span></td><td><span class="det-grp-s">${g.dets.length}det.</span></td><td><span class="det-grp-s">${g.q}vnt.</span></td><td><span class="det-grp-s" style="color:var(--ac)">${g.w.toFixed(3)}kg</span></td><td></td></tr>`;
    g.dets.forEach(d=>{
      idx++;
      rows+=`<tr><td class="mono" style="color:var(--tx3);font-size:10px">${idx}</td><td style="font-weight:600">${d.pavadinimas}</td><td><select class="det-inp" onchange="updDet('${d.detId}','storis',this.value)">${STORIAI.map(t=>`<option value="${t}"${d.storis===t?' selected':''}>${t}mm</option>`).join('')}</select></td><td class="mono" style="font-size:11px;color:var(--tx2)">${calcDims(d)}</td><td><input type="number" class="det-inp" value="${d.kiekis}" min="1" style="width:50px" onchange="updDet('${d.detId}','kiekis',this.value)"></td><td><input type="number" class="det-inp num" value="${d.svoris.toFixed(3)}" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-${d.detId}" onchange="updDetW('${d.detId}',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td><td><button class="btn btn-d btn-sm" onclick="delDet('${d.detId}')">✕</button></td></tr>`;
    });
  });
  w.innerHTML=`<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">${tq}vnt.</strong></span><span>Bendras svoris: <span class="tot">${tw.toFixed(3)}kg</span></span></div>`;
}

async function updDet(detId,field,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  if(field==='storis')d.storis=parseFloat(value);else if(field==='kiekis')d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  const wEl=document.getElementById('w-'+detId);if(wEl)wEl.value=d.svoris.toFixed(3);
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas});
}
async function updDetW(detId,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
function _updateTotals(){
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  document.getElementById('dvWt').textContent=tw.toFixed(3);
}
async function delDet(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/detales/'+id);dxfDets=dxfDets.filter(d=>d.detId!==id);rDets();_updateTotals();toast('Ištrinta');}

// DXF ĮKĖLIMAS
function handleDxf(e){if(e.target.files.length)handleMultiDxf(Array.from(e.target.files));}
function handleFolder(e){
  if(!e.target.files.length)return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failų!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' → '+ft+'mm, '+files.length+' failų',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files){
  if(!curOrd){toast('Pirma atidaryk užsakymą!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Įkeliama '+files.length+' failų...';
  for(const file of files){
    await new Promise(resolve=>{
      const r=new FileReader();
      r.onload=async e2=>{
        try{
          const res=pDxf(e2.target.result);
          if(res.areaCm2<=0){fail++;resolve();return;}
          const at=thickFromName(file.name)||defThick;
          const aq=qtyFromName(file.name)||defQty;
          const ctour=serializeContour(res.entities,res.dimW,res.dimH);
          const resp=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:file.name.replace(/[.]dxf$/i,''),storis:at,plotas:res.areaCm2,kiekis:aq,konturas:ctour});
          if(resp.success)ok++;else fail++;
        }catch(ex){fail++;}
        resolve();
      };
      r.readAsText(file);
    });
  }
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Tempk DXF failus čia arba spusk';
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?`Įkelta: ${ok}, nepavyko: ${fail}`:`Sėkmingai įkeltos ${ok} detalės!`);
}
function procDxf(file){
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2;
      curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name);const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq)document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
      toast('DXF: '+res.areaCm2.toFixed(2)+'cm²'+(at?' · '+at+'mm':''));
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm² · '+t+'mm × '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd)return;if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd)return;const a=parseFloat(document.getElementById('mArea').value)||0;if(a<=0){toast('Įvesk plotą!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:''});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}

// ATASKAITA
function setPeriod(days){
  const to=new Date(),from=new Date();
  if(days===0)from.setDate(1);else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep(){
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpį!',true);return;}
  const r=await api('GET',`/api/ataskaita?nuo=${from}&iki=${to}`);
  const el=document.getElementById('repOut');
  el.style.display='block';
  el.innerHTML=`<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: ${from} — ${to}</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.lakstai.gauta}</div><div class="l">Lakštų gauta</div></div><div class="rep-sc"><div class="n">${r.lakstai.surinkta}</div><div class="l">Surinkta</div></div><div class="rep-sc"><div class="n">${r.lakstai.perduota}</div><div class="l">Perduota</div></div><div class="rep-sc"><div class="n">${r.dxf.sk}</div><div class="l">DXF užsakymų</div></div><div class="rep-sc"><div class="n">${r.dxf.svoris.toFixed(1)}</div><div class="l">DXF svoris kg</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio judėjimas</div><div class="rep-sr"><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.sandelis.gautaKg.toFixed(1)}</div><div class="l">Gauta kg</div></div><div class="rep-sc"><div class="n" style="color:var(--rd)">${r.sandelis.sunaudotaKg.toFixed(1)}</div><div class="l">Sunaudota kg</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.gautaVerte.toFixed(2)}</div><div class="l">Gauta vertė €</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.sunaudotaVerte.toFixed(2)}</div><div class="l">Sunaudota €</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio likutis dabar</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.likutis.vnt}</div><div class="l">Viso vnt.</div></div><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.likutis.t}</div><div class="l">Tonos</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.likutis.verte.toFixed(2)}</div><div class="l">Vertė €</div></div></div></div></div>`;
}

// SPAUSDINIMAS
function printOrd(){
  if(!curOrd)return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return`<tr><td style="font-weight:700;color:#1e3a5f">${t}mm</td><td style="text-align:center">${dets.length}</td><td style="text-align:center">${gq}</td><td style="text-align:right;font-weight:700">${gw.toFixed(3)}</td></tr>`;}).join('');
  let html=`<div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div><div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">${totW.toFixed(3)} kg</div></div><div><div class="ppi-l">Viso detalių</div><div class="ppi-v">${totQ} vnt.</div></div><div><div class="ppi-l">Storių sk.</div><div class="ppi-v">${groups.size} storiai</div></div></div><table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>${sumRows}<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">${sorted.length}</td><td style="text-align:center">${totQ}</td><td style="text-align:right">${totW.toFixed(3)}</td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>Išspausdinta: ${now}</span><span>${curOrd.id}</span></div>`;
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>`<tr><td>${i+1}</td><td><strong>${d.pavadinimas}</strong></td><td style="text-align:center">${calcDims(d)}</td><td style="text-align:center">${d.kiekis}</td><td style="text-align:right"><strong>${d.svoris.toFixed(3)}</strong></td><td style="text-align:center;vertical-align:middle">${drawContourSvg(d.konturas,12)}</td></tr>`).join('');
    html+=`<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">${thick}mm</div></div><div class="ppinfo"><div><div class="ppi-l">Svoris (${thick}mm)</div><div class="ppi-v">${gw.toFixed(3)} kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">${gq}vnt. (${dets.length}poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">${now}</div></div></div><table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>${rows}<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">${gq}vnt.</td><td style="text-align:right">${gw.toFixed(3)}kg</td><td></td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>${thick}mm · ${dets.length}poz. · ${gq}vnt. · ${gw.toFixed(3)}kg</span><span>${curOrd.id}</span></div></div>`;
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}

function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  const s='<style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style>';
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'+s+'</head><body>'+c+'</body>');
  w.document.close();
  setTimeout(function(){w.print();},500);
}

function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}

// Nustatymų įkėlimas
const savedSett=localStorage.getItem('sandSettings');
if(savedSett)try{settings=JSON.parse(savedSett);}catch(e){}

async function siustiEmail(){
  const btn=document.getElementById('emailBtn');
  btn.textContent='Siunčiama...';btn.disabled=true;
  try{
    const r=await fetch('/api/email/siusti',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const d=await r.json();
    if(d.success){alert('✓ '+d.message);}
    else{alert('Klaida: '+(d.detail||d.message));}
  }catch(e){alert('Klaida: '+e.message);}
  btn.textContent='✉ Siųsti ataskaitą';btn.disabled=false;
}

"""

_HTML = """<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0969da">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sandelis">
<link rel="manifest" href="/manifest.json">
<title>Sandelio Sistema</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
<nav>
  <div class="brand"><div class="brand-ico"></div>SANDELIS</div>
  <div class="tabs">
    <button class="tab active" onclick="SW('lk')" id="tab-lk">Lakstai <span class="bdg" id="lkBdg">0</span></button>
    <button class="tab" onclick="SW('stk')" id="tab-stk">Sandelis <span class="bdg y" id="stkBdg">0</span></button>
    <button class="tab" onclick="SW('dxf')" id="tab-dxf">DXF <span class="bdg gray" id="dxfBdg">0</span></button>
    <button class="tab" onclick="SW('arch')" id="tab-arch">Archyvai <span class="bdg gray" id="archBdg">0</span></button>
    <button class="tab" onclick="SW('rep')" id="tab-rep">Ataskaita</button>
  </div>
  <div class="nav-r"><div class="dot ok" id="connDot"></div></div>
</nav>

<div class="view active" id="view-lk">
  <div class="lk-wrap">
    <div class="lk-main">
      <div class="card">
        <div class="ct">Skanavimas</div>
        <div class="scan-f"><span class="scan-ico">▦</span><input class="scan-inp" id="scanInp" placeholder="Skanuok arba ivesk koda..." autocomplete="off" spellcheck="false"></div>
        <div class="hint" id="scanHint">Laukiama skanavimo...</div>
        <div class="steps"><div class="step s1"></div><div class="step s2"></div><div class="step s3"></div></div>
        <div class="step-lbl"><span>1x Registruota</span><span>2x Surinkta</span><span>3x Perduota</span></div>
      </div>
      <div class="res" id="lkRes" style="display:none"><div class="rt" id="lkRt"></div><div class="rc" id="lkRc"></div><div class="rs" id="lkRs"></div></div>
      <div class="stats-row">
        <div class="stat"><div class="sn a" id="lkT">0</div><div class="sl">Is viso</div></div>
        <div class="stat"><div class="sn g" id="lkC">0</div><div class="sl">Surinkta</div></div>
        <div class="stat"><div class="sn b" id="lkD">0</div><div class="sl">Perduota</div></div>
        <div class="stat"><div class="sn y" id="lkP">0</div><div class="sl">Laukia</div></div>
      </div>
      <div class="prog-card">
        <div class="pt"><span>Progresas</span><span class="pct" id="lkPct">0%</span></div>
        <div class="ptr"><div class="pfd" id="lkPfd" style="width:0%"></div><div class="pfc" id="lkPfc" style="width:0%"></div></div>
      </div>
      <div class="stbar">
        <span class="stbar-lbl">Naujas etapas:</span>
        <input type="text" id="stageInp" placeholder="pvz. Etapas 221">
        <button class="btn btn-p btn-sm" onclick="askStage()">Archyvuoti</button>
      </div>
    </div>
    <div class="lk-sb">
      <div class="sbh">
        <div class="sbt">Uzsakymai</div>
        <button class="btn btn-g btn-sm" onclick="loadLk()">&#x21BB;</button>
        <button id="pdfBtn" class="btn btn-s btn-sm" onclick="genPdfReport()">&#x22C6; Atsisiusti PDF</button>
        <div class="sbsr"><span class="sbs-i">&#x2315;</span><input type="text" id="lkSrch" placeholder="Ieskoti..." oninput="rlkList()"></div>
      </div>
      <div class="frow">
        <button class="fb active" onclick="lkFlt('all',this)">Visi</button>
        <button class="fb" onclick="lkFlt('p',this)">Laukia</button>
        <button class="fb" onclick="lkFlt('c',this)">Surinkti</button>
        <button class="fb" onclick="lkFlt('d',this)">Perduoti</button>
      </div>
      <div class="olist" id="lkList"><div class="empty-s">Jungiamasi...</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-stk">
  <div class="page-wrap">
    <div class="ph"><div><div class="ph-t">Metalo sandelis</div><div class="ph-s">Lakstu likuciai pagal stori</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-s btn-sm" onclick="showSett()">Nustatymai</button>
        <button class="btn btn-p" onclick="showRecv()">+ Gauti lakstus</button>
      </div>
    </div>
    <div class="stk-sum" id="stkSum"></div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Likutis</span><button class="btn btn-s btn-sm" onclick="loadStock()">&#x21BB;</button></div>
      <div id="stkTbl"><div class="empty-s">Sandelis tuscias</div></div>
    </div>
    <div class="card" style="overflow:hidden;padding:0;margin-top:12px">
      <div class="card-h"><span class="card-t">Istorija</span><button class="btn btn-s btn-sm" onclick="loadHist()">&#x21BB;</button></div>
      <div id="histTbl"><div class="empty-s">Dar nera istorijos</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-dxf">
  <div class="page-wrap">
    <div class="ph"><div class="ph-t">DXF Uzsakymai</div><button class="btn btn-p" onclick="showNewOrd()">+ Naujas</button></div>
    <div class="sumr" id="dxfSum"></div>
    <div class="fbar">
      <button class="fb active" onclick="dxfFlt('all',this)">Visi</button>
      <button class="fb" onclick="dxfFlt('Naujas',this)">Nauji</button>
      <button class="fb" onclick="dxfFlt('Vykdomas',this)">Vykdomi</button>
      <button class="fb" onclick="dxfFlt('Baigtas',this)">Baigti</button>
      <input class="si" id="dxfSrch" placeholder="Ieskoti..." oninput="rOrds()">
    </div>
    <div class="og" id="ordsGrid"><div class="empty-s">Jungiamasi...</div></div>
  </div>
</div>

<div class="view" id="view-dv">
  <div class="page-wrap">
    <div class="back" onclick="back2Ords()">&#x2190; Grizti</div>
    <div class="card" style="margin-bottom:12px">
      <div class="oi-top">
        <div><div class="oid" id="dvId"></div><div class="oi-t" id="dvCli"></div><div class="oi-s" id="dvDsc"></div></div>
        <div style="text-align:right">
          <div class="wbig" id="dvWt">0</div><div class="wlbl">kg bendras svoris</div>
          <div style="margin-top:8px;display:flex;gap:5px;justify-content:flex-end;flex-wrap:wrap">
            <select class="stsel" id="dvSt" onchange="chSt()"><option>Naujas</option><option>Vykdomas</option><option>Baigtas</option></select>
            <button class="btn btn-p btn-sm" onclick="printOrd()">Spausdinti</button>
            <button class="btn btn-d btn-sm" onclick="delOrd()">Trinti</button>
          </div>
        </div>
      </div>
      <div id="dvMeta" style="font-size:11px;color:#57606a;font-family:'JetBrains Mono',monospace;margin-top:6px"></div>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Prideti detale is DXF</div>
      <div class="dropz" id="dropZ">
        <input type="file" id="dxfFile" accept=".dxf" multiple onchange="handleDxf(event)">
        <div class="dz-t">Tempk DXF failus cia arba spusk</div>
        <div class="dz-s">.dxf - galima ikelti kelis failus</div>
      </div>
      <div style="margin-top:8px">
        <label class="btn btn-s btn-sm" style="cursor:pointer">Ikelti aplanka<input type="file" id="dxfFolder" webkitdirectory multiple accept=".dxf" style="display:none" onchange="handleFolder(event)"></label>
      </div>
      <div class="cvw" id="cvW" style="display:none"><canvas id="dxfCv"></canvas></div>
      <div class="pf" id="pForm" style="display:none">
        <div class="wp"><div class="wv" id="wPv">0.000</div><div class="wl">kg (vieno vnt.)</div><div class="wa" id="wAr"></div></div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="dName"></div>
          <div><label class="fl">Storis (mm)</label><select id="dThk" onchange="rcW();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Kiekis</label><input type="number" id="dQty" value="1" min="1" oninput="rcW()"></div>
        </div>
        <button class="btn btn-p" style="width:100%" onclick="addDet()">+ Prideti detale</button>
      </div>
      <div class="msec">
        <div class="mlbl">arba ivesk rankiniu budu</div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="mName"></div>
          <div><label class="fl">Storis (mm)</label><select id="mThk" onchange="rcM();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Plotas (cm2)</label><input type="number" id="mArea" step="0.01" oninput="rcM()"></div>
        </div>
        <div class="fgrid">
          <div><label class="fl">Kiekis</label><input type="number" id="mQty" value="1" min="1" oninput="rcM()"></div>
          <div><label class="fl">Svoris</label><div class="svor-d" id="mWp">0.000 kg</div></div>
          <div style="display:flex;align-items:flex-end"><button class="btn btn-p" style="width:100%" onclick="addMDet()">+ Prideti</button></div>
        </div>
      </div>
    </div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Detaliu sarasas</span><button class="btn btn-s btn-sm" onclick="loadDets()">&#x21BB;</button></div>
      <div id="dtWrap"><div class="empty-s">Dar nera detaliu</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-arch">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Archyvai</div>
    <div class="sc-grid" id="stageCards"><div class="empty-s">Dar nera archivu</div></div>
    <div class="adbox" id="adBox" style="display:none">
      <div class="adh"><div class="adt" id="adTitle"></div><button class="btn btn-s btn-sm" onclick="closeAd()">X</button></div>
      <div class="adlist" id="adList"></div>
    </div>
  </div>
</div>

<div class="view" id="view-rep">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Ataskaita</div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Laikotarpis</div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr;margin-bottom:10px">
        <div><label class="fl">Nuo</label><input type="date" id="repFrom"></div>
        <div><label class="fl">Iki</label><input type="date" id="repTo"></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
        <button class="btn btn-s btn-sm" onclick="setPeriod(7)">7 dienos</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(30)">30 dienu</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(0)">Sis menuo</button>
      </div>
      <button class="btn btn-p" onclick="genRep()">Generuoti</button>
    </div>
    <div id="repOut" style="display:none"></div>
  </div>
</div>

<div class="mbg" id="noModal" style="display:none">
  <div class="modal">
    <div class="mh">Naujas DXF uzsakymas</div>
    <div class="mf">
      <div><label class="fl">Klientas *</label><input type="text" id="noC"></div>
      <div><label class="fl">Aprasymas</label><input type="text" id="noD"></div>
      <div><label class="fl">Pastabos</label><textarea id="noN"></textarea></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('noModal')">Atsaukti</button><button class="btn btn-p" onclick="createOrd()">Sukurti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="recvModal" style="display:none">
  <div class="modal">
    <div class="mh">Gauti lakstus</div>
    <div class="mf">
      <div><label class="fl">Storis (mm)</label><select id="recThk"><option value="3">3 mm</option><option value="4">4 mm</option><option value="5">5 mm</option><option value="6">6 mm</option><option value="8">8 mm</option><option value="10">10 mm</option><option value="12">12 mm</option><option value="14">14 mm</option><option value="15">15 mm</option><option value="16">16 mm</option><option value="18">18 mm</option><option value="20">20 mm</option><option value="25">25 mm</option></select></div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Plotis (mm)</label><input type="number" id="recW" oninput="rcRecv()"></div>
        <div><label class="fl">Ilgis (mm)</label><input type="number" id="recL" oninput="rcRecv()"></div>
      </div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Kiekis (vnt.)</label><input type="number" id="recQ" value="1" oninput="rcRecv()"></div>
        <div><label class="fl">Kaina / t (EUR)</label><input type="number" id="recP" step="0.01" oninput="rcRecv()"></div>
      </div>
      <div class="rec-prev" id="recPrev">Ivesk matmenis...</div>
      <div><label class="fl">Pastabos (SF nr.)</label><input type="text" id="recN"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('recvModal')">Atsaukti</button><button class="btn btn-p" onclick="doRecv()">Prideti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="useModal" style="display:none">
  <div class="modal">
    <div class="mh">Sunaudoti lakstus</div>
    <div class="mf">
      <div id="useInfo" class="rec-prev"></div>
      <div><label class="fl">Kiek vnt.?</label><input type="number" id="useQ" value="1" min="1"></div>
      <div><label class="fl">Pastabos</label><input type="text" id="useNote"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('useModal')">Atsaukti</button><button class="btn btn-y" onclick="doUse()">Sunaudoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="settModal" style="display:none">
  <div class="modal">
    <div class="mh">Nustatymai</div>
    <div class="mf">
      <div><label class="fl">Numatyta kaina / kg (EUR)</label><input type="number" id="settP" step="0.01"></div>
      <div><label class="fl">Zemos atsargos ispejimas</label><input type="number" id="settL" value="2" min="0"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('settModal')">Atsaukti</button><button class="btn btn-p" onclick="saveSett()">Issaugoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="stModal" style="display:none">
  <div class="modal">
    <div class="mh">Archyvuoti etapa?</div>
    <div id="stMn" style="font-size:11px;color:#57606a;margin-bottom:10px"></div>
    <div id="stMs" class="rec-prev" style="margin-bottom:12px;line-height:2"></div>
    <div class="mb"><button class="btn btn-s" onclick="CM('stModal')">Atsaukti</button><button class="btn btn-p" onclick="confirmStage()">Archyvuoti</button></div>
  </div>
</div>

<div class="pmb" id="printMod" style="display:none">
  <div class="pm">
    <div class="pbr">
      <button class="btn btn-p btn-sm" onclick="window.print()">Spausdinti</button>
      <button class="btn btn-s btn-sm" onclick="dlPdf()">PDF</button>
      <button class="btn btn-s btn-sm" onclick="CM('printMod')">Uzdaryti</button>
    </div>
    <div id="printArea"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const STORIAI=[3,4,5,6,8,10,12,14,15,16,18,20,25];
const TANKIS=8000;
</script>
<script src="/static/js/dxf.js"></script>
<script src="/static/js/main.js"></script>
</body>
</html>"""

@app.on_event("startup")
def startup():
    init_db()

@app.get("/static/css/main.css")
async def serve_css():
    return Response(content=_CSS, media_type="text/css")

@app.get("/static/js/dxf.js")
async def serve_dxfjs():
    return Response(content=_DXFJS, media_type="application/javascript")

@app.get("/static/js/main.js")
async def serve_mainjs():
    return Response(content=_MAINJS, media_type="application/javascript")

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({"name":"Sandelio Sistema","short_name":"Sandelis","start_url":"/","display":"standalone","background_color":"#f6f8fa","theme_color":"#0969da"})

@app.get("/sw.js")
async def sw():
    return Response(content="// sw", media_type="application/javascript")

@app.get("/icon.png")
async def icon():
    import base64
    return Response(content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="), media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=_HTML)


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
        raise HTTPException(400, "SMTP_PASS nenurodytas Railway Variables")
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti = [l for l in items if l.surinkta and not l.perduota]
    perduoti = [l for l in items if l.perduota]
    laukia = [l for l in items if not l.surinkta]
    def rows(lst, color):
        if not lst: return "<tr><td colspan=2 style='color:#aaa;padding:4px 8px'>Tuscia</td></tr>"
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else '-'}</td></tr>" for l in lst)
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
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
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th></tr>{rows(laukia,'#9a6700')}</table>
      <p style='color:#57606a;font-size:11px;margin-top:16px'>Issiusta is Sandelio sistemos - metalcraft.lt</p>
    </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandelio ataskaita {now}"
        msg["From"] = f"Metalcraft <{smtp_user}>"
        msg["To"] = gaivejas
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        # Bandome 587 su STARTTLS
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        except Exception as e1:
            # Bandome 465 su SSL
            with smtplib.SMTP_SSL(smtp_host, 465, timeout=30) as s:
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        return {"success": True, "message": f"Issiusta i {gaivejas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# LAKŠTAI API
# ══════════════════════════════════════════════════

@app.get("/api/lakstai")
def get_lakstai(etapas: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lakstai)
    if etapas:
        q = q.filter(Lakstai.etapas == etapas)
    else:
        q = q.filter(Lakstai.etapas == None)
    items = q.all()
    return {"orders": [_lk(l) for l in items]}

@app.get("/api/lakstai/find/{kodas}")
def find_lakstas(kodas: str, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == kodas).first()
    if not l:
        return {"found": False}
    return {"found": True, **_lk(l)}

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
        return {"success": False, "message": "Nėra užsakymų"}
    total = len(items); collected = sum(1 for l in items if l.surinkta); delivered = sum(1 for l in items if l.perduota)
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

# ══════════════════════════════════════════════════
# DXF API
# ══════════════════════════════════════════════════

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
    d = Detale(det_id=det_id, uzsakymo_id=data["uzsakymoId"], pavadinimas=data.get("pavadinimas", "Detalė"),
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

# ══════════════════════════════════════════════════
# SANDĖLIS API
# ══════════════════════════════════════════════════

@app.get("/api/sandelis")
def get_sandelis(db: Session = Depends(get_db)):
    items = db.query(Sandelis).order_by(Sandelis.storis).all()
    return {"stock": [_stk(s) for s in items]}

@app.post("/api/sandelis/gauti")
def gauti(data: dict, db: Session = Depends(get_db)):
    storis = float(data["storis"]); w = float(data["plotis"]); l = float(data["ilgis"]); qty = int(data["kiekis"])
    kaina = float(data.get("kaina", 0))
    svoris_vnt = round((w/1000) * (l/1000) * (storis/1000) * TANKIS, 2)
    liko_kg = round(svoris_vnt * qty, 2)
    liko_t = round(liko_kg / 1000, 3)
    verte = round(liko_t * kaina, 2)  # kaina uz tona
    stk_id = "STK-" + str(int(datetime.utcnow().timestamp() * 1000))
    s = Sandelis(stk_id=stk_id, storis=storis, matmenys=f"{int(w)}×{int(l)}", svoris_vnt=svoris_vnt,
                 gauta_vnt=qty, liko_vnt=qty, liko_kg=liko_kg, liko_t=liko_t, kaina_kg=kaina, verte=verte,
                 pastabos=data.get("pastabos", ""))
    db.add(s)
    hist = SandelioIstorijia(veiksmas="Gauta", storis=storis, matmenys=f"{int(w)}×{int(l)}", kiekis=qty,
                              svoris_vnt=svoris_vnt, svoris_iš_viso=liko_kg, kaina_kg=kaina, verte=verte, pastabos=data.get("pastabos", ""))
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
    s.verte = round(s.liko_t * s.kaina_kg, 2)  # kaina uz tona
    hist = SandelioIstorijia(veiksmas="Sunaudota", storis=s.storis, matmenys=s.matmenys, kiekis=qty,
                              svoris_vnt=s.svoris_vnt, svoris_iš_viso=round(qty*s.svoris_vnt, 2),
                              kaina_kg=s.kaina_kg, verte=round((qty*s.svoris_vnt/1000)*s.kaina_kg, 2), pastabos=data.get("pastabos", ""))
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
    return {"history": [{"data": h.data.strftime("%Y-%m-%d %H:%M"), "veiksmas": h.veiksmas, "storis": h.storis,
                          "matmenys": h.matmenys, "kiekis": h.kiekis, "svorisVnt": h.svoris_vnt,
                          "svorisIšViso": h.svoris_iš_viso, "kainaKg": h.kaina_kg, "verte": h.verte} for h in items]}

# ══════════════════════════════════════════════════
# ATASKAITA
# ══════════════════════════════════════════════════

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
            "pagalStori": [{"storis": s.storis, "vnt": s.liko_vnt, "kg": round(s.liko_kg, 1), "t": s.liko_t} for s in sorted(stock, key=lambda x: x.storis)]
        }
    }


# ══════════════════════════════════════════════════
# EL. PAŠTAS
# ══════════════════════════════════════════════════

@app.post("/api/email/siusti")
async def siusti_email(data: dict, db: Session = Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    smtp_host = os.getenv("SMTP_HOST", "vytis.serveriai.lt")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "info@metalcraft.lt")
    smtp_pass = os.getenv("SMTP_PASS", "")
    gavėjas   = os.getenv("EMAIL_TO", "gintaras@metalikalt.eu")
    
    if not smtp_pass:
        raise HTTPException(400, "SMTP slaptažodis nenurodytas")
    
    # Gauti lakštus
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti  = [l for l in items if l.surinkta and not l.perduota]
    perduoti  = [l for l in items if l.perduota]
    laukia    = [l for l in items if not l.surinkta]
    
    # HTML laiškas
    def rows(lst, color):
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else ''}</td></tr>" for l in lst)
    
    html = f"""
    <html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>
    <div style='background:#0969da;padding:16px;border-radius:8px 8px 0 0'>
      <h2 style='color:white;margin:0'>Sandėlio ataskaita – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</h2>
    </div>
    <div style='padding:16px;background:#f6f8fa;border-radius:0 0 8px 8px'>
      <p>Iš viso: <strong>{len(items)}</strong> | Surinkta: <strong style='color:#1a7f37'>{len(surinkti)}</strong> | Perduota: <strong style='color:#0969da'>{len(perduoti)}</strong> | Laukia: <strong style='color:#9a6700'>{len(laukia)}</strong></p>
      
      {'<h3 style="color:#1a7f37">✓ Surinkta</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Kodas</th><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Laikas</th></tr>' + rows(surinkti, '#1a7f37') + '</table>' if surinkti else ''}
      
      {'<h3 style="color:#0969da">→ Perduota</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Kodas</th><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Laikas</th></tr>' + rows(perduoti, '#0969da') + '</table>' if perduoti else ''}
      
      {'<h3 style="color:#9a6700">⏳ Laukia</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#fff8c5">Kodas</th><th style="text-align:left;padding:4px 8px;background:#fff8c5">Laikas</th></tr>' + rows(laukia, '#9a6700') + '</table>' if laukia else ''}
      
      <p style='color:#57606a;font-size:12px;margin-top:16px'>Išsiųsta iš Sandėlio sistemos – metalcraft.lt</p>
    </div>
    </body></html>
    """
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandėlio ataskaita {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        msg["From"]    = f"Metalcraft <{smtp_user}>"
        msg["To"]      = gavėjas
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, gavėjas, msg.as_string())
        
        return {"success": True, "message": f"Išsiųsta į {gavėjas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# ══════════════════════════════════════════════════
# PAGALBINĖS FUNKCIJOS
# ══════════════════════════════════════════════════

def _lk(l):
    return {"kodas": l.kodas, "registered": l.registruota.strftime("%Y-%m-%d %H:%M:%S") if l.registruota else "",
            "collected": l.surinkta, "collectedAt": l.surinkta_kada.strftime("%Y-%m-%d %H:%M:%S") if l.surinkta_kada else "",
            "delivered": l.perduota, "deliveredAt": l.perduota_kada.strftime("%Y-%m-%d %H:%M:%S") if l.perduota_kada else ""}

def _uzs(u):
    return {"id": u.uzs_id, "klientas": u.klientas, "aprasymas": u.aprasymas or "", "pastabos": u.pastabos or "",
            "statusas": u.statusas, "bendraSvoris": u.bendras_svoris, "detaliuSk": u.detaliu_sk,
            "sukurta": u.sukurta.strftime("%Y-%m-%d %H:%M:%S") if u.sukurta else ""}

def _det(d):
    return {"detId": d.det_id, "uzsakymoId": d.uzsakymo_id, "pavadinimas": d.pavadinimas,
            "storis": d.storis, "plotas": d.plotas, "kiekis": d.kiekis, "svoris": d.svoris,
            "konturas": d.konturas or "", "prideta": d.prideta.strftime("%Y-%m-%d %H:%M:%S") if d.prideta else ""}

def _stk(s):
    return {"id": s.stk_id, "storis": s.storis, "matmenys": s.matmenys, "svorisVnt": s.svoris_vnt,
            "gautaVnt": s.gauta_vnt, "sunaudotaVnt": s.sunaudota_vnt, "likoVnt": s.liko_vnt,
            "likoKg": s.liko_kg, "likoT": s.liko_t, "kainaKg": s.kaina_kg, "verte": s.verte,
            "prideta": s.prideta.strftime("%Y-%m-%d %H:%M:%S") if s.prideta else "", "pastabos": s.pastabos or ""}

def _recalc(uzs_id, db):
    dets = db.query(Detale).filter(Detale.uzsakymo_id == uzs_id).all()
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if u:
        u.bendras_svoris = round(sum(d.svoris for d in dets), 3)
        u.detaliu_sk = len(dets)
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os

from database import get_db, init_db, Lakstai, Etapas, Uzsakymas, Detale, Sandelis, SandelioIstorijia

app = FastAPI(title="Sandelio Sistema")
TANKIS = 8000

_CSS = """*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#f6f8fa;--s1:#ffffff;--s2:#f0f2f4;--s3:#e1e4e8;
  --bd:#d0d7de;--bd2:#afb8c1;
  --tx:#1f2328;--tx2:#57606a;--tx3:#848d97;
  --ac:#0969da;--ac2:#0550ae;--ac-bg:rgba(9,105,218,.08);
  --gn:#1a7f37;--gn-bg:rgba(26,127,55,.08);--gn-bd:rgba(26,127,55,.3);
  --yw:#9a6700;--yw-bg:rgba(154,103,0,.08);--yw-bd:rgba(154,103,0,.3);
  --rd:#cf222e;--rd-bg:rgba(207,34,46,.08);--rd-bd:rgba(207,34,46,.3);
  --pp:#6639ba;--pp-bg:rgba(102,57,186,.08);
  --or:#953800;
}
body{background:var(--bg);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;min-height:100vh;font-size:14px}

nav{background:var(--s1);border-bottom:1px solid var(--bd);padding:0 16px;height:52px;display:flex;align-items:center;gap:8px;position:sticky;top:0;z-index:50}
.brand{font-size:15px;font-weight:800;display:flex;align-items:center;gap:8px;flex-shrink:0}
.brand-ico{width:26px;height:26px;background:linear-gradient(135deg,#0969da,#6639ba);border-radius:6px}
.tabs{display:flex;height:100%;overflow-x:auto;flex:1;justify-content:center}
.tab{padding:0 13px;height:100%;display:flex;align-items:center;gap:4px;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;border:none;background:none;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}
.tab:hover{color:var(--tx)}.tab.active{color:var(--ac);border-bottom-color:var(--ac)}
.bdg{background:var(--ac);color:#fff;font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px}
.bdg.y{background:var(--yw)}.bdg.gray{background:var(--s3);color:var(--tx2)}.bdg.r{background:var(--rd)}
.nav-r{margin-left:auto;display:flex;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--bd2)}.dot.ok{background:var(--gn)}.dot.err{background:var(--rd)}

.view{display:none}.view.active{display:block}
.page-wrap{padding:16px;max-width:1000px;margin:0 auto}
.ph{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ph-t{font-size:18px;font-weight:800}.ph-s{font-size:11px;color:var(--tx2);margin-top:2px}

.btn{padding:7px 14px;border:none;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:12px;cursor:pointer;border-radius:6px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;white-space:nowrap}
.btn-p{background:var(--ac);color:#fff}.btn-p:hover{background:var(--ac2)}
.btn-s{background:transparent;border:1px solid var(--bd);color:var(--tx2)}.btn-s:hover{border-color:var(--tx);color:var(--tx)}
.btn-g{background:var(--gn-bg);border:1px solid var(--gn-bd);color:var(--gn)}.btn-g:hover{background:var(--gn);color:#fff}
.btn-d{background:transparent;border:1px solid transparent;color:var(--tx3)}.btn-d:hover{border-color:var(--rd-bd);color:var(--rd);background:var(--rd-bg)}
.btn-y{background:var(--yw-bg);border:1px solid var(--yw-bd);color:var(--yw)}.btn-y:hover{background:var(--yw);color:#fff}
.btn-sm{padding:4px 9px;font-size:11px}

.fl{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:4px}
input[type=text],input[type=number],input[type=date],input[type=email],textarea,select{width:100%;padding:7px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;outline:none;border-radius:6px;transition:border-color .15s;-webkit-appearance:none}
input:focus,textarea:focus,select:focus{border-color:var(--ac)}
textarea{resize:vertical;min-height:60px}
option{background:var(--s1)}

.card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;margin-bottom:12px}
.card-h{padding:12px 16px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.card-t{font-weight:700;font-size:14px}
.ct{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.ct::after{content:'';flex:1;height:1px;background:var(--bd)}

.mbg{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:24px;max-width:440px;width:100%;margin:auto}
.mh{font-size:17px;font-weight:800;margin-bottom:16px}
.mf{display:flex;flex-direction:column;gap:12px}
.mb{display:flex;gap:8px;justify-content:flex-end;margin-top:6px}

.toast{position:fixed;bottom:14px;right:14px;left:14px;max-width:340px;margin:0 auto;padding:11px 14px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;background:var(--s1);border:1px solid var(--bd);border-left:3px solid var(--gn);box-shadow:0 8px 24px rgba(0,0,0,.15);transform:translateY(70px);opacity:0;transition:all .25s;z-index:300;border-radius:6px}
.toast.w{border-left-color:var(--rd)}.toast.b{border-left-color:var(--ac)}.toast.p{border-left-color:var(--pp)}
.toast.show{transform:translateY(0);opacity:1}
.sp{display:inline-block;width:11px;height:11px;border:2px solid var(--bd2);border-top-color:var(--ac);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:4px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.empty-s{padding:40px;text-align:center;color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:12px}

/* LAKŠTAI */
.lk-wrap{display:grid;grid-template-columns:1fr 290px;min-height:calc(100vh - 52px)}
@media(max-width:680px){.lk-wrap{grid-template-columns:1fr}}
.lk-main{padding:16px;display:flex;flex-direction:column;gap:10px}
.lk-sb{border-left:1px solid var(--bd);background:var(--s1);display:flex;flex-direction:column}
.scan-f{position:relative}.scan-ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:16px;pointer-events:none;color:var(--tx3)}
.scan-inp{padding:11px 14px 11px 40px!important;font-size:17px!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important}
.scan-inp:focus{border-color:var(--ac)!important;box-shadow:0 0 0 3px var(--ac-bg)}
.hint{margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3)}
.steps{display:flex;gap:4px;margin-top:10px}
.step{flex:1;height:3px;background:var(--bd);border-radius:2px}
.s1{background:var(--yw)}.s2{background:var(--gn)}.s3{background:var(--ac)}
.step-lbl{display:flex;justify-content:space-between;margin-top:4px;font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.res{border:1px solid var(--bd);border-radius:8px;padding:12px 14px;animation:fadeUp .2s ease}
.res.rn{background:var(--yw-bg);border-color:var(--yw-bd)}.res.rc{background:var(--gn-bg);border-color:var(--gn-bd)}
.res.rd{background:var(--ac-bg);border-color:rgba(9,105,218,.3)}.res.re{background:var(--rd-bg);border-color:var(--rd-bd)}
.res.rp{background:var(--pp-bg);border-color:rgba(102,57,186,.3)}.res.ra{background:var(--gn-bg);border-color:var(--gn-bd)}
.rt{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}
.res.rn .rt{color:var(--yw)}.res.rc .rt{color:var(--gn)}.res.rd .rt{color:var(--ac)}.res.re .rt{color:var(--rd)}.res.rp .rt{color:var(--pp)}.res.ra .rt{color:var(--gn)}
.rc{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace}.rs{font-size:11px;color:var(--tx2);margin-top:2px}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
@media(max-width:480px){.stats-row{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.sn{font-size:22px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace}
.sn.a{color:var(--ac)}.sn.g{color:var(--gn)}.sn.b{color:var(--ac)}.sn.y{color:var(--yw)}
.sl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.prog-card{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px}
.pt{display:flex;justify-content:space-between;margin-bottom:6px;font-size:10px;color:var(--tx2);font-family:'JetBrains Mono',monospace}
.pct{color:var(--gn);font-weight:700}
.ptr{height:6px;background:var(--s2);border-radius:3px;overflow:hidden;position:relative}
.pfc{height:100%;background:var(--gn);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px}
.pfd{height:100%;background:var(--ac);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px;opacity:.4}
.stbar{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:12px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.stbar-lbl{font-weight:700;font-size:13px;white-space:nowrap}.stbar input{flex:1;min-width:130px}
.stbar-hint{font-size:9px;color:var(--tx3);width:100%;font-family:'JetBrains Mono',monospace}
.sbh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}
.sbt{font-weight:700;font-size:12px}.sbsr{position:relative;width:100%}
.sbsr input{padding:5px 10px 5px 26px;font-size:11px}.sbs-i{position:absolute;left:8px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--tx3);pointer-events:none}
.frow{padding:6px 14px;border-bottom:1px solid var(--bd);display:flex;gap:4px;flex-wrap:wrap}
.fb{padding:3px 8px;background:transparent;border:1px solid var(--bd);color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:9px;cursor:pointer;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;transition:all .15s}
.fb.active{background:var(--tx);color:var(--bg);border-color:var(--tx);font-weight:700}
.olist{flex:1;overflow-y:auto}
.oi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:6px;transition:background .1s}
.oi:hover{background:var(--s2)}
.od{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.oi.sc .od{background:var(--gn)}.oi.sdd .od{background:var(--ac)}
.oc{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ost{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700;flex-shrink:0}
.ost.s0{background:var(--yw-bg);color:var(--yw)}.ost.s1{background:var(--gn-bg);color:var(--gn)}.ost.s2{background:var(--ac-bg);color:var(--ac)}
.otm{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);flex-shrink:0}

/* SANDĖLIS */
.stk-sum{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin-bottom:14px}
.stk-s{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.stk-n{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.stk-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.stk-row{padding:10px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.stk-row:last-child{border-bottom:none}.stk-row:hover{background:var(--s2)}
@media(max-width:600px){.stk-row{grid-template-columns:1fr 1fr;gap:6px}}
.stk-thick{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:var(--ac)}
.stk-thick span{font-size:10px;color:var(--tx3)}
.stk-dims{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.stk-num{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700}
.stk-num.ok{color:var(--gn)}.stk-num.warn{color:var(--yw)}.stk-num.empty{color:var(--rd)}
.stk-sub{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.stk-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--or)}
.stk-acts{display:flex;gap:4px}
.stk-tot{padding:10px 16px;background:var(--s2);border-top:2px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.hist-row{padding:8px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:130px 60px 90px 60px 80px 80px;align-items:center;gap:8px;font-size:12px}
.hist-row:last-child{border-bottom:none}.hist-row:hover{background:var(--s2)}
.hist-act{font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700}
.hist-act.G{background:var(--gn-bg);color:var(--gn)}.hist-act.S{background:var(--rd-bg);color:var(--rd)}
.rec-prev{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--tx2)}

/* DXF */
.sumr{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin-bottom:14px}
.smc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.smn{font-size:20px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.sml{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.fbar{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.si{padding:5px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:11px;outline:none;border-radius:6px;min-width:150px}
.si:focus{border-color:var(--ac)}
.og{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.ocard{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.ocard:hover{border-color:var(--ac);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.oct{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.oid{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3)}
.stb{font-family:'JetBrains Mono',monospace;font-size:9px;padding:2px 7px;border-radius:4px;font-weight:700}
.stb.Naujas{background:var(--yw-bg);color:var(--yw);border:1px solid var(--yw-bd)}
.stb.Vykdomas{background:var(--ac-bg);color:var(--ac);border:1px solid rgba(9,105,218,.3)}
.stb.Baigtas{background:var(--gn-bg);color:var(--gn);border:1px solid var(--gn-bd)}
.ocli{font-size:14px;font-weight:700;margin-bottom:2px}.ocdesc{font-size:11px;color:var(--tx2);margin-bottom:10px}
.ocm{display:flex;gap:10px;flex-wrap:wrap}
.ocmi{font-family:'JetBrains Mono',monospace;font-size:10px}
.ocmi .v{color:var(--ac);font-weight:700}.ocmi .l{color:var(--tx3)}
.back{display:flex;align-items:center;gap:5px;color:var(--tx2);font-size:12px;cursor:pointer;margin-bottom:14px;font-family:'JetBrains Mono',monospace;transition:color .15s}
.back:hover{color:var(--ac)}
.oi-top{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px}
.oi-t{font-size:18px;font-weight:800}.oi-s{font-size:11px;color:var(--tx2);margin-top:2px}
.wbig{font-size:28px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac);line-height:1}
.wlbl{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px}
.stsel{padding:5px 10px;background:var(--s2);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:10px;outline:none;border-radius:6px;width:auto}
.dropz{border:2px dashed var(--bd);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:all .2s;position:relative}
.dropz:hover,.dropz.drag{border-color:var(--ac);background:var(--ac-bg)}
.dropz input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer}
.dz-t{font-size:12px;color:var(--tx2)}.dz-s{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.cvw{background:var(--s2);border:1px solid var(--bd);border-radius:6px;margin-top:10px;overflow:hidden}
canvas{display:block;max-width:100%;height:150px}
.pf{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:14px;margin-top:10px;animation:fadeUp .2s ease}
.wp{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;margin-bottom:10px}
.wv{font-size:19px;font-weight:700;color:var(--ac);font-family:'JetBrains Mono',monospace}
.wl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-top:1px;font-family:'JetBrains Mono',monospace}
.wa{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.fgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:480px){.fgrid{grid-template-columns:1fr}}
.msec{margin-top:12px;border-top:1px solid var(--bd);padding-top:12px}
.mlbl{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.svor-d{padding:7px 10px;background:var(--s1);border:1px solid var(--bd);border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ac)}
table{width:100%;border-collapse:collapse}
th{padding:7px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;text-align:left;border-bottom:1px solid var(--bd);background:var(--s2)}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}tr:hover td{background:var(--s2)}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px}
.num{color:var(--ac);font-weight:700;font-family:'JetBrains Mono',monospace}
.dttot{padding:10px 12px;background:var(--s2);border-top:2px solid var(--bd);display:flex;justify-content:flex-end;gap:14px;font-family:'JetBrains Mono',monospace;font-size:11px}
.tot{color:var(--ac);font-weight:700;font-size:13px}
.det-grp-hdr{padding:6px 12px;background:var(--s2);border-top:2px solid var(--bd);border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:10px}
.det-grp-t{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800;color:var(--ac)}
.det-grp-s{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.det-inp{padding:3px 6px!important;font-size:11px!important;width:auto!important}

/* ARCHYVAI */
.sc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:14px}
.scc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.scc:hover{border-color:var(--ac);transform:translateY(-1px)}.scc.open{border-color:var(--ac)}
.scn{font-size:13px;font-weight:700;margin-bottom:8px}
.scst{display:flex;gap:10px}
.scst .n{font-size:15px;font-weight:700;display:block;line-height:1;font-family:'JetBrains Mono',monospace}
.scst .n.g{color:var(--gn)}.scst .n.b{color:var(--ac)}.scst .n.r{color:var(--rd)}
.scst .l{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase}
.scp{margin-top:8px;height:3px;background:var(--s2);border-radius:2px;overflow:hidden}
.scpf{height:100%;background:var(--gn);border-radius:2px}
.adbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;margin-top:10px}
.adh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.adt{font-weight:700;font-size:13px}
.adlist{max-height:320px;overflow-y:auto}
.adi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:7px}
.addot{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.adi.sc .addot{background:var(--gn)}.adi.sdd .addot{background:var(--ac)}
.adcode{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1}
.adtag{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700}
.adtag.r{background:var(--yw-bg);color:var(--yw)}.adtag.c{background:var(--gn-bg);color:var(--gn)}.adtag.d{background:var(--ac-bg);color:var(--ac)}
.adtime{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx3)}

/* ATASKAITA */
.rep-s{margin-bottom:14px}
.rep-st{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--bd)}
.rep-sr{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}
.rep-sc{background:var(--s2);border-radius:6px;padding:10px 12px}
.rep-sc .n{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.rep-sc .l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}

/* PRINT */
@media print{body *{visibility:hidden!important}#printArea,#printArea *{visibility:visible!important}#printArea{position:fixed!important;left:0;top:0;width:100%}@page{margin:6mm;size:A4}}
.pmb{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:flex-start;justify-content:center;padding:16px;overflow-y:auto}
.pm{background:white;color:#000;max-width:210mm;width:100%;border-radius:8px;overflow:hidden;margin:auto}
.pbr{display:flex;gap:8px;padding:10px 14px;background:#f5f5f5;border-bottom:1px solid #ddd}
#printArea{background:white;color:#000;font-family:Arial,sans-serif;padding:10mm 8mm}
.pph{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}
.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666;font-family:monospace}
.ppbc{text-align:right;margin:2mm 0}
.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}
.ppi-l{font-size:7pt;color:#888;text-transform:uppercase;margin-bottom:.5mm}.ppi-v{font-size:10pt;font-weight:700}
.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}
.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}
.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}
.pptable tr:nth-child(even) td{background:#f9f9f9}
.ppsign{display:flex;gap:10mm;margin-top:5mm}
.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}
.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}
"""

_DXFJS = """
// DXF PARSERIS
const TANKIS = 8000;

function thickFromName(name){
  const m=name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)[ ]*mm/)||name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)/)||name.match(/([0-9]+(?:[.][0-9]+)?)[ ]*mm/);
  if(!m)return null;
  const v=parseFloat(m[1]);
  return STORIAI.includes(v)?v:null;
}

function qtyFromName(name){
  const m=name.match(/[_\x2D\x20]([0-9]+)[ ]*vnt/i)||name.match(/^([0-9]+)[ ]*vnt/i);
  if(!m)return null;
  const v=parseInt(m[1]);
  return v>0&&v<=9999?v:null;
}

function pDxf(txt){
  const lines=txt.split(/\r?\n/);
  const segs=[];
  let inE=false,curType=null,curV={},sf=1;

  for(let j=0;j<lines.length-1;j++){
    if(lines[j].trim()==='70'&&j>=2&&lines[j-2].trim()==='$INSUNITS'){
      const u=parseInt(lines[j+1]);if(u===1)sf=25.4;else if(u===6)sf=10;else if(u===5)sf=.1;
    }
  }

  const r4=v=>Math.round(v*10000)/10000;

  function saveSeg(t,v){
    if(t==='LINE'&&v._x1!==undefined&&v._y1!==undefined&&v._x2!==undefined&&v._y2!==undefined){
      segs.push({type:'L',x1:r4(v._x1*sf),y1:r4(v._y1*sf),x2:r4(v._x2*sf),y2:r4(v._y2*sf)});
    } else if(t==='CIRCLE'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf)});
    } else if((t==='LWPOLYLINE'||t==='POLYLINE')&&v._xs&&v._xs.length>=3){
      segs.push({type:'P',pts:v._xs.map((x,i)=>({x:r4(x*sf),y:r4((v._ys[i]||0)*sf)})),closed:((v[70]||0)&1)===1});
    } else if(t==='ARC'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf),arc:true});
    }
  }

  let i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i++;continue;}
    const val=(lines[i+1]||'').trim();
    if(code===2&&val==='ENTITIES'){inE=true;i+=2;continue;}
    if(code===0&&val==='ENDSEC'&&inE){saveSeg(curType,curV);break;}
    if(!inE){i+=2;continue;}
    if(code===0){saveSeg(curType,curV);curType=val;curV={};}
    else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._x1=n;}
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._y1=n;}
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11){curV._x2=n;}
        else if(code===21){curV._y2=n;}
        else if(code===70){curV[70]=parseInt(val)||0;}
        else{curV[code]=n;}
      }
    }
    i+=2;
  }

  let area=0;
  segs.filter(s=>s.type==='C'&&!s.arc).forEach(s=>area+=Math.PI*s.r*s.r);
  segs.filter(s=>s.type==='P').forEach(s=>{
    const pts=s.pts,n=pts.length;let a=0;
    for(let i=0;i<n;i++){const j=(i+1)%n;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}
    area+=Math.abs(a)/2;
  });
  const lineSegs=segs.filter(s=>s.type==='L');
  if(lineSegs.length){
    const adj=new Map();
    const key=p=>Math.round(p.x*100)/100+','+Math.round(p.y*100)/100;
    lineSegs.forEach(s=>{
      const p1={x:s.x1,y:s.y1},p2={x:s.x2,y:s.y2};
      const k1=key(p1),k2=key(p2);
      if(!adj.has(k1))adj.set(k1,{pt:p1,nb:[]});
      if(!adj.has(k2))adj.set(k2,{pt:p2,nb:[]});
      adj.get(k1).nb.push(k2);adj.get(k2).nb.push(k1);
    });
    const visitedE=new Set(),visitedP=new Set();
    adj.forEach((v,startK)=>{
      if(visitedP.has(startK))return;
      const path=[v.pt];let curK=startK;
      for(let iter=0;iter<adj.size*2;iter++){
        visitedP.add(curK);
        const nb=adj.get(curK).nb;let nextK=null;
        for(const nk of nb){
          const ek=[curK,nk].sort().join('|');
          if(!visitedE.has(ek)){visitedE.add(ek);nextK=nk;break;}
        }
        if(!nextK)break;
        path.push(adj.get(nextK).pt);curK=nextK;
      }
      if(path.length>=3){
        let a=0;const n=path.length;
        for(let i=0;i<n;i++){const j=(i+1)%n;a+=path[i].x*path[j].y-path[j].x*path[i].y;}
        area+=Math.abs(a)/2;
      }
    });
  }

  // Matmenys
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  segs.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  const dimW=isFinite(minX)?Math.round(maxX-minX):0;
  const dimH=isFinite(minY)?Math.round(maxY-minY):0;

  return{entities:segs,areaCm2:area/100,dimW,dimH};
}

function serializeContour(ents,dimW,dimH){
  try{
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    ents.forEach(s=>{
      if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
      else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
      else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
    });
    if(!isFinite(minX))return'';
    const W=maxX-minX||1,H=maxY-minY||1,sc=100/Math.max(W,H);
    const nx=x=>Math.round((x-minX)*sc*10)/10;
    const ny=y=>Math.round((maxY-y)*sc*10)/10;
    const paths=[];
    ents.forEach(s=>{
      if(s.type==='C'&&!s.arc)paths.push('C'+nx(s.cx)+','+ny(s.cy)+','+Math.round(s.r*sc*10)/10);
      else if(s.type==='P'){const step=Math.max(1,Math.floor(s.pts.length/50));const pts=[];for(let i=0;i<s.pts.length;i+=step)pts.push(nx(s.pts[i].x)+','+ny(s.pts[i].y));paths.push('L'+pts.join(' '));}
      else if(s.type==='L')paths.push('L'+nx(s.x1)+','+ny(s.y1)+' '+nx(s.x2)+','+ny(s.y2));
    });
    return('D:'+dimW+'x'+dimH+'|'+paths.join('|')).slice(0,2000);
  }catch(e){return'';}
}

function calcDims(d){
  if(d.konturas){
    const m=d.konturas.match(/D:([0-9]+)x([0-9]+)/);
    if(m)return m[1]+'×'+m[2]+'mm';
    try{
      let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
      d.konturas.split('|').forEach(p=>{
        if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);if(!isNaN(cx)){minX=Math.min(minX,cx-r);maxX=Math.max(maxX,cx+r);minY=Math.min(minY,cy-r);maxY=Math.max(maxY,cy+r);}}
        else if(p.startsWith('L')){p.slice(1).trim().split(' ').forEach(pt=>{const[x,y]=pt.split(',').map(Number);if(!isNaN(x)&&!isNaN(y)){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}});}
      });
      if(isFinite(minX)&&maxX>minX&&maxY>minY){
        const ratio=(maxX-minX)/(maxY-minY);const area=parseFloat(d.plotas)||0;
        if(area>0){const Hmm=Math.round(Math.sqrt(area*100/ratio));return Math.round(ratio*Hmm)+'×'+Hmm+'mm';}
      }
    }catch(e){}
  }
  const area=parseFloat(d.plotas)||0;
  if(!area)return'—';
  return'~'+Math.round(Math.sqrt(area*100))+'mm';
}

function drawPrev(ents){
  const w=document.getElementById('cvW'),c=document.getElementById('dxfCv');
  w.style.display='block';
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  ents.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  if(!isFinite(minX))return;
  const W=w.clientWidth||400,H=150;c.width=W;c.height=H;
  const ctx=c.getContext('2d');ctx.fillStyle='#f0f2f4';ctx.fillRect(0,0,W,H);
  const rX=maxX-minX||1,rY=maxY-minY||1,sc=Math.min((W-30)/rX,(H-30)/rY)*.9;
  const oX=(W-rX*sc)/2-minX*sc,oY=(H+rY*sc)/2+minY*sc;
  ctx.strokeStyle='#0969da';ctx.lineWidth=1.5;
  ents.forEach(s=>{
    ctx.beginPath();
    if(s.type==='C')ctx.arc(s.cx*sc+oX,oY-s.cy*sc,s.r*sc,0,Math.PI*2);
    else if(s.type==='P'&&s.pts.length){ctx.moveTo(s.pts[0].x*sc+oX,oY-s.pts[0].y*sc);for(let i=1;i<s.pts.length;i++)ctx.lineTo(s.pts[i].x*sc+oX,oY-s.pts[i].y*sc);if(s.closed)ctx.closePath();}
    else if(s.type==='L'){ctx.moveTo(s.x1*sc+oX,oY-s.y1*sc);ctx.lineTo(s.x2*sc+oX,oY-s.y2*sc);}
    ctx.stroke();
  });
}

function drawContourSvg(konturas,sizeMm=14){
  if(!konturas)return'';
  try{
    const parts=konturas.replace(/^D:[0-9]+x[0-9]+[|]/,'').split('|');
    let paths='';
    parts.forEach(p=>{
      if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);paths+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#000" stroke-width="2"/>`;}
      else if(p.startsWith('L')){const pts=p.slice(1).trim().split(' ');if(pts.length<2)return;const d='M'+pts[0]+' '+pts.slice(1).map(pt=>'L'+pt).join(' ');paths+=`<path d="${d}" fill="none" stroke="#000" stroke-width="2"/>`;}
    });
    const s=sizeMm+'mm';
    return`<svg viewBox="-5 -5 110 110" width="${s}" height="${s}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">${paths}</svg>`;
  }catch(e){return'';}
}

"""

_MAINJS = """
// SANDĖLIO SISTEMA – main.js

let lkOrders=[],lkF='all',lkLC=null,lkLT=0;
let dxfOrders=[],dxfF='all',dxfDets=[],curOrd=null,curArea=0,curContour='';
let stock=[],history=[],stages=[],archOpen=null;
let pendingSt='',curStockId=null;
let settings={defaultPrice:0,lowAlert:2};

// GARSAS
let actx=null;
function ga(){if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();return actx;}
function beep(t){try{const c=ga();if(c.state==='suspended')c.resume();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;if(t==='new'){o.frequency.value=880;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.2);o.start(n);o.stop(n+.2);}else if(t==='col'){o.frequency.setValueAtTime(660,n);o.frequency.setValueAtTime(880,n+.12);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.3);o.start(n);o.stop(n+.3);}else if(t==='del'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(660,n+.1);o.frequency.setValueAtTime(880,n+.2);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='err'){o.type='sawtooth';o.frequency.value=220;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='dup'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(220,n+.15);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.35);o.start(n);o.stop(n+.35);}}catch(e){}}

// API
async function api(method,url,data){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(data)opts.body=JSON.stringify(data);
  const r=await fetch(url,opts);
  if(!r.ok)throw new Error(r.statusText);
  return r.json();
}

// INIT
window.onload=()=>{
  loadAll();
  const lt=localStorage.getItem('lastThick');
  if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}
  setPeriod(30);
  const dz=document.getElementById('dropZ');
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
};
document.addEventListener('click',e=>{if(actx&&actx.state==='suspended')actx.resume();if(document.getElementById('view-lk').classList.contains('active')&&!e.target.closest('input,button,select'))focusScan();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mbg').forEach(m=>m.style.display='none');});

async function loadAll(){await loadLk();await loadDxfOrds();await loadStock();await loadHist();await loadStages();}

// NAVIGACIJA
function SW(v){
  document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById('view-'+v).classList.add('active');
  const t=document.getElementById('tab-'+v);if(t)t.classList.add('active');
  if(v==='lk')focusScan();
  if(v==='dv'){const lt=localStorage.getItem('lastThick');if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}}
}
function CM(id){document.getElementById(id).style.display='none';}
function focusScan(){try{document.getElementById('scanInp').focus();}catch(e){}}
function toast(msg,w=false,t=''){const el=document.getElementById('toast');el.textContent=msg;el.className='toast '+(w?'w':t)+' show';clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),3000);}

// ════ LAKŠTAI ════
const scanInp=document.getElementById('scanInp');
scanInp.addEventListener('keydown',async e=>{if(e.key==='Enter'){const c=scanInp.value.trim();if(c){scanInp.value='';await handleScan(c);}}});

async function handleScan(kodas){
  const now=Date.now();
  if(kodas===lkLC&&now-lkLT<3000){lkRes('rp','DUBLIKATAS',kodas,'Tas pats kodas du kartus!');beep('dup');toast('Dublikatas: '+kodas,false,'p');lkLC=null;return;}
  lkLC=kodas;lkLT=now;
  const local=lkOrders.find(o=>o.kodas===kodas);
  if(local){
    if(local.delivered){lkRes('ra','JAU PERDUOTA',kodas,'Perduota: '+local.deliveredAt);beep('err');return;}
    if(local.collected){
      lkRes('rd','PERDUOTA',kodas,'3× — siunčiama...');beep('del');
      local.delivered=true;local.deliveredAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Perduota: '+kodas,false,'b');else{local.delivered=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }else{
      lkRes('rc','SURINKTA',kodas,'2× — siunčiama...');beep('col');
      local.collected=true;local.collectedAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Surinkta: '+kodas);else{local.collected=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }
    return;
  }
  lkRes('rn','NAUJAS',kodas,'1× — siunčiama...');beep('new');
  const newOrd={kodas,registered:nowS(),collected:false,collectedAt:'',delivered:false,deliveredAt:''};
  lkOrders.push(newOrd);lkStats();rlkList();
  api('POST','/api/lakstai/register',{kodas}).then(r=>{
    if(r.success)toast('Užregistruota: '+kodas);
    else if(r.alreadyExists){lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkAddL(r.order);lkStats();rlkList();handleScan(kodas);}
    else{lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkRes('re','KLAIDA',kodas,'Nepavyko');beep('err');lkStats();rlkList();}
  });
}

function lkRes(c,t,kodas,s){
  const b=document.getElementById('lkRes');
  b.className='res '+c;b.style.display='block';
  document.getElementById('lkRt').textContent=t;
  document.getElementById('lkRc').textContent=kodas;
  document.getElementById('lkRs').textContent=s;
}

async function loadLk(){
  try{const r=await api('GET','/api/lakstai');lkOrders=r.orders||[];lkStats();rlkList();document.getElementById('connDot').className='dot ok';}
  catch(e){document.getElementById('connDot').className='dot err';toast('Nepavyko prisijungti',true);}
}
function lkAddL(o){const i=lkOrders.findIndex(x=>x.kodas===o.kodas);if(i>=0)lkOrders[i]=o;else lkOrders.push(o);}
function lkStats(){
  const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length,p=lkOrders.filter(o=>!o.collected).length;
  const pc=t>0?Math.round(c/t*100):0,pd=t>0?Math.round(d/t*100):0;
  document.getElementById('lkT').textContent=t;document.getElementById('lkC').textContent=c;
  document.getElementById('lkD').textContent=d;document.getElementById('lkP').textContent=p;
  document.getElementById('lkPct').textContent=pc+'%';
  document.getElementById('lkPfc').style.width=pc+'%';document.getElementById('lkPfd').style.width=pd+'%';
  document.getElementById('lkBdg').textContent=p||t;
}
function lkFlt(f,b){lkF=f;document.querySelectorAll('.frow .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rlkList();}
function sortLk(l){return[...l].sort((a,b)=>{const n=s=>parseInt((s.match(/[0-9]+/)||[0])[0]);return n(a.kodas)-n(b.kodas);});}
function rlkList(){
  const el=document.getElementById('lkList'),q=(document.getElementById('lkSrch').value||'').toLowerCase();
  let l=sortLk(lkOrders);
  if(lkF==='p')l=l.filter(o=>!o.collected);if(lkF==='c')l=l.filter(o=>o.collected&&!o.delivered);if(lkF==='d')l=l.filter(o=>o.delivered);
  if(q)l=l.filter(o=>o.kodas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(lkOrders.length===0?'Nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>{
    const sc=o.delivered?'sdd':o.collected?'sc':'';
    const sl=o.delivered?'s2':o.collected?'s1':'s0';
    const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
    const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);
    return`<div class="oi ${sc}"><div class="od"></div><div class="oc">${o.kodas}</div><span class="ost ${sl}">${st}</span><div class="otm">${tm}</div><button class="btn btn-d btn-sm" onclick="lkDel('${o.kodas}')">✕</button></div>`;
  }).join('');
}
async function lkDel(k){if(!confirm('Ištrinti "'+k+'"?'))return;await api('DELETE','/api/lakstai/'+k);lkOrders=lkOrders.filter(o=>o.kodas!==k);lkStats();rlkList();toast('Ištrinta');}
function askStage(){
  const n=document.getElementById('stageInp').value.trim();
  if(!n){toast('Įvesk etapo pavadinimą!',true);return;}
  if(!lkOrders.length){toast('Nėra užsakymų',true);return;}
  pendingSt=n;const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length;
  document.getElementById('stMn').textContent='Etapas: "'+n+'"';
  document.getElementById('stMs').innerHTML='Iš viso: <strong>'+t+'</strong><br>Surinkta: <strong>'+c+'</strong><br>Perduota: <strong>'+d+'</strong><br>Laukia: <strong>'+(t-c)+'</strong>';
  document.getElementById('stModal').style.display='flex';
}
async function confirmStage(){
  CM('stModal');
  const r=await api('POST','/api/lakstai/archive',{pavadinimas:pendingSt});
  if(r.success){lkOrders=[];document.getElementById('stageInp').value='';lkStats();rlkList();await loadStages();beep('del');toast('Archyvuota: "'+r.archiveName+'"');lkRes('ra','ARCHYVUOTA',r.archiveName,r.collected+'/'+r.total+' surinkta');}
  else toast(r.message||'Klaida',true);
  focusScan();
}

// ════ SANDĖLIS ════
async function loadStock(){try{const r=await api('GET','/api/sandelis');stock=r.stock||[];rStock();document.getElementById('stkBdg').textContent=stock.length;}catch(e){}}
async function loadHist(){try{const r=await api('GET','/api/sandelis/istorija');history=r.history||[];rHist();}catch(e){}}

function rStock(){
  const el=document.getElementById('stkTbl'),su=document.getElementById('stkSum');
  if(!stock.length){el.innerHTML='<div class="empty-s">Sandėlis tuščias</div>';su.innerHTML='';return;}
  const totVnt=stock.reduce((s,r)=>s+r.likoVnt,0);
  const totKg=stock.reduce((s,r)=>s+r.likoKg,0);
  const totT=Math.round(totKg/10)/100;
  const totVal=stock.reduce((s,r)=>s+r.verte,0);
  const byT={};stock.forEach(r=>{if(!byT[r.storis])byT[r.storis]={vnt:0,kg:0};byT[r.storis].vnt+=r.likoVnt;byT[r.storis].kg+=r.likoKg;});
  su.innerHTML=`<div class="stk-s"><div class="stk-n">${totVnt}</div><div class="stk-l">Viso vnt.</div></div><div class="stk-s"><div class="stk-n">${totKg.toFixed(1)}</div><div class="stk-l">Viso kg</div></div><div class="stk-s"><div class="stk-n" style="color:var(--gn)">${totT}</div><div class="stk-l">Tonos</div></div><div class="stk-s"><div class="stk-n" style="color:var(--or)">${totVal.toFixed(2)}</div><div class="stk-l">Vertė €</div></div>`+
    Object.entries(byT).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).map(([t,v])=>`<div class="stk-s"><div class="stk-n" style="font-size:15px">${v.vnt}vnt</div><div class="stk-l">${t}mm · ${(Math.round(v.kg/10)/100).toFixed(2)}t</div></div>`).join('');
  const sorted=[...stock].sort((a,b)=>a.storis-b.storis);
  el.innerHTML=sorted.map(r=>{
    const nc=r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return`<div class="stk-row"><div><div class="stk-thick">${r.storis}<span>mm</span></div></div><div><div class="stk-dims">${r.matmenys}mm</div><div class="stk-sub">${r.pastabos||''}</div></div><div><div class="stk-num ${nc}">${r.likoVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:13px;color:var(--tx2)">${r.likoKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${r.likoT.toFixed(3)}</div><div class="stk-sub">t</div></div><div><div class="stk-val">${r.verte.toFixed(2)}€</div><div class="stk-sub">${r.kainaKg>0?r.kainaKg+'€/kg':''}</div></div><div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse('${r.id}','${r.storis}mm ${r.matmenys}',${r.likoVnt})">−</button><button class="btn btn-d btn-sm" onclick="delStk('${r.id}')">✕</button></div></div>`;
  }).join('')+`<div class="stk-tot"><div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);font-weight:700">VISO</div><div></div><div><div class="stk-num" style="font-size:13px;color:var(--ac)">${totVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${totKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">${totT}</div><div class="stk-sub">t</div></div><div><div class="stk-val" style="font-size:13px;font-weight:800">${totVal.toFixed(2)}€</div></div><div></div></div>`;
}

function rHist(){
  const el=document.getElementById('histTbl');
  if(!history.length){el.innerHTML='<div class="empty-s">Dar nėra istorijos</div>';return;}
  el.innerHTML=`<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>${history.slice(0,50).map(h=>`<tr><td class="mono" style="font-size:10px;color:var(--tx3)">${h.data}</td><td><span class="hist-act ${h.veiksmas[0]}">${h.veiksmas}</span></td><td class="mono">${h.storis}mm</td><td class="mono" style="color:var(--tx2)">${h.matmenys}</td><td class="mono">${h.kiekis}vnt.</td><td class="num">${h.svorisIšViso.toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

function showRecv(){
  if(settings.defaultPrice)document.getElementById('recP').value=settings.defaultPrice;
  document.getElementById('recvModal').style.display='flex';
}
function rcRecv(){
  const t=parseFloat(document.getElementById('recThk').value)||0,w=parseFloat(document.getElementById('recW').value)||0,l=parseFloat(document.getElementById('recL').value)||0,q=parseInt(document.getElementById('recQ').value)||1,p=parseFloat(document.getElementById('recP').value)||0;
  if(!w||!l){document.getElementById('recPrev').textContent='Įvesk matmenis...';return;}
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100,totT=Math.round(tot/10)/100,val=p>0?Math.round(tot*p*100)/100:0;
  document.getElementById('recPrev').innerHTML=`1 lakštas: <strong style="color:var(--ac)">${we}kg</strong> · ${q}vnt.: <strong style="color:var(--gn)">${tot}kg = ${totT}t</strong>${val>0?' · <strong style="color:var(--or)">'+val+'€</strong>':''}`;
}
async function doRecv(){
  const t=document.getElementById('recThk').value,w=document.getElementById('recW').value,l=document.getElementById('recL').value,q=document.getElementById('recQ').value,p=document.getElementById('recP').value,n=document.getElementById('recN').value;
  if(!w||!l){toast('Įvesk matmenis!',true);return;}
  const r=await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if(r.success){CM('recvModal');await loadStock();await loadHist();toast('Pridėta: '+q+'vnt. × '+t+'mm ('+r.likoT+'t)');}
}
function showUse(id,label,rem){curStockId=id;document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';document.getElementById('useQ').value=1;document.getElementById('useNote').value='';document.getElementById('useModal').style.display='flex';}
async function doUse(){
  const q=parseInt(document.getElementById('useQ').value)||1,n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if(r.success){CM('useModal');await loadStock();await loadHist();toast('Sunaudota: '+q+'vnt. Liko: '+r.likoVnt+'vnt.');}
  else toast('Klaida',true);
}
async function delStk(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/sandelis/'+id);await loadStock();toast('Ištrinta');}
function showSett(){document.getElementById('settP').value=settings.defaultPrice||'';document.getElementById('settL').value=settings.lowAlert||2;document.getElementById('settModal').style.display='flex';}
function saveSett(){settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;settings.lowAlert=parseInt(document.getElementById('settL').value)||2;CM('settModal');localStorage.setItem('sandSettings',JSON.stringify(settings));toast('Nustatymai išsaugoti');}

// ════ ARCHYVAI ════
async function loadStages(){try{const r=await api('GET','/api/etapai');stages=r.stages||[];document.getElementById('archBdg').textContent=stages.length;rStages();}catch(e){}}
function rStages(){
  const el=document.getElementById('stageCards');
  if(!stages.length){el.innerHTML='<div class="empty-s">Dar nėra archyvų</div>';return;}
  el.innerHTML=stages.map(s=>{
    const t=s.total||0,c=s.collected||0,d=s.delivered||0,p=s.pending||(t-c),pct=t>0?Math.round(c/t*100):0;
    return`<div class="scc ${archOpen===s.name?'open':''}" onclick="toggleArch('${s.name.replace(/'/g,"\\'")}')"><div class="scn">${s.name}</div><div class="scst"><div><span class="n">${t}</span><span class="l">Viso</span></div><div><span class="n g">${c}</span><span class="l">Surinkta</span></div><div><span class="n b">${d}</span><span class="l">Perduota</span></div><div><span class="n ${p>0?'r':'g'}">${p}</span><span class="l">Liko</span></div></div><div class="scp"><div class="scpf" style="width:${pct}%"></div></div></div>`;
  }).join('');
}
async function toggleArch(name){
  if(archOpen===name){archOpen=null;closeAd();rStages();return;}
  archOpen=name;rStages();
  document.getElementById('adTitle').textContent=name;
  document.getElementById('adList').innerHTML='<div class="empty-s"><span class="sp"></span> Kraunama...</div>';
  document.getElementById('adBox').style.display='block';
  try{
    const r=await api('GET','/api/etapai/'+encodeURIComponent(name));
    const items=sortLk(r.orders||[]);
    if(!items.length){document.getElementById('adList').innerHTML='<div class="empty-s">Tuščias</div>';return;}
    document.getElementById('adList').innerHTML=items.map(o=>{
      const sc=o.delivered?'sdd':o.collected?'sc':'';const tc=o.delivered?'d':o.collected?'c':'r';const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
      const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(0,16);
      return`<div class="adi ${sc}"><div class="addot"></div><div class="adcode">${o.kodas}</div><span class="adtag ${tc}">${st}</span><div class="adtime">${tm}</div></div>`;
    }).join('');
  }catch(e){}
}
function closeAd(){document.getElementById('adBox').style.display='none';archOpen=null;rStages();}

// ════ DXF ════
async function loadDxfOrds(){try{const r=await api('GET','/api/uzsakymai');dxfOrders=r.orders||[];dxfSum();rOrds();document.getElementById('dxfBdg').textContent=dxfOrders.length;}catch(e){}}
function dxfSum(){
  const t=dxfOrders.length,n=dxfOrders.filter(o=>o.statusas==='Naujas').length,a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length,d=dxfOrders.filter(o=>o.statusas==='Baigtas').length,w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML=`<div class="smc"><div class="smn a">${t}</div><div class="sml">Iš viso</div></div><div class="smc"><div class="smn" style="color:var(--yw)">${n}</div><div class="sml">Nauji</div></div><div class="smc"><div class="smn a">${a}</div><div class="sml">Vykdomi</div></div><div class="smc"><div class="smn" style="color:var(--gn)">${d}</div><div class="sml">Baigti</div></div><div class="smc"><div class="smn a">${w.toFixed(2)}</div><div class="sml">Svoris kg</div></div>`;
}
function dxfFlt(f,b){dxfF=f;document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rOrds();}
function rOrds(){
  const el=document.getElementById('ordsGrid'),q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all')l=l.filter(o=>o.statusas===dxfF);if(q)l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>`<div class="ocard" onclick="openOrd('${o.id}')"><div class="oct"><div class="oid">${o.id}</div><div style="display:flex;gap:4px"><span class="stb ${o.statusas}">${o.statusas}</span><button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd('${o.id}','${o.klientas.replace(/'/g,"\\'")}')">✕</button></div></div><div class="ocli">${o.klientas}</div><div class="ocdesc">${o.aprasymas||'—'}</div><div class="ocm"><div class="ocmi"><span class="v">${o.bendraSvoris.toFixed(3)}</span><span class="l"> kg</span></div><div class="ocmi"><span class="v">${o.detaliuSk}</span><span class="l"> det.</span></div><div class="ocmi"><span class="l">${(o.sukurta||'').slice(0,10)}</span></div></div></div>`).join('');
}
async function quickDelOrd(id,klientas){if(!confirm('Ištrinti "'+klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+id);dxfOrders=dxfOrders.filter(o=>o.id!==id);dxfSum();rOrds();toast('Ištrinta');}
function showNewOrd(){document.getElementById('noModal').style.display='flex';setTimeout(()=>document.getElementById('noC').focus(),100);}
async function createOrd(){
  const c=document.getElementById('noC').value.trim();if(!c){toast('Įvesk klientą!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id){
  const o=dxfOrders.find(x=>x.id===id);if(!o)return;curOrd=o;
  document.getElementById('dvId').textContent=o.id;document.getElementById('dvCli').textContent=o.klientas;document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' · '+o.pastabos:'');
  SW('dv');await loadDets();
}
function back2Ords(){SW('dxf');loadDxfOrds();curArea=0;curContour='';document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';}
async function chSt(){if(!curOrd)return;await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value});toast('Statusas atnaujintas');}
async function delOrd(){if(!curOrd)return;if(!confirm('Ištrinti "'+curOrd.klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+curOrd.id);toast('Ištrinta');back2Ords();}
async function loadDets(){
  if(!curOrd)return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[];rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
}

function rDets(){
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nėra detalių</div>';return;}
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const groups={};
  dxfDets.forEach(d=>{const t=String(d.storis);if(!groups[t])groups[t]={t,dets:[],w:0,q:0};groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;});
  let rows='';let idx=0;
  Object.values(groups).forEach(g=>{
    rows+=`<tr class="det-grp-hdr"><td colspan="2"></td><td colspan="2"><span class="det-grp-t">${g.t}mm</span></td><td><span class="det-grp-s">${g.dets.length}det.</span></td><td><span class="det-grp-s">${g.q}vnt.</span></td><td><span class="det-grp-s" style="color:var(--ac)">${g.w.toFixed(3)}kg</span></td><td></td></tr>`;
    g.dets.forEach(d=>{
      idx++;
      rows+=`<tr><td class="mono" style="color:var(--tx3);font-size:10px">${idx}</td><td style="font-weight:600">${d.pavadinimas}</td><td><select class="det-inp" onchange="updDet('${d.detId}','storis',this.value)">${STORIAI.map(t=>`<option value="${t}"${d.storis===t?' selected':''}>${t}mm</option>`).join('')}</select></td><td class="mono" style="font-size:11px;color:var(--tx2)">${calcDims(d)}</td><td><input type="number" class="det-inp" value="${d.kiekis}" min="1" style="width:50px" onchange="updDet('${d.detId}','kiekis',this.value)"></td><td><input type="number" class="det-inp num" value="${d.svoris.toFixed(3)}" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-${d.detId}" onchange="updDetW('${d.detId}',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td><td><button class="btn btn-d btn-sm" onclick="delDet('${d.detId}')">✕</button></td></tr>`;
    });
  });
  w.innerHTML=`<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">${tq}vnt.</strong></span><span>Bendras svoris: <span class="tot">${tw.toFixed(3)}kg</span></span></div>`;
}

async function updDet(detId,field,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  if(field==='storis')d.storis=parseFloat(value);else if(field==='kiekis')d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  const wEl=document.getElementById('w-'+detId);if(wEl)wEl.value=d.svoris.toFixed(3);
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas});
}
async function updDetW(detId,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
function _updateTotals(){
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  document.getElementById('dvWt').textContent=tw.toFixed(3);
}
async function delDet(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/detales/'+id);dxfDets=dxfDets.filter(d=>d.detId!==id);rDets();_updateTotals();toast('Ištrinta');}

// DXF ĮKĖLIMAS
function handleDxf(e){if(e.target.files.length)handleMultiDxf(Array.from(e.target.files));}
function handleFolder(e){
  if(!e.target.files.length)return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failų!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' → '+ft+'mm, '+files.length+' failų',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files){
  if(!curOrd){toast('Pirma atidaryk užsakymą!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Įkeliama '+files.length+' failų...';
  for(const file of files){
    await new Promise(resolve=>{
      const r=new FileReader();
      r.onload=async e2=>{
        try{
          const res=pDxf(e2.target.result);
          if(res.areaCm2<=0){fail++;resolve();return;}
          const at=thickFromName(file.name)||defThick;
          const aq=qtyFromName(file.name)||defQty;
          const ctour=serializeContour(res.entities,res.dimW,res.dimH);
          const resp=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:file.name.replace(/[.]dxf$/i,''),storis:at,plotas:res.areaCm2,kiekis:aq,konturas:ctour});
          if(resp.success)ok++;else fail++;
        }catch(ex){fail++;}
        resolve();
      };
      r.readAsText(file);
    });
  }
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Tempk DXF failus čia arba spusk';
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?`Įkelta: ${ok}, nepavyko: ${fail}`:`Sėkmingai įkeltos ${ok} detalės!`);
}
function procDxf(file){
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2;
      curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name);const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq)document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
      toast('DXF: '+res.areaCm2.toFixed(2)+'cm²'+(at?' · '+at+'mm':''));
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm² · '+t+'mm × '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd)return;if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd)return;const a=parseFloat(document.getElementById('mArea').value)||0;if(a<=0){toast('Įvesk plotą!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:''});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}

// ATASKAITA
function setPeriod(days){
  const to=new Date(),from=new Date();
  if(days===0)from.setDate(1);else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep(){
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpį!',true);return;}
  const r=await api('GET',`/api/ataskaita?nuo=${from}&iki=${to}`);
  const el=document.getElementById('repOut');
  el.style.display='block';
  el.innerHTML=`<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: ${from} — ${to}</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.lakstai.gauta}</div><div class="l">Lakštų gauta</div></div><div class="rep-sc"><div class="n">${r.lakstai.surinkta}</div><div class="l">Surinkta</div></div><div class="rep-sc"><div class="n">${r.lakstai.perduota}</div><div class="l">Perduota</div></div><div class="rep-sc"><div class="n">${r.dxf.sk}</div><div class="l">DXF užsakymų</div></div><div class="rep-sc"><div class="n">${r.dxf.svoris.toFixed(1)}</div><div class="l">DXF svoris kg</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio judėjimas</div><div class="rep-sr"><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.sandelis.gautaKg.toFixed(1)}</div><div class="l">Gauta kg</div></div><div class="rep-sc"><div class="n" style="color:var(--rd)">${r.sandelis.sunaudotaKg.toFixed(1)}</div><div class="l">Sunaudota kg</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.gautaVerte.toFixed(2)}</div><div class="l">Gauta vertė €</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.sunaudotaVerte.toFixed(2)}</div><div class="l">Sunaudota €</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio likutis dabar</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.likutis.vnt}</div><div class="l">Viso vnt.</div></div><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.likutis.t}</div><div class="l">Tonos</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.likutis.verte.toFixed(2)}</div><div class="l">Vertė €</div></div></div></div></div>`;
}

// SPAUSDINIMAS
function printOrd(){
  if(!curOrd)return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return`<tr><td style="font-weight:700;color:#1e3a5f">${t}mm</td><td style="text-align:center">${dets.length}</td><td style="text-align:center">${gq}</td><td style="text-align:right;font-weight:700">${gw.toFixed(3)}</td></tr>`;}).join('');
  let html=`<div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div><div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">${totW.toFixed(3)} kg</div></div><div><div class="ppi-l">Viso detalių</div><div class="ppi-v">${totQ} vnt.</div></div><div><div class="ppi-l">Storių sk.</div><div class="ppi-v">${groups.size} storiai</div></div></div><table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>${sumRows}<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">${sorted.length}</td><td style="text-align:center">${totQ}</td><td style="text-align:right">${totW.toFixed(3)}</td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>Išspausdinta: ${now}</span><span>${curOrd.id}</span></div>`;
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>`<tr><td>${i+1}</td><td><strong>${d.pavadinimas}</strong></td><td style="text-align:center">${calcDims(d)}</td><td style="text-align:center">${d.kiekis}</td><td style="text-align:right"><strong>${d.svoris.toFixed(3)}</strong></td><td style="text-align:center;vertical-align:middle">${drawContourSvg(d.konturas,12)}</td></tr>`).join('');
    html+=`<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">${thick}mm</div></div><div class="ppinfo"><div><div class="ppi-l">Svoris (${thick}mm)</div><div class="ppi-v">${gw.toFixed(3)} kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">${gq}vnt. (${dets.length}poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">${now}</div></div></div><table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>${rows}<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">${gq}vnt.</td><td style="text-align:right">${gw.toFixed(3)}kg</td><td></td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>${thick}mm · ${dets.length}poz. · ${gq}vnt. · ${gw.toFixed(3)}kg</span><span>${curOrd.id}</span></div></div>`;
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}

function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  const s='<style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style>';
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'+s+'</head><body>'+c+'</body>');
  w.document.close();
  setTimeout(function(){w.print();},500);
}

function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}

// Nustatymų įkėlimas
const savedSett=localStorage.getItem('sandSettings');
if(savedSett)try{settings=JSON.parse(savedSett);}catch(e){}

async function siustiEmail(){
  const btn=document.getElementById('emailBtn');
  btn.textContent='Siunčiama...';btn.disabled=true;
  try{
    const r=await fetch('/api/email/siusti',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const d=await r.json();
    if(d.success){alert('✓ '+d.message);}
    else{alert('Klaida: '+(d.detail||d.message));}
  }catch(e){alert('Klaida: '+e.message);}
  btn.textContent='✉ Siųsti ataskaitą';btn.disabled=false;
}

"""

_HTML = """<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0969da">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sandelis">
<link rel="manifest" href="/manifest.json">
<title>Sandelio Sistema</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
<nav>
  <div class="brand"><div class="brand-ico"></div>SANDELIS</div>
  <div class="tabs">
    <button class="tab active" onclick="SW('lk')" id="tab-lk">Lakstai <span class="bdg" id="lkBdg">0</span></button>
    <button class="tab" onclick="SW('stk')" id="tab-stk">Sandelis <span class="bdg y" id="stkBdg">0</span></button>
    <button class="tab" onclick="SW('dxf')" id="tab-dxf">DXF <span class="bdg gray" id="dxfBdg">0</span></button>
    <button class="tab" onclick="SW('arch')" id="tab-arch">Archyvai <span class="bdg gray" id="archBdg">0</span></button>
    <button class="tab" onclick="SW('rep')" id="tab-rep">Ataskaita</button>
  </div>
  <div class="nav-r"><div class="dot ok" id="connDot"></div></div>
</nav>

<div class="view active" id="view-lk">
  <div class="lk-wrap">
    <div class="lk-main">
      <div class="card">
        <div class="ct">Skanavimas</div>
        <div class="scan-f"><span class="scan-ico">▦</span><input class="scan-inp" id="scanInp" placeholder="Skanuok arba ivesk koda..." autocomplete="off" spellcheck="false"></div>
        <div class="hint" id="scanHint">Laukiama skanavimo...</div>
        <div class="steps"><div class="step s1"></div><div class="step s2"></div><div class="step s3"></div></div>
        <div class="step-lbl"><span>1x Registruota</span><span>2x Surinkta</span><span>3x Perduota</span></div>
      </div>
      <div class="res" id="lkRes" style="display:none"><div class="rt" id="lkRt"></div><div class="rc" id="lkRc"></div><div class="rs" id="lkRs"></div></div>
      <div class="stats-row">
        <div class="stat"><div class="sn a" id="lkT">0</div><div class="sl">Is viso</div></div>
        <div class="stat"><div class="sn g" id="lkC">0</div><div class="sl">Surinkta</div></div>
        <div class="stat"><div class="sn b" id="lkD">0</div><div class="sl">Perduota</div></div>
        <div class="stat"><div class="sn y" id="lkP">0</div><div class="sl">Laukia</div></div>
      </div>
      <div class="prog-card">
        <div class="pt"><span>Progresas</span><span class="pct" id="lkPct">0%</span></div>
        <div class="ptr"><div class="pfd" id="lkPfd" style="width:0%"></div><div class="pfc" id="lkPfc" style="width:0%"></div></div>
      </div>
      <div class="stbar">
        <span class="stbar-lbl">Naujas etapas:</span>
        <input type="text" id="stageInp" placeholder="pvz. Etapas 221">
        <button class="btn btn-p btn-sm" onclick="askStage()">Archyvuoti</button>
      </div>
    </div>
    <div class="lk-sb">
      <div class="sbh">
        <div class="sbt">Uzsakymai</div>
        <button class="btn btn-g btn-sm" onclick="loadLk()">&#x21BB;</button>
        <button id="pdfBtn" class="btn btn-s btn-sm" onclick="genPdfReport()">&#x22C6; Atsisiusti PDF</button>
        <div class="sbsr"><span class="sbs-i">&#x2315;</span><input type="text" id="lkSrch" placeholder="Ieskoti..." oninput="rlkList()"></div>
      </div>
      <div class="frow">
        <button class="fb active" onclick="lkFlt('all',this)">Visi</button>
        <button class="fb" onclick="lkFlt('p',this)">Laukia</button>
        <button class="fb" onclick="lkFlt('c',this)">Surinkti</button>
        <button class="fb" onclick="lkFlt('d',this)">Perduoti</button>
      </div>
      <div class="olist" id="lkList"><div class="empty-s">Jungiamasi...</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-stk">
  <div class="page-wrap">
    <div class="ph"><div><div class="ph-t">Metalo sandelis</div><div class="ph-s">Lakstu likuciai pagal stori</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-s btn-sm" onclick="showSett()">Nustatymai</button>
        <button class="btn btn-p" onclick="showRecv()">+ Gauti lakstus</button>
      </div>
    </div>
    <div class="stk-sum" id="stkSum"></div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Likutis</span><button class="btn btn-s btn-sm" onclick="loadStock()">&#x21BB;</button></div>
      <div id="stkTbl"><div class="empty-s">Sandelis tuscias</div></div>
    </div>
    <div class="card" style="overflow:hidden;padding:0;margin-top:12px">
      <div class="card-h"><span class="card-t">Istorija</span><button class="btn btn-s btn-sm" onclick="loadHist()">&#x21BB;</button></div>
      <div id="histTbl"><div class="empty-s">Dar nera istorijos</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-dxf">
  <div class="page-wrap">
    <div class="ph"><div class="ph-t">DXF Uzsakymai</div><button class="btn btn-p" onclick="showNewOrd()">+ Naujas</button></div>
    <div class="sumr" id="dxfSum"></div>
    <div class="fbar">
      <button class="fb active" onclick="dxfFlt('all',this)">Visi</button>
      <button class="fb" onclick="dxfFlt('Naujas',this)">Nauji</button>
      <button class="fb" onclick="dxfFlt('Vykdomas',this)">Vykdomi</button>
      <button class="fb" onclick="dxfFlt('Baigtas',this)">Baigti</button>
      <input class="si" id="dxfSrch" placeholder="Ieskoti..." oninput="rOrds()">
    </div>
    <div class="og" id="ordsGrid"><div class="empty-s">Jungiamasi...</div></div>
  </div>
</div>

<div class="view" id="view-dv">
  <div class="page-wrap">
    <div class="back" onclick="back2Ords()">&#x2190; Grizti</div>
    <div class="card" style="margin-bottom:12px">
      <div class="oi-top">
        <div><div class="oid" id="dvId"></div><div class="oi-t" id="dvCli"></div><div class="oi-s" id="dvDsc"></div></div>
        <div style="text-align:right">
          <div class="wbig" id="dvWt">0</div><div class="wlbl">kg bendras svoris</div>
          <div style="margin-top:8px;display:flex;gap:5px;justify-content:flex-end;flex-wrap:wrap">
            <select class="stsel" id="dvSt" onchange="chSt()"><option>Naujas</option><option>Vykdomas</option><option>Baigtas</option></select>
            <button class="btn btn-p btn-sm" onclick="printOrd()">Spausdinti</button>
            <button class="btn btn-d btn-sm" onclick="delOrd()">Trinti</button>
          </div>
        </div>
      </div>
      <div id="dvMeta" style="font-size:11px;color:#57606a;font-family:'JetBrains Mono',monospace;margin-top:6px"></div>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Prideti detale is DXF</div>
      <div class="dropz" id="dropZ">
        <input type="file" id="dxfFile" accept=".dxf" multiple onchange="handleDxf(event)">
        <div class="dz-t">Tempk DXF failus cia arba spusk</div>
        <div class="dz-s">.dxf - galima ikelti kelis failus</div>
      </div>
      <div style="margin-top:8px">
        <label class="btn btn-s btn-sm" style="cursor:pointer">Ikelti aplanka<input type="file" id="dxfFolder" webkitdirectory multiple accept=".dxf" style="display:none" onchange="handleFolder(event)"></label>
      </div>
      <div class="cvw" id="cvW" style="display:none"><canvas id="dxfCv"></canvas></div>
      <div class="pf" id="pForm" style="display:none">
        <div class="wp"><div class="wv" id="wPv">0.000</div><div class="wl">kg (vieno vnt.)</div><div class="wa" id="wAr"></div></div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="dName"></div>
          <div><label class="fl">Storis (mm)</label><select id="dThk" onchange="rcW();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Kiekis</label><input type="number" id="dQty" value="1" min="1" oninput="rcW()"></div>
        </div>
        <button class="btn btn-p" style="width:100%" onclick="addDet()">+ Prideti detale</button>
      </div>
      <div class="msec">
        <div class="mlbl">arba ivesk rankiniu budu</div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="mName"></div>
          <div><label class="fl">Storis (mm)</label><select id="mThk" onchange="rcM();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Plotas (cm2)</label><input type="number" id="mArea" step="0.01" oninput="rcM()"></div>
        </div>
        <div class="fgrid">
          <div><label class="fl">Kiekis</label><input type="number" id="mQty" value="1" min="1" oninput="rcM()"></div>
          <div><label class="fl">Svoris</label><div class="svor-d" id="mWp">0.000 kg</div></div>
          <div style="display:flex;align-items:flex-end"><button class="btn btn-p" style="width:100%" onclick="addMDet()">+ Prideti</button></div>
        </div>
      </div>
    </div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Detaliu sarasas</span><button class="btn btn-s btn-sm" onclick="loadDets()">&#x21BB;</button></div>
      <div id="dtWrap"><div class="empty-s">Dar nera detaliu</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-arch">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Archyvai</div>
    <div class="sc-grid" id="stageCards"><div class="empty-s">Dar nera archivu</div></div>
    <div class="adbox" id="adBox" style="display:none">
      <div class="adh"><div class="adt" id="adTitle"></div><button class="btn btn-s btn-sm" onclick="closeAd()">X</button></div>
      <div class="adlist" id="adList"></div>
    </div>
  </div>
</div>

<div class="view" id="view-rep">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Ataskaita</div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Laikotarpis</div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr;margin-bottom:10px">
        <div><label class="fl">Nuo</label><input type="date" id="repFrom"></div>
        <div><label class="fl">Iki</label><input type="date" id="repTo"></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
        <button class="btn btn-s btn-sm" onclick="setPeriod(7)">7 dienos</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(30)">30 dienu</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(0)">Sis menuo</button>
      </div>
      <button class="btn btn-p" onclick="genRep()">Generuoti</button>
    </div>
    <div id="repOut" style="display:none"></div>
  </div>
</div>

<div class="mbg" id="noModal" style="display:none">
  <div class="modal">
    <div class="mh">Naujas DXF uzsakymas</div>
    <div class="mf">
      <div><label class="fl">Klientas *</label><input type="text" id="noC"></div>
      <div><label class="fl">Aprasymas</label><input type="text" id="noD"></div>
      <div><label class="fl">Pastabos</label><textarea id="noN"></textarea></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('noModal')">Atsaukti</button><button class="btn btn-p" onclick="createOrd()">Sukurti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="recvModal" style="display:none">
  <div class="modal">
    <div class="mh">Gauti lakstus</div>
    <div class="mf">
      <div><label class="fl">Storis (mm)</label><select id="recThk"><option value="3">3 mm</option><option value="4">4 mm</option><option value="5">5 mm</option><option value="6">6 mm</option><option value="8">8 mm</option><option value="10">10 mm</option><option value="12">12 mm</option><option value="14">14 mm</option><option value="15">15 mm</option><option value="16">16 mm</option><option value="18">18 mm</option><option value="20">20 mm</option><option value="25">25 mm</option></select></div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Plotis (mm)</label><input type="number" id="recW" oninput="rcRecv()"></div>
        <div><label class="fl">Ilgis (mm)</label><input type="number" id="recL" oninput="rcRecv()"></div>
      </div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Kiekis (vnt.)</label><input type="number" id="recQ" value="1" oninput="rcRecv()"></div>
        <div><label class="fl">Kaina / t (EUR)</label><input type="number" id="recP" step="0.01" oninput="rcRecv()"></div>
      </div>
      <div class="rec-prev" id="recPrev">Ivesk matmenis...</div>
      <div><label class="fl">Pastabos (SF nr.)</label><input type="text" id="recN"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('recvModal')">Atsaukti</button><button class="btn btn-p" onclick="doRecv()">Prideti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="useModal" style="display:none">
  <div class="modal">
    <div class="mh">Sunaudoti lakstus</div>
    <div class="mf">
      <div id="useInfo" class="rec-prev"></div>
      <div><label class="fl">Kiek vnt.?</label><input type="number" id="useQ" value="1" min="1"></div>
      <div><label class="fl">Pastabos</label><input type="text" id="useNote"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('useModal')">Atsaukti</button><button class="btn btn-y" onclick="doUse()">Sunaudoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="settModal" style="display:none">
  <div class="modal">
    <div class="mh">Nustatymai</div>
    <div class="mf">
      <div><label class="fl">Numatyta kaina / kg (EUR)</label><input type="number" id="settP" step="0.01"></div>
      <div><label class="fl">Zemos atsargos ispejimas</label><input type="number" id="settL" value="2" min="0"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('settModal')">Atsaukti</button><button class="btn btn-p" onclick="saveSett()">Issaugoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="stModal" style="display:none">
  <div class="modal">
    <div class="mh">Archyvuoti etapa?</div>
    <div id="stMn" style="font-size:11px;color:#57606a;margin-bottom:10px"></div>
    <div id="stMs" class="rec-prev" style="margin-bottom:12px;line-height:2"></div>
    <div class="mb"><button class="btn btn-s" onclick="CM('stModal')">Atsaukti</button><button class="btn btn-p" onclick="confirmStage()">Archyvuoti</button></div>
  </div>
</div>

<div class="pmb" id="printMod" style="display:none">
  <div class="pm">
    <div class="pbr">
      <button class="btn btn-p btn-sm" onclick="window.print()">Spausdinti</button>
      <button class="btn btn-s btn-sm" onclick="dlPdf()">PDF</button>
      <button class="btn btn-s btn-sm" onclick="CM('printMod')">Uzdaryti</button>
    </div>
    <div id="printArea"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const STORIAI=[3,4,5,6,8,10,12,14,15,16,18,20,25];
const TANKIS=8000;
</script>
<script src="/static/js/dxf.js"></script>
<script src="/static/js/main.js"></script>
</body>
</html>"""

@app.on_event("startup")
def startup():
    init_db()

@app.get("/static/css/main.css")
async def serve_css():
    return Response(content=_CSS, media_type="text/css")

@app.get("/static/js/dxf.js")
async def serve_dxfjs():
    return Response(content=_DXFJS, media_type="application/javascript")

@app.get("/static/js/main.js")
async def serve_mainjs():
    return Response(content=_MAINJS, media_type="application/javascript")

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({"name":"Sandelio Sistema","short_name":"Sandelis","start_url":"/","display":"standalone","background_color":"#f6f8fa","theme_color":"#0969da"})

@app.get("/sw.js")
async def sw():
    return Response(content="// sw", media_type="application/javascript")

@app.get("/icon.png")
async def icon():
    import base64
    return Response(content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="), media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=_HTML)


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
        raise HTTPException(400, "SMTP_PASS nenurodytas Railway Variables")
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti = [l for l in items if l.surinkta and not l.perduota]
    perduoti = [l for l in items if l.perduota]
    laukia = [l for l in items if not l.surinkta]
    def rows(lst, color):
        if not lst: return "<tr><td colspan=2 style='color:#aaa;padding:4px 8px'>Tuscia</td></tr>"
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else '-'}</td></tr>" for l in lst)
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
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
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th></tr>{rows(laukia,'#9a6700')}</table>
      <p style='color:#57606a;font-size:11px;margin-top:16px'>Issiusta is Sandelio sistemos - metalcraft.lt</p>
    </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandelio ataskaita {now}"
        msg["From"] = f"Metalcraft <{smtp_user}>"
        msg["To"] = gaivejas
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        # Bandome 587 su STARTTLS
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        except Exception as e1:
            # Bandome 465 su SSL
            with smtplib.SMTP_SSL(smtp_host, 465, timeout=30) as s:
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        return {"success": True, "message": f"Issiusta i {gaivejas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# LAKŠTAI API
# ══════════════════════════════════════════════════

@app.get("/api/lakstai")
def get_lakstai(etapas: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lakstai)
    if etapas:
        q = q.filter(Lakstai.etapas == etapas)
    else:
        q = q.filter(Lakstai.etapas == None)
    items = q.all()
    return {"orders": [_lk(l) for l in items]}

@app.get("/api/lakstai/find/{kodas}")
def find_lakstas(kodas: str, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == kodas).first()
    if not l:
        return {"found": False}
    return {"found": True, **_lk(l)}

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
        return {"success": False, "message": "Nėra užsakymų"}
    total = len(items); collected = sum(1 for l in items if l.surinkta); delivered = sum(1 for l in items if l.perduota)
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

# ══════════════════════════════════════════════════
# DXF API
# ══════════════════════════════════════════════════

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
    d = Detale(det_id=det_id, uzsakymo_id=data["uzsakymoId"], pavadinimas=data.get("pavadinimas", "Detalė"),
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

# ══════════════════════════════════════════════════
# SANDĖLIS API
# ══════════════════════════════════════════════════

@app.get("/api/sandelis")
def get_sandelis(db: Session = Depends(get_db)):
    items = db.query(Sandelis).order_by(Sandelis.storis).all()
    return {"stock": [_stk(s) for s in items]}

@app.post("/api/sandelis/gauti")
def gauti(data: dict, db: Session = Depends(get_db)):
    storis = float(data["storis"]); w = float(data["plotis"]); l = float(data["ilgis"]); qty = int(data["kiekis"])
    kaina = float(data.get("kaina", 0))
    svoris_vnt = round((w/1000) * (l/1000) * (storis/1000) * TANKIS, 2)
    liko_kg = round(svoris_vnt * qty, 2)
    liko_t = round(liko_kg / 1000, 3)
    verte = round(liko_t * kaina, 2)  # kaina uz tona
    stk_id = "STK-" + str(int(datetime.utcnow().timestamp() * 1000))
    s = Sandelis(stk_id=stk_id, storis=storis, matmenys=f"{int(w)}×{int(l)}", svoris_vnt=svoris_vnt,
                 gauta_vnt=qty, liko_vnt=qty, liko_kg=liko_kg, liko_t=liko_t, kaina_kg=kaina, verte=verte,
                 pastabos=data.get("pastabos", ""))
    db.add(s)
    hist = SandelioIstorijia(veiksmas="Gauta", storis=storis, matmenys=f"{int(w)}×{int(l)}", kiekis=qty,
                              svoris_vnt=svoris_vnt, svoris_iš_viso=liko_kg, kaina_kg=kaina, verte=verte, pastabos=data.get("pastabos", ""))
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
    s.verte = round(s.liko_t * s.kaina_kg, 2)  # kaina uz tona
    hist = SandelioIstorijia(veiksmas="Sunaudota", storis=s.storis, matmenys=s.matmenys, kiekis=qty,
                              svoris_vnt=s.svoris_vnt, svoris_iš_viso=round(qty*s.svoris_vnt, 2),
                              kaina_kg=s.kaina_kg, verte=round((qty*s.svoris_vnt/1000)*s.kaina_kg, 2), pastabos=data.get("pastabos", ""))
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
    return {"history": [{"data": h.data.strftime("%Y-%m-%d %H:%M"), "veiksmas": h.veiksmas, "storis": h.storis,
                          "matmenys": h.matmenys, "kiekis": h.kiekis, "svorisVnt": h.svoris_vnt,
                          "svorisIšViso": h.svoris_iš_viso, "kainaKg": h.kaina_kg, "verte": h.verte} for h in items]}

# ══════════════════════════════════════════════════
# ATASKAITA
# ══════════════════════════════════════════════════

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
            "pagalStori": [{"storis": s.storis, "vnt": s.liko_vnt, "kg": round(s.liko_kg, 1), "t": s.liko_t} for s in sorted(stock, key=lambda x: x.storis)]
        }
    }


# ══════════════════════════════════════════════════
# EL. PAŠTAS
# ══════════════════════════════════════════════════

@app.post("/api/email/siusti")
async def siusti_email(data: dict, db: Session = Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    smtp_host = os.getenv("SMTP_HOST", "vytis.serveriai.lt")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "info@metalcraft.lt")
    smtp_pass = os.getenv("SMTP_PASS", "")
    gavėjas   = os.getenv("EMAIL_TO", "gintaras@metalikalt.eu")
    
    if not smtp_pass:
        raise HTTPException(400, "SMTP slaptažodis nenurodytas")
    
    # Gauti lakštus
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti  = [l for l in items if l.surinkta and not l.perduota]
    perduoti  = [l for l in items if l.perduota]
    laukia    = [l for l in items if not l.surinkta]
    
    # HTML laiškas
    def rows(lst, color):
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else ''}</td></tr>" for l in lst)
    
    html = f"""
    <html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>
    <div style='background:#0969da;padding:16px;border-radius:8px 8px 0 0'>
      <h2 style='color:white;margin:0'>Sandėlio ataskaita – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</h2>
    </div>
    <div style='padding:16px;background:#f6f8fa;border-radius:0 0 8px 8px'>
      <p>Iš viso: <strong>{len(items)}</strong> | Surinkta: <strong style='color:#1a7f37'>{len(surinkti)}</strong> | Perduota: <strong style='color:#0969da'>{len(perduoti)}</strong> | Laukia: <strong style='color:#9a6700'>{len(laukia)}</strong></p>
      
      {'<h3 style="color:#1a7f37">✓ Surinkta</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Kodas</th><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Laikas</th></tr>' + rows(surinkti, '#1a7f37') + '</table>' if surinkti else ''}
      
      {'<h3 style="color:#0969da">→ Perduota</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Kodas</th><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Laikas</th></tr>' + rows(perduoti, '#0969da') + '</table>' if perduoti else ''}
      
      {'<h3 style="color:#9a6700">⏳ Laukia</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#fff8c5">Kodas</th><th style="text-align:left;padding:4px 8px;background:#fff8c5">Laikas</th></tr>' + rows(laukia, '#9a6700') + '</table>' if laukia else ''}
      
      <p style='color:#57606a;font-size:12px;margin-top:16px'>Išsiųsta iš Sandėlio sistemos – metalcraft.lt</p>
    </div>
    </body></html>
    """
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandėlio ataskaita {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        msg["From"]    = f"Metalcraft <{smtp_user}>"
        msg["To"]      = gavėjas
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, gavėjas, msg.as_string())
        
        return {"success": True, "message": f"Išsiųsta į {gavėjas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# ══════════════════════════════════════════════════
# PAGALBINĖS FUNKCIJOS
# ══════════════════════════════════════════════════

def _lk(l):
    return {"kodas": l.kodas, "registered": l.registruota.strftime("%Y-%m-%d %H:%M:%S") if l.registruota else "",
            "collected": l.surinkta, "collectedAt": l.surinkta_kada.strftime("%Y-%m-%d %H:%M:%S") if l.surinkta_kada else "",
            "delivered": l.perduota, "deliveredAt": l.perduota_kada.strftime("%Y-%m-%d %H:%M:%S") if l.perduota_kada else ""}

def _uzs(u):
    return {"id": u.uzs_id, "klientas": u.klientas, "aprasymas": u.aprasymas or "", "pastabos": u.pastabos or "",
            "statusas": u.statusas, "bendraSvoris": u.bendras_svoris, "detaliuSk": u.detaliu_sk,
            "sukurta": u.sukurta.strftime("%Y-%m-%d %H:%M:%S") if u.sukurta else ""}

def _det(d):
    return {"detId": d.det_id, "uzsakymoId": d.uzsakymo_id, "pavadinimas": d.pavadinimas,
            "storis": d.storis, "plotas": d.plotas, "kiekis": d.kiekis, "svoris": d.svoris,
            "konturas": d.konturas or "", "prideta": d.prideta.strftime("%Y-%m-%d %H:%M:%S") if d.prideta else ""}

def _stk(s):
    return {"id": s.stk_id, "storis": s.storis, "matmenys": s.matmenys, "svorisVnt": s.svoris_vnt,
            "gautaVnt": s.gauta_vnt, "sunaudotaVnt": s.sunaudota_vnt, "likoVnt": s.liko_vnt,
            "likoKg": s.liko_kg, "likoT": s.liko_t, "kainaKg": s.kaina_kg, "verte": s.verte,
            "prideta": s.prideta.strftime("%Y-%m-%d %H:%M:%S") if s.prideta else "", "pastabos": s.pastabos or ""}

def _recalc(uzs_id, db):
    dets = db.query(Detale).filter(Detale.uzsakymo_id == uzs_id).all()
    u = db.query(Uzsakymas).filter(Uzsakymas.uzs_id == uzs_id).first()
    if u:
        u.bendras_svoris = round(sum(d.svoris for d in dets), 3)
        u.detaliu_sk = len(dets)
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os

from database import get_db, init_db, Lakstai, Etapas, Uzsakymas, Detale, Sandelis, SandelioIstorijia

app = FastAPI(title="Sandelio Sistema")
TANKIS = 8000

_CSS = """*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#f6f8fa;--s1:#ffffff;--s2:#f0f2f4;--s3:#e1e4e8;
  --bd:#d0d7de;--bd2:#afb8c1;
  --tx:#1f2328;--tx2:#57606a;--tx3:#848d97;
  --ac:#0969da;--ac2:#0550ae;--ac-bg:rgba(9,105,218,.08);
  --gn:#1a7f37;--gn-bg:rgba(26,127,55,.08);--gn-bd:rgba(26,127,55,.3);
  --yw:#9a6700;--yw-bg:rgba(154,103,0,.08);--yw-bd:rgba(154,103,0,.3);
  --rd:#cf222e;--rd-bg:rgba(207,34,46,.08);--rd-bd:rgba(207,34,46,.3);
  --pp:#6639ba;--pp-bg:rgba(102,57,186,.08);
  --or:#953800;
}
body{background:var(--bg);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;min-height:100vh;font-size:14px}

nav{background:var(--s1);border-bottom:1px solid var(--bd);padding:0 16px;height:52px;display:flex;align-items:center;gap:8px;position:sticky;top:0;z-index:50}
.brand{font-size:15px;font-weight:800;display:flex;align-items:center;gap:8px;flex-shrink:0}
.brand-ico{width:26px;height:26px;background:linear-gradient(135deg,#0969da,#6639ba);border-radius:6px}
.tabs{display:flex;height:100%;overflow-x:auto;flex:1;justify-content:center}
.tab{padding:0 13px;height:100%;display:flex;align-items:center;gap:4px;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;border:none;background:none;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}
.tab:hover{color:var(--tx)}.tab.active{color:var(--ac);border-bottom-color:var(--ac)}
.bdg{background:var(--ac);color:#fff;font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px}
.bdg.y{background:var(--yw)}.bdg.gray{background:var(--s3);color:var(--tx2)}.bdg.r{background:var(--rd)}
.nav-r{margin-left:auto;display:flex;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--bd2)}.dot.ok{background:var(--gn)}.dot.err{background:var(--rd)}

.view{display:none}.view.active{display:block}
.page-wrap{padding:16px;max-width:1000px;margin:0 auto}
.ph{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ph-t{font-size:18px;font-weight:800}.ph-s{font-size:11px;color:var(--tx2);margin-top:2px}

.btn{padding:7px 14px;border:none;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:12px;cursor:pointer;border-radius:6px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;white-space:nowrap}
.btn-p{background:var(--ac);color:#fff}.btn-p:hover{background:var(--ac2)}
.btn-s{background:transparent;border:1px solid var(--bd);color:var(--tx2)}.btn-s:hover{border-color:var(--tx);color:var(--tx)}
.btn-g{background:var(--gn-bg);border:1px solid var(--gn-bd);color:var(--gn)}.btn-g:hover{background:var(--gn);color:#fff}
.btn-d{background:transparent;border:1px solid transparent;color:var(--tx3)}.btn-d:hover{border-color:var(--rd-bd);color:var(--rd);background:var(--rd-bg)}
.btn-y{background:var(--yw-bg);border:1px solid var(--yw-bd);color:var(--yw)}.btn-y:hover{background:var(--yw);color:#fff}
.btn-sm{padding:4px 9px;font-size:11px}

.fl{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:4px}
input[type=text],input[type=number],input[type=date],input[type=email],textarea,select{width:100%;padding:7px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;outline:none;border-radius:6px;transition:border-color .15s;-webkit-appearance:none}
input:focus,textarea:focus,select:focus{border-color:var(--ac)}
textarea{resize:vertical;min-height:60px}
option{background:var(--s1)}

.card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;margin-bottom:12px}
.card-h{padding:12px 16px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.card-t{font-weight:700;font-size:14px}
.ct{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.ct::after{content:'';flex:1;height:1px;background:var(--bd)}

.mbg{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:24px;max-width:440px;width:100%;margin:auto}
.mh{font-size:17px;font-weight:800;margin-bottom:16px}
.mf{display:flex;flex-direction:column;gap:12px}
.mb{display:flex;gap:8px;justify-content:flex-end;margin-top:6px}

.toast{position:fixed;bottom:14px;right:14px;left:14px;max-width:340px;margin:0 auto;padding:11px 14px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;background:var(--s1);border:1px solid var(--bd);border-left:3px solid var(--gn);box-shadow:0 8px 24px rgba(0,0,0,.15);transform:translateY(70px);opacity:0;transition:all .25s;z-index:300;border-radius:6px}
.toast.w{border-left-color:var(--rd)}.toast.b{border-left-color:var(--ac)}.toast.p{border-left-color:var(--pp)}
.toast.show{transform:translateY(0);opacity:1}
.sp{display:inline-block;width:11px;height:11px;border:2px solid var(--bd2);border-top-color:var(--ac);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:4px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.empty-s{padding:40px;text-align:center;color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:12px}

/* LAKŠTAI */
.lk-wrap{display:grid;grid-template-columns:1fr 290px;min-height:calc(100vh - 52px)}
@media(max-width:680px){.lk-wrap{grid-template-columns:1fr}}
.lk-main{padding:16px;display:flex;flex-direction:column;gap:10px}
.lk-sb{border-left:1px solid var(--bd);background:var(--s1);display:flex;flex-direction:column}
.scan-f{position:relative}.scan-ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:16px;pointer-events:none;color:var(--tx3)}
.scan-inp{padding:11px 14px 11px 40px!important;font-size:17px!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important}
.scan-inp:focus{border-color:var(--ac)!important;box-shadow:0 0 0 3px var(--ac-bg)}
.hint{margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3)}
.steps{display:flex;gap:4px;margin-top:10px}
.step{flex:1;height:3px;background:var(--bd);border-radius:2px}
.s1{background:var(--yw)}.s2{background:var(--gn)}.s3{background:var(--ac)}
.step-lbl{display:flex;justify-content:space-between;margin-top:4px;font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.res{border:1px solid var(--bd);border-radius:8px;padding:12px 14px;animation:fadeUp .2s ease}
.res.rn{background:var(--yw-bg);border-color:var(--yw-bd)}.res.rc{background:var(--gn-bg);border-color:var(--gn-bd)}
.res.rd{background:var(--ac-bg);border-color:rgba(9,105,218,.3)}.res.re{background:var(--rd-bg);border-color:var(--rd-bd)}
.res.rp{background:var(--pp-bg);border-color:rgba(102,57,186,.3)}.res.ra{background:var(--gn-bg);border-color:var(--gn-bd)}
.rt{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}
.res.rn .rt{color:var(--yw)}.res.rc .rt{color:var(--gn)}.res.rd .rt{color:var(--ac)}.res.re .rt{color:var(--rd)}.res.rp .rt{color:var(--pp)}.res.ra .rt{color:var(--gn)}
.rc{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace}.rs{font-size:11px;color:var(--tx2);margin-top:2px}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
@media(max-width:480px){.stats-row{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.sn{font-size:22px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace}
.sn.a{color:var(--ac)}.sn.g{color:var(--gn)}.sn.b{color:var(--ac)}.sn.y{color:var(--yw)}
.sl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.prog-card{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 14px}
.pt{display:flex;justify-content:space-between;margin-bottom:6px;font-size:10px;color:var(--tx2);font-family:'JetBrains Mono',monospace}
.pct{color:var(--gn);font-weight:700}
.ptr{height:6px;background:var(--s2);border-radius:3px;overflow:hidden;position:relative}
.pfc{height:100%;background:var(--gn);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px}
.pfd{height:100%;background:var(--ac);position:absolute;top:0;left:0;transition:width .5s;border-radius:3px;opacity:.4}
.stbar{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:12px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.stbar-lbl{font-weight:700;font-size:13px;white-space:nowrap}.stbar input{flex:1;min-width:130px}
.stbar-hint{font-size:9px;color:var(--tx3);width:100%;font-family:'JetBrains Mono',monospace}
.sbh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}
.sbt{font-weight:700;font-size:12px}.sbsr{position:relative;width:100%}
.sbsr input{padding:5px 10px 5px 26px;font-size:11px}.sbs-i{position:absolute;left:8px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--tx3);pointer-events:none}
.frow{padding:6px 14px;border-bottom:1px solid var(--bd);display:flex;gap:4px;flex-wrap:wrap}
.fb{padding:3px 8px;background:transparent;border:1px solid var(--bd);color:var(--tx3);font-family:'JetBrains Mono',monospace;font-size:9px;cursor:pointer;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;transition:all .15s}
.fb.active{background:var(--tx);color:var(--bg);border-color:var(--tx);font-weight:700}
.olist{flex:1;overflow-y:auto}
.oi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:6px;transition:background .1s}
.oi:hover{background:var(--s2)}
.od{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.oi.sc .od{background:var(--gn)}.oi.sdd .od{background:var(--ac)}
.oc{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ost{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700;flex-shrink:0}
.ost.s0{background:var(--yw-bg);color:var(--yw)}.ost.s1{background:var(--gn-bg);color:var(--gn)}.ost.s2{background:var(--ac-bg);color:var(--ac)}
.otm{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);flex-shrink:0}

/* SANDĖLIS */
.stk-sum{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin-bottom:14px}
.stk-s{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.stk-n{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.stk-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.stk-row{padding:10px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.stk-row:last-child{border-bottom:none}.stk-row:hover{background:var(--s2)}
@media(max-width:600px){.stk-row{grid-template-columns:1fr 1fr;gap:6px}}
.stk-thick{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:var(--ac)}
.stk-thick span{font-size:10px;color:var(--tx3)}
.stk-dims{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.stk-num{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700}
.stk-num.ok{color:var(--gn)}.stk-num.warn{color:var(--yw)}.stk-num.empty{color:var(--rd)}
.stk-sub{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.stk-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--or)}
.stk-acts{display:flex;gap:4px}
.stk-tot{padding:10px 16px;background:var(--s2);border-top:2px solid var(--bd);display:grid;grid-template-columns:70px 1fr 80px 80px 80px 90px auto;align-items:center;gap:10px}
.hist-row{padding:8px 16px;border-bottom:1px solid var(--bd);display:grid;grid-template-columns:130px 60px 90px 60px 80px 80px;align-items:center;gap:8px;font-size:12px}
.hist-row:last-child{border-bottom:none}.hist-row:hover{background:var(--s2)}
.hist-act{font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700}
.hist-act.G{background:var(--gn-bg);color:var(--gn)}.hist-act.S{background:var(--rd-bg);color:var(--rd)}
.rec-prev{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--tx2)}

/* DXF */
.sumr{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin-bottom:14px}
.smc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}
.smn{font-size:20px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.sml{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}
.fbar{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.si{padding:5px 10px;background:var(--s1);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:11px;outline:none;border-radius:6px;min-width:150px}
.si:focus{border-color:var(--ac)}
.og{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.ocard{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.ocard:hover{border-color:var(--ac);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.oct{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.oid{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3)}
.stb{font-family:'JetBrains Mono',monospace;font-size:9px;padding:2px 7px;border-radius:4px;font-weight:700}
.stb.Naujas{background:var(--yw-bg);color:var(--yw);border:1px solid var(--yw-bd)}
.stb.Vykdomas{background:var(--ac-bg);color:var(--ac);border:1px solid rgba(9,105,218,.3)}
.stb.Baigtas{background:var(--gn-bg);color:var(--gn);border:1px solid var(--gn-bd)}
.ocli{font-size:14px;font-weight:700;margin-bottom:2px}.ocdesc{font-size:11px;color:var(--tx2);margin-bottom:10px}
.ocm{display:flex;gap:10px;flex-wrap:wrap}
.ocmi{font-family:'JetBrains Mono',monospace;font-size:10px}
.ocmi .v{color:var(--ac);font-weight:700}.ocmi .l{color:var(--tx3)}
.back{display:flex;align-items:center;gap:5px;color:var(--tx2);font-size:12px;cursor:pointer;margin-bottom:14px;font-family:'JetBrains Mono',monospace;transition:color .15s}
.back:hover{color:var(--ac)}
.oi-top{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px}
.oi-t{font-size:18px;font-weight:800}.oi-s{font-size:11px;color:var(--tx2);margin-top:2px}
.wbig{font-size:28px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac);line-height:1}
.wlbl{font-size:9px;color:var(--tx3);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px}
.stsel{padding:5px 10px;background:var(--s2);border:1px solid var(--bd);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:10px;outline:none;border-radius:6px;width:auto}
.dropz{border:2px dashed var(--bd);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:all .2s;position:relative}
.dropz:hover,.dropz.drag{border-color:var(--ac);background:var(--ac-bg)}
.dropz input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer}
.dz-t{font-size:12px;color:var(--tx2)}.dz-s{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.cvw{background:var(--s2);border:1px solid var(--bd);border-radius:6px;margin-top:10px;overflow:hidden}
canvas{display:block;max-width:100%;height:150px}
.pf{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:14px;margin-top:10px;animation:fadeUp .2s ease}
.wp{background:var(--s1);border:1px solid var(--bd);border-radius:6px;padding:10px 12px;margin-bottom:10px}
.wv{font-size:19px;font-weight:700;color:var(--ac);font-family:'JetBrains Mono',monospace}
.wl{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-top:1px;font-family:'JetBrains Mono',monospace}
.wa{font-size:10px;color:var(--tx3);margin-top:4px;font-family:'JetBrains Mono',monospace}
.fgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:480px){.fgrid{grid-template-columns:1fr}}
.msec{margin-top:12px;border-top:1px solid var(--bd);padding-top:12px}
.mlbl{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.svor-d{padding:7px 10px;background:var(--s1);border:1px solid var(--bd);border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ac)}
table{width:100%;border-collapse:collapse}
th{padding:7px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:1px;text-align:left;border-bottom:1px solid var(--bd);background:var(--s2)}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}tr:hover td{background:var(--s2)}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px}
.num{color:var(--ac);font-weight:700;font-family:'JetBrains Mono',monospace}
.dttot{padding:10px 12px;background:var(--s2);border-top:2px solid var(--bd);display:flex;justify-content:flex-end;gap:14px;font-family:'JetBrains Mono',monospace;font-size:11px}
.tot{color:var(--ac);font-weight:700;font-size:13px}
.det-grp-hdr{padding:6px 12px;background:var(--s2);border-top:2px solid var(--bd);border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:10px}
.det-grp-t{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800;color:var(--ac)}
.det-grp-s{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2)}
.det-inp{padding:3px 6px!important;font-size:11px!important;width:auto!important}

/* ARCHYVAI */
.sc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:14px}
.scc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px;cursor:pointer;transition:all .15s}
.scc:hover{border-color:var(--ac);transform:translateY(-1px)}.scc.open{border-color:var(--ac)}
.scn{font-size:13px;font-weight:700;margin-bottom:8px}
.scst{display:flex;gap:10px}
.scst .n{font-size:15px;font-weight:700;display:block;line-height:1;font-family:'JetBrains Mono',monospace}
.scst .n.g{color:var(--gn)}.scst .n.b{color:var(--ac)}.scst .n.r{color:var(--rd)}
.scst .l{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--tx3);text-transform:uppercase}
.scp{margin-top:8px;height:3px;background:var(--s2);border-radius:2px;overflow:hidden}
.scpf{height:100%;background:var(--gn);border-radius:2px}
.adbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;margin-top:10px}
.adh{padding:10px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between}
.adt{font-weight:700;font-size:13px}
.adlist{max-height:320px;overflow-y:auto}
.adi{padding:7px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:7px}
.addot{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--s3)}
.adi.sc .addot{background:var(--gn)}.adi.sdd .addot{background:var(--ac)}
.adcode{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;flex:1}
.adtag{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700}
.adtag.r{background:var(--yw-bg);color:var(--yw)}.adtag.c{background:var(--gn-bg);color:var(--gn)}.adtag.d{background:var(--ac-bg);color:var(--ac)}
.adtime{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx3)}

/* ATASKAITA */
.rep-s{margin-bottom:14px}
.rep-st{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--bd)}
.rep-sr{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}
.rep-sc{background:var(--s2);border-radius:6px;padding:10px 12px}
.rep-sc .n{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--ac)}
.rep-sc .l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;font-family:'JetBrains Mono',monospace}

/* PRINT */
@media print{body *{visibility:hidden!important}#printArea,#printArea *{visibility:visible!important}#printArea{position:fixed!important;left:0;top:0;width:100%}@page{margin:6mm;size:A4}}
.pmb{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:flex-start;justify-content:center;padding:16px;overflow-y:auto}
.pm{background:white;color:#000;max-width:210mm;width:100%;border-radius:8px;overflow:hidden;margin:auto}
.pbr{display:flex;gap:8px;padding:10px 14px;background:#f5f5f5;border-bottom:1px solid #ddd}
#printArea{background:white;color:#000;font-family:Arial,sans-serif;padding:10mm 8mm}
.pph{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}
.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666;font-family:monospace}
.ppbc{text-align:right;margin:2mm 0}
.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}
.ppi-l{font-size:7pt;color:#888;text-transform:uppercase;margin-bottom:.5mm}.ppi-v{font-size:10pt;font-weight:700}
.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}
.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}
.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}
.pptable tr:nth-child(even) td{background:#f9f9f9}
.ppsign{display:flex;gap:10mm;margin-top:5mm}
.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}
.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}
"""

_DXFJS = """
// DXF PARSERIS
const TANKIS = 8000;

function thickFromName(name){
  const m=name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)[ ]*mm/)||name.match(/[tT]-?([0-9]+(?:[.][0-9]+)?)/)||name.match(/([0-9]+(?:[.][0-9]+)?)[ ]*mm/);
  if(!m)return null;
  const v=parseFloat(m[1]);
  return STORIAI.includes(v)?v:null;
}

function qtyFromName(name){
  const m=name.match(/[_\x2D\x20]([0-9]+)[ ]*vnt/i)||name.match(/^([0-9]+)[ ]*vnt/i);
  if(!m)return null;
  const v=parseInt(m[1]);
  return v>0&&v<=9999?v:null;
}

function pDxf(txt){
  const lines=txt.split(/\r?\n/);
  const segs=[];
  let inE=false,curType=null,curV={},sf=1;

  for(let j=0;j<lines.length-1;j++){
    if(lines[j].trim()==='70'&&j>=2&&lines[j-2].trim()==='$INSUNITS'){
      const u=parseInt(lines[j+1]);if(u===1)sf=25.4;else if(u===6)sf=10;else if(u===5)sf=.1;
    }
  }

  const r4=v=>Math.round(v*10000)/10000;

  function saveSeg(t,v){
    if(t==='LINE'&&v._x1!==undefined&&v._y1!==undefined&&v._x2!==undefined&&v._y2!==undefined){
      segs.push({type:'L',x1:r4(v._x1*sf),y1:r4(v._y1*sf),x2:r4(v._x2*sf),y2:r4(v._y2*sf)});
    } else if(t==='CIRCLE'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf)});
    } else if((t==='LWPOLYLINE'||t==='POLYLINE')&&v._xs&&v._xs.length>=3){
      segs.push({type:'P',pts:v._xs.map((x,i)=>({x:r4(x*sf),y:r4((v._ys[i]||0)*sf)})),closed:((v[70]||0)&1)===1});
    } else if(t==='ARC'&&v._x1!==undefined&&v._y1!==undefined&&40 in v){
      segs.push({type:'C',cx:r4(v._x1*sf),cy:r4(v._y1*sf),r:r4(v[40]*sf),arc:true});
    }
  }

  let i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i++;continue;}
    const val=(lines[i+1]||'').trim();
    if(code===2&&val==='ENTITIES'){inE=true;i+=2;continue;}
    if(code===0&&val==='ENDSEC'&&inE){saveSeg(curType,curV);break;}
    if(!inE){i+=2;continue;}
    if(code===0){saveSeg(curType,curV);curType=val;curV={};}
    else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._x1=n;}
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'){curV._y1=n;}
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11){curV._x2=n;}
        else if(code===21){curV._y2=n;}
        else if(code===70){curV[70]=parseInt(val)||0;}
        else{curV[code]=n;}
      }
    }
    i+=2;
  }

  let area=0;
  segs.filter(s=>s.type==='C'&&!s.arc).forEach(s=>area+=Math.PI*s.r*s.r);
  segs.filter(s=>s.type==='P').forEach(s=>{
    const pts=s.pts,n=pts.length;let a=0;
    for(let i=0;i<n;i++){const j=(i+1)%n;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}
    area+=Math.abs(a)/2;
  });
  const lineSegs=segs.filter(s=>s.type==='L');
  if(lineSegs.length){
    const adj=new Map();
    const key=p=>Math.round(p.x*100)/100+','+Math.round(p.y*100)/100;
    lineSegs.forEach(s=>{
      const p1={x:s.x1,y:s.y1},p2={x:s.x2,y:s.y2};
      const k1=key(p1),k2=key(p2);
      if(!adj.has(k1))adj.set(k1,{pt:p1,nb:[]});
      if(!adj.has(k2))adj.set(k2,{pt:p2,nb:[]});
      adj.get(k1).nb.push(k2);adj.get(k2).nb.push(k1);
    });
    const visitedE=new Set(),visitedP=new Set();
    adj.forEach((v,startK)=>{
      if(visitedP.has(startK))return;
      const path=[v.pt];let curK=startK;
      for(let iter=0;iter<adj.size*2;iter++){
        visitedP.add(curK);
        const nb=adj.get(curK).nb;let nextK=null;
        for(const nk of nb){
          const ek=[curK,nk].sort().join('|');
          if(!visitedE.has(ek)){visitedE.add(ek);nextK=nk;break;}
        }
        if(!nextK)break;
        path.push(adj.get(nextK).pt);curK=nextK;
      }
      if(path.length>=3){
        let a=0;const n=path.length;
        for(let i=0;i<n;i++){const j=(i+1)%n;a+=path[i].x*path[j].y-path[j].x*path[i].y;}
        area+=Math.abs(a)/2;
      }
    });
  }

  // Matmenys
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  segs.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  const dimW=isFinite(minX)?Math.round(maxX-minX):0;
  const dimH=isFinite(minY)?Math.round(maxY-minY):0;

  return{entities:segs,areaCm2:area/100,dimW,dimH};
}

function serializeContour(ents,dimW,dimH){
  try{
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    ents.forEach(s=>{
      if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
      else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
      else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
    });
    if(!isFinite(minX))return'';
    const W=maxX-minX||1,H=maxY-minY||1,sc=100/Math.max(W,H);
    const nx=x=>Math.round((x-minX)*sc*10)/10;
    const ny=y=>Math.round((maxY-y)*sc*10)/10;
    const paths=[];
    ents.forEach(s=>{
      if(s.type==='C'&&!s.arc)paths.push('C'+nx(s.cx)+','+ny(s.cy)+','+Math.round(s.r*sc*10)/10);
      else if(s.type==='P'){const step=Math.max(1,Math.floor(s.pts.length/50));const pts=[];for(let i=0;i<s.pts.length;i+=step)pts.push(nx(s.pts[i].x)+','+ny(s.pts[i].y));paths.push('L'+pts.join(' '));}
      else if(s.type==='L')paths.push('L'+nx(s.x1)+','+ny(s.y1)+' '+nx(s.x2)+','+ny(s.y2));
    });
    return('D:'+dimW+'x'+dimH+'|'+paths.join('|')).slice(0,2000);
  }catch(e){return'';}
}

function calcDims(d){
  if(d.konturas){
    const m=d.konturas.match(/D:([0-9]+)x([0-9]+)/);
    if(m)return m[1]+'×'+m[2]+'mm';
    try{
      let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
      d.konturas.split('|').forEach(p=>{
        if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);if(!isNaN(cx)){minX=Math.min(minX,cx-r);maxX=Math.max(maxX,cx+r);minY=Math.min(minY,cy-r);maxY=Math.max(maxY,cy+r);}}
        else if(p.startsWith('L')){p.slice(1).trim().split(' ').forEach(pt=>{const[x,y]=pt.split(',').map(Number);if(!isNaN(x)&&!isNaN(y)){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}});}
      });
      if(isFinite(minX)&&maxX>minX&&maxY>minY){
        const ratio=(maxX-minX)/(maxY-minY);const area=parseFloat(d.plotas)||0;
        if(area>0){const Hmm=Math.round(Math.sqrt(area*100/ratio));return Math.round(ratio*Hmm)+'×'+Hmm+'mm';}
      }
    }catch(e){}
  }
  const area=parseFloat(d.plotas)||0;
  if(!area)return'—';
  return'~'+Math.round(Math.sqrt(area*100))+'mm';
}

function drawPrev(ents){
  const w=document.getElementById('cvW'),c=document.getElementById('dxfCv');
  w.style.display='block';
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  ents.forEach(s=>{
    if(s.type==='C'){minX=Math.min(minX,s.cx-s.r);maxX=Math.max(maxX,s.cx+s.r);minY=Math.min(minY,s.cy-s.r);maxY=Math.max(maxY,s.cy+s.r);}
    else if(s.type==='P'){s.pts.forEach(p=>{minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);});}
    else if(s.type==='L'){minX=Math.min(minX,s.x1,s.x2);maxX=Math.max(maxX,s.x1,s.x2);minY=Math.min(minY,s.y1,s.y2);maxY=Math.max(maxY,s.y1,s.y2);}
  });
  if(!isFinite(minX))return;
  const W=w.clientWidth||400,H=150;c.width=W;c.height=H;
  const ctx=c.getContext('2d');ctx.fillStyle='#f0f2f4';ctx.fillRect(0,0,W,H);
  const rX=maxX-minX||1,rY=maxY-minY||1,sc=Math.min((W-30)/rX,(H-30)/rY)*.9;
  const oX=(W-rX*sc)/2-minX*sc,oY=(H+rY*sc)/2+minY*sc;
  ctx.strokeStyle='#0969da';ctx.lineWidth=1.5;
  ents.forEach(s=>{
    ctx.beginPath();
    if(s.type==='C')ctx.arc(s.cx*sc+oX,oY-s.cy*sc,s.r*sc,0,Math.PI*2);
    else if(s.type==='P'&&s.pts.length){ctx.moveTo(s.pts[0].x*sc+oX,oY-s.pts[0].y*sc);for(let i=1;i<s.pts.length;i++)ctx.lineTo(s.pts[i].x*sc+oX,oY-s.pts[i].y*sc);if(s.closed)ctx.closePath();}
    else if(s.type==='L'){ctx.moveTo(s.x1*sc+oX,oY-s.y1*sc);ctx.lineTo(s.x2*sc+oX,oY-s.y2*sc);}
    ctx.stroke();
  });
}

function drawContourSvg(konturas,sizeMm=14){
  if(!konturas)return'';
  try{
    const parts=konturas.replace(/^D:[0-9]+x[0-9]+[|]/,'').split('|');
    let paths='';
    parts.forEach(p=>{
      if(p.startsWith('C')){const[cx,cy,r]=p.slice(1).split(',').map(Number);paths+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#000" stroke-width="2"/>`;}
      else if(p.startsWith('L')){const pts=p.slice(1).trim().split(' ');if(pts.length<2)return;const d='M'+pts[0]+' '+pts.slice(1).map(pt=>'L'+pt).join(' ');paths+=`<path d="${d}" fill="none" stroke="#000" stroke-width="2"/>`;}
    });
    const s=sizeMm+'mm';
    return`<svg viewBox="-5 -5 110 110" width="${s}" height="${s}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">${paths}</svg>`;
  }catch(e){return'';}
}

"""

_MAINJS = """
// SANDĖLIO SISTEMA – main.js

let lkOrders=[],lkF='all',lkLC=null,lkLT=0;
let dxfOrders=[],dxfF='all',dxfDets=[],curOrd=null,curArea=0,curContour='';
let stock=[],history=[],stages=[],archOpen=null;
let pendingSt='',curStockId=null;
let settings={defaultPrice:0,lowAlert:2};

// GARSAS
let actx=null;
function ga(){if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();return actx;}
function beep(t){try{const c=ga();if(c.state==='suspended')c.resume();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;if(t==='new'){o.frequency.value=880;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.2);o.start(n);o.stop(n+.2);}else if(t==='col'){o.frequency.setValueAtTime(660,n);o.frequency.setValueAtTime(880,n+.12);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.3);o.start(n);o.stop(n+.3);}else if(t==='del'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(660,n+.1);o.frequency.setValueAtTime(880,n+.2);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='err'){o.type='sawtooth';o.frequency.value=220;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='dup'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(220,n+.15);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.35);o.start(n);o.stop(n+.35);}}catch(e){}}

// API
async function api(method,url,data){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(data)opts.body=JSON.stringify(data);
  const r=await fetch(url,opts);
  if(!r.ok)throw new Error(r.statusText);
  return r.json();
}

// INIT
window.onload=()=>{
  loadAll();
  const lt=localStorage.getItem('lastThick');
  if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}
  setPeriod(30);
  const dz=document.getElementById('dropZ');
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
};
document.addEventListener('click',e=>{if(actx&&actx.state==='suspended')actx.resume();if(document.getElementById('view-lk').classList.contains('active')&&!e.target.closest('input,button,select'))focusScan();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mbg').forEach(m=>m.style.display='none');});

async function loadAll(){await loadLk();await loadDxfOrds();await loadStock();await loadHist();await loadStages();}

// NAVIGACIJA
function SW(v){
  document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById('view-'+v).classList.add('active');
  const t=document.getElementById('tab-'+v);if(t)t.classList.add('active');
  if(v==='lk')focusScan();
  if(v==='dv'){const lt=localStorage.getItem('lastThick');if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}}
}
function CM(id){document.getElementById(id).style.display='none';}
function focusScan(){try{document.getElementById('scanInp').focus();}catch(e){}}
function toast(msg,w=false,t=''){const el=document.getElementById('toast');el.textContent=msg;el.className='toast '+(w?'w':t)+' show';clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),3000);}

// ════ LAKŠTAI ════
const scanInp=document.getElementById('scanInp');
scanInp.addEventListener('keydown',async e=>{if(e.key==='Enter'){const c=scanInp.value.trim();if(c){scanInp.value='';await handleScan(c);}}});

async function handleScan(kodas){
  const now=Date.now();
  if(kodas===lkLC&&now-lkLT<3000){lkRes('rp','DUBLIKATAS',kodas,'Tas pats kodas du kartus!');beep('dup');toast('Dublikatas: '+kodas,false,'p');lkLC=null;return;}
  lkLC=kodas;lkLT=now;
  const local=lkOrders.find(o=>o.kodas===kodas);
  if(local){
    if(local.delivered){lkRes('ra','JAU PERDUOTA',kodas,'Perduota: '+local.deliveredAt);beep('err');return;}
    if(local.collected){
      lkRes('rd','PERDUOTA',kodas,'3× — siunčiama...');beep('del');
      local.delivered=true;local.deliveredAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Perduota: '+kodas,false,'b');else{local.delivered=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }else{
      lkRes('rc','SURINKTA',kodas,'2× — siunčiama...');beep('col');
      local.collected=true;local.collectedAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Surinkta: '+kodas);else{local.collected=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }
    return;
  }
  lkRes('rn','NAUJAS',kodas,'1× — siunčiama...');beep('new');
  const newOrd={kodas,registered:nowS(),collected:false,collectedAt:'',delivered:false,deliveredAt:''};
  lkOrders.push(newOrd);lkStats();rlkList();
  api('POST','/api/lakstai/register',{kodas}).then(r=>{
    if(r.success)toast('Užregistruota: '+kodas);
    else if(r.alreadyExists){lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkAddL(r.order);lkStats();rlkList();handleScan(kodas);}
    else{lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkRes('re','KLAIDA',kodas,'Nepavyko');beep('err');lkStats();rlkList();}
  });
}

function lkRes(c,t,kodas,s){
  const b=document.getElementById('lkRes');
  b.className='res '+c;b.style.display='block';
  document.getElementById('lkRt').textContent=t;
  document.getElementById('lkRc').textContent=kodas;
  document.getElementById('lkRs').textContent=s;
}

async function loadLk(){
  try{const r=await api('GET','/api/lakstai');lkOrders=r.orders||[];lkStats();rlkList();document.getElementById('connDot').className='dot ok';}
  catch(e){document.getElementById('connDot').className='dot err';toast('Nepavyko prisijungti',true);}
}
function lkAddL(o){const i=lkOrders.findIndex(x=>x.kodas===o.kodas);if(i>=0)lkOrders[i]=o;else lkOrders.push(o);}
function lkStats(){
  const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length,p=lkOrders.filter(o=>!o.collected).length;
  const pc=t>0?Math.round(c/t*100):0,pd=t>0?Math.round(d/t*100):0;
  document.getElementById('lkT').textContent=t;document.getElementById('lkC').textContent=c;
  document.getElementById('lkD').textContent=d;document.getElementById('lkP').textContent=p;
  document.getElementById('lkPct').textContent=pc+'%';
  document.getElementById('lkPfc').style.width=pc+'%';document.getElementById('lkPfd').style.width=pd+'%';
  document.getElementById('lkBdg').textContent=p||t;
}
function lkFlt(f,b){lkF=f;document.querySelectorAll('.frow .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rlkList();}
function sortLk(l){return[...l].sort((a,b)=>{const n=s=>parseInt((s.match(/[0-9]+/)||[0])[0]);return n(a.kodas)-n(b.kodas);});}
function rlkList(){
  const el=document.getElementById('lkList'),q=(document.getElementById('lkSrch').value||'').toLowerCase();
  let l=sortLk(lkOrders);
  if(lkF==='p')l=l.filter(o=>!o.collected);if(lkF==='c')l=l.filter(o=>o.collected&&!o.delivered);if(lkF==='d')l=l.filter(o=>o.delivered);
  if(q)l=l.filter(o=>o.kodas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(lkOrders.length===0?'Nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>{
    const sc=o.delivered?'sdd':o.collected?'sc':'';
    const sl=o.delivered?'s2':o.collected?'s1':'s0';
    const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
    const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);
    return`<div class="oi ${sc}"><div class="od"></div><div class="oc">${o.kodas}</div><span class="ost ${sl}">${st}</span><div class="otm">${tm}</div><button class="btn btn-d btn-sm" onclick="lkDel('${o.kodas}')">✕</button></div>`;
  }).join('');
}
async function lkDel(k){if(!confirm('Ištrinti "'+k+'"?'))return;await api('DELETE','/api/lakstai/'+k);lkOrders=lkOrders.filter(o=>o.kodas!==k);lkStats();rlkList();toast('Ištrinta');}
function askStage(){
  const n=document.getElementById('stageInp').value.trim();
  if(!n){toast('Įvesk etapo pavadinimą!',true);return;}
  if(!lkOrders.length){toast('Nėra užsakymų',true);return;}
  pendingSt=n;const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length;
  document.getElementById('stMn').textContent='Etapas: "'+n+'"';
  document.getElementById('stMs').innerHTML='Iš viso: <strong>'+t+'</strong><br>Surinkta: <strong>'+c+'</strong><br>Perduota: <strong>'+d+'</strong><br>Laukia: <strong>'+(t-c)+'</strong>';
  document.getElementById('stModal').style.display='flex';
}
async function confirmStage(){
  CM('stModal');
  const r=await api('POST','/api/lakstai/archive',{pavadinimas:pendingSt});
  if(r.success){lkOrders=[];document.getElementById('stageInp').value='';lkStats();rlkList();await loadStages();beep('del');toast('Archyvuota: "'+r.archiveName+'"');lkRes('ra','ARCHYVUOTA',r.archiveName,r.collected+'/'+r.total+' surinkta');}
  else toast(r.message||'Klaida',true);
  focusScan();
}

// ════ SANDĖLIS ════
async function loadStock(){try{const r=await api('GET','/api/sandelis');stock=r.stock||[];rStock();document.getElementById('stkBdg').textContent=stock.length;}catch(e){}}
async function loadHist(){try{const r=await api('GET','/api/sandelis/istorija');history=r.history||[];rHist();}catch(e){}}

function rStock(){
  const el=document.getElementById('stkTbl'),su=document.getElementById('stkSum');
  if(!stock.length){el.innerHTML='<div class="empty-s">Sandėlis tuščias</div>';su.innerHTML='';return;}
  const totVnt=stock.reduce((s,r)=>s+r.likoVnt,0);
  const totKg=stock.reduce((s,r)=>s+r.likoKg,0);
  const totT=Math.round(totKg/10)/100;
  const totVal=stock.reduce((s,r)=>s+r.verte,0);
  const byT={};stock.forEach(r=>{if(!byT[r.storis])byT[r.storis]={vnt:0,kg:0};byT[r.storis].vnt+=r.likoVnt;byT[r.storis].kg+=r.likoKg;});
  su.innerHTML=`<div class="stk-s"><div class="stk-n">${totVnt}</div><div class="stk-l">Viso vnt.</div></div><div class="stk-s"><div class="stk-n">${totKg.toFixed(1)}</div><div class="stk-l">Viso kg</div></div><div class="stk-s"><div class="stk-n" style="color:var(--gn)">${totT}</div><div class="stk-l">Tonos</div></div><div class="stk-s"><div class="stk-n" style="color:var(--or)">${totVal.toFixed(2)}</div><div class="stk-l">Vertė €</div></div>`+
    Object.entries(byT).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).map(([t,v])=>`<div class="stk-s"><div class="stk-n" style="font-size:15px">${v.vnt}vnt</div><div class="stk-l">${t}mm · ${(Math.round(v.kg/10)/100).toFixed(2)}t</div></div>`).join('');
  const sorted=[...stock].sort((a,b)=>a.storis-b.storis);
  el.innerHTML=sorted.map(r=>{
    const nc=r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return`<div class="stk-row"><div><div class="stk-thick">${r.storis}<span>mm</span></div></div><div><div class="stk-dims">${r.matmenys}mm</div><div class="stk-sub">${r.pastabos||''}</div></div><div><div class="stk-num ${nc}">${r.likoVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:13px;color:var(--tx2)">${r.likoKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${r.likoT.toFixed(3)}</div><div class="stk-sub">t</div></div><div><div class="stk-val">${r.verte.toFixed(2)}€</div><div class="stk-sub">${r.kainaKg>0?r.kainaKg+'€/kg':''}</div></div><div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse('${r.id}','${r.storis}mm ${r.matmenys}',${r.likoVnt})">−</button><button class="btn btn-d btn-sm" onclick="delStk('${r.id}')">✕</button></div></div>`;
  }).join('')+`<div class="stk-tot"><div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);font-weight:700">VISO</div><div></div><div><div class="stk-num" style="font-size:13px;color:var(--ac)">${totVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${totKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">${totT}</div><div class="stk-sub">t</div></div><div><div class="stk-val" style="font-size:13px;font-weight:800">${totVal.toFixed(2)}€</div></div><div></div></div>`;
}

function rHist(){
  const el=document.getElementById('histTbl');
  if(!history.length){el.innerHTML='<div class="empty-s">Dar nėra istorijos</div>';return;}
  el.innerHTML=`<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>${history.slice(0,50).map(h=>`<tr><td class="mono" style="font-size:10px;color:var(--tx3)">${h.data}</td><td><span class="hist-act ${h.veiksmas[0]}">${h.veiksmas}</span></td><td class="mono">${h.storis}mm</td><td class="mono" style="color:var(--tx2)">${h.matmenys}</td><td class="mono">${h.kiekis}vnt.</td><td class="num">${h.svorisIšViso.toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

function showRecv(){
  if(settings.defaultPrice)document.getElementById('recP').value=settings.defaultPrice;
  document.getElementById('recvModal').style.display='flex';
}
function rcRecv(){
  const t=parseFloat(document.getElementById('recThk').value)||0,w=parseFloat(document.getElementById('recW').value)||0,l=parseFloat(document.getElementById('recL').value)||0,q=parseInt(document.getElementById('recQ').value)||1,p=parseFloat(document.getElementById('recP').value)||0;
  if(!w||!l){document.getElementById('recPrev').textContent='Įvesk matmenis...';return;}
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100,totT=Math.round(tot/10)/100,val=p>0?Math.round(tot*p*100)/100:0;
  document.getElementById('recPrev').innerHTML=`1 lakštas: <strong style="color:var(--ac)">${we}kg</strong> · ${q}vnt.: <strong style="color:var(--gn)">${tot}kg = ${totT}t</strong>${val>0?' · <strong style="color:var(--or)">'+val+'€</strong>':''}`;
}
async function doRecv(){
  const t=document.getElementById('recThk').value,w=document.getElementById('recW').value,l=document.getElementById('recL').value,q=document.getElementById('recQ').value,p=document.getElementById('recP').value,n=document.getElementById('recN').value;
  if(!w||!l){toast('Įvesk matmenis!',true);return;}
  const r=await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if(r.success){CM('recvModal');await loadStock();await loadHist();toast('Pridėta: '+q+'vnt. × '+t+'mm ('+r.likoT+'t)');}
}
function showUse(id,label,rem){curStockId=id;document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';document.getElementById('useQ').value=1;document.getElementById('useNote').value='';document.getElementById('useModal').style.display='flex';}
async function doUse(){
  const q=parseInt(document.getElementById('useQ').value)||1,n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if(r.success){CM('useModal');await loadStock();await loadHist();toast('Sunaudota: '+q+'vnt. Liko: '+r.likoVnt+'vnt.');}
  else toast('Klaida',true);
}
async function delStk(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/sandelis/'+id);await loadStock();toast('Ištrinta');}
function showSett(){document.getElementById('settP').value=settings.defaultPrice||'';document.getElementById('settL').value=settings.lowAlert||2;document.getElementById('settModal').style.display='flex';}
function saveSett(){settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;settings.lowAlert=parseInt(document.getElementById('settL').value)||2;CM('settModal');localStorage.setItem('sandSettings',JSON.stringify(settings));toast('Nustatymai išsaugoti');}

// ════ ARCHYVAI ════
async function loadStages(){try{const r=await api('GET','/api/etapai');stages=r.stages||[];document.getElementById('archBdg').textContent=stages.length;rStages();}catch(e){}}
function rStages(){
  const el=document.getElementById('stageCards');
  if(!stages.length){el.innerHTML='<div class="empty-s">Dar nėra archyvų</div>';return;}
  el.innerHTML=stages.map(s=>{
    const t=s.total||0,c=s.collected||0,d=s.delivered||0,p=s.pending||(t-c),pct=t>0?Math.round(c/t*100):0;
    return`<div class="scc ${archOpen===s.name?'open':''}" onclick="toggleArch('${s.name.replace(/'/g,"\\'")}')"><div class="scn">${s.name}</div><div class="scst"><div><span class="n">${t}</span><span class="l">Viso</span></div><div><span class="n g">${c}</span><span class="l">Surinkta</span></div><div><span class="n b">${d}</span><span class="l">Perduota</span></div><div><span class="n ${p>0?'r':'g'}">${p}</span><span class="l">Liko</span></div></div><div class="scp"><div class="scpf" style="width:${pct}%"></div></div></div>`;
  }).join('');
}
async function toggleArch(name){
  if(archOpen===name){archOpen=null;closeAd();rStages();return;}
  archOpen=name;rStages();
  document.getElementById('adTitle').textContent=name;
  document.getElementById('adList').innerHTML='<div class="empty-s"><span class="sp"></span> Kraunama...</div>';
  document.getElementById('adBox').style.display='block';
  try{
    const r=await api('GET','/api/etapai/'+encodeURIComponent(name));
    const items=sortLk(r.orders||[]);
    if(!items.length){document.getElementById('adList').innerHTML='<div class="empty-s">Tuščias</div>';return;}
    document.getElementById('adList').innerHTML=items.map(o=>{
      const sc=o.delivered?'sdd':o.collected?'sc':'';const tc=o.delivered?'d':o.collected?'c':'r';const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
      const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(0,16);
      return`<div class="adi ${sc}"><div class="addot"></div><div class="adcode">${o.kodas}</div><span class="adtag ${tc}">${st}</span><div class="adtime">${tm}</div></div>`;
    }).join('');
  }catch(e){}
}
function closeAd(){document.getElementById('adBox').style.display='none';archOpen=null;rStages();}

// ════ DXF ════
async function loadDxfOrds(){try{const r=await api('GET','/api/uzsakymai');dxfOrders=r.orders||[];dxfSum();rOrds();document.getElementById('dxfBdg').textContent=dxfOrders.length;}catch(e){}}
function dxfSum(){
  const t=dxfOrders.length,n=dxfOrders.filter(o=>o.statusas==='Naujas').length,a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length,d=dxfOrders.filter(o=>o.statusas==='Baigtas').length,w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML=`<div class="smc"><div class="smn a">${t}</div><div class="sml">Iš viso</div></div><div class="smc"><div class="smn" style="color:var(--yw)">${n}</div><div class="sml">Nauji</div></div><div class="smc"><div class="smn a">${a}</div><div class="sml">Vykdomi</div></div><div class="smc"><div class="smn" style="color:var(--gn)">${d}</div><div class="sml">Baigti</div></div><div class="smc"><div class="smn a">${w.toFixed(2)}</div><div class="sml">Svoris kg</div></div>`;
}
function dxfFlt(f,b){dxfF=f;document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rOrds();}
function rOrds(){
  const el=document.getElementById('ordsGrid'),q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all')l=l.filter(o=>o.statusas===dxfF);if(q)l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>`<div class="ocard" onclick="openOrd('${o.id}')"><div class="oct"><div class="oid">${o.id}</div><div style="display:flex;gap:4px"><span class="stb ${o.statusas}">${o.statusas}</span><button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd('${o.id}','${o.klientas.replace(/'/g,"\\'")}')">✕</button></div></div><div class="ocli">${o.klientas}</div><div class="ocdesc">${o.aprasymas||'—'}</div><div class="ocm"><div class="ocmi"><span class="v">${o.bendraSvoris.toFixed(3)}</span><span class="l"> kg</span></div><div class="ocmi"><span class="v">${o.detaliuSk}</span><span class="l"> det.</span></div><div class="ocmi"><span class="l">${(o.sukurta||'').slice(0,10)}</span></div></div></div>`).join('');
}
async function quickDelOrd(id,klientas){if(!confirm('Ištrinti "'+klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+id);dxfOrders=dxfOrders.filter(o=>o.id!==id);dxfSum();rOrds();toast('Ištrinta');}
function showNewOrd(){document.getElementById('noModal').style.display='flex';setTimeout(()=>document.getElementById('noC').focus(),100);}
async function createOrd(){
  const c=document.getElementById('noC').value.trim();if(!c){toast('Įvesk klientą!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id){
  const o=dxfOrders.find(x=>x.id===id);if(!o)return;curOrd=o;
  document.getElementById('dvId').textContent=o.id;document.getElementById('dvCli').textContent=o.klientas;document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' · '+o.pastabos:'');
  SW('dv');await loadDets();
}
function back2Ords(){SW('dxf');loadDxfOrds();curArea=0;curContour='';document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';}
async function chSt(){if(!curOrd)return;await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value});toast('Statusas atnaujintas');}
async function delOrd(){if(!curOrd)return;if(!confirm('Ištrinti "'+curOrd.klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+curOrd.id);toast('Ištrinta');back2Ords();}
async function loadDets(){
  if(!curOrd)return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[];rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
}

function rDets(){
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nėra detalių</div>';return;}
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const groups={};
  dxfDets.forEach(d=>{const t=String(d.storis);if(!groups[t])groups[t]={t,dets:[],w:0,q:0};groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;});
  let rows='';let idx=0;
  Object.values(groups).forEach(g=>{
    rows+=`<tr class="det-grp-hdr"><td colspan="2"></td><td colspan="2"><span class="det-grp-t">${g.t}mm</span></td><td><span class="det-grp-s">${g.dets.length}det.</span></td><td><span class="det-grp-s">${g.q}vnt.</span></td><td><span class="det-grp-s" style="color:var(--ac)">${g.w.toFixed(3)}kg</span></td><td></td></tr>`;
    g.dets.forEach(d=>{
      idx++;
      rows+=`<tr><td class="mono" style="color:var(--tx3);font-size:10px">${idx}</td><td style="font-weight:600">${d.pavadinimas}</td><td><select class="det-inp" onchange="updDet('${d.detId}','storis',this.value)">${STORIAI.map(t=>`<option value="${t}"${d.storis===t?' selected':''}>${t}mm</option>`).join('')}</select></td><td class="mono" style="font-size:11px;color:var(--tx2)">${calcDims(d)}</td><td><input type="number" class="det-inp" value="${d.kiekis}" min="1" style="width:50px" onchange="updDet('${d.detId}','kiekis',this.value)"></td><td><input type="number" class="det-inp num" value="${d.svoris.toFixed(3)}" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-${d.detId}" onchange="updDetW('${d.detId}',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td><td><button class="btn btn-d btn-sm" onclick="delDet('${d.detId}')">✕</button></td></tr>`;
    });
  });
  w.innerHTML=`<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">${tq}vnt.</strong></span><span>Bendras svoris: <span class="tot">${tw.toFixed(3)}kg</span></span></div>`;
}

async function updDet(detId,field,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  if(field==='storis')d.storis=parseFloat(value);else if(field==='kiekis')d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  const wEl=document.getElementById('w-'+detId);if(wEl)wEl.value=d.svoris.toFixed(3);
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas});
}
async function updDetW(detId,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
function _updateTotals(){
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  document.getElementById('dvWt').textContent=tw.toFixed(3);
}
async function delDet(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/detales/'+id);dxfDets=dxfDets.filter(d=>d.detId!==id);rDets();_updateTotals();toast('Ištrinta');}

// DXF ĮKĖLIMAS
function handleDxf(e){if(e.target.files.length)handleMultiDxf(Array.from(e.target.files));}
function handleFolder(e){
  if(!e.target.files.length)return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failų!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' → '+ft+'mm, '+files.length+' failų',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files){
  if(!curOrd){toast('Pirma atidaryk užsakymą!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Įkeliama '+files.length+' failų...';
  for(const file of files){
    await new Promise(resolve=>{
      const r=new FileReader();
      r.onload=async e2=>{
        try{
          const res=pDxf(e2.target.result);
          if(res.areaCm2<=0){fail++;resolve();return;}
          const at=thickFromName(file.name)||defThick;
          const aq=qtyFromName(file.name)||defQty;
          const ctour=serializeContour(res.entities,res.dimW,res.dimH);
          const resp=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:file.name.replace(/[.]dxf$/i,''),storis:at,plotas:res.areaCm2,kiekis:aq,konturas:ctour});
          if(resp.success)ok++;else fail++;
        }catch(ex){fail++;}
        resolve();
      };
      r.readAsText(file);
    });
  }
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Tempk DXF failus čia arba spusk';
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?`Įkelta: ${ok}, nepavyko: ${fail}`:`Sėkmingai įkeltos ${ok} detalės!`);
}
function procDxf(file){
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2;
      curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name);const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq)document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
      toast('DXF: '+res.areaCm2.toFixed(2)+'cm²'+(at?' · '+at+'mm':''));
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm² · '+t+'mm × '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd)return;if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd)return;const a=parseFloat(document.getElementById('mArea').value)||0;if(a<=0){toast('Įvesk plotą!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:''});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}

// ATASKAITA
function setPeriod(days){
  const to=new Date(),from=new Date();
  if(days===0)from.setDate(1);else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep(){
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpį!',true);return;}
  const r=await api('GET',`/api/ataskaita?nuo=${from}&iki=${to}`);
  const el=document.getElementById('repOut');
  el.style.display='block';
  el.innerHTML=`<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: ${from} — ${to}</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.lakstai.gauta}</div><div class="l">Lakštų gauta</div></div><div class="rep-sc"><div class="n">${r.lakstai.surinkta}</div><div class="l">Surinkta</div></div><div class="rep-sc"><div class="n">${r.lakstai.perduota}</div><div class="l">Perduota</div></div><div class="rep-sc"><div class="n">${r.dxf.sk}</div><div class="l">DXF užsakymų</div></div><div class="rep-sc"><div class="n">${r.dxf.svoris.toFixed(1)}</div><div class="l">DXF svoris kg</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio judėjimas</div><div class="rep-sr"><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.sandelis.gautaKg.toFixed(1)}</div><div class="l">Gauta kg</div></div><div class="rep-sc"><div class="n" style="color:var(--rd)">${r.sandelis.sunaudotaKg.toFixed(1)}</div><div class="l">Sunaudota kg</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.gautaVerte.toFixed(2)}</div><div class="l">Gauta vertė €</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.sunaudotaVerte.toFixed(2)}</div><div class="l">Sunaudota €</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio likutis dabar</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.likutis.vnt}</div><div class="l">Viso vnt.</div></div><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.likutis.t}</div><div class="l">Tonos</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.likutis.verte.toFixed(2)}</div><div class="l">Vertė €</div></div></div></div></div>`;
}

// SPAUSDINIMAS
function printOrd(){
  if(!curOrd)return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return`<tr><td style="font-weight:700;color:#1e3a5f">${t}mm</td><td style="text-align:center">${dets.length}</td><td style="text-align:center">${gq}</td><td style="text-align:right;font-weight:700">${gw.toFixed(3)}</td></tr>`;}).join('');
  let html=`<div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div><div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">${totW.toFixed(3)} kg</div></div><div><div class="ppi-l">Viso detalių</div><div class="ppi-v">${totQ} vnt.</div></div><div><div class="ppi-l">Storių sk.</div><div class="ppi-v">${groups.size} storiai</div></div></div><table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>${sumRows}<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">${sorted.length}</td><td style="text-align:center">${totQ}</td><td style="text-align:right">${totW.toFixed(3)}</td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>Išspausdinta: ${now}</span><span>${curOrd.id}</span></div>`;
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>`<tr><td>${i+1}</td><td><strong>${d.pavadinimas}</strong></td><td style="text-align:center">${calcDims(d)}</td><td style="text-align:center">${d.kiekis}</td><td style="text-align:right"><strong>${d.svoris.toFixed(3)}</strong></td><td style="text-align:center;vertical-align:middle">${drawContourSvg(d.konturas,12)}</td></tr>`).join('');
    html+=`<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">${thick}mm</div></div><div class="ppinfo"><div><div class="ppi-l">Svoris (${thick}mm)</div><div class="ppi-v">${gw.toFixed(3)} kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">${gq}vnt. (${dets.length}poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">${now}</div></div></div><table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>${rows}<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">${gq}vnt.</td><td style="text-align:right">${gw.toFixed(3)}kg</td><td></td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>${thick}mm · ${dets.length}poz. · ${gq}vnt. · ${gw.toFixed(3)}kg</span><span>${curOrd.id}</span></div></div>`;
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}

function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  const s='<style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style>';
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'+s+'</head><body>'+c+'</body>');
  w.document.close();
  setTimeout(function(){w.print();},500);
}

function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}

// Nustatymų įkėlimas
const savedSett=localStorage.getItem('sandSettings');
if(savedSett)try{settings=JSON.parse(savedSett);}catch(e){}

async function siustiEmail(){
  const btn=document.getElementById('emailBtn');
  btn.textContent='Siunčiama...';btn.disabled=true;
  try{
    const r=await fetch('/api/email/siusti',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const d=await r.json();
    if(d.success){alert('✓ '+d.message);}
    else{alert('Klaida: '+(d.detail||d.message));}
  }catch(e){alert('Klaida: '+e.message);}
  btn.textContent='✉ Siųsti ataskaitą';btn.disabled=false;
}

"""

_HTML = """<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0969da">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sandelis">
<link rel="manifest" href="/manifest.json">
<title>Sandelio Sistema</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
<nav>
  <div class="brand"><div class="brand-ico"></div>SANDELIS</div>
  <div class="tabs">
    <button class="tab active" onclick="SW('lk')" id="tab-lk">Lakstai <span class="bdg" id="lkBdg">0</span></button>
    <button class="tab" onclick="SW('stk')" id="tab-stk">Sandelis <span class="bdg y" id="stkBdg">0</span></button>
    <button class="tab" onclick="SW('dxf')" id="tab-dxf">DXF <span class="bdg gray" id="dxfBdg">0</span></button>
    <button class="tab" onclick="SW('arch')" id="tab-arch">Archyvai <span class="bdg gray" id="archBdg">0</span></button>
    <button class="tab" onclick="SW('rep')" id="tab-rep">Ataskaita</button>
  </div>
  <div class="nav-r"><div class="dot ok" id="connDot"></div></div>
</nav>

<div class="view active" id="view-lk">
  <div class="lk-wrap">
    <div class="lk-main">
      <div class="card">
        <div class="ct">Skanavimas</div>
        <div class="scan-f"><span class="scan-ico">▦</span><input class="scan-inp" id="scanInp" placeholder="Skanuok arba ivesk koda..." autocomplete="off" spellcheck="false"></div>
        <div class="hint" id="scanHint">Laukiama skanavimo...</div>
        <div class="steps"><div class="step s1"></div><div class="step s2"></div><div class="step s3"></div></div>
        <div class="step-lbl"><span>1x Registruota</span><span>2x Surinkta</span><span>3x Perduota</span></div>
      </div>
      <div class="res" id="lkRes" style="display:none"><div class="rt" id="lkRt"></div><div class="rc" id="lkRc"></div><div class="rs" id="lkRs"></div></div>
      <div class="stats-row">
        <div class="stat"><div class="sn a" id="lkT">0</div><div class="sl">Is viso</div></div>
        <div class="stat"><div class="sn g" id="lkC">0</div><div class="sl">Surinkta</div></div>
        <div class="stat"><div class="sn b" id="lkD">0</div><div class="sl">Perduota</div></div>
        <div class="stat"><div class="sn y" id="lkP">0</div><div class="sl">Laukia</div></div>
      </div>
      <div class="prog-card">
        <div class="pt"><span>Progresas</span><span class="pct" id="lkPct">0%</span></div>
        <div class="ptr"><div class="pfd" id="lkPfd" style="width:0%"></div><div class="pfc" id="lkPfc" style="width:0%"></div></div>
      </div>
      <div class="stbar">
        <span class="stbar-lbl">Naujas etapas:</span>
        <input type="text" id="stageInp" placeholder="pvz. Etapas 221">
        <button class="btn btn-p btn-sm" onclick="askStage()">Archyvuoti</button>
      </div>
    </div>
    <div class="lk-sb">
      <div class="sbh">
        <div class="sbt">Uzsakymai</div>
        <button class="btn btn-g btn-sm" onclick="loadLk()">&#x21BB;</button>
        <button id="pdfBtn" class="btn btn-s btn-sm" onclick="genPdfReport()">&#x22C6; Atsisiusti PDF</button>
        <div class="sbsr"><span class="sbs-i">&#x2315;</span><input type="text" id="lkSrch" placeholder="Ieskoti..." oninput="rlkList()"></div>
      </div>
      <div class="frow">
        <button class="fb active" onclick="lkFlt('all',this)">Visi</button>
        <button class="fb" onclick="lkFlt('p',this)">Laukia</button>
        <button class="fb" onclick="lkFlt('c',this)">Surinkti</button>
        <button class="fb" onclick="lkFlt('d',this)">Perduoti</button>
      </div>
      <div class="olist" id="lkList"><div class="empty-s">Jungiamasi...</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-stk">
  <div class="page-wrap">
    <div class="ph"><div><div class="ph-t">Metalo sandelis</div><div class="ph-s">Lakstu likuciai pagal stori</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-s btn-sm" onclick="showSett()">Nustatymai</button>
        <button class="btn btn-p" onclick="showRecv()">+ Gauti lakstus</button>
      </div>
    </div>
    <div class="stk-sum" id="stkSum"></div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Likutis</span><button class="btn btn-s btn-sm" onclick="loadStock()">&#x21BB;</button></div>
      <div id="stkTbl"><div class="empty-s">Sandelis tuscias</div></div>
    </div>
    <div class="card" style="overflow:hidden;padding:0;margin-top:12px">
      <div class="card-h"><span class="card-t">Istorija</span><button class="btn btn-s btn-sm" onclick="loadHist()">&#x21BB;</button></div>
      <div id="histTbl"><div class="empty-s">Dar nera istorijos</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-dxf">
  <div class="page-wrap">
    <div class="ph"><div class="ph-t">DXF Uzsakymai</div><button class="btn btn-p" onclick="showNewOrd()">+ Naujas</button></div>
    <div class="sumr" id="dxfSum"></div>
    <div class="fbar">
      <button class="fb active" onclick="dxfFlt('all',this)">Visi</button>
      <button class="fb" onclick="dxfFlt('Naujas',this)">Nauji</button>
      <button class="fb" onclick="dxfFlt('Vykdomas',this)">Vykdomi</button>
      <button class="fb" onclick="dxfFlt('Baigtas',this)">Baigti</button>
      <input class="si" id="dxfSrch" placeholder="Ieskoti..." oninput="rOrds()">
    </div>
    <div class="og" id="ordsGrid"><div class="empty-s">Jungiamasi...</div></div>
  </div>
</div>

<div class="view" id="view-dv">
  <div class="page-wrap">
    <div class="back" onclick="back2Ords()">&#x2190; Grizti</div>
    <div class="card" style="margin-bottom:12px">
      <div class="oi-top">
        <div><div class="oid" id="dvId"></div><div class="oi-t" id="dvCli"></div><div class="oi-s" id="dvDsc"></div></div>
        <div style="text-align:right">
          <div class="wbig" id="dvWt">0</div><div class="wlbl">kg bendras svoris</div>
          <div style="margin-top:8px;display:flex;gap:5px;justify-content:flex-end;flex-wrap:wrap">
            <select class="stsel" id="dvSt" onchange="chSt()"><option>Naujas</option><option>Vykdomas</option><option>Baigtas</option></select>
            <button class="btn btn-p btn-sm" onclick="printOrd()">Spausdinti</button>
            <button class="btn btn-d btn-sm" onclick="delOrd()">Trinti</button>
          </div>
        </div>
      </div>
      <div id="dvMeta" style="font-size:11px;color:#57606a;font-family:'JetBrains Mono',monospace;margin-top:6px"></div>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Prideti detale is DXF</div>
      <div class="dropz" id="dropZ">
        <input type="file" id="dxfFile" accept=".dxf" multiple onchange="handleDxf(event)">
        <div class="dz-t">Tempk DXF failus cia arba spusk</div>
        <div class="dz-s">.dxf - galima ikelti kelis failus</div>
      </div>
      <div style="margin-top:8px">
        <label class="btn btn-s btn-sm" style="cursor:pointer">Ikelti aplanka<input type="file" id="dxfFolder" webkitdirectory multiple accept=".dxf" style="display:none" onchange="handleFolder(event)"></label>
      </div>
      <div class="cvw" id="cvW" style="display:none"><canvas id="dxfCv"></canvas></div>
      <div class="pf" id="pForm" style="display:none">
        <div class="wp"><div class="wv" id="wPv">0.000</div><div class="wl">kg (vieno vnt.)</div><div class="wa" id="wAr"></div></div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="dName"></div>
          <div><label class="fl">Storis (mm)</label><select id="dThk" onchange="rcW();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Kiekis</label><input type="number" id="dQty" value="1" min="1" oninput="rcW()"></div>
        </div>
        <button class="btn btn-p" style="width:100%" onclick="addDet()">+ Prideti detale</button>
      </div>
      <div class="msec">
        <div class="mlbl">arba ivesk rankiniu budu</div>
        <div class="fgrid">
          <div><label class="fl">Pavadinimas</label><input type="text" id="mName"></div>
          <div><label class="fl">Storis (mm)</label><select id="mThk" onchange="rcM();localStorage.setItem('lastThick',this.value)"><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="8">8</option><option value="10">10</option><option value="12">12</option><option value="14">14</option><option value="15">15</option><option value="16">16</option><option value="18">18</option><option value="20">20</option><option value="25">25</option></select></div>
          <div><label class="fl">Plotas (cm2)</label><input type="number" id="mArea" step="0.01" oninput="rcM()"></div>
        </div>
        <div class="fgrid">
          <div><label class="fl">Kiekis</label><input type="number" id="mQty" value="1" min="1" oninput="rcM()"></div>
          <div><label class="fl">Svoris</label><div class="svor-d" id="mWp">0.000 kg</div></div>
          <div style="display:flex;align-items:flex-end"><button class="btn btn-p" style="width:100%" onclick="addMDet()">+ Prideti</button></div>
        </div>
      </div>
    </div>
    <div class="card" style="overflow:hidden;padding:0">
      <div class="card-h"><span class="card-t">Detaliu sarasas</span><button class="btn btn-s btn-sm" onclick="loadDets()">&#x21BB;</button></div>
      <div id="dtWrap"><div class="empty-s">Dar nera detaliu</div></div>
    </div>
  </div>
</div>

<div class="view" id="view-arch">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Archyvai</div>
    <div class="sc-grid" id="stageCards"><div class="empty-s">Dar nera archivu</div></div>
    <div class="adbox" id="adBox" style="display:none">
      <div class="adh"><div class="adt" id="adTitle"></div><button class="btn btn-s btn-sm" onclick="closeAd()">X</button></div>
      <div class="adlist" id="adList"></div>
    </div>
  </div>
</div>

<div class="view" id="view-rep">
  <div class="page-wrap">
    <div class="ph-t" style="margin-bottom:14px">Ataskaita</div>
    <div class="card" style="margin-bottom:12px">
      <div class="ct">Laikotarpis</div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr;margin-bottom:10px">
        <div><label class="fl">Nuo</label><input type="date" id="repFrom"></div>
        <div><label class="fl">Iki</label><input type="date" id="repTo"></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
        <button class="btn btn-s btn-sm" onclick="setPeriod(7)">7 dienos</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(30)">30 dienu</button>
        <button class="btn btn-s btn-sm" onclick="setPeriod(0)">Sis menuo</button>
      </div>
      <button class="btn btn-p" onclick="genRep()">Generuoti</button>
    </div>
    <div id="repOut" style="display:none"></div>
  </div>
</div>

<div class="mbg" id="noModal" style="display:none">
  <div class="modal">
    <div class="mh">Naujas DXF uzsakymas</div>
    <div class="mf">
      <div><label class="fl">Klientas *</label><input type="text" id="noC"></div>
      <div><label class="fl">Aprasymas</label><input type="text" id="noD"></div>
      <div><label class="fl">Pastabos</label><textarea id="noN"></textarea></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('noModal')">Atsaukti</button><button class="btn btn-p" onclick="createOrd()">Sukurti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="recvModal" style="display:none">
  <div class="modal">
    <div class="mh">Gauti lakstus</div>
    <div class="mf">
      <div><label class="fl">Storis (mm)</label><select id="recThk"><option value="3">3 mm</option><option value="4">4 mm</option><option value="5">5 mm</option><option value="6">6 mm</option><option value="8">8 mm</option><option value="10">10 mm</option><option value="12">12 mm</option><option value="14">14 mm</option><option value="15">15 mm</option><option value="16">16 mm</option><option value="18">18 mm</option><option value="20">20 mm</option><option value="25">25 mm</option></select></div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Plotis (mm)</label><input type="number" id="recW" oninput="rcRecv()"></div>
        <div><label class="fl">Ilgis (mm)</label><input type="number" id="recL" oninput="rcRecv()"></div>
      </div>
      <div class="fgrid" style="grid-template-columns:1fr 1fr">
        <div><label class="fl">Kiekis (vnt.)</label><input type="number" id="recQ" value="1" oninput="rcRecv()"></div>
        <div><label class="fl">Kaina / t (EUR)</label><input type="number" id="recP" step="0.01" oninput="rcRecv()"></div>
      </div>
      <div class="rec-prev" id="recPrev">Ivesk matmenis...</div>
      <div><label class="fl">Pastabos (SF nr.)</label><input type="text" id="recN"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('recvModal')">Atsaukti</button><button class="btn btn-p" onclick="doRecv()">Prideti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="useModal" style="display:none">
  <div class="modal">
    <div class="mh">Sunaudoti lakstus</div>
    <div class="mf">
      <div id="useInfo" class="rec-prev"></div>
      <div><label class="fl">Kiek vnt.?</label><input type="number" id="useQ" value="1" min="1"></div>
      <div><label class="fl">Pastabos</label><input type="text" id="useNote"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('useModal')">Atsaukti</button><button class="btn btn-y" onclick="doUse()">Sunaudoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="settModal" style="display:none">
  <div class="modal">
    <div class="mh">Nustatymai</div>
    <div class="mf">
      <div><label class="fl">Numatyta kaina / kg (EUR)</label><input type="number" id="settP" step="0.01"></div>
      <div><label class="fl">Zemos atsargos ispejimas</label><input type="number" id="settL" value="2" min="0"></div>
      <div class="mb"><button class="btn btn-s" onclick="CM('settModal')">Atsaukti</button><button class="btn btn-p" onclick="saveSett()">Issaugoti</button></div>
    </div>
  </div>
</div>

<div class="mbg" id="stModal" style="display:none">
  <div class="modal">
    <div class="mh">Archyvuoti etapa?</div>
    <div id="stMn" style="font-size:11px;color:#57606a;margin-bottom:10px"></div>
    <div id="stMs" class="rec-prev" style="margin-bottom:12px;line-height:2"></div>
    <div class="mb"><button class="btn btn-s" onclick="CM('stModal')">Atsaukti</button><button class="btn btn-p" onclick="confirmStage()">Archyvuoti</button></div>
  </div>
</div>

<div class="pmb" id="printMod" style="display:none">
  <div class="pm">
    <div class="pbr">
      <button class="btn btn-p btn-sm" onclick="window.print()">Spausdinti</button>
      <button class="btn btn-s btn-sm" onclick="dlPdf()">PDF</button>
      <button class="btn btn-s btn-sm" onclick="CM('printMod')">Uzdaryti</button>
    </div>
    <div id="printArea"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const STORIAI=[3,4,5,6,8,10,12,14,15,16,18,20,25];
const TANKIS=8000;
</script>
<script src="/static/js/dxf.js"></script>
<script src="/static/js/main.js"></script>
</body>
</html>"""

@app.on_event("startup")
def startup():
    init_db()

@app.get("/static/css/main.css")
async def serve_css():
    return Response(content=_CSS, media_type="text/css")

@app.get("/static/js/dxf.js")
async def serve_dxfjs():
    return Response(content=_DXFJS, media_type="application/javascript")

@app.get("/static/js/main.js")
async def serve_mainjs():
    return Response(content=_MAINJS, media_type="application/javascript")

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({"name":"Sandelio Sistema","short_name":"Sandelis","start_url":"/","display":"standalone","background_color":"#f6f8fa","theme_color":"#0969da"})

@app.get("/sw.js")
async def sw():
    return Response(content="// sw", media_type="application/javascript")

@app.get("/icon.png")
async def icon():
    import base64
    return Response(content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="), media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=_HTML)


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
        raise HTTPException(400, "SMTP_PASS nenurodytas Railway Variables")
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti = [l for l in items if l.surinkta and not l.perduota]
    perduoti = [l for l in items if l.perduota]
    laukia = [l for l in items if not l.surinkta]
    def rows(lst, color):
        if not lst: return "<tr><td colspan=2 style='color:#aaa;padding:4px 8px'>Tuscia</td></tr>"
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else '-'}</td></tr>" for l in lst)
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
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
      <table width='100%' style='border-collapse:collapse;background:white'><tr><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th><th style='text-align:left;padding:4px 8px;background:#fff8c5'>Kodas</th></tr>{rows(laukia,'#9a6700')}</table>
      <p style='color:#57606a;font-size:11px;margin-top:16px'>Issiusta is Sandelio sistemos - metalcraft.lt</p>
    </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandelio ataskaita {now}"
        msg["From"] = f"Metalcraft <{smtp_user}>"
        msg["To"] = gaivejas
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        # Bandome 587 su STARTTLS
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        except Exception as e1:
            # Bandome 465 su SSL
            with smtplib.SMTP_SSL(smtp_host, 465, timeout=30) as s:
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, gaivejas, msg.as_string())
        return {"success": True, "message": f"Issiusta i {gaivejas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# LAKŠTAI API
# ══════════════════════════════════════════════════

@app.get("/api/lakstai")
def get_lakstai(etapas: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lakstai)
    if etapas:
        q = q.filter(Lakstai.etapas == etapas)
    else:
        q = q.filter(Lakstai.etapas == None)
    items = q.all()
    return {"orders": [_lk(l) for l in items]}

@app.get("/api/lakstai/find/{kodas}")
def find_lakstas(kodas: str, db: Session = Depends(get_db)):
    l = db.query(Lakstai).filter(Lakstai.kodas == kodas).first()
    if not l:
        return {"found": False}
    return {"found": True, **_lk(l)}

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
        return {"success": False, "message": "Nėra užsakymų"}
    total = len(items); collected = sum(1 for l in items if l.surinkta); delivered = sum(1 for l in items if l.perduota)
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

# ══════════════════════════════════════════════════
# DXF API
# ══════════════════════════════════════════════════

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
    d = Detale(det_id=det_id, uzsakymo_id=data["uzsakymoId"], pavadinimas=data.get("pavadinimas", "Detalė"),
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

# ══════════════════════════════════════════════════
# SANDĖLIS API
# ══════════════════════════════════════════════════

@app.get("/api/sandelis")
def get_sandelis(db: Session = Depends(get_db)):
    items = db.query(Sandelis).order_by(Sandelis.storis).all()
    return {"stock": [_stk(s) for s in items]}

@app.post("/api/sandelis/gauti")
def gauti(data: dict, db: Session = Depends(get_db)):
    storis = float(data["storis"]); w = float(data["plotis"]); l = float(data["ilgis"]); qty = int(data["kiekis"])
    kaina = float(data.get("kaina", 0))
    svoris_vnt = round((w/1000) * (l/1000) * (storis/1000) * TANKIS, 2)
    liko_kg = round(svoris_vnt * qty, 2)
    liko_t = round(liko_kg / 1000, 3)
    verte = round(liko_t * kaina, 2)  # kaina uz tona
    stk_id = "STK-" + str(int(datetime.utcnow().timestamp() * 1000))
    s = Sandelis(stk_id=stk_id, storis=storis, matmenys=f"{int(w)}×{int(l)}", svoris_vnt=svoris_vnt,
                 gauta_vnt=qty, liko_vnt=qty, liko_kg=liko_kg, liko_t=liko_t, kaina_kg=kaina, verte=verte,
                 pastabos=data.get("pastabos", ""))
    db.add(s)
    hist = SandelioIstorijia(veiksmas="Gauta", storis=storis, matmenys=f"{int(w)}×{int(l)}", kiekis=qty,
                              svoris_vnt=svoris_vnt, svoris_iš_viso=liko_kg, kaina_kg=kaina, verte=verte, pastabos=data.get("pastabos", ""))
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
    s.verte = round(s.liko_t * s.kaina_kg, 2)  # kaina uz tona
    hist = SandelioIstorijia(veiksmas="Sunaudota", storis=s.storis, matmenys=s.matmenys, kiekis=qty,
                              svoris_vnt=s.svoris_vnt, svoris_iš_viso=round(qty*s.svoris_vnt, 2),
                              kaina_kg=s.kaina_kg, verte=round((qty*s.svoris_vnt/1000)*s.kaina_kg, 2), pastabos=data.get("pastabos", ""))
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
    return {"history": [{"data": h.data.strftime("%Y-%m-%d %H:%M"), "veiksmas": h.veiksmas, "storis": h.storis,
                          "matmenys": h.matmenys, "kiekis": h.kiekis, "svorisVnt": h.svoris_vnt,
                          "svorisIšViso": h.svoris_iš_viso, "kainaKg": h.kaina_kg, "verte": h.verte} for h in items]}

# ══════════════════════════════════════════════════
# ATASKAITA
# ══════════════════════════════════════════════════

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
            "pagalStori": [{"storis": s.storis, "vnt": s.liko_vnt, "kg": round(s.liko_kg, 1), "t": s.liko_t} for s in sorted(stock, key=lambda x: x.storis)]
        }
    }


# ══════════════════════════════════════════════════
# EL. PAŠTAS
# ══════════════════════════════════════════════════

@app.post("/api/email/siusti")
async def siusti_email(data: dict, db: Session = Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    smtp_host = os.getenv("SMTP_HOST", "vytis.serveriai.lt")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "info@metalcraft.lt")
    smtp_pass = os.getenv("SMTP_PASS", "")
    gavėjas   = os.getenv("EMAIL_TO", "gintaras@metalikalt.eu")
    
    if not smtp_pass:
        raise HTTPException(400, "SMTP slaptažodis nenurodytas")
    
    # Gauti lakštus
    items = db.query(Lakstai).filter(Lakstai.etapas == None).all()
    surinkti  = [l for l in items if l.surinkta and not l.perduota]
    perduoti  = [l for l in items if l.perduota]
    laukia    = [l for l in items if not l.surinkta]
    
    # HTML laiškas
    def rows(lst, color):
        return "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #eee'>{l.kodas}</td><td style='padding:4px 8px;border-bottom:1px solid #eee;color:{color}'>{l.surinkta_kada.strftime('%H:%M') if l.surinkta_kada else ''}</td></tr>" for l in lst)
    
    html = f"""
    <html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>
    <div style='background:#0969da;padding:16px;border-radius:8px 8px 0 0'>
      <h2 style='color:white;margin:0'>Sandėlio ataskaita – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</h2>
    </div>
    <div style='padding:16px;background:#f6f8fa;border-radius:0 0 8px 8px'>
      <p>Iš viso: <strong>{len(items)}</strong> | Surinkta: <strong style='color:#1a7f37'>{len(surinkti)}</strong> | Perduota: <strong style='color:#0969da'>{len(perduoti)}</strong> | Laukia: <strong style='color:#9a6700'>{len(laukia)}</strong></p>
      
      {'<h3 style="color:#1a7f37">✓ Surinkta</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Kodas</th><th style="text-align:left;padding:4px 8px;background:#e6f4ea">Laikas</th></tr>' + rows(surinkti, '#1a7f37') + '</table>' if surinkti else ''}
      
      {'<h3 style="color:#0969da">→ Perduota</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Kodas</th><th style="text-align:left;padding:4px 8px;background:#ddf4ff">Laikas</th></tr>' + rows(perduoti, '#0969da') + '</table>' if perduoti else ''}
      
      {'<h3 style="color:#9a6700">⏳ Laukia</h3><table width="100%" style="border-collapse:collapse;background:white"><tr><th style="text-align:left;padding:4px 8px;background:#fff8c5">Kodas</th><th style="text-align:left;padding:4px 8px;background:#fff8c5">Laikas</th></tr>' + rows(laukia, '#9a6700') + '</table>' if laukia else ''}
      
      <p style='color:#57606a;font-size:12px;margin-top:16px'>Išsiųsta iš Sandėlio sistemos – metalcraft.lt</p>
    </div>
    </body></html>
    """
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sandėlio ataskaita {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        msg["From"]    = f"Metalcraft <{smtp_user}>"
        msg["To"]      = gavėjas
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, gavėjas, msg.as_string())
        
        return {"success": True, "message": f"Išsiųsta į {gavėjas}"}
    except Exception as e:
        raise HTTPException(500, f"Klaida: {str(e)}")


# ══════════════════════════════════════════════════
# PAGALBINĖS FUNKCIJOS
# ══════════════════════════════════════════════════

def _lk(l):
    return {"kodas": l.kodas, "registered": l.registruota.strftime("%Y-%m-%d %H:%M:%S") if l.registruota else "",
            "collected": l.surinkta, "collectedAt": l.surinkta_kada.strftime("%Y-%m-%d %H:%M:%S") if l.surinkta_kada else "",
            "delivered": l.perduota, "deliveredAt": l.perduota_kada.strftime("%Y-%m-%d %H:%M:%S") if l.perduota_kada else ""}

def _uzs(u):
    return {"id": u.uzs_id, "klientas": u.klientas, "aprasymas": u.aprasymas or "", "pastabos": u.pastabos or "",
            "statusas": u.statusas, "bendraSvoris": u.bendras_svoris, "detaliuSk": u.detaliu_sk,
            "sukurta": u.sukurta.strftime("%Y-%m-%d %H:%M:%S") if u.sukurta else ""}

def _det(d):
    return {"detId": d.det_id, "uzsakymoId": d.uzsakymo_id, "pavadinimas": d.pavadinimas,
            "storis": d.storis, "plotas": d.plotas, "kiekis": d.kiekis, "svoris": d.svoris,
            "konturas": d.konturas or "", "prideta": d.prideta.strftime("%Y-%m-%d %H:%M:%S") if d.prideta else ""}

def _stk(s):
    return {"id": s.stk_id, "storis": s.storis, "matmenys": s.matmenys, "svorisVnt": s.svoris_vnt,
            "gautaVnt": s.gauta_vnt, "sunaudotaVnt": s.sunaudota_vnt, "likoVnt": s.liko_vnt,
            "likoKg": s.liko_kg, "likoT": s.liko_t, "kainaKg": s.kaina_kg, "verte": s.verte,
            "prideta": s.prideta.strftime("%Y-%m-%d %H:%M:%S") if s.prideta else "", "pastabos": s.pastabos or ""}

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
