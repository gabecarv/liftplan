"""Search Wikimedia Commons for public-domain vintage photos and download candidates for review.
Runs on the GitHub Actions runner (the dev sandbox can't reach Commons)."""
import json, os, re, sys, urllib.parse, urllib.request, time
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "LiftPlan-vintage-fetch/1.0 (github.com/gabecarv/liftplan)"}
TERMS = {
  "lift80": ["weightlifting 1980s", "bodybuilding 1980s", "weight room 1980s", "bench press 1985", "Marines weight lifting 1980s", "Air Force fitness center 1980s", "Navy weight room 1980s", "Nautilus machine 1980s", "powerlifting 1980s", "Olympic weightlifting 1984", "weightlifting 1988 Olympics", "Soldiers lifting weights 1980s"],
  "gym80":  ["gym 1980s", "fitness center 1980s", "aerobics 1980s", "health club 1980s", "jazzercise", "gymnasium 1985 photograph", "exercise class 1980s"],
  "desk80": ["office 1980s photograph", "computer office 1980s", "desk 1985 photograph", "appointment calendar 1980s", "Filofax", "typewriter office 1980s", "planner desk 1980s"],
  "run80":  ["jogging 1980s", "running 1980s photograph", "track athlete 1980s", "stopwatch 1980s", "marathon 1980s photograph"],
}
OK_LICENSE = re.compile(r"public domain|cc0|pd-|^cc by( \d\.\d)?$|cc-by(-\d\.\d)?$", re.I)
def api(params):
    params.update({"format": "json"}); url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r: time.sleep(1.5); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(8 * (attempt + 1)); continue
            raise
    raise RuntimeError("rate limited")
def search(term, n=14):
    j = api({"action": "query", "list": "search", "srsearch": term + " filetype:bitmap", "srnamespace": 6, "srlimit": n})
    return [h["title"] for h in j.get("query", {}).get("search", [])]
def info(titles):
    out = []
    for i in range(0, len(titles), 20):
        j = api({"action": "query", "prop": "imageinfo", "titles": "|".join(titles[i:i+20]), "iiprop": "url|size|extmetadata", "iiurlwidth": 1024})
        for p in j.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [None])[0]
            if not ii: continue
            em = ii.get("extmetadata", {}); g = lambda k: (em.get(k) or {}).get("value", "")
            out.append({"title": p["title"], "thumb": ii.get("thumburl") or ii["url"], "url": ii["url"], "w": ii.get("width"), "h": ii.get("height"),
                        "license": re.sub("<[^>]+>", "", g("LicenseShortName")), "date": re.sub("<[^>]+>", "", g("DateTimeOriginal"))[:40],
                        "desc": re.sub("<[^>]+>", "", g("ImageDescription"))[:200], "credit": re.sub("<[^>]+>", "", g("Artist"))[:80]})
    return out
def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "candidates"
    manifest = []
    for group, terms in TERMS.items():
        seen = set()
        for t in terms:
            try: titles = search(t)
            except Exception as e: print("search fail", t, e); continue
            for it in info(titles):
                if it["title"] in seen: continue
                seen.add(it["title"])
                if not OK_LICENSE.search(it["license"]): continue
                if (it["w"] or 0) < 500: continue
                slug = re.sub(r"[^A-Za-z0-9]+", "_", it["title"].replace("File:", ""))[:80]
                path = f"{root}/{group}/{slug}.jpg"; os.makedirs(os.path.dirname(path), exist_ok=True)
                try:
                    req = urllib.request.Request(it["thumb"], headers=UA)
                    with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f: f.write(r.read())
                except Exception as e: print("dl fail", it["title"], e); continue
                it.update({"group": group, "term": t, "path": path}); manifest.append(it); time.sleep(1.0)
        print(group, len([m for m in manifest if m["group"] == group]))
    json.dump(manifest, open(f"{root}/manifest.json", "w"), indent=1)
if __name__ == "__main__": main()
