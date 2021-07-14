from peewee import SqliteDatabase, Model, IntegerField, TextField
from playhouse.migrate import SqliteMigrator


connection = SqliteDatabase('ask_support_bot.sqlite')
migrator = SqliteMigrator(connection)


class BaseModel(Model):
    class Meta:
        database = connection


class User(BaseModel):
    id = IntegerField(column_name='id', primary_key=True)
    user_id = IntegerField(column_name='user_id', unique=True)
    alias = TextField(column_name='alias', null=True)
    name = TextField(column_name='name', null=True)
    telephone = TextField(column_name='telephone', null=True)
    address = TextField(column_name='address', null=True)
    reason = TextField(column_name='reason', null=True)

    @staticmethod
    def create_new_user(user_id: int) -> None:
        User.insert(user_id=user_id)

    @staticmethod
    def get_all_users_ids() -> list:
        return [user_id['user_id'] for user_id in User.select(User.user_id).dicts().execute()]


class Chat(BaseModel):
    id = IntegerField(column_name='id', primary_key=True)
    chat_id = IntegerField(column_name='chat_id', unique=True)

    @staticmethod
    def create_new_chat(chat_id: int) -> None:
        Chat.insert(chat_id=chat_id)

    @staticmethod
    def get_all_chats_ids() -> list:
        return [chat_id['chat_id'] for chat_id in Chat.select(Chat.chat_id).dicts().execute()]


connection.create_tables([User, Chat])
