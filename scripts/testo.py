import pandas as pd
from pathlib import Path
import requests
import time

# df = pd.read_csv('aircraft.csv')

PLANES = [
    "Aero Vodochody L-39",
    "AeroElvira Optica",
    "Air Tractor AT-802",
    "Airbus A310-300",
    "Airbus A320neo",
    "Airbus A321LR",
    "Airbus A330 (-200, -300, 300P2F)",
    "Airbus A330-743L Beluga XL",
    "Airbus A400M Atlas",
    "Airbus Helicopter H125",
    "Airship Industries Skyship 600",
    "Archer Midnight",
    "Aviat Pitts Special S1S",
    "Aviat Pitts Special S2S",
    "Beechcraft Bonanza G36",
    "Beechcraft King Air 350i",
    "Bell 407",
    "CGS Hawk Arrow II",
    "Cessna 152",
    "Cessna 172 Skyhawk (G1000)",
    "Cessna 208 B Grand Caravan EX",
    "Cessna 400 Corvalis TT",
    "Cessna Citation CJ4",
    "Cirrus Vision SF50 (VisionJet)",
    "CubCrafters NX Cub",
    "CubCrafters XCub",
    "Curtiss JN-4 Jenny",
    "DG Aviation DG-1001E",
    "DG Aviation LS8-18",
    "Daher TBM 930",
    "De Havilland Canada CL-415",
    "De Havilland Canada DHC-2 Beaver",
    "De Havilland Canada DHC-6 Twin Otter",
    "Diamond Aircraft DA40 NG",
    "Diamond Aircraft DA62",
    "Douglas DC-3",
    "Draco X",
    "EXTRA 330LT",
    "Erickson S-64F Aircrane",
    "Fairchild Republic A-10 Thunderbolt II",
    "Flight Design CTSL",
    "FlyDoo Hot Air Balloon",
    "Grumman G-21A Goose",
    "Guimbal Cabri G2",
    "Heart Aerospace ES-30",
    "Hot Air Balloon",
    "Hughes Aircraft Company H-4 Hercules (Spruce Goose)",
    "ICON Aircraft ICON A5",
    "JMB Aircraft s.r.o VL-3",
    "Jetson Jetson One",
    "Joby Aviation Joby S4",
    "MX Aircraft Company MXS-R",
    "Magni Gyro M-24 Orion",
    "North American P-51 Mustang",
    "North American T-6 Texan",
    "Pilatus PC-12 NGX",
    "Pilatus PC-6 B2",
    "Powrachute Sky Rascal",
    "Robin Aircraft SAS CAP 10",
    "Robin Aircraft SAS DR400-100 Cadet",
    "Robinson R66",
    "Ryan NYP Spirit of St. Louis",
    "Stemme S12G",
    "The Boeing Company 737 MAX 8",
    "The Boeing Company 747-8I (-8F)",
    "The Boeing Company F/A-18E",
    "Volocopter VoloCity",
    "Wright Cycle Company Wright Flyer",
    "Zivko Edge 540",
    "Zlin Aviation Savage Cub"
]

"""
Téléchargement d'images d'avions via l'API Wikipedia/Wikimedia.
Pour chaque nom d'avion, récupère la première image de la page Wikipedia
et la sauvegarde localement.
"""

import os
import time
import requests
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────


OUTPUT_DIR = Path("plane_images")
DELAY = 1.0          # secondes entre chaque requête (soyez gentil avec l'API)
LANG = "en"          # langue Wikipedia : "en", "fr", etc.

# ── Helpers ────────────────────────────────────────────────────────────────────

WIKI_API = f"https://{LANG}.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "careermanager/1.0 (laurendi.mugica@gmail.com)"}


def get_wikipedia_image_url(plane_name: str) -> str | None:
    """Retourne l'URL de la première image trouvée sur la page Wikipedia."""
    # Étape 1 : récupérer le titre canonique de la page
    search_resp = requests.get(
        WIKI_API,
        params={
            "action": "query",
            "list": "search",
            "srsearch": plane_name,
            "srlimit": 1,
            "format": "json",
        },
        headers=HEADERS,
        timeout=10,
    )
    search_resp.raise_for_status()
    results = search_resp.json().get("query", {}).get("search", [])
    if not results:
        print(f"  ✗ Aucune page Wikipedia trouvée pour « {plane_name} »")
        return None

    page_title = results[0]["title"]

    # Étape 2 : récupérer les images listées sur cette page
    images_resp = requests.get(
        WIKI_API,
        params={
            "action": "query",
            "titles": page_title,
            "prop": "images",
            "imlimit": 20,
            "format": "json",
        },
        headers=HEADERS,
        timeout=10,
    )
    images_resp.raise_for_status()
    pages = images_resp.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    images = page.get("images", [])

    # Filtrer : garder uniquement jpg/png, exclure logos/icônes
    EXCLUDE_KEYWORDS = ("flag", "logo", "icon", "map", "coat", "seal", "commons")
    candidates = [
        img["title"]
        for img in images
        if img["title"].lower().endswith((".jpg", ".jpeg", ".png"))
        and not any(kw in img["title"].lower() for kw in EXCLUDE_KEYWORDS)
    ]
    if not candidates:
        print(f"  ✗ Pas d'image utilisable sur la page « {page_title} »")
        return None

    # Étape 3 : obtenir l'URL directe du fichier via imageinfo
    file_title = candidates[0]
    info_resp = requests.get(
        WIKI_API,
        params={
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 1200,   # redimensionné à 1200px max
            "format": "json",
        },
        headers=HEADERS,
        timeout=10,
    )
    info_resp.raise_for_status()
    info_pages = info_resp.json().get("query", {}).get("pages", {})
    info_page = next(iter(info_pages.values()))
    imageinfo = info_page.get("imageinfo", [])
    if not imageinfo:
        return None

    return imageinfo[0].get("thumburl") or imageinfo[0].get("url")


def download_image(url: str, dest: Path) -> bool:
    """Télécharge une image vers dest. Retourne True si succès."""
    resp = requests.get(url, headers=HEADERS, timeout=30, stream=True)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return True


def safe_filename(name: str) -> str:
    """Transforme un nom d'avion en nom de fichier valide."""
    return "".join(c if c.isalnum() or c in " -_()" else "_" for c in name).strip()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Dossier de sortie : {OUTPUT_DIR.resolve()}\n")

    ok, fail = 0, 0
    for plane in PLANES:
        print(f"→ {plane}")
        try:
            url = get_wikipedia_image_url(plane)
            if not url:
                fail += 1
                continue

            ext = Path(url.split("?")[0]).suffix or ".jpg"
            filename = OUTPUT_DIR / f"{safe_filename(plane)}{ext}"
            download_image(url, filename)
            print(f"  ✓ Sauvegardé : {filename.name}")
            ok += 1
        except Exception as e:
            print(f"  ✗ Erreur : {e}")
            fail += 1

        time.sleep(DELAY)

    print(f"\nTerminé — {ok} réussi(s), {fail} échoué(s).")


if __name__ == "__main__":
    main()