from peewee import SqliteDatabase, Model, IntegerField, TextField, BooleanField
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
    is_active = BooleanField(column_name='is_active')
    is_admin = BooleanField(column_name='is_admin', null=True)
    name = TextField(column_name='name', null=True)
    telephone = TextField(column_name='telephone', null=True)
    address = TextField(column_name='address', null=True)
    reason = TextField(column_name='reason', null=True)

    @staticmethod
    def get_all_users_ids() -> list:
        return [user_id['user_id'] for user_id in User.select(User.user_id).dicts().execute()]

    @staticmethod
    def get_user_info(user_id, ticket_id) -> list:
        user = User.get(User.user_id == user_id)
        info = {
            'alias': user.alias,
            'name': user.name,
            'telephone_number': user.telephone,
            'address': user.address,
            'reason': user.reason,
            'ticket_id': ticket_id
        }
        return info


class Chat(BaseModel):
    id = IntegerField(column_name='id', primary_key=True)
    chat_id = IntegerField(column_name='chat_id', unique=True)

    @staticmethod
    def get_all_chats_ids() -> list:
        return [chat_id['chat_id'] for chat_id in Chat.select(Chat.chat_id).dicts().execute()]


class Ticket(BaseModel):
    id = IntegerField(column_name='id', primary_key=True)
    user_id = IntegerField(column_name='user_id')
    is_available = BooleanField(column_name='is_available')


connection.create_tables([User, Chat, Ticket])
