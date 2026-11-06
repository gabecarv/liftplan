"""Walk Commons categories (with subcategories) and keep files dated 1978–1992 with PD/CC0/CC BY licenses."""
import json, os, re, sys, time, urllib.parse, urllib.request
API="https://commons.wikimedia.org/w/api.php"; UA={"User-Agent":"LiftPlan-vintage-fetch/1.0 (github.com/gabecarv/liftplan)"}
CATS=["Category:Weight training","Category:Weightlifting","Category:Weightlifters","Category:Bodybuilding","Category:Fitness centers","Category:Aerobics",
      "Category:Gyms","Category:Exercise equipment","Category:Dumbbells","Category:Barbells","Category:Weight machines","Category:Physical fitness in the United States military",
      "Category:1980s fashion","Category:Personal computers of the 1980s","Category:Offices in the 1980s","Category:Running in the 1980s","Category:Sport in the 1980s","Category:1980s photographs"]
OK=re.compile(r"public domain|cc0|pd-|^cc by( \d\.\d)?$", re.I); YEAR=re.compile(r"(19[7-9]\d)")
def api(params):
    params.update({"format":"json"}); url=API+"?"+urllib.parse.urlencode(params)
    for a in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60) as r: time.sleep(1.2); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(10*(a+1)); continue
            raise
    raise RuntimeError("429")
def members(cat, depth=0, seen=None):
    seen=seen if seen is not None else set(); out=[]
    if cat in seen or depth>2: return out
    seen.add(cat); cont={}
    while True:
        j=api({"action":"query","list":"categorymembers","cmtitle":cat,"cmlimit":200,"cmtype":"file|subcat",**cont})
        for m in j.get("query",{}).get("categorymembers",[]):
            if m["ns"]==6: out.append(m["title"])
            elif m["ns"]==14 and depth<2 and len(out)<600: out+=members(m["title"],depth+1,seen)
        if "continue" in j and len(out)<600: cont=j["continue"]
        else: break
    return out
def info(titles):
    out=[]
    for i in range(0,len(titles),30):
        j=api({"action":"query","prop":"imageinfo","titles":"|".join(titles[i:i+30]),"iiprop":"url|size|extmetadata","iiurlwidth":1024})
        for p in j.get("query",{}).get("pages",{}).values():
            ii=(p.get("imageinfo") or [None])[0]
            if not ii: continue
            em=ii.get("extmetadata",{}); g=lambda k:re.sub("<[^>]+>","",(em.get(k) or {}).get("value",""))
            out.append({"title":p["title"],"thumb":ii.get("thumburl") or ii["url"],"w":ii.get("width"),"license":g("LicenseShortName"),"date":g("DateTimeOriginal")[:40],"desc":g("ImageDescription")[:200],"credit":g("Artist")[:80]})
    return out
def main():
    root=sys.argv[1] if len(sys.argv)>1 else "candidates"; manifest=[]; seen=set()
    for cat in CATS:
        try: titles=[t for t in members(cat) if t not in seen]
        except Exception as e: print("cat fail",cat,e); continue
        seen.update(titles); kept=0
        for it in info(titles):
            yrs=YEAR.findall(it["date"]+" "+it["desc"]+" "+it["title"])
            if not yrs or not any(1978<=int(y)<=1992 for y in yrs): continue
            if not OK.search(it["license"]) or (it["w"] or 0)<500: continue
            slug=re.sub(r"[^A-Za-z0-9]+","_",it["title"].replace("File:",""))[:80]; path=f"{root}/eighties/{slug}.jpg"; os.makedirs(os.path.dirname(path),exist_ok=True)
            try:
                with urllib.request.urlopen(urllib.request.Request(it["thumb"],headers=UA),timeout=60) as r, open(path,"wb") as f: f.write(r.read())
            except Exception as e: print("dl fail",it["title"],e); time.sleep(5); continue
            it.update({"cat":cat,"path":path}); manifest.append(it); kept+=1; time.sleep(2.5)
        print(cat,len(titles),"files,",kept,"kept")
    json.dump(manifest,open(f"{root}/manifest.json","w"),indent=1)
main()
