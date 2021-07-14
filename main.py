import os
import logging

from database import User, Chat

from telegram import Bot, Update
from telegram.ext import Updater, CallbackContext, Filters, MessageHandler


bot = Bot(
    token=os.getenv('API_TOKEN')
)


def message_handler(update: Update, context: CallbackContext):
    text = update.message.text
    curr_chat = update.message.chat

    if curr_chat['type'] == 'private':
        curr_user_id = int(curr_chat['id'])
        all_users_ids = User.get_all_users_ids()
        print('MESSAGE FROM USER')
        print(all_users_ids)

        if curr_user_id not in all_users_ids:
            if curr_chat['username']:
                new_user = User(user_id=curr_user_id, alias=curr_chat['username'])
            else:
                new_user = User(user_id=curr_user_id)
            new_user.save()

    elif curr_chat['type'] == 'group':
        if text == '/start':
            all_chats_ids = Chat.get_all_chats_ids()
            print('MESSAGE FROM GROUP')
            print(all_chats_ids)

            curr_chat_id = int(curr_chat['id'])
            if curr_chat_id not in all_chats_ids:
                new_chat = Chat(chat_id=curr_chat_id)
                new_chat.save()

    print(curr_chat)


def start() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    updater = Updater(
        token=os.getenv('API_TOKEN'),
        use_context=True
    )
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start()
