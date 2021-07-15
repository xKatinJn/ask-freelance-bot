from localization import messages_loc

from telegram import Update, ReplyKeyboardMarkup, Bot, ParseMode
from telegram.ext import CallbackContext


def send_message(update: Update, context: CallbackContext, text: str, reply_markup: ReplyKeyboardMarkup = None) -> None:
    update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='markdown'
    )


def send_message_to_chat(bot: Bot, text: str, chat_id: int) -> None:
    bot.send_message(
        chat_id=chat_id,
        text=text
    )


def get_user_ticket(info: dict):
    text = messages_loc['ticket_info'].format(info['ticket_id'], info['alias'], info['name'],
                                              info['telephone_number'], info['address'], info['reason'])
    return text


def send_user_ticket(bot: Bot, info: dict, chat_id: int, reply_markup: ReplyKeyboardMarkup = None) -> None:
    text = get_user_ticket(info)
    bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup
    )
