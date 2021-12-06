import asyncio
from datetime import datetime

from telethon.tl import functions, types

from userbot import catub

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.utils import _format
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "utils"

LOGS = logging.getLogger(__name__)


class AFK:
    def __init__(self):
        self.USERAFK_ON = {}
        self.afk_time = None
        self.last_afk_message = {}
        self.afk_star = {}
        self.afk_end = {}
        self.reason = None
        self.msg_link = False
        self.afk_type = None
        self.media_afk = None
        self.afk_on = False


AFK_ = AFK()


@catub.cat_cmd(outgoing=True, edited=False)
async def set_not_afk(event):
    if AFK_.afk_on is False:
        return
    back_alive = datetime.now()
    AFK_.afk_end = back_alive.replace(microsecond=0)
    if AFK_.afk_star != {}:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time = int(total_afk_time.seconds)
        d = time // (24 * 3600)
        time %= 24 * 3600
        h = time // 3600
        time %= 3600
        m = time // 60
        time %= 60
        s = time
        endtime = ""
        if d > 0:
            endtime += f"{d}d {h}h {m}m {s}s"
        elif h > 0:
            endtime += f"{h}h {m}m {s}s"
        else:
            endtime += f"{m}m {s}s" if m > 0 else f"{s}s"
    current_message = event.message.message
    if (("afk" not in current_message) or ("#afk" not in current_message)) and (
        "on" in AFK_.USERAFK_ON
    ):
        shite = await event.client.send_message(
            event.chat_id,
            "`Salom, men qaytdim.\nBand bo'lgan vaqtim " + endtime + "`",
        )
        AFK_.USERAFK_ON = {}
        AFK_.afk_time = None
        await asyncio.sleep(5)
        await shite.delete()
        AFK_.afk_on = False
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#AFKFALSE \n`Bandlik rejimini FALSE deb belgilash\n"
                + "Salom, men qaytdim.\nBand bo'lgan vaqtim "
                + endtime
                + "`",
            )


@catub.cat_cmd(
    incoming=True, func=lambda e: bool(e.mentioned or e.is_private), edited=False
)
async def on_afk(event):  # sourcery no-metrics
    if AFK_.afk_on is False:
        return
    back_alivee = datetime.now()
    AFK_.afk_end = back_alivee.replace(microsecond=0)
    if AFK_.afk_star != {}:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time = int(total_afk_time.seconds)
        d = time // (24 * 3600)
        time %= 24 * 3600
        h = time // 3600
        time %= 3600
        m = time // 60
        time %= 60
        s = time
        endtime = ""
        if d > 0:
            endtime += f"{d}d {h}h {m}m {s}s"
        elif h > 0:
            endtime += f"{h}h {m}m {s}s"
        else:
            endtime += f"{m}m {s}s" if m > 0 else f"{s}s"
    current_message_text = event.message.message.lower()
    if "afk" in current_message_text or "#afk" in current_message_text:
        return False
    if not await event.get_sender():
        return
    if AFK_.USERAFK_ON and not (await event.get_sender()).bot:
        msg = None
        if AFK_.afk_type == "media":
            if AFK_.reason:
                message_to_reply = (
                    f"`Hozir yozolmayman .\n\n{endtime} dan beri bandman\nSababi : {AFK_.reason}`"
                )
            else:
                message_to_reply = f"` Hozir yozolmayman.\n\n {endtime} dan beri bandman`"
            if event.chat_id:
                msg = await event.reply(message_to_reply, file=AFK_.media_afk.media)
        elif AFK_.afk_type == "text":
            if AFK_.msg_link and AFK_.reason:
                message_to_reply = (
                    f"**Hozir yozolmayman .\n\n{endtime} dan beri bandman\nSababi : **{AFK_.reason}"
                )
            elif AFK_.reason:
                message_to_reply = (
                    f"`Hozir yozolmayman .\n\n{endtime} dan beri bandman\nSababi : {AFK_.reason}`"
                )
            else:
                message_to_reply = f"`Hozir yozolmayman.\n\n{endtime} dan beri bandman`"
            if event.chat_id:
                msg = await event.reply(message_to_reply)
        if event.chat_id in AFK_.last_afk_message:
            await AFK_.last_afk_message[event.chat_id].delete()
        AFK_.last_afk_message[event.chat_id] = msg
        if event.is_private:
            return
        hmm = await event.get_chat()
        if Config.PM_LOGGER_GROUP_ID == -100:
            return
        full = None
        try:
            full = await event.client.get_entity(event.message.from_id)
        except Exception as e:
            LOGS.info(str(e))
        messaget = media_type(event)
        resalt = f"#AFK_TAGS \n<b>Group : </b><code>{hmm.title}</code>"
        if full is not None:
            resalt += f"\n<b>From : </b> 👤{_format.htmlmentionuser(full.first_name , full.id)}"
        if messaget is not None:
            resalt += f"\n<b>Xabar turi : </b><code>{messaget}</code>"
        else:
            resalt += f"\n<b>Xabar : </b>{event.message.message}"
        resalt += f"\n<b>Xabar linki: </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> link</a>"
        if not event.is_private:
            await event.client.send_message(
                Config.PM_LOGGER_GROUP_ID,
                resalt,
                parse_mode="html",
                link_preview=False,
            )


@catub.cat_cmd(
    pattern="afk(?:\s|$)([\s\S]*)",
    command=("afk", plugin_category),
    info={
        "header": "Bandlik rejimi sizga yozganlarga band ekaningiz haqida xabar beradi",
        "description": "Guruhda, chatda kimdir sizga reply qilsa yoki yozsa botingiz sizni band ekaningiz haqida xabar berib turadi.\
        ",
        "options": "Agar siz bandligingiz sababida giperlink ishlatmoqchi bo'lsangiz sababni ortidan [ ; ] ni qo'shib keting, so'ng mediafaylingiz linkini qo'ying.",
        "usage": [
            "{tr}afk <Sababingiz>",
            "{tr}afk <Sababingiz> ; <Biror nimani linki>",
        ],
        "examples": "{tr}afk Ozroq uxlab olay",
        "note": "Bandlik rejimi qayergadir nimadir yozishingiz bilan avtomat tugatiladi va sizga yozganlarga Telegramga qaytganingiz haqida xabar beriladi. Siz kimgadir yozsangiz ham bandlik rejimida qolishni istasangiz xabaringiz ichida #afk ni qo'shib kiritib keting",
    },
)
async def _(event):
    "Bandlik rejimiga o'tish (afk)"
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = {}
    AFK_.afk_type = "text"
    start_1 = datetime.now()
    AFK_.afk_on = True
    AFK_.afk_star = start_1.replace(microsecond=0)
    if not AFK_.USERAFK_ON:
        input_str = event.pattern_match.group(1)
        if ";" in input_str:
            msg, mlink = input_str.split(";", 1)
            AFK_.reason = f"[{msg.strip()}]({mlink.strip()})"
            AFK_.msg_link = True
        else:
            AFK_.reason = input_str
            AFK_.msg_link = False
        last_seen_status = await event.client(
            functions.account.GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp())
        )
        if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
            AFK_.afk_time = datetime.now()
        AFK_.USERAFK_ON = f"on: {AFK_.reason}"
        if AFK_.reason:
            await edit_delete(
                event, f"`Mayli, men borishim kerak, sababi ~` {AFK_.reason}, ko'rishguncha.", 5
            )
        else:
            await edit_delete(event, "`Mayli, men borishim kerak, ko'rishguncha `", 5)
        if BOTLOG:
            if AFK_.reason:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"#AFKTRUE \nBandlik rejimini yoqish, va sababini {AFK_.reason} deb belgilash",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#AFKTRUE \nBandlik rejimini yoqish, va sababini ko'rsatmaslik",
                )


@catub.cat_cmd(
    pattern="mafk(?:\s|$)([\s\S]*)",
    command=("mafk", plugin_category),
    info={
        "header": "Bandlik rejimini yoqish va sababiga mediafayl ko'rsatish",
        "description": "Buni yoqsangiz sizga kim qayerdadir yozsa yoki reply qilsa unga sizni band deb xabar beriladi.",
        "options": "Agar siz bandlik sababida giperlink ishlatmoqchi bo'lsangiz sabab oxirida [ ; ] qo'yib, keyin linkingizni joylang.",
        "usage": [
            "{tr}mafk <sababi> ni yozib, biror mediafaylga reply qiling",
        ],
        "examples": "{tr}mafk ozroq uxlab olay",
        "note": "Bandlik rejimi qayergadir nimadir yozganingiz zahoti tugatiladi va sizga yozganlarga qaytganingiz haqida xabar beriladi. Bandlik rejimini o'chirmasdan ham yozishish uchun #afk ni yozayotgan xabaringiz ichiga kiritib keting",
    },
)
async def _(event):
    "Bandlik rejimiga o'tish va sababda mediafayl ko'rsatish"
    reply = await event.get_reply_message()
    media_t = media_type(reply)
    if media_t == "Sticker" or not media_t:
        return await edit_or_reply(
            event, "`Mediafaylli bandlik rejimini yoqish uchun qandaydir media xabarga reply qilishingiz kerak`"
        )
    if not BOTLOG:
        return await edit_or_reply(
            event, "`To use media afk you need to set PRIVATE_GROUP_BOT_API_ID config`"
        )
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = {}
    AFK_.media_afk = None
    AFK_.afk_type = "media"
    start_1 = datetime.now()
    AFK_.afk_on = True
    AFK_.afk_star = start_1.replace(microsecond=0)
    if not AFK_.USERAFK_ON:
        input_str = event.pattern_match.group(1)
        AFK_.reason = input_str
        last_seen_status = await event.client(
            functions.account.GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp())
        )
        if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
            AFK_.afk_time = datetime.now()
        AFK_.USERAFK_ON = f"on: {AFK_.reason}"
        if AFK_.reason:
            await edit_delete(
                event, f"`Mayli, men borishim kerak, sababi ~` {AFK_.reason}, ko'rishguncha", 5
            )
        else:
            await edit_delete(event, "`I shall be Going afk! `", 5)
        AFK_.media_afk = await reply.forward_to(BOTLOG_CHATID)
        if AFK_.reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#AFKTRUE \nBandlik rejimini yoqish va sababiga {AFK_.reason} ni ko'rsatish",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#AFKTRUE \nBanlik rejimini yoqish va sababni ko'rsatmaslik",
            )
