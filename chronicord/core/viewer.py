STYLE = r"""
:root{--bg:#313338;--bg2:#2b2d31;--bg3:#1e1f22;--tx:#dbdee1;--mu:#949ba4;--ac:#5865f2;--ln:#00a8fc}
body.light{--bg:#fff;--bg2:#f2f3f5;--bg3:#e3e5e8;--tx:#313338;--mu:#5c5e66;--ac:#5865f2;--ln:#006ce7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.4 "Segoe UI",system-ui,sans-serif}
a{color:var(--ln);text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:5;background:var(--bg2);border-bottom:1px solid var(--bg3);padding:10px 16px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
header h1{font-size:17px;margin:0 12px 0 0}header .sub{color:var(--mu);font-size:13px}
input,select,button{background:var(--bg3);color:var(--tx);border:1px solid transparent;border-radius:6px;padding:6px 9px;font:inherit;font-size:14px}
button{cursor:pointer;background:var(--ac);color:#fff}button.g{background:var(--bg3);color:var(--tx)}
.wrap{max-width:1100px;margin:0 auto;padding:8px 0 40px}
"""

CHANNEL_HTML = r"""<!doctype html><html lang="__LANG__"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<meta name="generator" content="Chronicord"><style>""" + STYLE + r"""
.m{display:flex;gap:14px;padding:3px 18px;margin-top:14px}.m.c{margin-top:0}.m:hover{background:rgba(0,0,0,.08)}
.av{width:40px;height:40px;border-radius:50%;flex:none;background:var(--ac);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;overflow:hidden}
.av{position:relative}.av img{position:absolute;inset:0;width:100%;height:100%}.m.c .av{visibility:hidden;height:0}
.b{min-width:0;flex:1}.h{display:flex;gap:8px;align-items:baseline}.n{font-weight:600}.t{color:var(--mu);font-size:12px}
.tag{background:var(--ac);color:#fff;font-size:10px;padding:0 4px;border-radius:3px;font-weight:600}
.x{white-space:pre-wrap;word-wrap:break-word}.x code{background:var(--bg3);padding:1px 4px;border-radius:4px;font-family:Consolas,monospace;font-size:13px}
.x pre{background:var(--bg3);padding:8px;border-radius:6px;white-space:pre-wrap;font-family:Consolas,monospace;font-size:13px;margin:4px 0}
.x blockquote{border-left:4px solid var(--mu);margin:2px 0;padding-left:10px}.sp{background:var(--bg3);color:transparent;border-radius:3px;cursor:pointer}.sp.o{color:inherit}
.e{width:22px;height:22px;vertical-align:-5px}.big .e{width:44px;height:44px}
.rp{position:relative;display:flex;align-items:center;gap:5px;color:var(--mu);font-size:13px;margin-top:14px;padding:0 18px 0 72px;cursor:pointer;white-space:nowrap;overflow:hidden}.rp:before{content:"";position:absolute;left:37px;top:50%;width:29px;height:11px;border:2px solid var(--bg3);border-right:0;border-bottom:0;border-top-left-radius:6px}.rp:hover{color:var(--tx)}.rp b{color:var(--tx);font-weight:600;flex:none}.rp .ra{width:16px;height:16px;border-radius:50%;flex:none;object-fit:cover}.rp .rt{overflow:hidden;text-overflow:ellipsis}.m.r{margin-top:2px}
.att img,.att video{max-width:min(420px,100%);max-height:350px;border-radius:8px;display:block;margin-top:4px;cursor:zoom-in}
.file{display:inline-block;background:var(--bg2);border:1px solid var(--bg3);padding:8px 12px;border-radius:8px;margin-top:4px}
.emb{border-left:4px solid var(--bg3);background:var(--bg2);border-radius:4px;padding:8px 12px;margin-top:4px;max-width:520px}
.emb .et{font-weight:600}.emb .ef{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px}.emb .fn{font-weight:600;font-size:13px}.emb .ft{color:var(--mu);font-size:12px;margin-top:6px}.emb img{max-width:100%;border-radius:4px;margin-top:6px}
.stk img{width:160px;height:160px;object-fit:contain;margin-top:4px}.stk span{display:inline-block;margin-top:4px;color:var(--mu)}
.rx{display:flex;gap:4px;flex-wrap:wrap;margin-top:4px}.rx span{background:var(--bg2);border:1px solid var(--bg3);border-radius:8px;padding:1px 7px;font-size:13px}.rx .e{width:16px;height:16px;vertical-align:-3px}
.poll{background:var(--bg2);border:1px solid var(--bg3);border-radius:8px;padding:10px 12px;max-width:460px;margin-top:4px}.poll .q{font-weight:600;margin-bottom:6px}
.pa{position:relative;background:var(--bg3);border-radius:6px;padding:6px 10px;margin:4px 0;overflow:hidden}.pa i{position:absolute;inset:0 auto 0 0;background:var(--ac);opacity:.35}.pa b{position:relative;font-weight:400}.pa s{position:relative;float:right;text-decoration:none;color:var(--mu)}
.sys{color:var(--mu);font-style:italic}.fw{border-left:3px solid var(--mu);padding-left:8px;margin-top:4px}.fw .t{display:block}
.th{display:inline-block;margin-top:4px;background:var(--bg2);border-radius:6px;padding:4px 10px;font-size:13px}
.day{display:flex;align-items:center;gap:8px;color:var(--mu);font-size:12px;margin:20px 18px 6px}.day:before,.day:after{content:"";flex:1;border-top:1px solid var(--bg3)}
.hl{background:rgba(250,168,26,.15)!important}mark{background:#faa81a;color:#000;border-radius:2px}
#pager{display:flex;gap:6px;justify-content:center;padding:16px;flex-wrap:wrap}#info{color:var(--mu);font-size:13px;padding:6px 18px}
#zoom{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}#zoom img{max-width:95%;max-height:95%}
.threads{padding:6px 18px}.threads a{display:block;padding:6px 10px;background:var(--bg2);border-radius:6px;margin:4px 0}
</style></head><body>
<header><h1 id="ttl"></h1><span class="sub" id="sub"></span>
<input id="q" size="18"><select id="u"><option value=""></option></select>
<input type="date" id="d1"><input type="date" id="d2">
<button class="g" id="th"></button><a id="up" href="../index.html"></a></header>
<div class="wrap"><div id="info"></div><div id="threads" class="threads"></div><div id="list"></div><div id="pager"></div></div>
<div id="zoom"><img></div>
<script>
var META=__META__,FILES=__FILES__,ALL=[],BYID={},PAGE=300,cur=0,view=[];
var L=__L__;
var CHR={push:function(a){for(var i=0;i<a.length;i++)ALL.push(a[i]);}};
var AS=(META.assets||"../assets")+"/";
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]});}
function day(ts){return new Date(ts*1000).toLocaleDateString(L.locale,{day:"numeric",month:"long",year:"numeric"});}
function tm(ts){var d=new Date(ts*1000);return d.toLocaleDateString(L.locale)+" "+d.toLocaleTimeString(L.locale,{hour:"2-digit",minute:"2-digit"});}
var SYS=L.sys;
function md(s,em,q){
  var codes=[];s=esc(s);
  s=s.replace(/```(?:\w+\n)?([\s\S]*?)```/g,function(_,c){codes.push("<pre>"+c+"</pre>");return"\u0000"+(codes.length-1)+"\u0000";});
  s=s.replace(/`([^`\n]+)`/g,function(_,c){codes.push("<code>"+c+"</code>");return"\u0000"+(codes.length-1)+"\u0000";});
  s=s.replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/__(.+?)__/g,"<u>$1</u>").replace(/(^|[^*])\*([^*\n]+)\*/g,"$1<i>$2</i>")
     .replace(/~~(.+?)~~/g,"<s>$1</s>").replace(/\|\|(.+?)\|\|/g,'<span class="sp" onclick="this.classList.add(\'o\')">$1</span>')
     .replace(/^&gt; (.*)$/gm,"<blockquote>$1</blockquote>").replace(/^#{1,3} (.*)$/gm,"<b>$1</b>")
     .replace(/\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>')
     .replace(/(^|[\s(])(https?:\/\/[^\s<]+)/g,'$1<a href="$2" target="_blank" rel="noopener">$2</a>');
  if(em)em.forEach(function(e){s=s.split(":"+esc(e.n)+":").join('<img class="e" src="'+AS+e.file+'" alt=":'+esc(e.n)+':" title=":'+esc(e.n)+':">');});
  if(q){var re=new RegExp("("+q.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")(?![^<]*>)","gi");s=s.replace(re,"<mark>$1</mark>");}
  return s.replace(/\u0000(\d+)\u0000/g,function(_,i){return codes[+i];});
}
function emj(r){return r.file?'<img class="e" src="'+AS+r.file+'" alt="'+esc(r.e)+'">':esc(r.e);}
function atts(list){var h="";(list||[]).forEach(function(a){var src="media/"+a.file,ct=a.ct||"";
  if(/^image\//.test(ct)||/\.(png|jpe?g|gif|webp)$/i.test(a.file))h+='<img src="'+src+'" alt="'+esc(a.fn)+'" loading="lazy" onerror="this.replaceWith(\'📎 \'+this.alt)">';
  else if(/^video\//.test(ct))h+='<video src="'+src+'" controls preload="none"></video>';
  else if(/^audio\//.test(ct))h+='<audio src="'+src+'" controls preload="none"></audio>';
  else h+='<a class="file" href="'+src+'" download>📎 '+esc(a.fn)+' <span class="t">'+(a.sz/1048576).toFixed(1)+L.mb+'</span></a>';});
  return h?'<div class="att">'+h+"</div>":"";}
function body(m,q){var h="";
  if(SYS[m.k]&&!m.c)h+='<div class="sys">'+SYS[m.k]+"</div>";
  if(m.c){var big=m.em&&m.c.replace(/:\w+:/g,"").trim()==="";h+='<div class="x'+(big?" big":"")+'">'+md(m.c,m.em,q)+"</div>";}
  (m.fwd||[]).forEach(function(f){h+='<div class="fw"><span class="t">'+L.forwarded+'</span><div class="x">'+md(f.c||"",m.em,q)+"</div>"+atts(f.att)+"</div>";});
  h+=atts(m.att);
  (m.emb||[]).forEach(function(e){h+='<div class="emb"'+(e.col!=null?' style="border-color:#'+("00000"+e.col.toString(16)).slice(-6)+'"':"")+">"+
    (e.au?'<div class="fn">'+esc(e.au)+"</div>":"")+(e.t?'<div class="et">'+(e.u?'<a href="'+esc(e.u)+'" target="_blank" rel="noopener">'+md(e.t)+"</a>":md(e.t))+"</div>":"")+
    (e.d?'<div class="x">'+md(e.d,m.em,q)+"</div>":"")+(e.f?'<div class="ef">'+e.f.map(function(f){return"<div><div class=fn>"+md(f[0])+'</div><div class="x">'+md(f[1],m.em)+"</div></div>";}).join("")+"</div>":"")+
    (e.ft?'<div class="ft">'+esc(e.ft)+"</div>":"")+"</div>";});
  if(m.stk)h+='<div class="stk">'+m.stk.map(function(s){return s.file&&s.f!=3?'<img src="'+AS+s.file+'" alt="'+esc(s.n)+'" title="'+esc(s.n)+'">':"<span>["+L.sticker+": "+esc(s.n)+"]</span>";}).join(" ")+"</div>";
  else if(m.st)h+='<div class="stk"><span>['+L.sticker+': '+m.st.map(esc).join(", ")+"]</span></div>";
  if(m.pl){var tot=0;m.pl.ans.forEach(function(a){tot+=a.n||0;});h+='<div class="poll"><div class="q">📊 '+esc(m.pl.q)+"</div>"+m.pl.ans.map(function(a){var p=tot?Math.round(100*(a.n||0)/tot):0;
    return'<div class="pa"><i style="width:'+p+'%"></i><b>'+(a.e?emj(a)+" ":"")+esc(a.t)+"</b><s>"+(a.n||0)+" · "+p+"%</s></div>";}).join("")+'<div class="t">'+tot+L.votes+(m.pl.multi?L.multi:"")+"</div></div>";}
  else if(m.poll)h+='<div class="poll"><div class="q">📊 '+esc(m.poll)+"</div></div>";
  if(m.th){var t=(META.threads||[]).filter(function(x){return x.id===m.th.id;})[0];h+='<div class="th">🧵 '+(t?'<a href="../'+t.dir+'/index.html">'+esc(m.th.n)+"</a>":esc(m.th.n))+"</div>";}
  if(m.rx)h+='<div class="rx">'+m.rx.map(function(r){return"<span>"+emj(r)+" "+r.n+"</span>";}).join("")+"</div>";
  return h;}
function avatar(a){var l=esc((a.n||"?").charAt(0).toUpperCase());return'<div class="av">'+(a.av?'<img src="'+AS+a.av+'" onerror="this.remove()" loading="lazy" alt="">':"")+l+"</div>";}
function render(){
  var list=document.getElementById("list"),q=document.getElementById("q").value.trim(),h="",prev=null,lastDay="";
  var slice=view.slice(cur*PAGE,(cur+1)*PAGE);
  slice.forEach(function(m){var dd=day(m.ts);if(dd!==lastDay){h+='<div class="day">'+dd+"</div>";lastDay=dd;prev=null;}
    var cont=prev&&!m.rp&&prev.a.id===m.a.id&&m.ts-prev.ts<420;
    if(m.rp){var r=BYID[m.rp];h+='<div class="rp" onclick="go(\''+m.rp+'\')">'+(r?(r.a.av?'<img class="ra" src="'+AS+r.a.av+'" onerror="this.remove()" alt="">':"")+"<b>"+esc(r.a.n)+'</b><span class="rt">'+esc((r.c||L.attachment).replace(/[*_~`|]{1,3}/g,"").replace(/\s+/g," ").slice(0,140))+"</span>":L.unavailable)+"</div>";}
    h+='<div class="m'+(cont?" c":"")+(m.rp?" r":"")+'" id="m'+m.id+'">'+avatar(m.a)+'<div class="b">'+(cont?"":'<div class="h"><span class="n">'+esc(m.a.n)+"</span>"+(m.a.bot?'<span class="tag">'+(m.a.wh?L.webhook:L.bot)+"</span>":"")+'<span class="t">'+tm(m.ts)+(m.ed?L.edited:"")+(m.pin?" 📌":"")+"</span></div>")+body(m,q)+"</div></div>";prev=m;});
  list.innerHTML=h||'<div id="info">'+L.nothing+'</div>';
  var pages=Math.ceil(view.length/PAGE),p="";
  if(pages>1){for(var i=0;i<pages;i++){if(i<2||i>pages-3||Math.abs(i-cur)<3)p+='<button class="'+(i===cur?"":"g")+'" onclick="cur='+i+';render();scrollTo(0,0)">'+(i+1)+"</button>";else if(p.slice(-3)!=="…")p+="…";}}
  document.getElementById("pager").innerHTML=p;
  document.getElementById("info").textContent=L.messages+view.length+(view.length!==ALL.length?L.of+ALL.length:"");}
function go(id){var i=view.findIndex(function(m){return m.id===id;});if(i<0)return;cur=Math.floor(i/PAGE);render();var e=document.getElementById("m"+id);if(e){e.scrollIntoView({block:"center"});e.classList.add("hl");setTimeout(function(){e.classList.remove("hl")},2000);}}
function filter(){var q=document.getElementById("q").value.trim().toLowerCase(),u=document.getElementById("u").value,
  d1=document.getElementById("d1").value,d2=document.getElementById("d2").value,t1=d1?new Date(d1+"T00:00").getTime()/1000:0,t2=d2?new Date(d2+"T23:59:59").getTime()/1000:1e12;
  view=ALL.filter(function(m){if(u&&m.a.id!==u)return false;if(m.ts<t1||m.ts>t2)return false;
    if(q){var s=(m.c||"")+" "+(m.a.n||"")+" "+(m.emb||[]).map(function(e){return(e.t||"")+" "+(e.d||"")}).join(" ")+" "+(m.att||[]).map(function(a){return a.fn}).join(" ")+" "+(m.pl?m.pl.q:"");if(s.toLowerCase().indexOf(q)<0)return false;}return true;});
  cur=0;render();}
function load(i){if(i>=FILES.length){done();return;}var s=document.createElement("script");s.src=FILES[i];s.onload=function(){document.getElementById("info").textContent=L.loading+" "+ALL.length;load(i+1);};
  s.onerror=function(){load(i+1);};document.body.appendChild(s);}
function done(){ALL.forEach(function(m){BYID[m.id]=m;});var users={};ALL.forEach(function(m){users[m.a.id]=m.a.n;});
  var sel=document.getElementById("u");Object.keys(users).sort(function(a,b){return users[a].localeCompare(users[b]);}).forEach(function(id){var o=document.createElement("option");o.value=id;o.textContent=users[id];sel.appendChild(o);});
  view=ALL;var h=location.hash.slice(2);render();if(h)go(h);}
document.getElementById("ttl").textContent=(META.parent?"🧵 ":"#")+(META.channel||"");
document.getElementById("sub").textContent=(META.guild||"")+(META.parent?L["in"]+META.parent:"");
if(META.parent_dir){var up=document.getElementById("up");up.href="../"+META.parent_dir+"/index.html";up.textContent="← #"+META.parent;}else document.getElementById("up").textContent=L.all_channels;
document.getElementById("q").placeholder=L.search;document.getElementById("u").options[0].textContent=L.all_authors;
document.getElementById("d1").title=L.from;document.getElementById("d2").title=L.to;
var thb=document.getElementById("th");thb.textContent=L.theme;thb.title=L.theme_t;document.getElementById("info").textContent=L.loading;
if(META.threads&&META.threads.length)document.getElementById("threads").innerHTML="<b>"+L.threads+"</b>"+META.threads.map(function(t){return'<a href="../'+t.dir+'/index.html">🧵 '+esc(t.n)+"</a>";}).join("");
var tmr;["q","u","d1","d2"].forEach(function(id){document.getElementById(id).addEventListener("input",function(){clearTimeout(tmr);tmr=setTimeout(filter,250);});});
document.getElementById("th").onclick=function(){document.body.classList.toggle("light");try{localStorage.chrTheme=document.body.classList.contains("light")?"l":"d"}catch(e){}};
try{if(localStorage.chrTheme==="l")document.body.classList.add("light")}catch(e){}
document.addEventListener("click",function(e){if(e.target.tagName==="IMG"&&e.target.closest(".att,.emb")){var z=document.getElementById("zoom");z.firstChild.src=e.target.src;z.style.display="flex";}});
document.getElementById("zoom").onclick=function(){this.style.display="none";};
if(FILES.length)load(0);else document.getElementById("info").textContent=META.type==15||META.type==16?L.forum:L.no_msgs;
</script></body></html>
"""

ROOT_HTML = r"""<!doctype html><html lang="__LANG__"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__ARCHIVE__</title>
<meta name="generator" content="Chronicord"><style>""" + STYLE + r"""
.g{margin:18px}.g h2{font-size:13px;text-transform:uppercase;color:var(--mu);letter-spacing:.04em}
.c{display:flex;justify-content:space-between;padding:8px 12px;background:var(--bg2);border-radius:6px;margin:4px 0}
.c.t{margin-left:28px}.c span{color:var(--mu);font-size:13px}
</style></head><body><header><h1>__ARCHIVE__</h1><span class="sub">__MADE__</span></header>
<div class="wrap" id="root"></div><script>
var I=__ITEMS__,L=__L__,by={};function esc(s){return String(s||"").replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]});}
I.forEach(function(x){(by[x.guild]=by[x.guild]||[]).push(x);});
document.getElementById("root").innerHTML=Object.keys(by).map(function(g){return'<div class="g"><h2>'+esc(g)+"</h2>"+by[g].map(function(x){
  var n=(x.parent?"🧵 ":(x.type==15||x.type==16?"💬 ":"#"))+esc(x.channel),cnt="<span>"+(x.count||0)+L.msgs_short+"</span>";
  return'<div class="c'+(x.parent?" t":"")+'">'+(x.html?'<a href="'+encodeURI(x.dir)+'/index.html">'+n+"</a>":n)+cnt+"</div>";}).join("")+"</div>";}).join("")||'<p class="g">'+L.empty+'</p>';
</script></body></html>
"""
