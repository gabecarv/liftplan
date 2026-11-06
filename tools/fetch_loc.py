"""Search the Library of Congress (loc.gov JSON API, no key) for 1978–1992 photos and download candidates."""
import json, os, re, sys, time, urllib.parse, urllib.request
UA={"User-Agent":"LiftPlan-vintage-fetch/1.0 (github.com/gabecarv/liftplan)"}
TERMS=["weight lifting","weightlifting","weight training","bodybuilding","body building","exercise gymnasium","physical fitness","aerobics","aerobic exercise","health club","fitness center","jogging","running marathon","exercise machine","barbell","dumbbell","gym class","office computer","personal computer office","desk calendar","appointment book","typewriter office","stopwatch","track and field"]
def get(url):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90) as r: return r.read()
        except Exception as e:
            print("retry",url[:80],e); time.sleep(8*(a+1))
    return None
def main():
    root=sys.argv[1] if len(sys.argv)>1 else "candidates"; os.makedirs(f"{root}/loc",exist_ok=True); manifest=[]; seen=set()
    for t in TERMS:
        url="https://www.loc.gov/photos/?"+urllib.parse.urlencode({"q":t,"fo":"json","c":60,"dates":"1978/1992","fa":"online-format:image"})
        raw=get(url); time.sleep(3)
        if not raw: continue
        try: j=json.loads(raw)
        except Exception as e: print("json fail",t,e); continue
        kept=0
        for r in j.get("results",[]):
            if r.get("id") in seen: continue
            seen.add(r.get("id"))
            date=str(r.get("date") or ""); yrs=re.findall(r"(19[7-9]\d)",date+" "+str(r.get("title","")))
            if not yrs or not any(1978<=int(y)<=1992 for y in yrs): continue
            imgs=[u for u in (r.get("image_url") or []) if isinstance(u,str)]
            if not imgs: continue
            big=sorted(imgs,key=lambda u:(("pct:100" in u) or ("full" in u), len(u)))[-1]
            slug=re.sub(r"[^A-Za-z0-9]+","_",(r.get("title") or r.get("id",""))[:70]); path=f"{root}/loc/{slug}_{abs(hash(r.get('id')))%100000}.jpg"
            data=get(big)
            if not data or len(data)<20000: continue
            open(path,"wb").write(data); kept+=1
            manifest.append({"title":r.get("title"),"date":date,"id":r.get("id"),"url":big,"rights":str(r.get("rights") or "")[:120],"term":t,"path":path,"desc":" ".join(r.get("description") or [])[:200]})
            time.sleep(1.5)
        print(t,"->",kept)
    json.dump(manifest,open(f"{root}/loc_manifest.json","w"),indent=1)
main()
