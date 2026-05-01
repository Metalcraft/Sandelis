// DXF PARSERIS
// TANKIS defined in HTML

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
  let sf=1;

  for(let j=0;j<lines.length-1;j++){
    if(lines[j].trim()==='70'&&j>=2&&lines[j-2].trim()==='$INSUNITS'){
      const u=parseInt(lines[j+1]);
      if(u===1)sf=25.4;else if(u===4)sf=1;else if(u===5)sf=10;else if(u===6)sf=1000;else if(u===2)sf=304.8;
    }
  }

  const r4=v=>Math.round(v*10000)/10000;

  function pushSeg(t,v,ox,oy,scx,scy,ang){
    const c=Math.cos(ang),s=Math.sin(ang);
    function tx(x,y){return r4((ox+scx*(x*c-y*s))*sf);}
    function ty(x,y){return r4((oy+scy*(x*s+y*c))*sf);}
    function tr(r){return r4(Math.abs(scx)*r*sf);}
    if(t==='LINE'&&v._x1!==undefined&&v._x2!==undefined){
      segs.push({type:'L',x1:tx(v._x1,v._y1),y1:ty(v._x1,v._y1),x2:tx(v._x2,v._y2),y2:ty(v._x2,v._y2)});
    }else if(t==='CIRCLE'&&v._x1!==undefined&&40 in v){
      segs.push({type:'C',cx:tx(v._x1,v._y1),cy:ty(v._x1,v._y1),r:tr(v[40])});
    }else if((t==='LWPOLYLINE'||t==='POLYLINE')&&v._xs&&v._xs.length>=3){
      segs.push({type:'P',pts:v._xs.map((x,i)=>({x:tx(x,v._ys[i]||0),y:ty(x,v._ys[i]||0)})),closed:((v[70]||0)&1)===1});
    }else if(t==='ARC'&&v._x1!==undefined&&40 in v){
      segs.push({type:'C',cx:tx(v._x1,v._y1),cy:ty(v._x1,v._y1),r:tr(v[40]),arc:true});
    }
  }

  // --- 1 praejimas: BLOCKS sekcija ---
  const blockDefs={};
  let inSection=false,sectionName='',inBlock=false,curBlockName=null,curBlockEnts=null;
  let curType=null,curV={};

  let i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i+=2;continue;}
    const val=(lines[i+1]||'').trim();

    if(code===0&&val==='SECTION'){inSection=true;i+=2;continue;}
    if(code===2&&inSection&&!inBlock){sectionName=val;i+=2;continue;}
    if(code===0&&val==='ENDSEC'){
      if(inBlock&&curBlockEnts)curBlockEnts.push({type:curType,v:curV});
      inSection=false;inBlock=false;curBlockName=null;curBlockEnts=null;curType=null;curV={};
      i+=2;continue;
    }

    if(sectionName!=='BLOCKS'){i+=2;continue;}

    if(code===0&&val==='BLOCK'){
      if(inBlock&&curBlockEnts)curBlockEnts.push({type:curType,v:curV});
      inBlock=true;curBlockName=null;curBlockEnts=[];curType=null;curV={};
      i+=2;continue;
    }
    if(code===0&&val==='ENDBLK'){
      if(inBlock&&curBlockEnts)curBlockEnts.push({type:curType,v:curV});
      if(curBlockName)blockDefs[curBlockName]=curBlockEnts||[];
      inBlock=false;curBlockName=null;curBlockEnts=null;curType=null;curV={};
      i+=2;continue;
    }

    if(!inBlock){i+=2;continue;}

    if(code===2&&curBlockName===null){curBlockName=val;i+=2;continue;}

    if(code===0){
      if(curBlockEnts)curBlockEnts.push({type:curType,v:curV});
      curType=val;curV={};
    }else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'||curType==='INSERT')curV._x1=n;
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'||curType==='INSERT')curV._y1=n;
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11)curV._x2=n;
        else if(code===21)curV._y2=n;
        else if(code===70)curV[70]=parseInt(val)||0;
        else curV[code]=n;
      }else if(code===2&&curType==='INSERT'){
        curV._bname=val;
      }
    }
    i+=2;
  }

  // --- Bloko geometrijos iskleidimas ---
  function expandBlock(ents,ox,oy,scx,scy,ang){
    for(const e of ents){
      if(!e||!e.type)continue;
      if(e.type==='INSERT'&&e.v._bname&&blockDefs[e.v._bname]){
        const iox=e.v._x1||0,ioy=e.v._y1||0;
        const iscx=e.v[41]||1,iscy=e.v[42]||1;
        const iang=(e.v[50]||0)*Math.PI/180;
        const c2=Math.cos(ang),s2=Math.sin(ang);
        const nox=ox+scx*(iox*c2-ioy*s2);
        const noy=oy+scy*(iox*s2+ioy*c2);
        expandBlock(blockDefs[e.v._bname],nox,noy,scx*iscx,scy*iscy,ang+iang);
      }else{
        pushSeg(e.type,e.v,ox,oy,scx,scy,ang);
      }
    }
  }

  // --- 2 praejimas: ENTITIES sekcija ---
  let inE=false;
  curType=null;curV={};
  i=0;
  while(i<lines.length){
    const code=parseInt(lines[i].trim());
    if(isNaN(code)){i+=2;continue;}
    const val=(lines[i+1]||'').trim();
    if(code===2&&val==='ENTITIES'){inE=true;i+=2;continue;}
    if(code===0&&val==='ENDSEC'&&inE){
      if(curType==='INSERT'&&curV._bname&&blockDefs[curV._bname])
        expandBlock(blockDefs[curV._bname],curV._x1||0,curV._y1||0,curV[41]||1,curV[42]||1,(curV[50]||0)*Math.PI/180);
      else pushSeg(curType,curV,0,0,1,1,0);
      break;
    }
    if(!inE){i+=2;continue;}
    if(code===0){
      if(curType==='INSERT'&&curV._bname&&blockDefs[curV._bname])
        expandBlock(blockDefs[curV._bname],curV._x1||0,curV._y1||0,curV[41]||1,curV[42]||1,(curV[50]||0)*Math.PI/180);
      else pushSeg(curType,curV,0,0,1,1,0);
      curType=val;curV={};
    }else{
      const n=parseFloat(val);
      if(!isNaN(n)){
        if(code===10){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'||curType==='INSERT')curV._x1=n;
          else{if(!curV._xs)curV._xs=[];curV._xs.push(n);}
        }else if(code===20){
          if(curType==='LINE'||curType==='CIRCLE'||curType==='ARC'||curType==='INSERT')curV._y1=n;
          else{if(!curV._ys)curV._ys=[];curV._ys.push(n);}
        }else if(code===11)curV._x2=n;
        else if(code===21)curV._y2=n;
        else if(code===70)curV[70]=parseInt(val)||0;
        else curV[code]=n;
      }else if(code===2&&curType==='INSERT'){
        curV._bname=val;
      }
    }
    i+=2;
  }

  // --- Ploto skaiciavimas ---
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

  // --- Matmenys ---
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
