#!/usr/bin/env python3
"""Daily site content updater - generates JSON data for todayfortune.net"""

import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SITE_DIR = Path(__file__).parent
DATA_DIR = SITE_DIR / "data"
SHORTS_DIR = Path.home() / "youtube-shorts"

sys.path.insert(0, str(SHORTS_DIR))


def update():
    DATA_DIR.mkdir(exist_ok=True)

    # English horoscope
    log.info("Generating English horoscope...")
    from horoscope_en import generate_western_horoscopes_sync
    en_data = generate_western_horoscopes_sync()
    with open(DATA_DIR / "en.json", "w") as f:
        json.dump(en_data, f, ensure_ascii=False, indent=2)
    log.info(f"English: {len(en_data)} signs")

    # Japanese horoscope
    log.info("Generating Japanese horoscope...")
    from horoscope_jp import generate_japanese_horoscopes_sync
    jp_data = generate_japanese_horoscopes_sync()
    with open(DATA_DIR / "ja.json", "w") as f:
        json.dump(jp_data, f, ensure_ascii=False, indent=2)
    log.info(f"Japanese: {len(jp_data)} signs")

    # Korean horoscope (tti)
    log.info("Generating Korean horoscope...")
    from horoscope import generate_horoscopes_sync
    ko_data = generate_horoscopes_sync()
    with open(DATA_DIR / "ko.json", "w") as f:
        json.dump(ko_data, f, ensure_ascii=False, indent=2)
    log.info(f"Korean tti: {len(ko_data)} signs")

    # Korean zodiac
    log.info("Generating Korean zodiac...")
    from horoscope_kr_zodiac import generate_kr_zodiac_horoscopes_sync
    ko_z_data = generate_kr_zodiac_horoscopes_sync()
    with open(DATA_DIR / "ko_zodiac.json", "w") as f:
        json.dump(ko_z_data, f, ensure_ascii=False, indent=2)
    log.info(f"Korean zodiac: {len(ko_z_data)} signs")

    log.info("Site data updated!")


if __name__ == "__main__":
    update()
