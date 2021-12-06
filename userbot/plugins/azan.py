# ported from uniborg
# https://github.com/muhammedfurkan/UniBorg/blob/master/stdplugins/ezanvakti.py
import json

import requests

from ..sql_helper.globals import gvarstatus
from . import catub, edit_delete, edit_or_reply

plugin_category = "extra"


@catub.cat_cmd(
    pattern="azan(?:\s|$)([\s\S]*)",
    command=("azan", plugin_category),
    info={
        "header": "Namoz vaqtlari shaharlar kesimida.",
        "note": "Birlamchi Toshknet shahri uchun ko'rsatadi. {tr}setcity komandasi orqali o'zgartirsa bo'ladi",
        "usage": "{tr}azan <Shahar nomi ingliz tilida>",
        "examples": "{tr}azan Kokand",
    },
)
async def get_adzan(adzan):
    "Ko'rsatilgan shahar uchun bugungi namoz vaqtlarini muslimsalat.com saytidan to'g'ridan to'g'ri olib ko'rsatadi"
    input_str = adzan.pattern_match.group(1)
    LOKASI = gvarstatus("DEFCITY") or "Tashkent" if not input_str else input_str
    url = f"http://muslimsalat.com/{LOKASI}.json?key=bd099c5825cbedb9aa934e255a81a5fc"
    request = requests.get(url)
    if request.status_code != 200:
        return await edit_delete(
            adzan, f"`{LOKASI} bo'yicha hech qanday ma'lumot topilmadi`", 5
        )
    result = json.loads(request.text)
    catresult = f"<b>Namoz vaqtlari </b>\
            \n\n<b>Shahar -----: </b><i>{result['query']}</i>\
            \n<b>Mamlakat ---: </b><i>{result['country']}</i>\
            \n<b>Sana -------: </b><i>{result['items'][0]['date_for']}</i>\
            \n<b>Bomdod -----: </b><i>{result['items'][0]['fajr']}</i>\
            \n<b>kun chiqishi: </b><i>{result['items'][0]['shurooq']}</i>\
            \n<b>Peshin -----: </b><i>{result['items'][0]['dhuhr']}</i>\
            \n<b>Asr --------: </b><i>{result['items'][0]['asr']}</i>\
            \n<b>Shom -------: </b><i>{result['items'][0]['maghrib']}</i>\
            \n<b>Hufton -----: </b><i>{result['items'][0]['isha']}</i>\
    "
    await edit_or_reply(adzan, catresult, "html")
