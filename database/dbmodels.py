from playhouse.sqlite_ext import *

db = SqliteExtDatabase('filmbot.db', pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)))


class User(Model):
    uid = BigIntegerField()
    username = CharField()
    history = JSONField(null=True,
                        default={})

    class Meta:
        database = db


if not User.table_exists():
    db.create_tables([User])


class Film(Model):
    title = TextField(null=True)
    file_id = JSONField(null=True,
                        default={})
    download_url = JSONField(null=True,
                             default={})
    quality = JSONField(null=True,
                        default={})

    class Meta:
        database = db


if not Film.table_exists():
    db.create_tables([Film])

