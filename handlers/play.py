from os import path

from pyrogram import Client
from pyrogram.types import Message, Voice

import callsmusic

import converter
from downloaders import youtube

from config import BOT_NAME as bn, DURATION_LIMIT
from helpers.filters import command, other_filters
from helpers.decorators import errors
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name


@Client.on_message(command("play") & other_filters)
@errors
async def play(_, message: Message):
    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)
    if audio:
        if round(audio.duration / 100) > DURATION_LIMIT:
            raise DurationLimitError(
                f"**{bn} :-**  يجب ان يكون حجم مقطع الاغنيه  {DURATION_LIMIT} لايمكن تحميل \n المقطع هذا لان حجمه {audio.duration / 100} "
            )

        file_name = get_file_name(audio)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name)) else file_name
        )
    elif url:
        file_path = await converter.convert(youtube.download(url))
    else:
        return await message.reply_text(f"**{bn} :** قم بالرد على الاغنيه او الرابط اولا ")

    if message.chat.id in callsmusic.pytgcalls.active_calls:
        await message.reply_text(f"**{bn} :** تم اضافه الاغنيه الى الدور #{await callsmusic.queues.put(message.chat.id, file_path=file_path)} ")
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_text(f"**{bn} :-** تـم تشغيل الأغنـية بنجاح ✅ ")
@Client.on_message(command("vol"))
async def volume_bot(_, message):
    usage = "**Usage:**\n/volume [1-200]"
    if len(message.command) != 2:
        await send(usage)
        return
    volume = int(message.text.split(None, 1)[1])
    if (volume < 1) or (volume > 200):
        await send(usage)
        return
    try:
        await vc.set_my_volume(volume=volume)
    except ValueError:
        await send(usage)
        return
    await send(f"**تم وضع مستوى صوت البوت  {volume}**")
