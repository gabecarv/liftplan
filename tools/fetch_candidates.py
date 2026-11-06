"""Search Wikimedia Commons for public-domain vintage photos and download candidates for review.
Runs on the GitHub Actions runner (the dev sandbox can't reach Commons)."""
import json, os, re, sys, urllib.parse, urllib.request, time
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "LiftPlan-vintage-fetch/1.0 (github.com/gabecarv/liftplan)"}
TERMS = {
  "lift":  ["Sandow barbell", "Eugen Sandow dumbbell photograph", "Louis Cyr", "George Hackenschmidt", "globe barbell", "Siegmund Klein", "weightlifter 1936 Olympics", "Hermann Goerner", "Launceston Elliot", "weight lifting Bain News Service", "strongman Harris Ewing"],
  "desk":  ["man reading at desk lamp Harris Ewing", "desk writing Bain News Service", "clerk desk 1920s photograph", "calendar wall office 1930s photograph", "student desk books 1920s photograph", "man writing letter 1920s photograph", "accountant ledger photograph 1930s", "appointment desk diary photograph"],
}
OK_LICENSE = re.compile(r"public domain|cc0|pd-", re.I)
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
def search(term, n=10):
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
