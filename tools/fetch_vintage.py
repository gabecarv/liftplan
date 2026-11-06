"""Download the curated public-domain photos listed in vintage.json into images/vintage/ (run on the deploy runner)."""
import json, os, sys, time, urllib.request
from PIL import Image
UA={"User-Agent":"LiftPlan-vintage/1.0 (github.com/gabecarv/liftplan)"}
m=json.load(open("vintage.json")); os.makedirs("images/vintage",exist_ok=True); ok=0
for key,v in m.items():
    if key.startswith("_"): continue
    out=f"images/vintage/{key}.jpg"
    if os.path.exists(out): ok+=1; continue
    for attempt in range(5):
        try:
            req=urllib.request.Request(v["url"],headers=UA)
            with urllib.request.urlopen(req,timeout=60) as r: data=r.read()
            tmp=out+".tmp"; open(tmp,"wb").write(data)
            im=Image.open(tmp).convert("RGB"); im.thumbnail((1200,1200)); im.save(out,"JPEG",quality=78,optimize=True); os.remove(tmp); ok+=1; break
        except Exception as e:
            print("retry",key,e); time.sleep(15*(attempt+1))
    time.sleep(2.5)
print("vintage images:",ok,"/",len([k for k in m if not k.startswith('_')]))
