from random import choice
from html import escape
from time import sleep, time
from telegram import InlineKeyboardMarkup, InputMediaPhoto
from telegram.message import Message
from telegram.error import RetryAfter
from pyrogram import enums
from pyrogram.errors import FloodWait
from os import remove
from bot import botStartTime
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time

from bot import LOGGER, status_reply_dict, status_reply_dict_lock, \
                Interval, bot, rss_session, app, config_dict
from bot.helper.ext_utils.bot_utils import get_readable_message, setInterval


def sendMessage(text, bot, message):
    try:
        return bot.sendMessage(message.chat_id,
                            reply_to_message_id=message.message_id,
                            text=text, allow_sending_without_reply=True, parse_mode='HTML', disable_web_page_preview=True)
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendMessage(text, bot, message)
    except Exception as e:
        LOGGER.error(str(e))
        return

def sendMarkup(text, bot, message, reply_markup: InlineKeyboardMarkup):
    try:
        return bot.sendMessage(message.chat_id,
                            reply_to_message_id=message.message_id,
                            text=text, reply_markup=reply_markup, allow_sending_without_reply=True,
                            parse_mode='HTML', disable_web_page_preview=True)
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendMarkup(text, bot, message, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return

def editMessage(text, message, reply_markup=None):
    try:
        bot.editMessageText(text=text, message_id=message.message_id,
                              chat_id=message.chat.id,reply_markup=reply_markup,
                              parse_mode='HTML', disable_web_page_preview=True)
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return editMessage(text, message, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

def editCaption(text, message, reply_markup=None):
    try:
        bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id, caption=text, 
                              reply_markup=reply_markup, parse_mode='HTML')
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return editMessage(text, message, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

def sendRss(text, bot):
    if not rss_session:
        try:
            return bot.sendMessage(config_dict['RSS_CHAT_ID'], text, parse_mode='HTML', disable_web_page_preview=True)
        except RetryAfter as r:
            LOGGER.warning(str(r))
            sleep(r.retry_after * 1.5)
            return sendRss(text, bot)
        except Exception as e:
            LOGGER.error(str(e))
            return
    else:
        try:
            with rss_session:
                return rss_session.send_message(config_dict['RSS_CHAT_ID'], text, disable_web_page_preview=True)
        except FloodWait as e:
            LOGGER.warning(str(e))
            sleep(e.value * 1.5)
            return sendRss(text, bot)
        except Exception as e:
            LOGGER.error(str(e))
            return


async def sendRss_pyro(text: str):
    rss_session = Client(name='rss_session', api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH, session_string=USER_STRING_SESSION, parse_mode=enums.ParseMode.HTML)
    await rss_session.start()
    try:
        return await rss_session.send_message(config_dict['RSS_CHAT_ID'], text, disable_web_page_preview=True)
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asleep(e.value * 1.5)
        return await sendRss(text)
    except Exception as e:
        LOGGER.error(str(e))
        return

def sendPhoto(text, bot, message, photo, reply_markup=None):
    try:
        return bot.send_photo(chat_id=message.chat_id, photo=photo, reply_to_message_id=message.message_id,
            caption=text, reply_markup=reply_markup, parse_mode='html')
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendPhoto(text, bot, message, photo, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return

def editPhoto(text, message, photo, reply_markup=None):
    try:
        return bot.edit_message_media(media=InputMediaPhoto(media=photo, caption=text, parse_mode='html'), chat_id=message.chat.id, message_id=message.message_id,
                                      reply_markup=reply_markup)
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return editPhoto(text, message, photo, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return

def deleteMessage(bot, message):
    try:
        bot.deleteMessage(chat_id=message.chat.id,
                           message_id=message.message_id)
    except Exception as e:
        pass

def sendLogFile(bot, message):
    logFileRead = open('log.txt', 'r')
    logFileLines = logFileRead.read().splitlines()
    ind = 1
    Loglines = ''
    try:
        while len(Loglines) <= 2500:
            Loglines = logFileLines[-ind]+'\n'+Loglines
            if ind == len(logFileLines): break
            ind += 1
        startLine = f"Generated Last {ind} Lines from log.txt: \n\n---------------- START LOG -----------------\n\n"
        endLine = "\n---------------- END LOG -----------------"
        sendMessage(escape(startLine+Loglines+endLine), bot, message)
    except Exception as err:
        LOGGER.error(f"Log Display : {err}")
    app.send_document(document='log.txt', thumb='Thumbnails/weeb.jpg',
                          reply_to_message_id=message.message_id,
                          chat_id=message.chat_id, caption=f'log.txt\n\n⏰️ UpTime: {get_readable_time(time() - botStartTime)}')

def sendFile(bot, message, name, caption=""):
    try:
        app.send_document(document=name, reply_to_message_id=message.message_id,
                             caption=caption, parse_mode=enums.ParseMode.HTML, chat_id=message.chat_id,
                             thumb='Thumbnails/weeb.jpg')
        remove(name)
        return
    except FloodWait as r:
        LOGGER.warning(str(r))
        sleep(r.value * 1.5)
        return sendFile(bot, message, name, caption)
    except Exception as e:
        LOGGER.error(str(e))
        return

def auto_delete_message(bot, cmd_message, bot_message):
    if config_dict['AUTO_DELETE_MESSAGE_DURATION'] != -1:
        sleep(config_dict['AUTO_DELETE_MESSAGE_DURATION'])
        deleteMessage(bot, cmd_message)
        deleteMessage(bot, bot_message)


def auto_delete_upload_message(bot, cmd_message, bot_message):
    if cmd_message.chat.type == 'private':
        pass
    elif config_dict['AUTO_DELETE_UPLOAD_MESSAGE_DURATION'] != -1:
        sleep(config_dict['AUTO_DELETE_UPLOAD_MESSAGE_DURATION'])
        deleteMessage(bot, cmd_message)
        deleteMessage(bot, bot_message)

def delete_all_messages():
    with status_reply_dict_lock:
        for data in list(status_reply_dict.values()):
            try:
                deleteMessage(bot, data[0])
                del status_reply_dict[data[0].chat.id]
            except Exception as e:
                LOGGER.error(str(e))

def update_all_messages(force=False):
    with status_reply_dict_lock:
        if not status_reply_dict or not Interval or (not force and time() - list(status_reply_dict.values())[0][1] < 3):
            return
        for chat_id in status_reply_dict:
            status_reply_dict[chat_id][1] = time()

    msg, buttons = get_readable_message()
    if msg is None:
        return
    with status_reply_dict_lock:
        for chat_id in status_reply_dict:
            if status_reply_dict[chat_id] and msg != status_reply_dict[chat_id][0].text:
                if buttons == "" and config_dict['PICS']:
                    rmsg = editPhoto(msg, status_reply_dict[chat_id][0], choice(config_dict['PICS']))
                elif buttons == "":
                    rmsg = editMessage(msg, status_reply_dict[chat_id][0])
                elif config_dict['PICS']:
                    rmsg = editPhoto(msg, status_reply_dict[chat_id][0], choice(config_dict['PICS']), buttons)
                else:
                    rmsg = editMessage(msg, status_reply_dict[chat_id][0], buttons)
                if rmsg == "Message to edit not found":
                    del status_reply_dict[chat_id]
                    return
                status_reply_dict[chat_id][0].text = msg
                status_reply_dict[chat_id][1] = time()

def sendStatusMessage(msg, bot):
    progress, buttons = get_readable_message()
    if progress is None:
        return
    with status_reply_dict_lock:
        if msg.chat.id in status_reply_dict:
            message = status_reply_dict[msg.chat.id][0]
            deleteMessage(bot, message)
            del status_reply_dict[msg.chat.id]
        if buttons == "" and config_dict['PICS']:
            message = sendPhoto(progress, bot, msg, choice(config_dict['PICS']))
        elif buttons == "":
            message = sendMessage(progress, bot, msg)
        elif config_dict['PICS']:
            message = sendPhoto(progress, bot, msg, choice(config_dict['PICS']), buttons)
        else:
            message = sendMarkup(progress, bot, msg, buttons)
        status_reply_dict[msg.chat.id] = [message, time()]
        if not Interval:
            Interval.append(setInterval(config_dict['STATUS_UPDATE_INTERVAL'], update_all_messages))
