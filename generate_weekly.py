#!/usr/bin/env python3
"""Generate 7 days of horoscope data for the website."""

import json
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SITE_DIR = Path(__file__).parent
DATA_DIR = SITE_DIR / "data"
SHORTS_DIR = Path.home() / "youtube-shorts"
sys.path.insert(0, str(SHORTS_DIR))

from config import GEMINI_URL
import aiohttp


async def call_gemini(prompt):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 8192},
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(GEMINI_URL, json=payload) as r:
            data = await r.json()
    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw.strip())


def generate_day(date_str, lang, sign_type):
    """Generate horoscope for a specific date."""
    if lang == "en" and sign_type == "zodiac":
        prompt = f"""Generate horoscope for {date_str} for all 12 Western zodiac signs in English.
JSON array: [{{"name":"Aries","emoji":"♈","dates":"Mar 21 - Apr 19","content":"2-3 sentences","lucky_numbers":[12,28,35,49,67,14],"lucky_color":"Gold","advice":"one line"}}]
lucky_numbers: 5 main (1-70) + 1 Mega Ball (1-25). Signs: Aries,Taurus,Gemini,Cancer,Leo,Virgo,Libra,Scorpio,Sagittarius,Capricorn,Aquarius,Pisces. JSON only."""
    elif lang == "en" and sign_type == "tti":
        prompt = f"""Generate horoscope for {date_str} for 12 Korean Animal Zodiac in English.
JSON array: [{{"name":"Mouse","emoji":"🐭","years":"1960, 1972, 1984, 1996, 2008, 2020","content":"2-3 sentences","lucky_numbers":[12,28,35,49,67,14],"lucky_color":"Gold","advice":"one line"}}]
lucky_numbers: 5 main (1-70) + 1 Mega Ball (1-25). Signs: Mouse,Cow,Tiger,Rabbit,Dragon,Snake,Horse,Sheep,Monkey,Rooster,Dog,Pig. JSON only."""
    elif lang == "ja" and sign_type == "zodiac":
        prompt = f"""{date_str}の12星座の運勢を日本語で。
JSON配列: [{{"name":"牡羊座","emoji":"♈","dates":"3/21-4/19","content":"2-3文","lucky_numbers":[3,12,25,33,41,7],"lucky_color":"ゴールド","advice":"一行"}}]
lucky_numbers: ロト6(1-43の6個)。12星座全て。JSONのみ。"""
    elif lang == "ja" and sign_type == "tti":
        prompt = f"""{date_str}の韓国12支の運勢を日本語で。
JSON配列: [{{"name":"ネズミ年","emoji":"🐭","years":"1960, 1972, 1984, 1996, 2008, 2020","content":"2-3文","lucky_numbers":[3,12,25,33,41,7],"lucky_color":"ゴールド","advice":"一行"}}]
lucky_numbers: ロト6(1-43の6個)。JSONのみ。"""
    elif lang == "ko" and sign_type == "tti":
        prompt = f"""{date_str} 한국 12띠별 운세. JSON배열: [{{"name":"쥐띠","emoji":"🐭","years":"1960, 1972, 1984, 1996, 2008, 2020","content":"2-3문장","lucky_numbers":[3,12,25,33,41,7],"advice":"한 줄 조언"}}]
lucky_numbers: 로또번호 6개(1-45). 12띠 전부. JSON만."""
    elif lang == "ko" and sign_type == "zodiac":
        prompt = f"""{date_str} 서양 12별자리 운세를 한국어로. JSON배열: [{{"name":"양자리","name_en":"Aries","emoji":"♈","dates":"3/21-4/19","content":"2-3문장","lucky_numbers":[3,12,25,33,41,7],"lucky_color":"골드","advice":"한 줄 조언"}}]
lucky_numbers: 로또번호 6개(1-45). 12별자리 전부. JSON만."""
    else:
        return []

    try:
        return asyncio.run(call_gemini(prompt))
    except Exception as e:
        log.error(f"Failed {lang}/{sign_type} for {date_str}: {e}")
        return []


def generate_week():
    """Generate 7 days of data."""
    DATA_DIR.mkdir(exist_ok=True)
    weekly_dir = DATA_DIR / "weekly"
    weekly_dir.mkdir(exist_ok=True)

    today = datetime.now()
    dates = []
    # 과거 3일 + 오늘 + 앞으로 7일 = 총 11일
    for i in range(-3, 8):
        d = today + timedelta(days=i)
        dates.append(d.strftime("%Y-%m-%d"))

    # Save date index
    date_index = []
    for d in dates:
        dt = datetime.strptime(d, "%Y-%m-%d")
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][dt.weekday()]
        weekday_ja = ["月", "火", "水", "木", "金", "土", "日"][dt.weekday()]
        date_index.append({
            "date": d,
            "weekday": weekday,
            "weekday_kr": weekday_kr,
            "weekday_ja": weekday_ja,
            "display_en": dt.strftime(f"%b %d ({weekday})"),
            "display_ja": f"{dt.month}/{dt.day}({weekday_ja})",
            "display_ko": f"{dt.month}/{dt.day}({weekday_kr})",
        })

    with open(weekly_dir / "index.json", "w") as f:
        json.dump(date_index, f, ensure_ascii=False, indent=2)

    configs = [
        ("en", "zodiac", "en"),
        ("en", "tti", "en_tti"),
        ("ja", "zodiac", "ja"),
        ("ja", "tti", "ja_tti"),
        ("ko", "tti", "ko"),
        ("ko", "zodiac", "ko_zodiac"),
    ]

    for date_str in dates:
        log.info(f"=== Generating {date_str} ===")
        for lang, sign_type, prefix in configs:
            log.info(f"  {prefix}...")
            data = generate_day(date_str, lang, sign_type)
            if data:
                with open(weekly_dir / f"{prefix}_{date_str}.json", "w") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                log.info(f"  {prefix}: {len(data)} signs")
            import time
            time.sleep(2)  # Rate limit

    log.info("Weekly data generation complete!")


if __name__ == "__main__":
    generate_week()
