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

    # English tti (Korean animal zodiac in English)
    log.info("Generating English tti...")
    import asyncio, aiohttp
    from config import GEMINI_URL
    async def _call(prompt):
        payload = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.9, 'maxOutputTokens': 8192}}
        async with aiohttp.ClientSession() as s:
            async with s.post(GEMINI_URL, json=payload) as r:
                data = await r.json()
        raw = data['candidates'][0]['content']['parts'][0]['text'].strip()
        if raw.startswith('```'): raw = raw.split('\n',1)[1]
        if raw.endswith('```'): raw = raw.rsplit('```',1)[0]
        return json.loads(raw.strip())

    try:
        en_tti = asyncio.run(_call('Generate today\'s horoscope for 12 Korean Animal Zodiac signs in English. JSON array: [{"name":"Mouse","emoji":"🐭","years":"1960,1972,1984,1996,2008,2020","content":"...","lucky_numbers":[12,28,35,49,67,14],"lucky_color":"Gold","advice":"..."}] lucky_numbers: 5 main numbers (1-70) + 1 Mega Ball (1-25) = 6 numbers total. Signs: Mouse,Cow,Tiger,Rabbit,Dragon,Snake,Horse,Sheep,Monkey,Rooster,Dog,Pig. JSON only.'))
        with open(DATA_DIR / "en_tti.json", "w") as f:
            json.dump(en_tti, f, ensure_ascii=False, indent=2)
        log.info(f"English tti: {len(en_tti)} signs")
    except Exception as e:
        log.error(f"English tti failed: {e}")

    # Japanese tti
    log.info("Generating Japanese tti...")
    try:
        ja_tti = asyncio.run(_call('韓国の12支の今日の運勢を日本語で。JSON配列: [{"name":"ネズミ年","emoji":"🐭","years":"1960,1972,1984,1996,2008,2020","content":"...","lucky_numbers":[3,12,25,33,41,7],"lucky_color":"ゴールド","advice":"..."}] lucky_numbers: ロト6推薦番号(1-43の整数6個)。12支: ネズミ,牛,トラ,うさぎ,龍,ヘビ,馬,羊,猿,鶏,犬,豚。JSONのみ。'))
        with open(DATA_DIR / "ja_tti.json", "w") as f:
            json.dump(ja_tti, f, ensure_ascii=False, indent=2)
        log.info(f"Japanese tti: {len(ja_tti)} signs")
    except Exception as e:
        log.error(f"Japanese tti failed: {e}")

    # Save date-stamped copies for history
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    history_dir = DATA_DIR / "history"
    history_dir.mkdir(exist_ok=True)
    import shutil
    for fname in ["en.json", "ja.json", "ko.json", "ko_zodiac.json", "en_tti.json", "ja_tti.json"]:
        src = DATA_DIR / fname
        if src.exists():
            dst = history_dir / f"{fname.replace('.json', '')}_{date_str}.json"
            shutil.copy2(src, dst)
    log.info(f"History saved for {date_str}")

    log.info("Site data updated!")


if __name__ == "__main__":
    update()
