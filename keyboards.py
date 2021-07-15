from localization import buttons_loc

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton


remove_keyboard = ReplyKeyboardRemove(
    remove_keyboard=True
)

repeat_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=buttons_loc['user_repeat'])]
    ]
)


def make_inline_keyboard(ticket_id, user_id: str = None, ban: bool = True):
    if ban:
        ban_keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=buttons_loc['ban_user'], callback_data=f'ban|{user_id}|{ticket_id}')]
            ]
        )
    else:
        ban_keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=buttons_loc['unban_user'], callback_data=f'unban|{user_id}|{ticket_id}')]
            ]
        )
    return ban_keyboard

