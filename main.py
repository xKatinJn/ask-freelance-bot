import os
import logging
import pprint

from database import User, Chat, Ticket

from chatting import send_message, send_message_to_chat, send_user_ticket, get_user_ticket

from localization import messages_loc

from keyboards import remove_keyboard, repeat_keyboard, make_inline_keyboard

from telegram import Bot, Update
from telegram.ext import Updater, CallbackContext, Filters, MessageHandler, CallbackQueryHandler


# TODO: общение, запись информации, отсылка в группу
# TODO: ограничение по возможности использования бота в группах

API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    API_TOKEN = open('token.txt', 'r').read().replace('\n', '').replace(' ', '')

bot = Bot(
    token=API_TOKEN
)


def message_handler(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    curr_chat = update.message.chat
    if curr_chat['type'] == 'private':
        curr_user_id = int(curr_chat['id'])
        if text == 'Написать еще одну заявку':
            curr_user = User.get(User.user_id == curr_user_id)
            if curr_user.name and curr_user.telephone and curr_user.address and curr_user.reason:
                curr_user.name = curr_user.telephone = curr_user.address = curr_user.reason = None
                curr_user.save()
                send_message(update, context, messages_loc['user_repeat_ok'], remove_keyboard)
                curr_user_fields = vars(curr_user)['__data__']
                curr_user_fields_keys = list(curr_user_fields.keys())[5:]

                for key in curr_user_fields_keys:
                    if not curr_user_fields[key]:
                        send_message(update, context, messages_loc[key])
                        break
                return
        all_users_ids = User.get_all_users_ids()
        print('MESSAGE FROM USER')
        print(all_users_ids)
        if curr_user_id not in all_users_ids:
            if curr_chat['username']:
                new_user = User(user_id=curr_user_id, is_active=True, alias='@'+curr_chat['username'])
            else:
                new_user = User(user_id=curr_user_id, is_active=True)
            new_user.save()
            send_message(update, context, messages_loc['hello'])

            curr_user = User.get(User.user_id == curr_user_id)
            curr_user_fields = vars(curr_user)['__data__']
            curr_user_fields_keys = list(curr_user_fields.keys())[5:]

            for key in curr_user_fields_keys:
                if not curr_user_fields[key]:
                    send_message(update, context, messages_loc[key])
                    break
        else:
            curr_user = User.get(User.user_id == curr_user_id)
            if not curr_user.is_active:
                return
            curr_user_fields = vars(curr_user)['__data__']
            curr_user_fields_keys = list(curr_user_fields.keys())[5:]
            print(curr_user_fields_keys)
            for i, key in enumerate(curr_user_fields_keys):
                if not curr_user_fields[key]:
                    if i != 0 and len(curr_user_fields_keys) != i + 1:
                        setattr(curr_user, curr_user_fields_keys[i], text)
                        print(curr_user_fields_keys[i])
                        send_message(update, context, messages_loc[curr_user_fields_keys[i+1]])
                        curr_user.save()
                    elif i == 0:
                        setattr(curr_user, curr_user_fields_keys[i], text)
                        send_message(update, context, messages_loc[curr_user_fields_keys[i+1]])
                        curr_user.save()
                    else:
                        setattr(curr_user, curr_user_fields_keys[i], text)
                        curr_user.save()
                        ticket = Ticket(user_id=curr_user_id, is_available=True)
                        ticket.save()
                        info = User.get_user_info(curr_user_id, ticket.id)
                        for chat_id in Chat.get_all_chats_ids():
                            send_user_ticket(bot, info, chat_id, make_inline_keyboard(ticket.id, curr_user_id))
                        send_message(update, context, messages_loc['sent'])
                        send_message(update, context, messages_loc['user_repeat'], repeat_keyboard)
                        ticket.is_available = False
                        ticket.save()
                    break
            print(curr_user_fields)

    elif curr_chat['type'] == 'group' or curr_chat['type'] == 'supergroup':
        all_chats_ids = Chat.get_all_chats_ids()
        curr_chat_id = int(curr_chat['id'])
        if text == '/start':
            print('MESSAGE FROM GROUP')
            print(all_chats_ids)

            if not all_chats_ids:
                new_chat = Chat(chat_id=curr_chat_id)
                new_chat.save()
                send_message_to_chat(bot, messages_loc['chat_start'], curr_chat_id)
        elif text == '/end' and curr_chat_id in all_chats_ids:
            curr_chat = Chat.get(Chat.chat_id == curr_chat_id)
            Chat.delete_by_id(curr_chat.id)
            send_message_to_chat(bot, messages_loc['chat_end'], curr_chat_id)


def handle_query(update: Update, call: CallbackContext):
    try:
        callback_data = update.callback_query['message']['reply_markup']['inline_keyboard'][0][0]['callback_data'].split('|')
    except Exception as exc:
        print('CALLBACK EXC ', exc)

    if callback_data[0].startswith("ban"):
        user_id_to_ban = callback_data[1]
        ticket_id = callback_data[2]
        text = get_user_ticket(User.get_user_info(user_id_to_ban, ticket_id))
        user = User.get(User.user_id == user_id_to_ban)
        user.is_active = False
        user.save()
        bot.answer_callback_query(callback_query_id=update['callback_query']['id'],
                                  show_alert=True,
                                  text=messages_loc['alert_ban'])
        bot.edit_message_text(chat_id=update['callback_query']['message']['chat']['id'],
                              text=text,
                              message_id=update['callback_query']['message']['message_id'],
                              reply_markup=make_inline_keyboard(ticket_id, user_id_to_ban, False),
                              parse_mode='HTML')

    elif callback_data[0].startswith("unban"):
        user_id_to_unban = callback_data[1]
        ticket_id = callback_data[2]
        text = get_user_ticket(User.get_user_info(user_id_to_unban, ticket_id))
        user = User.get(User.user_id == user_id_to_unban)
        user.is_active = True
        user.save()
        bot.answer_callback_query(callback_query_id=update['callback_query']['id'],
                                  show_alert=True,
                                  text=messages_loc['alert_unban'])
        bot.edit_message_text(chat_id=update['callback_query']['message']['chat']['id'],
                              text=text,
                              message_id=update['callback_query']['message']['message_id'],
                              reply_markup=make_inline_keyboard(ticket_id, user_id_to_unban, True),
                              parse_mode='HTML')


def start() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    updater = Updater(
        token=API_TOKEN if API_TOKEN else open('token.txt', 'r').read().replace('\n', '').replace(' ', ''),
        use_context=True
    )
    updater.dispatcher.add_handler(CallbackQueryHandler(callback=handle_query))
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start()
